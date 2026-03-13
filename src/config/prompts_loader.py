"""提示词加载模块"""

from src.common.utils import time_util, sys_util
from src.config.prompts.assistant_prompt import (
    ASSISTANT_PROMPT,
    SKILL_PROMPT_TEMPLATE,
    ENV_PROMPT_TEMPLATE,
)


class PromptsLoader:
    """提示词模板加载器"""

    def get_assistant_prompt(
        self,
        available_modules_prompt: str,
    ) -> str:
        """获取助手系统提示词"""
        return ASSISTANT_PROMPT.format(
            available_modules_prompt=available_modules_prompt
        )

    def get_skill_prompt(self, available_skills_prompt: str) -> str:
        """获取技能提示词"""
        return SKILL_PROMPT_TEMPLATE.format(
            available_skills_prompt=available_skills_prompt,
        )

    def get_env_prompt(self, model_key: str) -> str:
        """获取环境变量提示词"""
        return ENV_PROMPT_TEMPLATE.format(
            os=sys_util.get_os(),
            model_key=model_key,
            today_date=time_util.get_now_str(time_util.STR_FORMATTER_DATE_WITH_MARKS),
        )


# 全局提示词加载器实例
prompts_loader = PromptsLoader()
