"""
鍛婅閫氱煡鍙戦€佹湇鍔?
鎻愪緵閭欢锛圫MTP锛夈€侀拤閽夋満鍣ㄤ汉銆佷紒涓氬井淇℃満鍣ㄤ汉鍜岄涔︽満鍣ㄤ汉鍥涚閫氱煡娓犻亾锛?浠ュ強缁勫悎鍙戦€佺殑 NotificationService銆?"""

import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Dict, List

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# ============================================================
# HTML 閭欢妯℃澘
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
  SQL Monitor &mdash; Automated Notification / 鑷姩閫氱煡
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
        f'&#9888; 璇峰Ε鍠勪繚绠℃偍鐨勭櫥褰曚俊鎭紝璇峰嬁杞彂缁欎粬浜恒€?br>'
        f'Please keep your login credentials secure and do not share them.</p></td></tr>'
    )


# ============================================================
# EmailNotifier
# ============================================================

class EmailNotifier:
    """閭欢閫氱煡鍙戦€佸櫒

    浣跨敤 SMTP 鍗忚閫氳繃閰嶇疆鐨勯偖浠舵湇鍔″櫒鍙戦€佸憡璀﹂偖浠躲€?    鏀寔 TLS 鍔犲瘑锛岄粯璁ょ鍙?587銆?    浼樺厛浠庢暟鎹簱閰嶇疆璇诲彇 SMTP 璁剧疆锛屽洖閫€鍒扮幆澧冨彉閲忋€?    """

    def __init__(self) -> None:
        self.server: str = ""
        self.port: int = 587
        self.user: str = ""
        self.password: str = ""
        self.recipients: List[str] = []
        self._db_loaded = False

    async def _load_db_config(self) -> None:
        """浠庢暟鎹簱鍔犺浇 SMTP 閰嶇疆"""
        if self._db_loaded:
            return
        try:
            from app.database import async_session_factory
            from sqlalchemy import text

            async with async_session_factory() as session:
                result = await session.execute(
                    text("SELECT config_key, config_value FROM system_configs WHERE config_key IN ('smtp_server', 'smtp_port', 'smtp_user', 'smtp_password', 'smtp_recipients', 'smtp_enabled')")
                )
                config = {row[0]: row[1] for row in result}
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
            logger.warning("Failed to load SMTP config from DB: %s", e)
            self.server = settings.SMTP_SERVER
            self.port = settings.SMTP_PORT
            self.user = settings.SMTP_USER
            self.password = settings.SMTP_PASSWORD
            self.recipients = settings.ALERT_EMAILS
        self._db_loaded = True

    def _is_configured(self) -> bool:
        return bool(self.server and self.user and self.password)

    def _build_message(self, subject: str, html_body: str, recipients: List[str]) -> MIMEMultipart:
        """鏋勫缓 HTML 閭欢"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = formataddr(("SQL Monitor", self.user))
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        return msg

    def _send_msg(self, msg: MIMEMultipart, recipients: List[str]) -> bool:
        """鍚屾鍙戦€侀偖浠?""
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
        """鍙戦€?HTML 閭欢閫氱煡"""
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

    async def send_welcome_email(self, username: str, password: str, full_name: str = "", to_email: str = "") -> bool:
        """鍙戦€佹柊鐢ㄦ埛娆㈣繋閭欢锛堜腑鑻卞弻璇?HTML锛?""
        await self._load_db_config()
        if not self._is_configured():
            return False

        recipients = [to_email] if to_email else self.recipients
        if not recipients:
            return False

        display_name = full_name or username
        subject = f"SQL Monitor 璐﹀彿宸插垱寤?/ Account Created - {display_name}"
        login_url = getattr(settings, "PROJECT_NAME", "SQL Monitor")

        html = _HTML_HEAD
        html += _html_header("娆㈣繋鍔犲叆 SQL Monitor", "Welcome to SQL Monitor", "#1890ff")
        html += _html_section("璐﹀彿淇℃伅", "Account Information")
        html += _html_body_row("濮撳悕", "Name", display_name)
        html += _html_body_row("鐢ㄦ埛鍚?, "Username", username)
        html += _html_body_row("鍒濆瀵嗙爜", "Initial Password",
                               f'<span style="background:#fff1f0;padding:3px 8px;border-radius:4px;color:#cf1322;font-family:monospace;">{password}</span>')
        html += _html_section("鐧诲綍鍦板潃", "Login URL")
        html += _html_button(login_url, "绔嬪嵆鐧诲綍", "Login Now")
        html += _html_footer_note()
        html += _HTML_FOOT

        msg = self._build_message(subject, html, recipients)
        ok = self._send_msg(msg, recipients)
        if ok:
            logger.info("Welcome email sent to %s", recipients)
        else:
            logger.error("Failed to send welcome email to %s", recipients)
        return ok

    async def send_alert_email(self, subject: str, alert_type: str, alert_detail: str,
                               server_address: str = "", severity: str = "warning") -> bool:
        """鍙戦€佸憡璀﹂€氱煡閭欢锛堜腑鑻卞弻璇?HTML锛?""
        await self._load_db_config()
        if not self._is_configured():
            return False
        if not self.recipients:
            return False

        color_map = {"critical": "#f5222d", "warning": "#fa8c16", "info": "#1890ff"}
        color = color_map.get(severity, "#fa8c16")
        severity_zh = {"critical": "涓ラ噸", "warning": "璀﹀憡", "info": "淇℃伅"}.get(severity, "璀﹀憡")
        severity_en = severity.capitalize()

        html = _HTML_HEAD
        html += _html_header(f"{severity_zh}鍛婅 / {severity_en} Alert", alert_type, color)
        html += _html_section("鍛婅绫诲瀷", "Alert Type")
        html += _html_body_row("绫诲瀷", "Type", alert_type)
        if server_address:
            html += _html_body_row("鏈嶅姟鍣?, "Server", server_address)
        html += _html_section("鍛婅璇︽儏", "Details")
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
    """閽夐拤鏈哄櫒浜洪€氱煡鍙戦€佸櫒"""

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
    """浼佷笟寰俊鏈哄櫒浜洪€氱煡鍙戦€佸櫒"""

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
    """椋炰功鏈哄櫒浜洪€氱煡鍙戦€佸櫒"""

    def __init__(self) -> None:
        self.webhook_url: str = getattr(settings, "FEISHU_WEBHOOK_URL", "")

    async def send(self, message: str) -> bool:
        if not self.webhook_url:
            return False
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": "SQL Monitor 鍛婅 / Alert"},
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
    """缁勫悎閫氱煡鏈嶅姟"""

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
        # 閭欢锛堜紭鍏?HTML锛?        if html_body:
            result["email"] = await self.email_notifier.send(subject, html_body)
        else:
            result["email"] = await self.email_notifier.send(subject, f"<pre>{body}</pre>")
        result["dingtalk"] = await self.dingtalk_notifier.send(body)
        result["wecom"] = await self.wecom_notifier.send(body)
        result["feishu"] = await self.feishu_notifier.send(body)
        return result
