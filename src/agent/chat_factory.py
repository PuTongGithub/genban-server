"""Chat 工厂类，用于创建各种 Chat 和 Message 对象"""

from src.agent.entities import Message, Chat, CallResponse, MessageRole, ChatType
from src.common.utils import time_util


class _ChatFactory:
    """Chat 工厂类"""

    def __init__(self) -> None:
        self.current_time = time_util.get_timestamp()
        self.index = 0

    def _create_chat_id(self) -> str:
        """创建对话 ID"""
        current = time_util.get_timestamp()
        if current != self.current_time:
            self.current_time = current
            self.index = 0

        self.index += 1
        return f"{self.current_time}{self.index:04d}"

    def create_system_message(self, content: str) -> Message:
        """创建系统消息"""
        return Message(role=MessageRole.SYSTEM.value, content=content)

    def create_user_message(self, user_id: str, user_input: str) -> Message:
        """创建用户消息"""
        time_str = time_util.get_now_str(time_util.STR_FORMATTER_WITH_MARKS)
        return Message(
            role=MessageRole.USER.value,
            content=f"[user:{user_id}:{time_str}]" + user_input,
        )

    def create_tool_message(self, tool_call_id: str, tool_result: str) -> Message:
        """创建工具消息"""
        return Message(
            role=MessageRole.TOOL.value,
            tool_call_id=tool_call_id,
            content=tool_result,
        )

    def create_assistant_message(self, content: str) -> Message:
        """创建助手消息"""
        return Message(role=MessageRole.ASSISTANT.value, content=content)

    def create_default_message(self, content: str) -> Message:
        """创建默认消息（用户角色）"""
        return Message(role=MessageRole.USER.value, content=content)

    # 创建 Chat 对象
    def create_prompt_chat(self, content: str) -> Chat:
        """创建提示词对话"""
        return Chat(
            type=ChatType.PROMPT.type,
            id=self._create_chat_id(),
            message=self.create_system_message(content=content),
        )

    def create_user_chat(self, user_id: str, user_input: str) -> Chat:
        """创建用户对话"""
        return Chat(
            type=ChatType.USER.type,
            id=self._create_chat_id(),
            message=self.create_user_message(user_id=user_id, user_input=user_input),
        )

    def create_tool_chat(self, tool_call_id: str, tool_result: str) -> Chat:
        """创建工具对话"""
        return Chat(
            type=ChatType.TOOL.type,
            id=self._create_chat_id(),
            message=self.create_tool_message(
                tool_call_id=tool_call_id, tool_result=tool_result
            ),
        )

    def create_command_chats(self, command_results: list[str]) -> list[Chat]:
        """创建命令结果对话列表"""
        return [
            Chat(
                type=ChatType.COMMAND.type,
                id=self._create_chat_id(),
                message=self.create_assistant_message(content=content),
            )
            for content in command_results
        ]

    def create_error_chat(self, content: str) -> Chat:
        """创建错误对话"""
        return Chat(
            type=ChatType.ERROR.type,
            id=self._create_chat_id(),
            message=self.create_default_message(content=content),
        )

    # 根据大模型返回的响应，创建响应的 Chat 对象
    def create_assistant_chat(self, response: CallResponse) -> Chat:
        """根据模型响应创建助手对话"""
        return Chat(
            type=ChatType.ASSISTANT.type,
            id=self._create_chat_id(),
            message=response.message,
            total_tokens=response.total_tokens,
        )


chat_factory = _ChatFactory()
