"""
SMTP 邮件测试路由
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.notification import EmailNotifier

router = APIRouter()


class SmtpTestRequest(BaseModel):
    server: str
    port: int = 587
    user: str
    password: str
    recipients: str = ""


@router.post("/test", summary="测试 SMTP 邮件发送")
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

    subject = "SQL Monitor - SMTP Test"
    body = (
        "This is a test email from SQL Monitoring Platform.\n\n"
        "If you received this email, SMTP is configured correctly.\n\n"
        "---\nSQL Monitor Alert System"
    )

    import asyncio
    success = await asyncio.get_event_loop().run_in_executor(
        None, lambda: notifier._send_sync(subject, body)
    )

    if success:
        return {"success": True, "message": "Test email sent successfully"}
    return {"success": False, "error": "Failed to send test email. Check SMTP settings."}
