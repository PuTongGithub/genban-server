"""Chat 工厂类，用于创建各种 Chat 和 Message 对象"""

from src.agent.entities import Message, Chat, MessageRole, ChatType
from src.agent.model.entities import CallResponse
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

    # 创建消息字符串

    def create_system_remainder_str(self, content: str) -> str:
        """创建系统消息内容，返回字符串格式"""
        return f"[{ChatType.SYSTEM_REMAINDER.type}]{content}"

    # 创建消息内容

    def _normalize_content(self, content: str | list) -> list:
        """将 content 统一转换为列表格式

        Args:
            content: 字符串或列表类型的内容

        Returns:
            列表格式的内容，字符串会被包装为 [{"text": content}]
        """
        if isinstance(content, str):
            return [{"text": content}]
        return content

    def create_user_content(self, user_id: str, user_input: str) -> list:
        """创建用户消息内容，返回列表格式 [{"text": ...}]"""
        time_str = time_util.get_now_str(time_util.STR_FORMATTER_WITH_MARKS)
        text_content = f"[{ChatType.USER.type}:{user_id}:{time_str}]" + user_input
        return self._normalize_content(text_content)

    def create_system_remainder_content(self, content: str) -> list:
        """创建系统消息内容，返回列表格式 [{"text": ...}]"""
        text_content = self.create_system_remainder_str(content)
        return self._normalize_content(text_content)

    # 创建消息对象

    def create_system_message(self, content: str | list) -> Message:
        """创建系统消息，content 支持字符串或列表"""
        return Message(
            role=MessageRole.SYSTEM.value, content=self._normalize_content(content)
        )

    def create_user_message(self, user_id: str, user_input: str) -> Message:
        """创建用户消息"""
        return Message(
            role=MessageRole.USER.value,
            content=self.create_user_content(user_id, user_input),
        )

    def create_tool_message(self, tool_call_id: str, tool_result: str) -> Message:
        """创建工具消息，tool_result 转换为列表格式"""
        return Message(
            role=MessageRole.TOOL.value,
            tool_call_id=tool_call_id,
            content=self._normalize_content(tool_result),
        )

    def create_system_remainder_message(self, content: str) -> Message:
        """创建系统提醒消息（用户角色）"""
        return Message(
            role=MessageRole.USER.value,
            content=self.create_system_remainder_content(content),
        )

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

    def create_system_remainder_chat(self, content: str) -> Chat:
        """创建系统提醒对话"""
        return Chat(
            type=ChatType.SYSTEM_REMAINDER.type,
            id=self._create_chat_id(),
            message=self.create_system_remainder_message(content=content),
        )

    def create_error_chat(self, content: str) -> Chat:
        """创建错误对话"""
        return Chat(
            type=ChatType.ERROR.type,
            id=self._create_chat_id(),
            message=self.create_system_remainder_message(content=content),
        )

    def create_stop_chat(self) -> Chat:
        """创建停止对话，用于中断 Agent 执行"""
        return Chat(
            type=ChatType.STOP.type,
            id=self._create_chat_id(),
            message=self.create_system_remainder_message(content="用户请求中断执行"),
        )

    # 根据大模型返回的响应，创建响应的 Chat 对象
    def create_assistant_chat(self, response: CallResponse) -> Chat:
        """根据模型响应创建助手对话"""
        return Chat(
            type=ChatType.ASSISTANT.type,
            id=response.request_id,
            message=response.message,
        )


chat_factory = _ChatFactory()
