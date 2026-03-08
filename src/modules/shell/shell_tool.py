"""命令行执行工具"""

import subprocess
from typing import Any

from src.agent.tools.base_tool import BaseTool
from src.agent.entities import ToolParameter, AgentContext
from src.common.utils import sys_util
from src.config.config import app_config
from src.modules.file_system.path_validator import get_user_base_dir


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
    ]

    def __init__(self) -> None:
        if sys_util.is_mswindows():
            sysTypeDesc = "当前系统是Windows"
        else:
            sysTypeDesc = "当前系统是Linux"
        self.description = (
            sysTypeDesc
            + "，使用该工具可以执行shell命令。在调用工具前请务必确保命令是安全的，避免执行恶意代码。"
        )

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
        cwd = str(get_user_base_dir(context.user_id))
        timeout = app_config.get("tools")["shell_timeout"]
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
            )
            return result.stdout
        except subprocess.TimeoutExpired as e:
            return f"命令执行超时，超时时间：{timeout}秒\n输出：{e.output}\n"
        except subprocess.CalledProcessError as e:
            return f"命令执行失败，返回码：{e.returncode}\n标准输出：{e.stdout}\n标准错误：{e.stderr}"
