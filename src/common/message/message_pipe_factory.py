"""消息管道工厂模块"""

from src.common.logger import get_logger
from src.common.message.message_pipe import MessagePipe
from src.agent.entities import Chat, MessagePipeContent

logger = get_logger(__name__)


class MessagePipeFactory:
    """消息管道工厂，管理共享的 AsyncExecutor"""

    @classmethod
    def create_in_pipe(cls, user_id: str) -> MessagePipe[MessagePipeContent]:
        """创建输入消息管道

        输入管道用于批量接收消息，对应原有的 InMessagePipe

        Returns:
            输入消息管道实例
        """
        return MessagePipe[MessagePipeContent](
            name=f"AgentChatInPipe_{user_id}",
            maxsize=10000,
        )

    @classmethod
    def create_out_pipe(cls, user_id: str) -> MessagePipe[MessagePipeContent]:
        """创建输出消息管道

        输出管道用于单条发送消息，对应原有的 OutMessagePipe

        Returns:
            输出消息管道实例
        """
        return MessagePipe[MessagePipeContent](
            name=f"AgentChatOutPipe_{user_id}",
            maxsize=10000,
        )

    @classmethod
    def create_stream_pipe(cls, user_id: str) -> MessagePipe[Chat]:
        """创建流式消息管道

        流式管道用于持续接收 Agent 产生的新消息，对应 SSE 连接

        Returns:
            流式消息管道实例
        """
        return MessagePipe[Chat](
            name=f"StreamChatPipe_{user_id}",
            maxsize=10000,
        )
