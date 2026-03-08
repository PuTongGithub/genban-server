"""编辑文件工具"""

from typing import Any

from src.agent.tools.base_tool import BaseTool
from src.agent.entities import ToolParameter, AgentContext
from src.modules.file_system.path_validator import validate_path
from src.modules.file_system.exceptions import (
    FileNotFoundException,
    LineNumberOutOfRangeException,
)
from src.storage.file.file_storage import file_storage


class EditReplaceItem:
    """替换项"""

    def __init__(self, start_line: int, end_line: int, content: str):
        self.start_line = start_line
        self.end_line = end_line
        self.content = content


class EditFileTool(BaseTool):
    """编辑文件内容工具（支持多范围替换）"""

    name = "edit_file"
    description = "编辑文件内容，支持同时对文件的多个部分进行替换。每个替换项指定起始行号、结束行号和替换内容。"
    parameters = [
        ToolParameter(
            name="path",
            type="string",
            description="文件路径（相对于用户目录的相对路径）",
            required=True,
        ),
        ToolParameter(
            name="replacements",
            type="array",
            description="替换项列表，每项包含 start_line（起始行号）、end_line（结束行号）、content（替换内容）",
            required=True,
        ),
    ]

    def __init__(self, user_id: str):
        self.user_id = user_id

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行编辑文件操作

        Args:
            context: Agent 执行上下文
            path: 文件路径
            replacements: 替换项列表，每项为 dict，包含 start_line、end_line、content

        Returns:
            操作结果信息

        Raises:
            FileNotFoundException: 文件不存在
            LineNumberOutOfRangeException: 行号超出范围
        """
        path = kwargs.get("path", "")
        replacements = kwargs.get("replacements", [])

        file_path = validate_path(path, self.user_id)

        if not file_storage.exists(file_path):
            raise FileNotFoundException(path)

        lines = file_storage.read_lines(file_path)
        total_lines = len(lines)

        # 解析替换项
        replace_items = []
        for item in replacements:
            start_line = item.get("start_line", 0)
            end_line = item.get("end_line", 0)
            content = item.get("content", "")

            # 验证行号
            if start_line < 1 or end_line < start_line or end_line > total_lines:
                raise LineNumberOutOfRangeException(start_line, total_lines)

            replace_items.append(EditReplaceItem(start_line, end_line, content))

        # 按起始行号降序排序，从后向前替换，避免行号变化
        replace_items.sort(key=lambda x: x.start_line, reverse=True)

        # 执行替换
        for item in replace_items:
            # 将内容按行分割
            new_lines = item.content.split("\n")
            # 确保每行以换行符结尾
            new_lines = [
                line + "\n" if not line.endswith("\n") else line for line in new_lines
            ]
            if new_lines and new_lines[-1] == "\n":
                new_lines = new_lines[:-1]

            # 替换指定范围的行
            start_idx = item.start_line - 1
            end_idx = item.end_line
            lines = lines[:start_idx] + new_lines + lines[end_idx:]

        # 写回文件
        file_storage.write_lines(file_path, lines)

        return f"成功执行 {len(replace_items)} 处替换"
