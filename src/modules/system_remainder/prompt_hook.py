"""Prompt Hook 实现"""

from src.agent.chat_factory import chat_factory
from src.agent.entities import AgentContext, Chat
from src.agent.hooks.base_hook import PromptHook
from src.config.prompts_loader import prompts_loader
from src.modules.module_manager import build_modules_prompt


class PromptSetupHook(PromptHook):
    """设置系统提示词的钩子"""

    order = 0

    def execute(self, data: list[Chat] | None, context: AgentContext) -> list[Chat] | None:
        """设置系统提示词"""
        from src.assistant.modules import ASSISTANT_MODULES

        modules_prompt = build_modules_prompt(ASSISTANT_MODULES)
        prompt = prompts_loader.get_assistant_prompt(available_modules_prompt=modules_prompt)
        data.append(chat_factory.create_prompt_chat(prompt))

        env_prompt = prompts_loader.get_env_prompt(
            model_key=context.model_config.model_key, user_id=context.user_id
        )
        data.append(chat_factory.create_system_remainder_chat(env_prompt))

        return data
