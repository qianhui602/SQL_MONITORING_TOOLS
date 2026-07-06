"""
告警通知发送服务

提供邮件（SMTP）、钉钉机器人、企业微信机器人和飞书机器人四种通知渠道，
以及组合发送的 NotificationService。
"""

import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Dict, List

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# ============================================================
# HTML 邮件模板
# ============================================================

_HTML_HEAD = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:'Microsoft YaHei','Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:32px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">
"""

_HTML_FOOT = """\
</table>
<p style="text-align:center;color:#999;font-size:12px;margin-top:16px;">
  SQL Monitor &mdash; Automated Notification / 自动通知
</p>
</td></tr></table></body></html>"""


def _html_header(title_zh: str, title_en: str, color: str = "#1890ff") -> str:
    return (
        f'<tr><td style="background:{color};padding:28px 32px;">'
        f'<h1 style="margin:0;color:#fff;font-size:20px;font-weight:600;">'
        f'{title_zh}</h1>'
        f'<p style="margin:6px 0 0;color:rgba(255,255,255,0.85);font-size:13px;">'
        f'{title_en}</p></td></tr>'
    )


def _html_body_row(label_zh: str, label_en: str, value: str) -> str:
    return (
        f'<tr><td style="padding:12px 32px;border-bottom:1px solid #f0f0f0;">'
        f'<span style="color:#888;font-size:13px;">{label_zh} / {label_en}</span><br>'
        f'<span style="color:#222;font-size:15px;font-weight:500;">{value}</span>'
        f'</td></tr>'
    )


def _html_section(title_zh: str, title_en: str) -> str:
    return (
        f'<tr><td style="padding:20px 32px 8px;">'
        f'<h2 style="margin:0;font-size:15px;color:#333;border-left:3px solid #1890ff;padding-left:10px;">'
        f'{title_zh}<span style="font-weight:400;color:#999;font-size:12px;margin-left:6px;">{title_en}</span>'
        f'</h2></td></tr>'
    )


def _html_button(url: str, text_zh: str, text_en: str) -> str:
    return (
        f'<tr><td style="padding:20px 32px;text-align:center;">'
        f'<a href="{url}" style="display:inline-block;padding:12px 32px;background:#1890ff;color:#fff;'
        f'text-decoration:none;border-radius:6px;font-size:14px;font-weight:500;">'
        f'{text_zh} / {text_en}</a></td></tr>'
    )


def _html_footer_note() -> str:
    return (
        f'<tr><td style="padding:16px 32px 24px;">'
        f'<p style="margin:0;color:#999;font-size:12px;line-height:1.6;">'
        f'&#9888; 请妥善保管您的登录信息，请勿转发给他人。<br>'
        f'Please keep your login credentials secure and do not share them.</p></td></tr>'
    )


# ============================================================
# EmailNotifier
# ============================================================

class EmailNotifier:
    """邮件通知发送器

    使用 SMTP 协议通过配置的邮件服务器发送告警邮件。
    支持 TLS 加密，默认端口 587。
    优先从数据库配置读取 SMTP 设置，回退到环境变量。
    """

    def __init__(self) -> None:
        self.server: str = ""
        self.port: int = 587
        self.user: str = ""
        self.password: str = ""
        self.recipients: List[str] = []
        self.frontend_url: str = ""
        self._db_loaded = False

    async def _load_db_config(self) -> None:
        """从数据库加载 SMTP 和前端 URL 配置"""
        if self._db_loaded:
            return
        try:
            from app.database import async_session_factory
            from sqlalchemy import text

            async with async_session_factory() as session:
                result = await session.execute(
                    text("SELECT config_key, config_value FROM system_configs WHERE config_key IN ('smtp_server', 'smtp_port', 'smtp_user', 'smtp_password', 'smtp_recipients', 'smtp_enabled', 'frontend_url')")
                )
                config = {row[0]: row[1] for row in result}

                self.frontend_url = config.get("frontend_url", "") or getattr(settings, "FRONTEND_URL", "")

                if config.get("smtp_enabled", "false").lower() != "true":
                    self._db_loaded = True
                    return
                self.server = config.get("smtp_server", "")
                self.port = int(config.get("smtp_port", "587"))
                self.user = config.get("smtp_user", "")
                self.password = config.get("smtp_password", "")
                raw_recipients = config.get("smtp_recipients", "")
                self.recipients = [r.strip() for r in raw_recipients.split(",") if r.strip()]
        except Exception as e:
            logger.warning("Failed to load config from DB: %s", e)
            self.server = settings.SMTP_SERVER
            self.port = settings.SMTP_PORT
            self.user = settings.SMTP_USER
            self.password = settings.SMTP_PASSWORD
            self.recipients = settings.ALERT_EMAILS
            self.frontend_url = getattr(settings, "FRONTEND_URL", "")
        self._db_loaded = True

    def _is_configured(self) -> bool:
        return bool(self.server and self.user and self.password)

    def _build_message(self, subject: str, html_body: str, recipients: List[str]) -> MIMEMultipart:
        """构建 HTML 邮件"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = formataddr(("SQL Monitor", self.user))
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        return msg

    def _send_msg(self, msg: MIMEMultipart, recipients: List[str]) -> bool:
        """同步发送邮件"""
        try:
            import smtplib
            with smtplib.SMTP(self.server, self.port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(self.user, self.password)
                smtp.sendmail(self.user, recipients, msg.as_string())
            return True
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed for user %s", self.user)
            return False
        except smtplib.SMTPException as e:
            logger.error("SMTP error: %s", e)
            return False
        except OSError as e:
            logger.error("Network error: %s", e)
            return False

    async def send(self, subject: str, html_body: str) -> bool:
        """发送 HTML 邮件通知"""
        await self._load_db_config()
        if not self._is_configured():
            logger.warning("SMTP not configured, skipping email notification")
            return False
        if not self.recipients:
            logger.warning("No alert email recipients configured, skipping")
            return False

        msg = self._build_message(subject, html_body, self.recipients)
        ok = self._send_msg(msg, self.recipients)
        if ok:
            logger.info("Email sent to %s: %s", self.recipients, subject)
        return ok

    async def send_welcome_email(self, username: str, full_name: str = "", to_email: str = "", base_url: str = "") -> bool:
        """发送新用户欢迎邮件（中英双语 HTML）"""
        await self._load_db_config()
        if not self._is_configured():
            return False

        recipients = [to_email] if to_email else self.recipients
        if not recipients:
            return False

        display_name = full_name or username
        subject = f"SQL Monitor 账号已创建 / Account Created - {display_name}"
        effective_url = (self.frontend_url or base_url or "").rstrip("/")
        reset_url = f"{effective_url}/reset-password" if effective_url else ""

        html = _HTML_HEAD
        html += _html_header("欢迎加入 SQL Monitor", "Welcome to SQL Monitor", "#1890ff")
        html += _html_section("账号信息", "Account Information")
        html += _html_body_row("姓名", "Name", display_name)
        html += _html_body_row("用户名", "Username", username)
        html += _html_section("设置密码", "Set Your Password")
        html += f'<tr><td style="padding:12px 32px;">'
        html += f'<p style="margin:0;color:#666;font-size:13px;line-height:1.6;">'
        html += f'请点击下方按钮设置您的登录密码。<br>'
        html += f'Please click the button below to set your login password.</p></td></tr>'
        html += _html_button(reset_url, "设置密码", "Set Password")
        html += _html_footer_note()
        html += _HTML_FOOT

        msg = self._build_message(subject, html, recipients)
        ok = self._send_msg(msg, recipients)
        if ok:
            logger.info("Welcome email sent to %s", recipients)
        else:
            logger.error("Failed to send welcome email to %s", recipients)
        return ok

    async def send_password_reset_email(self, username: str, email: str, token: str, full_name: str = "", base_url: str = "") -> bool:
        """发送密码重置邮件（中英双语 HTML）"""
        await self._load_db_config()
        if not self._is_configured():
            return False

        recipients = [email]
        if not recipients:
            return False

        display_name = full_name or username
        subject = f"SQL Monitor 密码重置 / Password Reset - {display_name}"
        effective_url = (self.frontend_url or base_url or "").rstrip("/")
        if effective_url:
            reset_url = f"{effective_url}/reset-password?token={token}"
        else:
            logger.warning("frontend_url not configured, password reset link will be empty in email")
            reset_url = ""

        html = _HTML_HEAD
        html += _html_header("密码重置", "Password Reset", "#fa8c16")
        html += _html_section("尊敬的用户", "Dear User")
        html += f'<tr><td style="padding:12px 32px;">'
        html += f'<p style="margin:0;color:#666;font-size:13px;line-height:1.6;">'
        html += f'您收到此邮件是因为有人请求重置您的 SQL Monitor 账户密码。<br>'
        html += f'如果这不是您本人操作，请忽略此邮件。</p></td></tr>'
        html += _html_section("重置密码", "Reset Password")
        html += f'<tr><td style="padding:12px 32px;">'
        html += f'<p style="margin:0;color:#666;font-size:13px;line-height:1.6;">'
        html += f'请点击下方按钮重置您的密码，此链接将在 30 分钟后失效。<br>'
        html += f'Please click the button below to reset your password. This link will expire in 30 minutes.</p></td></tr>'
        html += _html_button(reset_url, "重置密码", "Reset Password")
        html += _html_section("用户名", "Username")
        html += _html_body_row("用户名", "Username", username)
        html += _html_footer_note()
        html += _HTML_FOOT

        msg = self._build_message(subject, html, recipients)
        ok = self._send_msg(msg, recipients)
        if ok:
            logger.info("Password reset email sent to %s", recipients)
        else:
            logger.error("Failed to send password reset email to %s", recipients)
        return ok

    async def send_alert_email(self, subject: str, alert_type: str, alert_detail: str,
                               server_address: str = "", severity: str = "warning") -> bool:
        """发送告警通知邮件（中英双语 HTML）"""
        await self._load_db_config()
        if not self._is_configured():
            return False
        if not self.recipients:
            return False

        color_map = {"critical": "#f5222d", "warning": "#fa8c16", "info": "#1890ff"}
        color = color_map.get(severity, "#fa8c16")
        severity_zh = {"critical": "严重", "warning": "警告", "info": "信息"}.get(severity, "警告")
        severity_en = severity.capitalize()

        html = _HTML_HEAD
        html += _html_header(f"{severity_zh}告警 / {severity_en} Alert", alert_type, color)
        html += _html_section("告警类型", "Alert Type")
        html += _html_body_row("类型", "Type", alert_type)
        if server_address:
            html += _html_body_row("服务器", "Server", server_address)
        html += _html_section("告警详情", "Details")
        html += f'<tr><td style="padding:12px 32px 24px;">'
        html += f'<pre style="background:#f8f8f8;padding:16px;border-radius:8px;font-size:13px;'
        html += f'color:#333;line-height:1.6;overflow-x:auto;white-space:pre-wrap;">'
        html += f'{alert_detail}</pre></td></tr>'
        html += _HTML_FOOT

        msg = self._build_message(subject, html, self.recipients)
        ok = self._send_msg(msg, self.recipients)
        if ok:
            logger.info("Alert email sent to %s: %s", self.recipients, subject)
        return ok


# ============================================================
# Webhook Notifiers (DingTalk / WeCom / Feishu)
# ============================================================

class DingTalkNotifier:
    """钉钉机器人通知发送器"""

    def __init__(self) -> None:
        self.webhook_url: str = settings.DINGTALK_WEBHOOK_URL

    async def send(self, message: str) -> bool:
        if not self.webhook_url:
            return False
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": "SQL Monitor Alert", "text": message},
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json=payload)
                resp.raise_for_status()
                result = resp.json()
                if result.get("errcode") == 0:
                    logger.info("DingTalk notification sent successfully")
                    return True
                logger.error("DingTalk API error: %s", result.get("errmsg"))
                return False
        except Exception as e:
            logger.error("DingTalk send failed: %s", e)
            return False


