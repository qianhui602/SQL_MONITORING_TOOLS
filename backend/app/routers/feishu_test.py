"""
飞书应用通知测试路由
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.user import User
from app.services.auth_service import require_admin
from app.services.notification import FeishuAppNotifier

router = APIRouter()


class FeishuTestRequest(BaseModel):
    """飞书应用通知测试请求体"""

    app_id: str = ""
    app_secret: str = ""
    receive_open_id: str = ""


@router.post("/test", summary="测试飞书应用通知")
async def test_feishu(
    payload: FeishuTestRequest,
    _: User = Depends(require_admin),
):
    """使用传入的配置发送一条测试消息，验证飞书自建应用通知是否可用。"""
    if not payload.app_id or not payload.app_secret or not payload.receive_open_id:
        raise HTTPException(
            status_code=400,
            detail="请填写 App ID、App Secret 和接收人 open_id",
        )

    notifier = FeishuAppNotifier()
    notifier.enabled = True
    notifier.app_id = payload.app_id
    notifier.app_secret = payload.app_secret
    notifier.receive_open_id = payload.receive_open_id
    notifier._db_loaded = True

    test_msg = (
        "## 飞书应用通知测试 / Test\n\n"
        "- **状态**: 配置验证成功\n"
        "- **时间**: 请以收到此消息为准\n\n"
        "此消息由 SQL Monitor 系统自动发送，用于验证飞书应用通知配置是否正确。"
    )
    success, message = await notifier.send_test(test_msg)
    if success:
        return {"success": True, "message": message}
    return {"success": False, "error": message}
