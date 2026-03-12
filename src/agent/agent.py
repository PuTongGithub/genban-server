"""Agent 主流程控制器"""

from src.agent.entities import Chat, AgentContext
from src.agent.exceptions import ModelCallException
from src.agent.model.model_caller import model_caller
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.tool_caller import ToolCaller
from src.agent.hooks.base_hook import (
    BaseHook,
    ChatHook,
    PromptHook,
    ChatsHook,
    ModelHook,
    ToolsHook,
    NewChatHook,
    CompleteHook,
)
from src.agent.hooks.hook_manager import HookManager
from src.agent.tools.tool_parser import ToolParser
from src.agent.chat_factory import chat_factory
from src.config.config import app_config
from src.common.logger import get_logger

logger = get_logger(__name__)


class Agent:
    """Agent 主流程控制器，编排单次 AI 调用的完整流程"""

    def __init__(
        self,
        user_id: str,
        tools: list[BaseTool] | None = None,
        hooks: list[BaseHook] | None = None,
    ) -> None:
        self.user_id = user_id
        self.model_caller = model_caller  # 使用单例
        self.tool_caller = ToolCaller()
        self.hook_manager = HookManager()
        self.tool_parser = ToolParser()
        self.max_iterations = 50  # 最大工具调用迭代次数

        # 注册工具
        if tools:
            for tool in tools:
                self.register_tool(tool)

        # 注册钩子
        if hooks:
            for hook in hooks:
                self.register_hook(hook)

    def register_tool(self, tool: BaseTool) -> None:
        """注册工具"""
        self.tool_caller.register(tool)

    def register_hook(self, hook: BaseHook) -> None:
        """注册钩子"""
        self.hook_manager.register(hook)

    def _execute_pre_hooks(self, context: AgentContext) -> None:
        """执行前置钩子链：model -> chat -> prompt -> chats -> tools

        钩子执行结果写入 context：
        - model_key: model_hook 结果
        - input_chat: chat_hook 结果
        - prompt_chat: prompt_hook 结果
        - history_chats: chats_hook 结果

        """
        # 1. ModelHook - 决定模型 key
        model_result = self.hook_manager.execute(ModelHook, context.model_key, context)
        if model_result is not None:
            context.model_key = model_result

        # 2. ChatHook - 处理单个对话
        chat_result = self.hook_manager.execute(ChatHook, context.input_chat, context)
        if chat_result is not None:
            context.input_chat = chat_result

        # 3. PromptHook - 处理提示词
        prompt_result = self.hook_manager.execute(
            PromptHook, context.prompt_chat, context
        )
        if prompt_result is not None:
            context.prompt_chat = prompt_result

        # 4. ChatsHook - 处理对话列表
        chats_result = self.hook_manager.execute(
            ChatsHook, context.history_chats, context
        )
        if chats_result is not None:
            context.history_chats = chats_result

        # 5. ToolsHook - 处理工具注册表
        self.hook_manager.execute(ToolsHook, self.tool_caller.registry, context)

        # 6. NewChatHook - 处理新增的 Chat
        for chat in context.new_chats:
            self.hook_manager.async_execute(NewChatHook, chat, context)

    def _call_model(self, context: AgentContext, chats: list[Chat]) -> Chat:
        """调用大模型"""
        tools_schemas = self.tool_caller.get_tools_schemas()
        tools = tools_schemas if tools_schemas else None

        chat = None
        for response_chat in self.model_caller.stream_call(
            model_key=context.model_key,
            chats=chats,
            tools=tools,
            enable_thinking=True,
        ):
            self.hook_manager.async_execute(NewChatHook, response_chat, context)
            chat = response_chat
        if chat is None:
            raise ModelCallException("model call failed")
        else:
            return chat

    def _handle_new_chat(
        self,
        current_chats: list[Chat],
        new_chats: list[Chat],
        context: AgentContext,
        newChat: Chat,
    ) -> None:
        """处理新增的 Chat ，并触发 NewChatHook 钩子执行"""
        current_chats.append(newChat)
        new_chats.append(newChat)
        self.hook_manager.async_execute(NewChatHook, newChat, context)

    def run(self, chat: Chat) -> list[Chat]:
        """执行 Agent 调用，返回本次所有新增的 Chat 列表（包括新增输入的 Chat）

        Args:
            chat: 当前输入的对话

        Returns:
            本次所有新增的 Chat 列表（包含 assistant 响应和 tool 调用结果）
        """
        logger.debug(f"Agent 开始执行，user_id: {self.user_id}")

        context = AgentContext(
            model_key=app_config.get_default_model(),
            user_id=self.user_id,
            input_chat=chat,
            new_chats=[chat],
        )

        # 执行前置钩子链
        self._execute_pre_hooks(context)
        logger.debug(f"前置钩子执行完成，使用模型: {context.model_key}")

        iteration = 0
        current_chats = (
            [context.prompt_chat] + context.history_chats + context.new_chats
        )
        new_chats = context.new_chats

        while iteration < self.max_iterations:
            iteration += 1
            logger.debug(f"开始第 {iteration} 轮迭代")

            # 调用模型
            try:
                response_chat = self._call_model(context, current_chats)
                logger.debug(f"模型调用完成，role: {response_chat.message.role}")
            except Exception:
                logger.exception(f"模型调用失败，user_id: {self.user_id}")
                raise

            self._handle_new_chat(current_chats, new_chats, context, response_chat)

            # 检查是否需要工具调用
            if response_chat.message.tool_calls is not None:
                logger.debug(f"检测到工具调用，数量: {len(response_chat.message.tool_calls)}")
                # 处理工具调用
                tool_results = self.tool_caller.execute_from_model_response(
                    response_chat.message.tool_calls, context
                )
                for tool_result in tool_results:
                    tool_chat = chat_factory.create_tool_chat(
                        tool_call_id=tool_result.tool_call_id,
                        tool_result=tool_result.content,
                    )
                    self._handle_new_chat(current_chats, new_chats, context, tool_chat)
            else:
                logger.debug("Agent 执行完成，无需工具调用")
                self.hook_manager.async_execute(CompleteHook, new_chats, context)
                return new_chats

        # 超过最大迭代次数，返回错误
        logger.error(f"Agent 执行超过最大迭代次数 {self.max_iterations}，user_id: {self.user_id}")
        error_chat = chat_factory.create_error_chat(content="Error: 超过最大迭代次数")
        self._handle_new_chat(current_chats, new_chats, context, error_chat)
        self.hook_manager.async_execute(CompleteHook, new_chats, context)
        return new_chats
