"""发送文件工具"""

from typing import Any

from src.agent.chat_factory import chat_factory
from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolExecute, ToolParameter
from src.storage.file.file_storage import file_storage
from src.user.auth import get_relative_path, validate_path


class SendFileTool(BaseTool):
    """发送文件工具，将指定文件通过聊天消息发送给用户"""

    name = "send_file"
    description = "将指定路径的文件发送给用户。文件路径必须是用户目录下的相对路径。"
    parameters = [
        ToolParameter(
            name="paths",
            type="array",
            description="要发送的文件路径列表（用户目录相对路径），例如：[\"document.txt\", \"images/photo.jpg\"]",
            required=True,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> ToolExecute:
        """执行发送文件操作

        Args:
            context: Agent 执行上下文
            paths: 文件路径列表

        Returns:
            ToolExecute: 工具执行结果，包含 result_content 和 tool_chats
        """
        paths = kwargs.get("paths", [])

        if not paths:
            return ToolExecute(result_content="未提供文件路径", error=True)

        file_chats = []
        success_files = []
        failed_files = []

        for path in paths:
            try:
                # 校验文件路径权限
                file_path = validate_path(path, context.user_id)

                # 校验文件是否存在
                if not file_storage.exists(file_path):
                    failed_files.append(f"{path}（文件不存在）")
                    continue

                # 校验是否为文件（而非目录）
                if not file_storage.is_file(file_path):
                    failed_files.append(f"{path}（不是文件）")
                    continue

                # 生成 file 类型的 Chat 对象（使用相对路径）
                relative_path = get_relative_path(file_path, context.user_id)
                file_chat = chat_factory.create_file_chat(relative_path)
                file_chats.append(file_chat)
                success_files.append(path)

            except Exception as e:
                failed_files.append(f"{path}（{str(e)}）")

        # 构建返回结果
        result_parts = []
        if success_files:
            result_parts.append(f"已成功发送以下文件：{', '.join(success_files)}")
        if failed_files:
            result_parts.append(f"发送失败的文件：{', '.join(failed_files)}")

        result_content = "；".join(result_parts) if result_parts else "文件发送完成"

        return ToolExecute(
            result_content=result_content,
            tool_chats=file_chats if file_chats else None,
            error=bool(failed_files) and not bool(success_files),
        )
