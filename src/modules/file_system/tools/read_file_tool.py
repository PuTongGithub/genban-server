"""读取文件工具"""

from typing import Any

from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolParameter
from src.modules.file_system.exceptions import FileNotFoundException
from src.storage.file.file_storage import file_storage
from src.user.auth import validate_path


class ReadFileTool(BaseTool):
    """读取文件内容工具"""

    name = "read_file"
    description = "读取文件内容，若文件过大，请使用指定行号范围读取"
    parameters = [
        ToolParameter(
            name="path",
            type="string",
            description="文件路径（用户目录相对路径，或绝对路径）",
            required=True,
        ),
        ToolParameter(
            name="start_line",
            type="integer",
            description="起始行号（从1开始，包含），默认为1",
            required=False,
        ),
        ToolParameter(
            name="end_line",
            type="integer",
            description="结束行号（包含），默认为文件末尾",
            required=False,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行读取文件操作

        Args:
            context: Agent 执行上下文
            path: 文件路径
            start_line: 起始行号（从1开始）
            end_line: 结束行号

        Returns:
            文件内容

        Raises:
            FileNotFoundException: 文件不存在
        """
        path = kwargs.get("path", "")
        start_line = kwargs.get("start_line", 1)
        end_line = kwargs.get("end_line", None)

        file_path = validate_path(path, context.user_id)

        if not file_storage.exists(file_path):
            raise FileNotFoundException(path)

        lines = file_storage.read_lines(file_path)

        # 处理行号范围
        total_lines = len(lines)
        start = max(1, start_line)
        end = end_line if end_line is not None else total_lines
        end = min(end, total_lines)

        if start > total_lines:
            return ""

        # 提取指定范围的行
        selected_lines = lines[start - 1 : end]

        return "".join(selected_lines)
