"""
告警通知发送服务

提供邮件（SMTP）、钉钉机器人、企业微信机器人和飞书机器人四种通知渠道，
以及组合发送的 NotificationService。
"""

import logging
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Dict, List

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


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
        self._db_loaded = False

    async def _load_db_config(self) -> None:
        """从数据库加载 SMTP 配置"""
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
            # 回退到环境变量
            self.server = settings.SMTP_SERVER
            self.port = settings.SMTP_PORT
            self.user = settings.SMTP_USER
            self.password = settings.SMTP_PASSWORD
            self.recipients = settings.ALERT_EMAILS
        self._db_loaded = True

    async def send(self, subject: str, body: str) -> bool:
        """发送邮件通知"""
        await self._load_db_config()
        if not self._is_configured():
            logger.warning("SMTP not configured, skipping email notification")
            return False

        if not self.recipients:
            logger.warning("No alert email recipients configured, skipping")
            return False

        try:
            import smtplib

            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = formataddr(("SQL Monitor Alert", self.user))
            msg["To"] = ", ".join(self.recipients)

            with smtplib.SMTP(self.server, self.port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(self.user, self.password)
                smtp.sendmail(self.user, self.recipients, msg.as_string())

            logger.info("Email notification sent to %s: %s", self.recipients, subject)
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed for user %s", self.user)
            return False
        except smtplib.SMTPException as e:
            logger.error("SMTP error while sending email: %s", e)
            return False
        except OSError as e:
            logger.error("Network error while sending email: %s", e)
            return False

    def _is_configured(self) -> bool:
        return bool(self.server and self.user and self.password)

    async def send_async(self, subject: str, body: str) -> bool:
        """异步发送邮件（在线程池中执行同步 SMTP）"""
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(None, lambda: self._send_sync(subject, body))

    def _send_sync(self, subject: str, body: str) -> bool:
        """同步发送邮件（供线程池调用）"""
        if not self._is_configured():
            return False
        if not self.recipients:
            return False
        try:
            import smtplib
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = formataddr(("SQL Monitor Alert", self.user))
            msg["To"] = ", ".join(self.recipients)
            with smtplib.SMTP(self.server, self.port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(self.user, self.password)
                smtp.sendmail(self.user, self.recipients, msg.as_string())
            logger.info("Email sent to %s: %s", self.recipients, subject)
            return True
        except Exception as e:
            logger.error("Email send failed: %s", e)
            return False

    async def send_welcome_email(self, username: str, password: str, full_name: str = "", to_email: str = "") -> bool:
        """发送新用户欢迎邮件"""
        await self._load_db_config()
        if not self._is_configured():
            return False

        # 优先发送到用户邮箱，其次发送到管理员配置的收件人
        recipients = [to_email] if to_email else self.recipients
        if not recipients:
            return False

        display_name = full_name or username
        subject = "Welcome to SQL Monitor - Account Created"
        body = (
            f"Hello {display_name},\n\n"
            f"Your account has been created for the SQL Monitoring Platform.\n\n"
            f"Login Details:\n"
            f"  URL: {settings.PROJECT_NAME}\n"
            f"  Username: {username}\n"
            f"  Password: {password}\n\n"
            f"Please change your password after first login.\n\n"
            f"If you have any questions, please contact your administrator.\n\n"
            f"---\n"
            f"SQL Monitor Alert System"
        )

        try:
            import smtplib
            from email.header import Header
            from email.utils import formataddr

            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = formataddr(("SQL Monitor Alert", self.user))
            msg["To"] = ", ".join(recipients)

            with smtplib.SMTP(self.server, self.port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(self.user, self.password)
                smtp.sendmail(self.user, recipients, msg.as_string())

            logger.info("Welcome email sent to %s", recipients)
            return True
        except Exception as e:
            logger.error("Failed to send welcome email: %s", e)
            return False


class DingTalkNotifier:
    """钉钉机器人通知发送器

    通过钉钉自定义机器人 Webhook 发送 Markdown 格式消息。
    使用 httpx 异步发送 POST 请求。
    """

    def __init__(self) -> None:
        self.webhook_url: str = settings.DINGTALK_WEBHOOK_URL

    async def send(self, message: str) -> bool:
        """发送钉钉机器人消息

        消息格式为 Markdown 类型。
        https://open.dingtalk.com/document/robots/custom-robot-access

        Args:
            message: Markdown 格式消息内容

        Returns:
            bool: 发送成功返回 True，否则返回 False
        """
        if not self.webhook_url:
            logger.warning("DingTalk webhook URL not configured, skipping")
            return False

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "SQL Monitor Alert",
                "text": message,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json=payload)
                resp.raise_for_status()
                result = resp.json()

                if result.get("errcode") == 0:
                    logger.info("DingTalk notification sent successfully")
                    return True

                logger.error(
                    "DingTalk API returned error: errcode=%s, errmsg=%s",
                    result.get("errcode"),
                    result.get("errmsg"),
                )
                return False

        except httpx.TimeoutException:
            logger.error("DingTalk webhook request timed out")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(
                "DingTalk webhook returned HTTP %s: %s",
                e.response.status_code,
                e.response.text,
            )
            return False
        except httpx.RequestError as e:
            logger.error("DingTalk webhook request failed: %s", e)
            return False


class WeComNotifier:
    """企业微信机器人通知发送器

    通过企业微信群机器人 Webhook 发送 Markdown 格式消息。
    使用 httpx 异步发送 POST 请求。
    https://developer.work.weixin.qq.com/document/path/91770
    """

    def __init__(self) -> None:
        self.webhook_url: str = getattr(settings, "WECOM_WEBHOOK_URL", "")

    async def send(self, message: str) -> bool:
        """发送企业微信机器人消息

        消息格式为 Markdown 类型。

        Args:
            message: Markdown 格式消息内容

        Returns:
            bool: 发送成功返回 True，否则返回 False
        """
        if not self.webhook_url:
            logger.warning("WeCom webhook URL not configured, skipping")
            return False

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": message,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json=payload)
                resp.raise_for_status()
                result = resp.json()

                if result.get("errcode") == 0:
                    logger.info("WeCom notification sent successfully")
                    return True

                logger.error(
                    "WeCom API returned error: errcode=%s, errmsg=%s",
                    result.get("errcode"),
                    result.get("errmsg"),
                )
                return False

        except httpx.TimeoutException:
            logger.error("WeCom webhook request timed out")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(
                "WeCom webhook returned HTTP %s: %s",
                e.response.status_code,
                e.response.text,
            )
            return False
        except httpx.RequestError as e:
            logger.error("WeCom webhook request failed: %s", e)
            return False


class FeishuNotifier:
    """飞书机器人通知发送器

    通过飞书自定义机器人 Webhook 发送富文本消息。
    使用 httpx 异步发送 POST 请求。
    https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
    """

    def __init__(self) -> None:
        self.webhook_url: str = getattr(settings, "FEISHU_WEBHOOK_URL", "")

    async def send(self, message: str) -> bool:
        """发送飞书机器人消息

        消息格式为 Interactive（卡片消息），支持 Markdown 子集。

        Args:
            message: Markdown 格式消息内容

        Returns:
            bool: 发送成功返回 True，否则返回 False
        """
        if not self.webhook_url:
            logger.warning("Feishu webhook URL not configured, skipping")
            return False

        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "SQL Monitor Alert",
                    },
                    "template": "red",
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": message,
                    }
                ],
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

                logger.error(
                    "Feishu API returned error: code=%s, msg=%s",
                    result.get("code"),
                    result.get("msg"),
                )
                return False

        except httpx.TimeoutException:
            logger.error("Feishu webhook request timed out")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(
                "Feishu webhook returned HTTP %s: %s",
                e.response.status_code,
                e.response.text,
            )
            return False
        except httpx.RequestError as e:
            logger.error("Feishu webhook request failed: %s", e)
            return False