class WeComNotifier:
    """企业微信机器人通知发送器"""

    def __init__(self) -> None:
        self.webhook_url: str = getattr(settings, "WECOM_WEBHOOK_URL", "")

    async def send(self, message: str) -> bool:
        if not self.webhook_url:
            return False
        payload = {"msgtype": "markdown", "markdown": {"content": message}}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json=payload)
                resp.raise_for_status()
                result = resp.json()
                if result.get("errcode") == 0:
                    logger.info("WeCom notification sent successfully")
                    return True
                logger.error("WeCom API error: %s", result.get("errmsg"))
                return False
        except Exception as e:
            logger.error("WeCom send failed: %s", e)
            return False


class FeishuNotifier:
    """飞书机器人通知发送器"""

    def __init__(self) -> None:
        self.webhook_url: str = getattr(settings, "FEISHU_WEBHOOK_URL", "")

    async def send(self, message: str) -> bool:
        if not self.webhook_url:
            return False
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": "SQL Monitor 告警 / Alert"},
                    "template": "red",
                },
                "elements": [{"tag": "markdown", "content": message}],
            },
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json=payload)
                resp.raise_for_status()
                result = resp.json()
                if result.get("code") == 0:
                    logger.info("Feishu notification sent successfully")
                    return True
                logger.error("Feishu API error: %s", result.get("msg"))
                return False
        except Exception as e:
            logger.error("Feishu send failed: %s", e)
            return False


