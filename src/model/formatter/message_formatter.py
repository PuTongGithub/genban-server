"""消息格式化工具模块"""

import copy

from src.agent.entities import Message, MessageRole, ToolCall, ToolCallFunction
from src.agent.exceptions import ModelResponseException
from src.model.entities import CallResponse


def convert_dashscope_tool_calls(tool_calls_data: list | None) -> list[ToolCall] | None:
    """将 DashScope 的 tool_calls 转换为 ToolCall 对象列表

    Args:
        tool_calls_data: DashScope 返回的 tool_calls 数据（dict 类型）

    Returns:
        ToolCall 对象列表，如果输入为空则返回 None
    """
    if tool_calls_data is None:
        return None

    tool_calls: list[ToolCall] = []
    for data in tool_calls_data:
        func_data = data.get("function", {})
        tool_calls.append(
            ToolCall(
                index=data.get("index", 0),
                id=data.get("id", ""),
                type=data.get("type", "function"),
                function=ToolCallFunction(
                    name=func_data.get("name", ""),
                    arguments=func_data.get("arguments", ""),
                ),
            )
        )
    return tool_calls


def convert_openai_tool_calls(tool_calls_data) -> list[ToolCall] | None:
    """将 OpenAI 的 tool_calls 转换为 ToolCall 对象列表

    Args:
        tool_calls_data: OpenAI 返回的 tool_calls 数据（class 类型）

    Returns:
        ToolCall 对象列表，如果输入为空则返回 None
    """
    if tool_calls_data is None:
        return None

    tool_calls: list[ToolCall] = []
    for data in tool_calls_data:
        func = data.function
        tool_calls.append(
            ToolCall(
                index=getattr(data, "index", 0),
                id=data.id or "",
                type=data.type or "function",
                function=ToolCallFunction(
                    name=func.name if func and func.name else "",
                    arguments=func.arguments if func and func.arguments else "",
                ),
            )
        )
    return tool_calls


def convert_dashscope_to_call_response(response) -> CallResponse:
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

    if (
        output is None
        or not hasattr(output, "choices")
        or output.choices is None
        or len(output.choices) == 0
    ):
        raise ModelResponseException(f"响应异常：{response}", response)

    message_data = output.choices[0].message
    content = format_text_content(message_data.content)

    tool_calls_data = message_data.get("tool_calls") if "tool_calls" in message_data else None
    tool_calls = convert_dashscope_tool_calls(tool_calls_data)

    message = Message(
        role=message_data.role or MessageRole.ASSISTANT.value,
        content=content,
        reasoning_content=message_data["reasoning_content"]
        if "reasoning_content" in message_data
        else "",
        tool_calls=tool_calls,
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


def convert_openai_to_call_response(response) -> CallResponse:
    """将 OpenAI API 响应转换为 CallResponse

    Args:
        response: OpenAI ChatCompletion 响应对象

    Returns:
        CallResponse 实例

    Raises:
        ModelResponseException: 当响应格式异常时抛出
    """
    if response.choices is None or len(response.choices) == 0:
        raise ModelResponseException(f"响应异常：{response}", response)

    choice = response.choices[0]
    message_data = choice.delta

    content = format_text_content(message_data.content or "")
    reasoning_content = ""
    if hasattr(message_data, "reasoning_content") and message_data.reasoning_content:
        reasoning_content = message_data.reasoning_content

    tool_calls = convert_openai_tool_calls(message_data.tool_calls)

    message = Message(
        role=message_data.role or MessageRole.ASSISTANT.value,
        content=content,
        reasoning_content=reasoning_content,
        tool_calls=tool_calls,
    )

    usage = response.usage

    return CallResponse(
        request_id=response.id,
        status_code=200,
        total_tokens=usage.total_tokens if usage else 0,
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
        finish_reason=choice.finish_reason,
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
            "reasoning_content": msg.reasoning_content,
        }

        if msg.tool_calls:
            msg_dict["tool_calls"] = [tc.to_dict() for tc in msg.tool_calls]

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
            "reasoning_content": msg.reasoning_content,
        }

        if msg.tool_calls:
            msg_dict["tool_calls"] = [tc.to_dict() for tc in msg.tool_calls]

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
