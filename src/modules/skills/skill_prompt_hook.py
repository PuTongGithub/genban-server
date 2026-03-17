"""技能提示词 Hook 实现"""

from src.agent.hooks.base_hook import PromptHook
from src.agent.entities import Chat, AgentContext
from src.agent.chat_factory import chat_factory
from src.config.prompts_loader import prompts_loader
from src.modules.skills.skills_manager import skills_manager


class SkillPromptHook(PromptHook):
    """设置技能提示词的钩子"""

    order = 1

    def execute(
        self, data: list[Chat] | None, context: AgentContext
    ) -> list[Chat] | None:
        """设置技能提示词"""

        skills_prompt = prompts_loader.get_skill_prompt(
            available_skills_prompt=skills_manager.to_prompt(context.user_id)
        )
        data.append(chat_factory.create_system_remainder_chat(skills_prompt))

        return data