# ============================================================
# NotificationService
# ============================================================

class NotificationService:
    """组合通知服务"""

    def __init__(self) -> None:
        self.email_notifier = EmailNotifier()
        self.dingtalk_notifier = DingTalkNotifier()
        self.wecom_notifier = WeComNotifier()
        self.feishu_notifier = FeishuNotifier()

    async def send_webhook(self, channel: str, message: str) -> bool:
        if channel == "dingtalk":
            return await self.dingtalk_notifier.send(message)
        elif channel == "wecom":
            return await self.wecom_notifier.send(message)
        elif channel == "feishu":
            return await self.feishu_notifier.send(message)
        return False

    async def notify_all(self, subject: str, body: str, html_body: str = "") -> Dict[str, bool]:
        result: Dict[str, bool] = {"email": False, "dingtalk": False, "wecom": False, "feishu": False}
        # 邮件（优先 HTML）
        if html_body:
            result["email"] = await self.email_notifier.send(subject, html_body)
        else:
            result["email"] = await self.email_notifier.send(subject, f"<pre>{body}</pre>")
        result["dingtalk"] = await self.dingtalk_notifier.send(body)
        result["wecom"] = await self.wecom_notifier.send(body)
        result["feishu"] = await self.feishu_notifier.send(body)
        return result
