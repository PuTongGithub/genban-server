"""OpenAI 兼容 API 封装"""

from openai import OpenAI

from src.common.logger import get_logger
from src.model.entities import ModelCallOptions

logger = get_logger(__name__)


def _build_kwargs(
    model: str,
    messages: list[dict],
    stream: bool,
    tools: list | None,
    enable_thinking: bool,
    options: ModelCallOptions | None = None
) -> dict:
    """构建 OpenAI API 调用参数

    Args:
        model: 模型名称
        messages: 消息列表
        stream: 是否流式
        tools: 工具列表
        enable_thinking: 是否启用思考模式
        options: 模型调用选项参数

    Returns:
        API 调用参数字典
    """
    opts = options or ModelCallOptions()

    extra_body: dict = {
        "preserve_thinking": True,
        "chat_template_kwargs": {"preserve_thinking": True},
        "thinking": {"clear_thinking": False},
    }

    kwargs: dict = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "extra_body": extra_body,
    }

    if stream:
        kwargs["stream_options"] = {"include_usage": True}

    if tools:
        kwargs["tools"] = tools
        kwargs["parallel_tool_calls"] = True

    if enable_thinking:
        extra_body["enable_thinking"] = True
        extra_body["thinking"]["type"] = "enabled"
    else:
        extra_body["enable_thinking"] = False
        extra_body["thinking"]["type"] = "disabled"
        extra_body["chat_template_kwargs"]["enable_thinking"] = False

    if opts.max_tokens is not None:
        kwargs["max_tokens"] = opts.max_tokens
    if opts.presence_penalty is not None:
        kwargs["presence_penalty"] = opts.presence_penalty
    if opts.top_p is not None:
        kwargs["top_p"] = opts.top_p
    if opts.temperature is not None:
        kwargs["temperature"] = opts.temperature
    if opts.response_format_type is not None:
        kwargs["response_format"] = {"type": opts.response_format_type}
    if opts.top_k is not None:
        extra_body["top_k"] = opts.top_k
    if opts.repetition_penalty is not None:
        extra_body['repetition_penalty'] = opts.repetition_penalty

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
    options: ModelCallOptions | None = None,
):
    """调用 OpenAI 兼容 API（非流式）

    Args:
        model: 模型名称
        messages: 消息列表
        api_key: API 密钥
        base_url: API 服务端点地址
        tools: 工具列表
        enable_thinking: 是否启用思考模式
        options: 模型调用选项参数

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
        options=options,
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
    options: ModelCallOptions | None = None,
):
    """调用 OpenAI 兼容 API（流式）

    Args:
        model: 模型名称
        messages: 消息列表
        api_key: API 密钥
        base_url: API 服务端点地址
        tools: 工具列表
        enable_thinking: 是否启用思考模式
        options: 模型调用选项参数

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
        options=options,
    )

    try:
        for chunk in client.chat.completions.create(**kwargs):
            yield chunk
    except Exception:
        logger.exception(f"OpenAI API 流式调用失败，model: {model}, base_url: {base_url}")
        raise
