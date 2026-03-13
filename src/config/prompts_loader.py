"""提示词加载模块"""

from src.config.prompts.assistant_prompt import ASSISTANT_PROMPT


class PromptsLoader:
    """提示词模板加载器"""

    def get_assistant_prompt(
        self, skill_path: str, 
        available_modules_prompt:str, 
        available_skills_prompt: str
    ) -> str:
        """获取助手系统提示词"""
        return ASSISTANT_PROMPT.format(
            skill_path=skill_path,
            available_modules_prompt=available_modules_prompt,
            available_skills_prompt=available_skills_prompt,
        )


# 全局提示词加载器实例
prompts_loader = PromptsLoader()
