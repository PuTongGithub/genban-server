"""模块管理器

提供模块相关的通用功能
"""

from src.modules.base_module import BaseModule


def build_modules_prompt(modules: list[BaseModule]) -> str:
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
