"""
SMTP 閭欢娴嬭瘯璺敱
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.notification import EmailNotifier, _HTML_HEAD, _HTML_FOOT, _html_header, _html_body_row

router = APIRouter()


class SmtpTestRequest(BaseModel):
    server: str
    port: int = 587
    user: str
    password: str
    recipients: str = ""


@router.post("/test", summary="娴嬭瘯 SMTP 閭欢鍙戦€?)
async def test_smtp(
    payload: SmtpTestRequest,
    _: User = Depends(get_current_user),
):
    notifier = EmailNotifier()
    notifier.server = payload.server
    notifier.port = payload.port
    notifier.user = payload.user
    notifier.password = payload.password
    notifier.recipients = [r.strip() for r in payload.recipients.split(",") if r.strip()]
    notifier._db_loaded = True

    subject = "SQL Monitor SMTP 杩炴帴娴嬭瘯 / Connection Test"

    html = _HTML_HEAD
    html += _html_header("SMTP 杩炴帴娴嬭瘯", "SMTP Connection Test", "#52c41a")
    html += _html_body_row("鐘舵€?, "Status", '<span style="color:#52c41a;font-weight:600;">&#10003; SMTP 閰嶇疆姝ｇ‘ / Configuration OK</span>')
    html += _html_body_row("鏈嶅姟鍣?, "Server", f"{payload.server}:{payload.port}")
    html += _html_body_row("鍙戜欢浜?, "From", payload.user)
    html += (
        '<tr><td style="padding:20px 32px 24px;">'
        '<p style="margin:0;color:#666;font-size:13px;line-height:1.6;">'
        '姝ら偖浠剁敱 SQL Monitor 绯荤粺鑷姩鍙戦€侊紝鐢ㄤ簬楠岃瘉 SMTP 閭欢鏈嶅姟閰嶇疆鏄惁姝ｇ‘銆?br>'
        'This email was sent automatically to verify your SMTP configuration.</p></td></tr>'
    )
    html += _HTML_FOOT

    import asyncio
    success = await asyncio.get_event_loop().run_in_executor(
        None, lambda: notifier._send_sync(subject, html)
    )

    if success:
        return {"success": True, "message": "娴嬭瘯閭欢鍙戦€佹垚鍔?/ Test email sent successfully"}
    return {"success": False, "error": "鍙戦€佸け璐ワ紝璇锋鏌?SMTP 閰嶇疆 / Failed. Check SMTP settings."}
