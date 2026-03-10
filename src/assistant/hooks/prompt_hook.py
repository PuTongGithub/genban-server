"""Prompt Hook 实现"""

from src.agent.hooks.base_hook import PromptHook
from src.agent.entities import Chat, AgentContext
from src.agent.chat_factory import chat_factory
from src.config.prompts_loader import prompts_loader
from src.modules.skills.skills_manager import skills_manager


class PromptSetupHook(PromptHook):
    """设置系统提示词的钩子"""

    def execute(self, data: Chat | None, context: AgentContext) -> Chat | None:
        """设置系统提示词"""
        # 创建系统提示词 Chat
        prompt = prompts_loader.get_assistant_prompt(
            skills_instructions=skills_manager.to_prompt(context.user_id)
        )
        prompt_chat = chat_factory.create_prompt_chat(prompt)
        return prompt_chat
