"""Agent 主流程控制器"""

from src.agent.entities import Chat, AgentContext, ChatType
from src.agent.exceptions import ModelCallException, ModelHookException
from src.agent.model.model_caller import model_caller
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.tool_caller import ToolCaller
from src.agent.hooks.base_hook import (
    BaseHook,
    PromptHook,
    HistoryChatsHook,
    ModelHook,
    ConfirmedChatHook,
)
from src.agent.hooks.hook_manager import HookManager
from src.agent.chat_factory import chat_factory
from src.common.message.message_pipe_factory import MessagePipeFactory
from src.agent.entities import MessagePipeContent
from src.modules.base_module import BaseModule
from src.common.thread_executor import ThreadExecutor
from src.common.logger import get_logger

logger = get_logger(__name__)


class Agent:
    """Agent 主流程控制器，编排单次 AI 调用的完整流程"""

    def __init__(
        self,
        user_id: str,
        tools: list[BaseTool] | None = None,
        hooks: list[BaseHook] | None = None,
        modules: list[BaseModule] | None = None,
    ) -> None:
        self.user_id = user_id
        self._tool_caller = ToolCaller()
        self._hook_manager = HookManager(user_id)
        self._modules: list[BaseModule] = []
        self._in_message_pipe = MessagePipeFactory.create_in_pipe(user_id)
        self._out_message_pipe = MessagePipeFactory.create_out_pipe(user_id)

        # 注册模块（先注册模块，模块会提供tools和hooks）
        if modules:
            for module in modules:
                self.register_module(module)

        # 注册工具
        if tools:
            for tool in tools:
                self.register_tool(tool)

        # 注册钩子
        if hooks:
            for hook in hooks:
                self.register_hook(hook)

        self._executor = ThreadExecutor(
            name=f"Agent-{user_id}",
            target=self._run,
            on_stop=self.stop,
        )
        self._executor.start()

    def register_tool(self, tool: BaseTool) -> None:
        """注册工具"""
        self._tool_caller.register(tool)

    def register_hook(self, hook: BaseHook) -> None:
        """注册钩子"""
        self._hook_manager.register(hook)

    def register_module(self, module: BaseModule) -> None:
        """注册模块，自动注入模块的tools和hooks

        Args:
            module: 模块实例，需继承 BaseModule
        """
        self._modules.append(module)

        # 自动注册模块提供的工具
        tools = module.get_tools()
        if tools:
            for tool in tools:
                self.register_tool(tool)

        # 自动注册模块提供的钩子
        hooks = module.get_hooks()
        if hooks:
            for hook in hooks:
                self.register_hook(hook)

    def send_chat(self, chat: Chat) -> None:
        """发送消息到输入管道"""
        self._in_message_pipe.push(MessagePipeContent(chat=chat))

    def recv_chat(self) -> Chat | None:
        """从输出管道接收消息"""
        content = self._out_message_pipe.pull()
        return content.chat if content else None

    def stop(self) -> None:
        """停止 Agent 主流程"""
        self._executor.stop()
        self._hook_manager.stop()

    def _run(self):
        """运行 Agent 主流程"""
        logger.info(f"Agent 开始执行，user_id: {self.user_id}")

        block_pull = True
        while True:
            if not self._executor.is_running():
                logger.info(f"用户 {self.user_id} 服务端已关闭，退出循环")
                break

            try:
                if block_pull:
                    # 阻塞3秒拉取所有消息，有消息则执行
                    contents = self._in_message_pipe.pull_all()
                    if contents:
                        block_pull = self._process_contents(contents)
                else:
                    # 非阻塞拉取所有消息，无论是否有消息都执行
                    if not self._in_message_pipe.is_empty():
                        contents = self._in_message_pipe.pull_all()
                    else:
                        contents = []
                    block_pull = self._process_contents(contents)
            except Exception as e:
                logger.exception(f"Agent 处理消息时出错: {e}")
                block_pull = True

    def _process_contents(
        self,
        contents: list[MessagePipeContent],
    ) -> bool:
        """收到一批消息，执行处理流程，进行调用大模型等操作。
        若有工具调用，返回 False 表示非阻塞拉取，否则返回 True 表示阻塞拉取。
        """
        try:
            context = AgentContext(
                user_id=self.user_id,
                modules=self._modules,
            )

            self._handle_new_chat(context, contents)

            if self._has_stop_signal(context):
                return True
            logger.info(f"用户 {self.user_id} 的 Agent 收到 {len(contents)} 条消息")

            self._execute_pre_hooks(context)

            chats = context.prompt_chats + context.history_chats
            response_chat = self._call_model(context, chats)

            return self._handle_tool_calls(context, response_chat)
        except Exception as e:
            logger.exception(f"Agent 处理消息时出错: {e}")
            error_chat = chat_factory.create_error_chat(
                f"Agent 处理消息时出错: {str(e)}"
            )
            self._handle_confirmed_chat(context, error_chat)
            return True

    def _handle_new_chat(
        self, context: AgentContext, contents: list[MessagePipeContent]
    ) -> None:
        """处理新增的 Chat ，触发 OutMessagePipe 发送"""
        for content in contents:
            new_chat = content.chat
            context.new_chats.append(new_chat)
            self._handle_confirmed_chat(context, new_chat)

    def _has_stop_signal(self, context: AgentContext) -> bool:
        """判断新增的 Chat 是否为停止信号"""
        if not context.new_chats:
            return False

        last_chat = context.new_chats[-1]
        return ChatType.STOP.type == last_chat.type

    def _execute_pre_hooks(self, context: AgentContext) -> None:
        """执行前置钩子链"""
        # ModelHook - 决定模型 key
        model_result = self._hook_manager.execute(
            ModelHook, context.model_config, context
        )
        if model_result is not None:
            context.model_config = model_result
        else:
            raise ModelHookException(f"uid:{self.user_id} model hook failed")

        # PromptHook - 处理提示词
        self._hook_manager.execute(PromptHook, context.prompt_chats, context)

        # HistoryChatsHook - 处理历史对话列表
        self._hook_manager.execute(HistoryChatsHook, context.history_chats, context)

    def _call_model(self, context: AgentContext, chats: list[Chat]) -> Chat:
        """调用大模型"""
        if context.model_config is None:
            raise ModelCallException("model config is None")

        for response_chat in model_caller.stream_call(
            model_key=context.model_config.model_key,
            chats=chats,
            tools=self._tool_caller.get_tools_schemas(),
            enable_thinking=context.model_config.enable_thinking,
        ):
            self._out_message_pipe.push(MessagePipeContent(chat=response_chat))
            chat = response_chat
        if chat is not None:
            self._handle_confirmed_chat(context, chat)
            return chat
        else:
            raise ModelCallException(f"uid:{self.user_id} model call failed")

    def _handle_tool_calls(self, context: AgentContext, response_chat: Chat) -> bool:
        """处理工具调用"""
        if response_chat.message.tool_calls is None:
            # 没有工具调用，返回阻塞拉取消息
            return True

        # 处理工具调用
        tool_results = self._tool_caller.execute_from_model_response(
            response_chat.message.tool_calls, context
        )
        for tool_result in tool_results:
            tool_chat = chat_factory.create_tool_chat(
                tool_call_id=tool_result.tool_call_id,
                tool_result=tool_result.content,
            )
            self._handle_confirmed_chat(context, tool_chat)
        return False

    def _handle_confirmed_chat(self, context: AgentContext, chat: Chat) -> None:
        """处理确认的消息"""
        self._out_message_pipe.push(MessagePipeContent(chat=chat))
        self._hook_manager.async_execute(ConfirmedChatHook, chat, context)
