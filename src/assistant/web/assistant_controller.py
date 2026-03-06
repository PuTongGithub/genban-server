"""Assistant 模块路由控制器"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.user.auth import get_current_user_id
from src.agent.chat_factory import chat_factory
from src.assistant.entities import SubmitRequest, SubmitResponse, QueueItem
from src.assistant.worker.agent_worker_manager import agent_worker_manager
from src.assistant.web.stream_manager import stream_manager


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
    try:
        # 创建用户输入 Chat
        input_chat = chat_factory.create_user_chat(
            user_id=current_user_id, user_input=request.message
        )

        # 创建队列项并入队
        item = QueueItem(user_id=current_user_id, chat=input_chat)
        agent_worker_manager.put(item)

        return SubmitResponse(success=True, chat_id=input_chat.id)

    except Exception as e:
        return SubmitResponse(success=False, chat_id="", error=str(e))


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
    return StreamingResponse(
        stream_manager.subscribe(current_user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
