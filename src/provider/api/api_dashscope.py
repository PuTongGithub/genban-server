"""阿里云DashScope API封装"""

import dashscope  # type: ignore
from src.config.config import env_config
from src.common.logger import get_logger

logger = get_logger(__name__)

# 百炼平台接口文档：https://bailian.console.aliyun.com/cn-beijing/?tab=api#/api


def call(model, messages, tools, enable_thinking):
    """调用大模型生成接口（非流式）"""
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


def stream_call(model, messages, tools, enable_thinking):
    """调用大模型生成接口（流式）"""
    kwargs = {
        "api_key": env_config.get("DASHSCOPE_API_KEY"),
        "model": model,
        "messages": messages,
        "tools": tools,
        "enable_thinking": enable_thinking,
        "result_format": "message",
        "stream": True,
        "parallel_tool_calls": True,
        "incremental_output": False,
    }
    try:
        responses = dashscope.Generation.call(**kwargs)
        for response in responses:
            yield response
    except Exception:
        logger.exception(f"DashScope API 流式调用失败，model: {model}")
        raise


def call_multimodal(model, messages, tools, enable_thinking):
    """调用多模态大模型接口（非流式）"""
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
        response = dashscope.MultiModalConversation.call(**kwargs)
        return response
    except Exception:
        logger.exception(f"DashScope 多模态 API 调用失败，model: {model}")
        raise


def stream_call_multimodal(model, messages, tools, enable_thinking):
    """调用多模态大模型接口（流式）"""
    kwargs = {
        "api_key": env_config.get("DASHSCOPE_API_KEY"),
        "model": model,
        "messages": messages,
        "tools": tools,
        "enable_thinking": enable_thinking,
        "result_format": "message",
        "stream": True,
        "parallel_tool_calls": True,
        "incremental_output": False,
    }
    try:
        responses = dashscope.MultiModalConversation.call(**kwargs)
        for response in responses:
            yield response
    except Exception:
        logger.exception(f"DashScope 多模态 API 流式调用失败，model: {model}")
        raise