class NotificationService:
    """组合通知服务

    整合 EmailNotifier、DingTalkNotifier、WeComNotifier 和 FeishuNotifier，
    提供一次性发送所有渠道通知和按渠道单独发送的便捷方法。
    """

    def __init__(self) -> None:
        self.email_notifier = EmailNotifier()
        self.dingtalk_notifier = DingTalkNotifier()
        self.wecom_notifier = WeComNotifier()
        self.feishu_notifier = FeishuNotifier()

    async def send_webhook(self, channel: str, message: str) -> bool:
        """按指定渠道发送 Webhook 通知

        Args:
            channel: 通知渠道 ("dingtalk" / "wecom" / "feishu")
            message: Markdown 格式消息内容

        Returns:
            bool: 发送成功返回 True，否则返回 False
        """
        if channel == "dingtalk":
            return await self.dingtalk_notifier.send(message)
        elif channel == "wecom":
            return await self.wecom_notifier.send(message)
        elif channel == "feishu":
            return await self.feishu_notifier.send(message)
        else:
            logger.warning("Unknown webhook channel: %s", channel)
            return False

    async def notify_all(self, subject: str, body: str) -> Dict[str, bool]:
        """同时发送所有渠道通知

        Args:
            subject: 通知主题（邮件主题/钉钉标题）
            body: 通知正文（纯文本/Markdown）

        Returns:
            dict: 各渠道发送结果，格式:
                {"email": True/False, "dingtalk": True/False, "wecom": True/False, "feishu": True/False}
        """
        result: Dict[str, bool] = {
            "email": False,
            "dingtalk": False,
            "wecom": False,
            "feishu": False,
        }

        # 邮件异步发送（从 DB 加载配置）
        result["email"] = await self.email_notifier.send(subject, body)

        # 钉钉异步发送
        result["dingtalk"] = await self.dingtalk_notifier.send(body)

        # 企业微信异步发送
        result["wecom"] = await self.wecom_notifier.send(body)

        # 飞书异步发送
        result["feishu"] = await self.feishu_notifier.send(body)

        return result
