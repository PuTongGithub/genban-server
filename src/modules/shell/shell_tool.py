"""命令行执行工具"""

import subprocess
from typing import Any

from src.agent.tools.base_tool import BaseTool
from src.agent.entities import ToolParameter, AgentContext
from src.common.utils import sys_util
from src.config.config import app_config
from src.common.utils.path_util import (
    get_user_dir,
    validate_path,
    PathNotAllowedException,
)


# 命令行执行工具
class ShellTool(BaseTool):
    name = "shell"
    description = ""
    parameters = [
        ToolParameter(
            name="command",
            type="string",
            description="要执行的shell命令（命令执行的工作目录为用户目录）",
            required=True,
        ),
        ToolParameter(
            name="cwd",
            type="string",
            description="命令执行的工作目录（可选，默认为用户目录）",
            required=False,
        ),
        ToolParameter(
            name="description",
            type="string",
            description="编写清晰、简洁的描述，说明你的命令做什么。包含足够的上下文，以便用户能够理解你的命令将做什么。",
            required=False,
        ),
    ]

    def __init__(self, user_id: str) -> None:
        systemDesc = "Windows" if sys_util.is_mswindows() else "Linux"
        self.description = f"""使用该工具可以执行shell命令。
重要提示：
- 当前系统：{systemDesc}
- 用户目录：{get_user_dir(user_id)}
- 在执行破坏性操作（例如 git reset --hard、git push --force、rm -rf）之前，请考虑是否有更安全的替代方案可以达到相同的目标。仅在破坏性操作确实是最佳方法时才使用它们
- 尽量在整个会话期间使用绝对路径，避免使用相对路径（cd 切换目录）
- 不要使用换行符来分隔命令（在引号字符串中可以使用换行符）
- 始终在命令中使用双引号引用包含空格的文件路径（例如 cd "path with spaces/file.txt"）
- 虽然 shell 工具可以做很多的事情，但最好优先使用其他内置工具，因为它们提供更好的用户体验，并且更容易监控工具调用情况和管控权限。
"""

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行shell命令操作

        Args:
            context: Agent 执行上下文
            command: 要执行的shell命令
            cwd: 命令执行的工作目录

        Returns:
            命令执行结果的标准输出（包含标准错误）

        Raises:
            TimeoutExpired: 命令执行超时
            CalledProcessError: 命令执行失败，返回非零状态码
        """

        command = kwargs.get("command", "")
        cwd_param = kwargs.get("cwd", "")
        timeout = app_config.get("tools")["shell_timeout"]

        # 确定工作目录
        if cwd_param:
            try:
                cwd = str(validate_path(cwd_param, context.user_id))
            except PathNotAllowedException:
                return f"错误：工作目录 '{cwd_param}' 不在允许访问的范围内"
        else:
            cwd = str(get_user_dir(context.user_id))

        if not command.strip():
            return "命令不能为空"

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                check=True,
                text=True,
                capture_output=True,
                timeout=timeout,
                stdin=subprocess.DEVNULL,
                encoding="utf-8",
                errors="replace",
            )
            return result.stdout
        except subprocess.TimeoutExpired as e:
            return f"命令执行超时，超时时间：{timeout}秒\n输出：{e.output}\n"
        except subprocess.CalledProcessError as e:
            return f"命令执行失败，返回码：{e.returncode}\n标准输出：{e.stdout}\n标准错误：{e.stderr}"
