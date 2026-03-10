"""提示词加载模块"""

from src.config.prompts.assistant_prompt import ASSISTANT_PROMPT


class PromptsLoader:
    """提示词模板加载器"""

    def get_assistant_prompt(self, skills_instructions: str) -> str:
        """获取助手系统提示词"""
        return ASSISTANT_PROMPT.format(skills_instructions=skills_instructions)


# 全局提示词加载器实例
prompts_loader = PromptsLoader()
