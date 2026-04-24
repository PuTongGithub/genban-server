"""读取文件工具"""

from typing import Any

from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolParameter, ToolExecute
from src.agent.chat_factory import chat_factory
from src.modules.file_system.components.file_share_link_generator import (
    FileShareLinkGenerator,
)
from src.modules.file_system.exceptions import FileNotFoundException
from src.storage.file.file_storage import file_storage, FileType
from src.user.auth import validate_path, get_relative_path


class ReadFileTool(BaseTool):
    """读取文件内容工具"""

    name = "read_file"
    description = "读取文件内容。对于文本文件，将返回文件内容，若文本文件过大，请使用指定行号范围读取。对于非文本文件，将返回url。"
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

    def execute(self, context: AgentContext, **kwargs: Any) -> ToolExecute:
        """执行读取文件操作

        Args:
            context: Agent 执行上下文
            path: 文件路径
            start_line: 起始行号（从1开始）
            end_line: 结束行号

        Raises:
            FileNotFoundException: 文件不存在
        """
        path = kwargs.get("path", "")
        start_line = kwargs.get("start_line", 1)
        end_line = kwargs.get("end_line", None)

        file_path = validate_path(path, context.user_id)

        if not file_storage.exists(file_path):
            raise FileNotFoundException(path)

        file_type = file_storage.get_file_type(file_path)

        if file_type == FileType.TEXT:
            content = self._handle_text_file(file_path, start_line, end_line)
            return ToolExecute(result_content=content)
        elif file_type == FileType.IMAGE:
            relative_path = get_relative_path(file_path, context.user_id)
            share_link = FileShareLinkGenerator.generate_link(context.user_id, relative_path)
            chats = [chat_factory.create_tool_result_chat(text=f"图片文件（{relative_path}）内容", images=[share_link])]
            return ToolExecute(result_content=f"该文件为图片文件，内容见后续消息", tool_chats=chats)
        else:
            return ToolExecute(result_content="无法处理的文件类型", error=True)


    def _handle_text_file(self, file_path: str, start_line: int, end_line: int) -> str:
        """处理文本文件读取"""
        lines = file_storage.read_lines(file_path)

        # 处理行号范围
        total_lines = len(lines)
        start = max(1, start_line)
        end = end_line if end_line is not None else total_lines
        end = min(end, total_lines)

        if start > total_lines:
            return ToolExecute(result_content="指定的起始行号超出文件范围", error=True)

        # 提取指定范围的行
        selected_lines = lines[start - 1 : end]
        return "".join(selected_lines)

