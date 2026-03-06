"""Prompt Hook 实现"""

from src.agent.hooks.base_hook import PromptHook
from src.agent.entities import Chat, AgentContext
from src.agent.chat_factory import chat_factory
from src.config.prompts.assistant_prompt import ASSISTANT_PROMPT


class PromptSetupHook(PromptHook):
    """设置系统提示词的钩子"""

    def execute(self, data: Chat | None, context: AgentContext) -> Chat | None:
        """设置系统提示词"""
        # 创建系统提示词 Chat
        prompt_chat = chat_factory.create_prompt_chat(ASSISTANT_PROMPT)
        return prompt_chat
