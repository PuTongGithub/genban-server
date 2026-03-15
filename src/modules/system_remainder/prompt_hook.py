"""Prompt Hook 实现"""

from src.agent.hooks.base_hook import PromptHook
from src.agent.entities import Chat, AgentContext
from src.agent.chat_factory import chat_factory
from src.config.prompts_loader import prompts_loader
from src.modules.skills.skills_manager import skills_manager
from src.modules.base_module import BaseModule


class PromptSetupHook(PromptHook):
    """设置系统提示词的钩子"""

    def _build_modules_prompt(self, modules: list[BaseModule]) -> str:
        """构建模块提示词

        Args:
            modules: 模块列表

        Returns:
            模块提示词 XML 字符串
        """
        if not modules:
            return "<available_modules></available_modules>"

        modules_content = "\n".join([module.to_prompt() for module in modules])
        return f"<available_modules>\n{modules_content}\n</available_modules>"

    def execute(
        self, data: list[Chat] | None, context: AgentContext
    ) -> list[Chat] | None:
        """设置系统提示词"""
        # 创建系统提示词 Chat
        chats = []

        # 从 context.modules 生成提示词
        modules_prompt = self._build_modules_prompt(context.modules)

        prompt = prompts_loader.get_assistant_prompt(
            available_modules_prompt=modules_prompt
        )
        chats.append(chat_factory.create_prompt_chat(prompt))

        skills_prompt = prompts_loader.get_skill_prompt(
            available_skills_prompt=skills_manager.to_prompt(context.user_id)
        )
        chats.append(chat_factory.create_system_remainder_chat(skills_prompt))

        env_prompt = prompts_loader.get_env_prompt(
            model_key=context.model_config.model_key
        )
        chats.append(chat_factory.create_system_remainder_chat(env_prompt))

        return chats
