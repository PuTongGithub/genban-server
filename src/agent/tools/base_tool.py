"""工具基类定义"""

from abc import ABC, abstractmethod
from typing import Any

from src.agent.entities import ToolParameter


class BaseTool(ABC):
    """工具基类"""

    name: str = ""
    description: str = ""
    parameters: list[ToolParameter] = []

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """执行工具"""
        pass

    def get_schema(self) -> dict[str, Any]:
        """获取工具的 OpenAI 格式 Schema"""
        properties: dict[str, dict[str, Any]] = {}
        required: list[str] = []

        for param in self.parameters:
            prop: dict[str, Any] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            properties[param.name] = prop

            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
