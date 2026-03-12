"""阿里云DashScope API封装"""

import dashscope
from src.config.config import env_config
from src.common.logger import get_logger

logger = get_logger(__name__)


def call(model, messages, tools, enable_thinking):
    """调用大模型生成接口"""
    kwargs = {
        "api_key": env_config.get("DASHSCOPE_API_KEY"),
        "model": model,
        "messages": messages,
        "tools": tools,
        "enable_thinking": enable_thinking,
        "result_format": "message",
        "stream": False,
        "parallel_tool_calls": True,
    }
    try:
        response = dashscope.Generation.call(**kwargs)
        return response
    except Exception:
        logger.exception(f"DashScope API 调用失败，model: {model}")
        raise
