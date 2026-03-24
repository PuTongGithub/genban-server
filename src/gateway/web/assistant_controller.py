"""Assistant 模块路由控制器"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.agent.chat_factory import chat_factory
from src.assistant.assistant_manager import assistant_manager
from src.common.logger import get_logger
from src.gateway.web.entities import (
    HistoryChatItem,
    HistoryRequest,
    HistoryResponse,
    StopResponse,
    SubmitRequest,
    SubmitResponse,
)
from src.gateway.web.sse_formatter import sse_formatter
from src.gateway.web.stream_manager import stream_manager
from src.modules.conversation.chat.chat_repository import chat_repository
from src.user.auth import get_current_user_id

logger = get_logger(__name__)

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
        assistant_manager.submit_chat(user_id=current_user_id, chat=input_chat)

        logger.info(f"消息已提交，user_id: {current_user_id}, chat_id: {input_chat.id}")
        return SubmitResponse(success=True, chat_id=input_chat.id)

    except Exception:
        logger.exception(f"消息提交失败，user_id: {current_user_id}")
        return SubmitResponse(success=False, chat_id="", error="消息提交失败")


@router.post("/stop")
async def stop(current_user_id: str = Depends(get_current_user_id)) -> StopResponse:
    """停止当前对话

    Args:
        current_user_id: 当前用户ID（通过鉴权依赖注入）

    Returns:
        StopResponse: 停止结果
    """
    logger.info(f"收到停止请求，user_id: {current_user_id}")
    try:
        # 创建停止 Chat
        stop_chat = chat_factory.create_stop_chat()

        # 提交到处理队列
        assistant_manager.submit_chat(user_id=current_user_id, chat=stop_chat)

        logger.info(f"停止请求已提交，user_id: {current_user_id}, chat_id: {stop_chat.id}")
        return StopResponse(success=True, chat_id=stop_chat.id)

    except Exception:
        logger.exception(f"停止请求提交失败，user_id: {current_user_id}")
        return StopResponse(success=False, chat_id="", error="停止请求提交失败")


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


@router.post("/history")
async def get_history(
    request: HistoryRequest,
    current_user_id: str = Depends(get_current_user_id),
) -> HistoryResponse:
    """查询用户历史对话内容

    以 chat_id 为起点往前查询 count 条历史对话，若 chat_id 为空则返回最新的 count 条

    Args:
        request: 查询历史对话请求
        current_user_id: 当前用户ID（通过鉴权依赖注入）

    Returns:
        HistoryResponse: 历史对话列表
    """
    # 参数校验：count 范围限制
    count = max(1, min(request.count, 100))

    logger.info(
        f"收到历史对话查询请求，user_id: {current_user_id}, chat_id: {request.chat_id}, count: {count}"
    )

    try:
        # 调用 repository 获取历史对话
        chats = chat_repository.get_chats_before(
            user_id=current_user_id,
            before_chat_id=request.chat_id,
            before_time=request.chat_time,
            count=count,
        )

        # 转换为响应格式（使用 SSE formatter 的清理逻辑）
        history_chats: list[HistoryChatItem] = []
        for chat in chats:
            cleaned_content = sse_formatter._clean_content(chat.type, chat.message.content)
            history_chats.append(
                HistoryChatItem(
                    id=chat.id,
                    type=chat.type,
                    time=chat.time,
                    content=cleaned_content,
                    reasoning_content=chat.message.reasoning_content or "",
                    tool_calls=chat.message.tool_calls,
                )
            )

        # 由于返回的是降序（最新的在前），需要反转为升序以符合阅读习惯
        history_chats.reverse()

        logger.info(f"历史对话查询成功，user_id: {current_user_id}, 返回数量: {len(history_chats)}")
        return HistoryResponse(success=True, chats=history_chats, total=len(history_chats))

    except Exception:
        logger.exception(f"历史对话查询失败，user_id: {current_user_id}")
        return HistoryResponse(success=False, chats=[], total=0, error="历史对话查询失败")
