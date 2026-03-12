"""Assistant 模块路由控制器"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.user.auth import get_current_user_id
from src.agent.chat_factory import chat_factory
from src.assistant.entities import SubmitRequest, SubmitResponse, QueueItem
from src.assistant.worker.agent_worker_manager import agent_worker_manager
from src.assistant.web.stream_manager import stream_manager
from src.common.logger import get_logger

logger = get_logger(__name__)

# 创建路由
router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/submit")
async def submit(
    request: SubmitRequest, current_user_id: str = Depends(get_current_user_id)
) -> SubmitResponse:
    """提交用户消息到处理队列

    Args:
        request: 包含用户输入消息
        current_user_id: 当前用户ID（通过鉴权依赖注入）

    Returns:
        SubmitResponse: 提交结果
    """
    logger.info(f"收到消息提交请求，user_id: {current_user_id}")
    try:
        # 创建用户输入 Chat
        input_chat = chat_factory.create_user_chat(
            user_id=current_user_id, user_input=request.message
        )

        # 创建队列项并入队
        item = QueueItem(user_id=current_user_id, chat=input_chat)
        agent_worker_manager.put(item)

        logger.info(f"消息已入队，user_id: {current_user_id}, chat_id: {input_chat.id}")
        return SubmitResponse(success=True, chat_id=input_chat.id)

    except Exception:
        logger.exception(f"消息提交失败，user_id: {current_user_id}")
        return SubmitResponse(success=False, chat_id="", error="消息提交失败")


@router.get("/stream")
async def stream(
    current_user_id: str = Depends(get_current_user_id),
) -> StreamingResponse:
    """SSE 流式推送对话消息

    建立 SSE 连接，持续接收 Agent 产生的新消息

    Args:
        current_user_id: 当前用户ID（通过鉴权依赖注入）

    Returns:
        StreamingResponse: SSE 流
    """
    logger.info(f"建立 SSE 连接，user_id: {current_user_id}")
    return StreamingResponse(
        stream_manager.subscribe(current_user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
