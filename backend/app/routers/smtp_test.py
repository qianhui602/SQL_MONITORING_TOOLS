"""
SMTP 邮件测试路由
"""

import ipaddress
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.services.auth_service import require_admin
from app.services.notification import EmailNotifier, _HTML_HEAD, _HTML_FOOT, _html_header, _html_body_row

router = APIRouter()


class SmtpTestRequest(BaseModel):
    server: str
    port: int = 587
    user: str
    password: str
    recipients: str = ""


def _is_internal_address(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        internal_hostnames = {
            "localhost", "127.0.0.1", "0.0.0.0",
            "localhost.localdomain", "local",
        }
        return host.lower() in internal_hostnames


@router.post("/test", summary="测试 SMTP 邮件发送")
async def test_smtp(
    payload: SmtpTestRequest,
    _: User = Depends(require_admin),
):
    if _is_internal_address(payload.server):
        raise HTTPException(status_code=400, detail="不允许使用内网地址作为 SMTP 服务器")

    notifier = EmailNotifier()
    notifier.server = payload.server
    notifier.port = payload.port
    notifier.user = payload.user
    notifier.password = payload.password
    notifier.recipients = [r.strip() for r in payload.recipients.split(",") if r.strip()]
    notifier._db_loaded = True

    subject = "SQL Monitor SMTP 连接测试 / Connection Test"

    html = _HTML_HEAD
    html += _html_header("SMTP 连接测试", "SMTP Connection Test", "#52c41a")
    html += _html_body_row("状态", "Status", '<span style="color:#52c41a;font-weight:600;">&#10003; SMTP 配置正确 / Configuration OK</span>')
    html += _html_body_row("服务器", "Server", f"{payload.server}:{payload.port}")
    html += _html_body_row("发件人", "From", payload.user)
    html += (
        '<tr><td style="padding:20px 32px 24px;">'
        '<p style="margin:0;color:#666;font-size:13px;line-height:1.6;">'
        '此邮件由 SQL Monitor 系统自动发送，用于验证 SMTP 邮件服务配置是否正确。<br>'
        'This email was sent automatically to verify your SMTP configuration.</p></td></tr>'
    )
    html += _HTML_FOOT

    import asyncio
    success = await asyncio.get_event_loop().run_in_executor(
        None, lambda: notifier._send_msg(notifier._build_message(subject, html, notifier.recipients), notifier.recipients)
    )

    if success:
        return {"success": True, "message": "测试邮件发送成功 / Test email sent successfully"}
    return {"success": False, "error": "发送失败，请检查 SMTP 配置 / Failed. Check SMTP settings."}
