"""写入文件工具"""

from typing import Any

from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolParameter
from src.storage.file.file_storage import file_storage
from src.user.auth import validate_path


class WriteFileTool(BaseTool):
    """写入文件内容工具（覆盖写入）"""

    name = "write_file"
    description = "写入文件内容，会覆盖原有内容"
    parameters = [
        ToolParameter(
            name="path",
            type="string",
            description="文件路径（用户目录相对路径，或绝对路径）",
            required=True,
        ),
        ToolParameter(
            name="content",
            type="string",
            description="要写入的内容",
            required=True,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行写入文件操作

        Args:
            context: Agent 执行上下文
            path: 文件路径
            content: 文件内容

        Returns:
            操作结果信息
        """
        path = kwargs.get("path", "")
        content = kwargs.get("content", "")

        file_path = validate_path(path, context.user_id)

        file_storage.write_text(file_path, content)

        return f"文件已成功写入: {path}"
