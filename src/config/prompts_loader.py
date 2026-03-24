"""提示词加载模块"""

from src.common.utils import path_util, sys_util, time_util
from src.config.prompts.assistant_prompt import (
    ASSISTANT_PROMPT,
    ENV_PROMPT_TEMPLATE,
    SKILL_PROMPT_TEMPLATE,
)
from src.config.prompts.memory_prompt import CONTEXT_COMPRESSION_PROMPT_TEMPLATE
from src.config.prompts.web_search_prompt import SEARCH_RESULT_COMPRESSION_PROMPT_TEMPLATE


class PromptsLoader:
    """提示词模板加载器"""

    def get_assistant_prompt(
        self,
        available_modules_prompt: str,
    ) -> str:
        """获取助手系统提示词"""
        return ASSISTANT_PROMPT.format(available_modules_prompt=available_modules_prompt)

    def get_skill_prompt(self, available_skills_prompt: str) -> str:
        """获取技能提示词"""
        return SKILL_PROMPT_TEMPLATE.format(
            available_skills_prompt=available_skills_prompt,
        )

    def get_env_prompt(self, model_key: str, user_id: str) -> str:
        """获取环境变量提示词"""
        return ENV_PROMPT_TEMPLATE.format(
            os=sys_util.get_os(),
            model_key=model_key,
            user_dir=str(path_util.get_user_dir(user_id)),
            today_date=time_util.get_now_str(time_util.STR_FORMATTER_DATE_WITH_MARKS),
        )

    def get_conversation_compression_prompt(
        self,
        available_modules_prompt: str,
        chat_history: str,
    ) -> str:
        """获取对话压缩提示词"""
        return CONTEXT_COMPRESSION_PROMPT_TEMPLATE.format(
            available_modules_prompt=available_modules_prompt,
            chat_history=chat_history,
            current_timestamp=time_util.get_timestamp(),
        )

    def get_search_compression_prompt(
        self,
        search_query: str,
        search_results: str,
    ) -> str:
        """获取搜索结果压缩提示词"""
        return SEARCH_RESULT_COMPRESSION_PROMPT_TEMPLATE.format(
            search_query=search_query,
            search_results=search_results,
        )


# 全局提示词加载器实例
prompts_loader = PromptsLoader()
