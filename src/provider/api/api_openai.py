"""OpenAI 兼容 API 封装"""

from openai import OpenAI

from src.common.logger import get_logger

logger = get_logger(__name__)


def call(
    model: str,
    messages: list[dict],
    api_key: str,
    base_url: str,
    tools: list | None = None,
    enable_thinking: bool = True,
    response_format_type: str = "text",
):
    """调用 OpenAI 兼容 API（非流式）

    Args:
        model: 模型名称
        messages: 消息列表
        api_key: API 密钥
        base_url: API 服务端点地址
        tools: 工具列表
        enable_thinking: 是否启用思考模式
        response_format_type: 响应格式类型

    Returns:
        OpenAI ChatCompletion 响应对象
    """
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    kwargs: dict = {
        "model": model,
        "messages": messages,
        "stream": False,
    }

    if tools:
        kwargs["tools"] = tools
        kwargs["parallel_tool_calls"] = True

    if enable_thinking:
        kwargs["extra_body"] = {
            "thinking": {"type": "enabled", "clear_thinking": False},
            "enable_thinking": True,
            "preserve_thinking": True,
        }
    else:
        kwargs["extra_body"] = {
            "thinking": {"type": "disabled", "clear_thinking": False},
            "enable_thinking": False,
            "preserve_thinking": True,
        }

    if response_format_type != "text":
        kwargs["response_format"] = {"type": response_format_type}

    try:
        response = client.chat.completions.create(**kwargs)
        return response
    except Exception:
        logger.exception(f"OpenAI API 调用失败，model: {model}, base_url: {base_url}")
        raise


def stream_call(
    model: str,
    messages: list[dict],
    api_key: str,
    base_url: str,
    tools: list | None = None,
    enable_thinking: bool = True,
    response_format_type: str = "text",
):
    """调用 OpenAI 兼容 API（流式）

    Args:
        model: 模型名称
        messages: 消息列表
        api_key: API 密钥
        base_url: API 服务端点地址
        tools: 工具列表
        enable_thinking: 是否启用思考模式
        response_format_type: 响应格式类型

    Yields:
        OpenAI ChatCompletionChunk 响应块
    """
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    kwargs: dict = {
        "model": model,
        "messages": messages,
        "stream": True,
        "stream_options": {"include_usage": True},
    }

    if tools:
        kwargs["tools"] = tools
        kwargs["parallel_tool_calls"] = True

    if enable_thinking:
        kwargs["extra_body"] = {
            "thinking": {"type": "enabled", "clear_thinking": False},
            "enable_thinking": True,
            "preserve_thinking": True,
        }
    else:
        kwargs["extra_body"] = {
            "thinking": {"type": "disabled", "clear_thinking": False},
            "enable_thinking": False,
            "preserve_thinking": True,
        }

    if response_format_type != "text":
        kwargs["response_format"] = {"type": response_format_type}

    try:
        for chunk in client.chat.completions.create(**kwargs):
            yield chunk
    except Exception:
        logger.exception(f"OpenAI API 流式调用失败，model: {model}, base_url: {base_url}")
        raise
