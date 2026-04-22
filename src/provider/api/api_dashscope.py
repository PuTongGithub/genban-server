"""阿里云DashScope API封装"""

import dashscope  # type: ignore

from src.common.logger import get_logger
from src.config.config import env_config
from src.model.entities import ModelCallOptions

logger = get_logger(__name__)

# 百炼平台接口文档：https://bailian.console.aliyun.com/cn-beijing/?tab=api#/api


def _build_common_kwargs(
    model: str,
    messages: list,
    tools: list | None,
    enable_thinking: bool,
    stream: bool,
    options: ModelCallOptions | None = None,
) -> dict:
    """构建通用调用参数

    Args:
        model: 模型名称
        messages: 消息列表
        tools: 工具列表
        enable_thinking: 是否启用思考模式
        stream: 是否为流式调用
        options: 模型调用选项参数

    Returns:
        API 调用参数字典
    """
    opts = options or ModelCallOptions()

    kwargs: dict = {
        "api_key": env_config.get("DASHSCOPE_API_KEY"),
        "model": model,
        "messages": messages,
        "tools": tools,
        "enable_thinking": enable_thinking,
        "stream": stream,
        "preserve_thinking": True,
        "result_format": "message",
        "parallel_tool_calls": True,
    }

    if stream:
        kwargs["incremental_output"] = True
    if opts.temperature is not None:
        kwargs["temperature"] = opts.temperature
    if opts.top_p is not None:
        kwargs["top_p"] = opts.top_p
    if opts.top_k is not None:
        kwargs["top_k"] = opts.top_k
    if opts.presence_penalty is not None:
        kwargs["presence_penalty"] = opts.presence_penalty
    if opts.repetition_penalty is not None:
        kwargs["repetition_penalty"] = opts.repetition_penalty
    if opts.max_tokens is not None:
        kwargs["max_tokens"] = opts.max_tokens
    if opts.response_format_type is not None:
        kwargs["response_format"] = {"type": opts.response_format_type}

    return kwargs


def call(
    model: str,
    messages: list,
    tools: list | None = None,
    enable_thinking: bool = True,
    options: ModelCallOptions | None = None,
):
    """调用大模型生成接口（非流式）

    Args:
        model: 模型名称
        messages: 消息列表
        tools: 工具列表
        enable_thinking: 是否启用思考模式
        options: 模型调用选项参数

    Returns:
        DashScope 响应对象
    """
    kwargs = _build_common_kwargs(
        model=model,
        messages=messages,
        tools=tools,
        enable_thinking=enable_thinking,
        stream=False,
        options=options,
    )

    try:
        response = dashscope.Generation.call(**kwargs)
        return response
    except Exception:
        logger.exception(f"DashScope API 调用失败，model: {model}")
        raise


def stream_call(
    model: str,
    messages: list,
    tools: list | None = None,
    enable_thinking: bool = True,
    options: ModelCallOptions | None = None,
):
    """调用大模型生成接口（流式）

    Args:
        model: 模型名称
        messages: 消息列表
        tools: 工具列表
        enable_thinking: 是否启用思考模式
        options: 模型调用选项参数

    Yields:
        DashScope 流式响应块
    """
    kwargs = _build_common_kwargs(
        model=model,
        messages=messages,
        tools=tools,
        enable_thinking=enable_thinking,
        stream=True,
        options=options,
    )

    try:
        responses = dashscope.Generation.call(**kwargs)
        for response in responses:
            yield response
    except Exception:
        logger.exception(f"DashScope API 流式调用失败，model: {model}")
        raise


def call_multimodal(
    model: str,
    messages: list,
    tools: list | None = None,
    enable_thinking: bool = True,
    options: ModelCallOptions | None = None,
):
    """调用多模态大模型接口（非流式）

    Args:
        model: 模型名称
        messages: 消息列表
        tools: 工具列表
        enable_thinking: 是否启用思考模式
        options: 模型调用选项参数

    Returns:
        DashScope 响应对象
    """
    kwargs = _build_common_kwargs(
        model=model,
        messages=messages,
        tools=tools,
        enable_thinking=enable_thinking,
        stream=False,
        options=options,
    )

    try:
        response = dashscope.MultiModalConversation.call(**kwargs)
        return response
    except Exception:
        logger.exception(f"DashScope 多模态 API 调用失败，model: {model}")
        raise


def stream_call_multimodal(
    model: str,
    messages: list,
    tools: list | None = None,
    enable_thinking: bool = True,
    options: ModelCallOptions | None = None,
):
    """调用多模态大模型接口（流式）

    Args:
        model: 模型名称
        messages: 消息列表
        tools: 工具列表
        enable_thinking: 是否启用思考模式
        options: 模型调用选项参数

    Yields:
        DashScope 流式响应块
    """
    kwargs = _build_common_kwargs(
        model=model,
        messages=messages,
        tools=tools,
        enable_thinking=enable_thinking,
        stream=True,
        options=options,
    )

    try:
        responses = dashscope.MultiModalConversation.call(**kwargs)
        for response in responses:
            yield response
    except Exception:
        logger.exception(f"DashScope 多模态 API 流式调用失败，model: {model}")
        raise
