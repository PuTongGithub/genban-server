"""OpenAI 兼容 API 封装"""

from openai import OpenAI

from src.common.logger import get_logger

logger = get_logger(__name__)


def _build_kwargs(
    model: str,
    messages: list[dict],
    stream: bool,
    tools: list | None,
    enable_thinking: bool,
    response_format_type: str,
) -> dict:
    """构建 OpenAI API 调用参数

    Args:
        model: 模型名称
        messages: 消息列表
        stream: 是否流式
        tools: 工具列表
        enable_thinking: 是否启用思考模式
        response_format_type: 响应格式类型

    Returns:
        API 调用参数字典
    """
    kwargs: dict = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "presence_penalty": 1.5,
        "max_tokens": 16384,
    }

    if stream:
        kwargs["stream_options"] = {"include_usage": True}

    if tools:
        kwargs["tools"] = tools
        kwargs["parallel_tool_calls"] = True

    if enable_thinking:
        kwargs["extra_body"] = {
            "thinking": {"type": "enabled", "clear_thinking": False},
            "chat_template_kwargs": {"preserve_thinking": True},
            "enable_thinking": True,
            "preserve_thinking": True,
            "top_k": 20,
            "repetition_penalty": 1.0,
        }
        kwargs["temperature"] = 1.0
        kwargs["top_p"] = 0.95
    else:
        kwargs["extra_body"] = {
            "thinking": {"type": "disabled", "clear_thinking": False},
            "chat_template_kwargs": {"enable_thinking": False, "preserve_thinking": True},
            "enable_thinking": False,
            "preserve_thinking": True,
            "top_k": 20,
            "repetition_penalty": 1.0,
        }
        kwargs["temperature"] = 0.7
        kwargs["top_p"] = 0.8

    if response_format_type != "text":
        kwargs["response_format"] = {"type": response_format_type}

    return kwargs


def _create_client(api_key: str, base_url: str) -> OpenAI:
    """创建 OpenAI 客户端

    Args:
        api_key: API 密钥
        base_url: API 服务端点地址

    Returns:
        OpenAI 客户端实例
    """
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


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
    client = _create_client(api_key, base_url)
    kwargs = _build_kwargs(
        model=model,
        messages=messages,
        stream=False,
        tools=tools,
        enable_thinking=enable_thinking,
        response_format_type=response_format_type,
    )

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
    client = _create_client(api_key, base_url)
    kwargs = _build_kwargs(
        model=model,
        messages=messages,
        stream=True,
        tools=tools,
        enable_thinking=enable_thinking,
        response_format_type=response_format_type,
    )

    try:
        for chunk in client.chat.completions.create(**kwargs):
            yield chunk
    except Exception:
        logger.exception(f"OpenAI API 流式调用失败，model: {model}, base_url: {base_url}")
        raise
