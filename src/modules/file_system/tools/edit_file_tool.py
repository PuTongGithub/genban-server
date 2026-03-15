"""编辑文件工具"""

from typing import Any

from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolParameter
from src.agent.entities import AgentContext
from src.common.utils.path_util import validate_path
from src.modules.file_system.exceptions import (
    FileNotFoundException,
)
from src.storage.file.file_storage import file_storage


class EditFileTool(BaseTool):
    """编辑文件内容工具（支持全文替换）"""

    name = "edit_file"
    description = "在文件中执行精确的字符串替换。当replace_all=false时，old_string必须在文件中唯一存在，否则编辑失败；当replace_all=true时，替换所有匹配项。"
    parameters = [
        ToolParameter(
            name="path",
            type="string",
            description="文件路径（用户目录相对路径，或绝对路径）",
            required=True,
        ),
        ToolParameter(
            name="old_string",
            type="string",
            description="要被替换的原始字符串",
            required=True,
        ),
        ToolParameter(
            name="new_string",
            type="string",
            description="用于替换的新字符串",
            required=True,
        ),
        ToolParameter(
            name="replace_all",
            type="boolean",
            description="是否替换所有匹配项，默认为false",
            required=False,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行编辑文件操作

        Args:
            context: Agent 执行上下文
            path: 文件路径
            old_string: 要被替换的原始字符串
            new_string: 用于替换的新字符串
            replace_all: 是否替换所有匹配项，默认为false

        Returns:
            操作结果信息

        Raises:
            FileNotFoundException: 文件不存在
            ValueError: old_string在文件中不存在或不唯一（当replace_all=false时）
        """
        path = kwargs.get("path", "")
        old_string = kwargs.get("old_string", "")
        new_string = kwargs.get("new_string", "")
        replace_all = kwargs.get("replace_all", False)

        file_path = validate_path(path, context.user_id)

        if not file_storage.exists(file_path):
            raise FileNotFoundException(path)

        content = file_storage.read_text(file_path)

        # 检查old_string是否存在
        count = content.count(old_string)
        if count == 0:
            return f"未找到要替换的字符串: {old_string}"

        if not replace_all:
            # 当replace_all=false时，要求old_string必须唯一
            if count > 1:
                return f"找到 {count} 处匹配 '{old_string}'，请提供更大范围的字符串确保其唯一性，"
            # 执行单次替换
            new_content = content.replace(old_string, new_string, 1)
        else:
            # 替换所有匹配项
            new_content = content.replace(old_string, new_string)

        # 写回文件
        file_storage.write_text(file_path, new_content)

        if replace_all:
            return f"成功替换 {count} 处内容"
        else:
            return "成功替换 1 处内容"
