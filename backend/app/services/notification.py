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
    """

    def __init__(self) -> None:
        self.server: str = settings.SMTP_SERVER
        self.port: int = settings.SMTP_PORT
        self.user: str = settings.SMTP_USER
        self.password: str = settings.SMTP_PASSWORD
        self.recipients: List[str] = settings.ALERT_EMAILS

    def send(self, subject: str, body: str) -> bool:
        """发送邮件通知

        Args:
            subject: 邮件主题
            body: 邮件正文（纯文本格式）

        Returns:
            bool: 发送成功返回 True，否则返回 False
        """
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

            logger.info(
                "Email notification sent to %s: %s", self.recipients, subject
            )
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
        """检查 SMTP 配置是否完整

        Returns:
            bool: 配置完整返回 True
        """
        return bool(self.server and self.user and self.password)


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

        # 邮件同步发送
        result["email"] = self.email_notifier.send(subject, body)

        # 钉钉异步发送
        result["dingtalk"] = await self.dingtalk_notifier.send(body)

        # 企业微信异步发送
        result["wecom"] = await self.wecom_notifier.send(body)

        # 飞书异步发送
        result["feishu"] = await self.feishu_notifier.send(body)

        return result
