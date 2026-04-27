"""Chat 工厂类，用于创建各种 Chat 和 Message 对象"""

import threading

from src.agent.entities import Chat, ChatExtra, ChatType, Content, Message, MessageRole
from src.common.utils import time_util
from src.model.entities import CallResponse


class _ChatFactory:
    """Chat 工厂类"""

    def __init__(self) -> None:
        self.current_time = time_util.get_timestamp()
        self.index = 0
        self._lock = threading.Lock()

    def _create_chat_id(self) -> str:
        """创建对话 ID"""
        with self._lock:
            current = time_util.get_timestamp()
            if current != self.current_time:
                self.current_time = current
                self.index = 0

            self.index += 1
            return f"{self.current_time}{self.index:04d}"

    # 创建消息字符串

    def create_str_with_tag(self, content: str, tag: str | None = None) -> str:
        """创建消息字符串，添加标签"""
        if tag:
            return f"[{tag}]{content}"
        else:
            return content

    def create_system_remainder_str(self, content: str) -> str:
        """创建系统消息内容，返回字符串格式"""
        return self.create_str_with_tag(content, ChatType.SYSTEM_REMAINDER.type)

    # 创建消息内容

    def create_content(self, text: str, images: list[str] | None = None, videos: list[str] | None = None) -> list:
        """创建消息内容"""
        content = []
        content.append(Content(text=text))
        if images is not None:
            content.extend([Content(image=image) for image in images])
        if videos is not None:
            content.extend([Content(video=video) for video in videos])
        return content

    def create_user_content(self, user_id: str, user_input: str, channel_type: str, images: list[str] | None = None, videos: list[str] | None = None) -> list:
        """创建用户消息内容"""
        time_str = time_util.get_now_str(time_util.STR_FORMATTER_WITH_MARKS)
        text_content = self.create_str_with_tag(
            user_input, f"{ChatType.USER.type}:{user_id}:{channel_type}:{time_str}"
        )
        return self.create_content(text_content, images, videos)

    def create_content_with_tag(self, content: str, chat_type: ChatType) -> list:
        """创建消息内容，添加标签"""
        if chat_type.message_with_tag:
            str = self.create_str_with_tag(content, chat_type.type)
        else:
            str = content
        return self.create_content(text=str)

    # 创建消息对象

    def create_content_message(self, role: MessageRole, content: list[Content]) -> Message:
        """创建消息对象，添加标签"""
        return Message(
            role=role.value,
            content=content,
        )

    def create_message(self, content: str, role: MessageRole, chat_type: ChatType) -> Message:
        """创建消息对象，添加标签"""
        return self.create_content_message(role, self.create_content_with_tag(content, chat_type))

    def create_user_message(self, user_id: str, user_input: str, channel_type: str, images: list[str] | None = None, videos: list[str] | None = None) -> Message:
        """创建用户消息"""
        return self.create_content_message(
            role=MessageRole.USER,
            content=self.create_user_content(user_id, user_input, channel_type, images, videos),
        )

    def create_tool_message(self, tool_call_id: str, tool_result: str) -> Message:
        """创建工具消息，tool_result 转换为列表格式"""
        return Message(
            role=MessageRole.TOOL.value,
            tool_call_id=tool_call_id,
            content=self.create_content(text=tool_result),
        )

    # 创建 Chat 对象

    def create_default_chat(self, content: str) -> Chat:
        """创建 Chat 对象"""
        return Chat(
            type=ChatType.DEFAULT.type,
            id=self._create_chat_id(),
            message=self.create_message(content=content, role=MessageRole.USER, chat_type=ChatType.DEFAULT),
        )

    def create_prompt_chat(self, content: str) -> Chat:
        """创建提示词对话"""
        return Chat(
            type=ChatType.PROMPT.type,
            id=self._create_chat_id(),
            message=self.create_message(
                content=content, role=MessageRole.SYSTEM, chat_type=ChatType.PROMPT
            ),
        )

    def create_user_chat(self, user_id: str, user_input: str, channel_type: str = "web", images: list[str] | None = None, videos: list[str] | None = None) -> Chat:
        """创建用户对话"""
        return Chat(
            type=ChatType.USER.type,
            id=self._create_chat_id(),
            message=self.create_user_message(
                user_id=user_id, user_input=user_input, channel_type=channel_type, images=images, videos=videos
            ),
            extra=ChatExtra(channel_type=channel_type),
        )

    def create_tool_chat(self, tool_call_id: str, tool_result: str) -> Chat:
        """创建工具对话"""
        return Chat(
            type=ChatType.TOOL.type,
            id=self._create_chat_id(),
            message=self.create_tool_message(tool_call_id=tool_call_id, tool_result=tool_result),
        )

    def create_tool_result_chat(self, text: str, images: list[str] | None = None, videos: list[str] | None = None) -> Chat:
        """创建工具结果对话"""
        return Chat(
            type=ChatType.TOOL_RESULT.type,
            id=self._create_chat_id(),
            message=self.create_content_message(
                role=MessageRole.USER,
                content=self.create_content(text, images, videos),
            ),
        )

    def create_file_chat(self, file_path: str) -> Chat:
        """创建 Chat 对象"""
        return Chat(
            type=ChatType.FILE.type,
            id=self._create_chat_id(),
            message=self.create_message(content=file_path, role=MessageRole.USER, chat_type=ChatType.FILE),
        )

    def create_file_upload_chat(self, content: str) -> Chat:
        """创建 Chat 对象"""
        return Chat(
            type=ChatType.FILE_UPLOAD.type,
            id=self._create_chat_id(),
            message=self.create_message(content=content, role=MessageRole.USER, chat_type=ChatType.SYSTEM_REMAINDER),
        )

    def create_system_remainder_chat(self, content: str) -> Chat:
        """创建系统提醒对话"""
        return Chat(
            type=ChatType.SYSTEM_REMAINDER.type,
            id=self._create_chat_id(),
            message=self.create_message(
                content=content, role=MessageRole.USER, chat_type=ChatType.SYSTEM_REMAINDER
            ),
        )

    def create_skill_prompt_chat(self, content: str) -> Chat:
        """创建技能提示对话"""
        return Chat(
            type=ChatType.SKILL_PROMPT.type,
            id=self._create_chat_id(),
            message=self.create_message(
                content=content, role=MessageRole.USER, chat_type=ChatType.SKILL_PROMPT
            ),
        )

    def create_schedule_prompt_chat(self, content: str) -> Chat:
        """创建日程提示对话"""
        return Chat(
            type=ChatType.SCHEDULE.type,
            id=self._create_chat_id(),
            message=self.create_message(
                content=content, role=MessageRole.USER, chat_type=ChatType.SCHEDULE
            ),
        )

    def create_schedule_remainder_chat(self, content: str) -> Chat:
        """创建日程提醒对话"""
        return Chat(
            type=ChatType.SCHEDULE_REMINDER.type,
            id=self._create_chat_id(),
            message=self.create_message(
                content=content, role=MessageRole.USER, chat_type=ChatType.SCHEDULE_REMINDER
            ),
        )

    def create_conversation_chat(self, content: str) -> Chat:
        """创建对话概要对话"""
        return Chat(
            type=ChatType.CONVERSATION.type,
            id=self._create_chat_id(),
            message=self.create_message(
                content=content, role=MessageRole.USER, chat_type=ChatType.CONVERSATION
            ),
        )

    def create_error_chat(self, content: str) -> Chat:
        """创建错误对话"""
        return Chat(
            type=ChatType.ERROR.type,
            id=self._create_chat_id(),
            message=self.create_message(
                content=content, role=MessageRole.USER, chat_type=ChatType.SYSTEM_REMAINDER
            ),
        )

    def create_stop_chat(self) -> Chat:
        """创建停止对话，用于中断 Agent 执行"""
        return Chat(
            type=ChatType.STOP.type,
            id=self._create_chat_id(),
            message=self.create_message(
                content="用户请求中断执行",
                role=MessageRole.USER,
                chat_type=ChatType.SYSTEM_REMAINDER,
            ),
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
