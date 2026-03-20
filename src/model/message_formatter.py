"""消息格式化工具模块"""

import copy
from typing import Callable
from src.agent.entities import Message
from src.model.entities import CallResponse
from src.agent.exceptions import ModelResponseException


def convert_to_call_response(
    response,
    content_formatter: Callable,
) -> CallResponse:
    """将模型响应转换为 CallResponse

    Args:
        response: 模型响应对象
        content_formatter: 可选的 content 格式化函数，用于处理特殊格式

    Returns:
        CallResponse 实例

    Raises:
        ModelResponseException: 当响应格式异常时抛出
    """
    output = response.output
    usage = response.usage

    if output is None or not hasattr(output, "choices") or output.choices is None:
        raise ModelResponseException(f"响应异常：{response}", response)

    message_data = output.choices[0].message
    content = content_formatter(message_data.content)

    message = Message(
        role=message_data.role,
        content=content,
        reasoning_content=message_data["reasoning_content"]
        if "reasoning_content" in message_data
        else "",
        tool_calls=message_data["tool_calls"] if "tool_calls" in message_data else None,
        tool_call_id=message_data["tool_call_id"]
        if "tool_call_id" in message_data
        else None,
    )

    return CallResponse(
        request_id=response.request_id,
        status_code=response.status_code,
        total_tokens=usage.total_tokens,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        finish_reason=output.choices[0].finish_reason,
        message=message,
    )


def format_text_content(content: str | list) -> list:
    """将纯文本 content 转换为列表格式

    Args:
        content: 字符串或列表类型的 content

    Returns:
        列表格式的 content，字符串会被包装为 [{"text": content}]
    """
    if isinstance(content, str):
        return [{"text": content}]
    return content


def pass_through_content(content: list) -> list:
    """直接透传 content，不做转换（用于多模态）

    Args:
        content: 列表类型的 content（多模态响应已经是 list 格式）

    Returns:
        原样返回 content
    """
    return copy.deepcopy(content)


def convert_messages_for_text_model(messages: list[Message]) -> list[dict]:
    """将 Message 列表转换为纯文本模型所需的字典格式

    DashScope Generation API 期望 content 为字符串格式，
    而我们的 Message.content 是列表格式 [{"text": "..."}]，
    需要将其转换为字符串。

    Args:
        messages: Message 对象列表

    Returns:
        转换后的消息字典列表，content 为字符串格式
    """
    converted_messages = []
    for msg in messages:
        msg_dict: dict = {
            "role": msg.role,
            "content": _extract_text_from_content(msg.content),
        }

        if msg.tool_calls:
            msg_dict["tool_calls"] = msg.tool_calls

        if msg.tool_call_id:
            msg_dict["tool_call_id"] = msg.tool_call_id

        converted_messages.append(msg_dict)

    return converted_messages


def convert_messages_for_multimodal_model(messages: list[Message]) -> list[dict]:
    """将 Message 列表转换为多模态模型所需的字典格式

    DashScope MultiModalConversation API 支持列表格式的 content，
    直接使用 Message.content 的列表格式即可。

    Args:
        messages: Message 对象列表

    Returns:
        转换后的消息字典列表，content 为列表格式
    """
    converted_messages = []
    for msg in messages:
        msg_dict: dict = {
            "role": msg.role,
            "content": msg.content,
        }

        if msg.tool_calls:
            msg_dict["tool_calls"] = msg.tool_calls

        if msg.tool_call_id:
            msg_dict["tool_call_id"] = msg.tool_call_id

        converted_messages.append(msg_dict)

    return converted_messages


def _extract_text_from_content(content: list) -> str:
    """从列表格式的 content 中提取文本

    Args:
        content: 列表格式的 content [{"text": "..."}, ...]

    Returns:
        拼接后的字符串
    """
    text_parts = []
    for item in content:
        if isinstance(item, dict) and "text" in item:
            text_parts.append(item["text"])
    return "".join(text_parts)
