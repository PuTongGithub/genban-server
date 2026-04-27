"""消息格式化工具模块"""

from src.agent.entities import Content, Message, MessageRole, ToolCall, ToolCallFunction
from src.agent.exceptions import ModelResponseException
from src.model.entities import CallResponse
from src.modules.file_system.components.file_share_link_generator import FileShareLinkGenerator
from src.user.auth import validate_path


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
    content = format_text_content(message_data.content or "")

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
        role = MessageRole.ASSISTANT.value
        content = ""
        reasoning_content = ""
        tool_calls = None
        finish_reason = None
    else:
        choice = response.choices[0]
        if hasattr(choice, "delta"):
            message_data = choice.delta
        elif hasattr(choice, "message"):
            message_data = choice.message
        else:
            raise ModelResponseException(f"响应异常：{response}", response)

        role = message_data.role or MessageRole.ASSISTANT.value
        content = format_text_content(message_data.content or "")
        reasoning_content = ""
        if hasattr(message_data, "reasoning_content") and message_data.reasoning_content:
            reasoning_content = message_data.reasoning_content
        if hasattr(message_data, "reasoning") and message_data.reasoning:
            reasoning_content = message_data.reasoning
        tool_calls = convert_openai_tool_calls(message_data.tool_calls)
        finish_reason = choice.finish_reason

    message = Message(
        role=role,
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
        finish_reason=finish_reason,
        message=message,
    )


def format_text_content(content: str | list) -> list[Content]:
    """将纯文本 content 转换为列表格式

    Args:
        content: 字符串或列表类型的 content

    Returns:
        列表格式的 content，字符串会被包装为 [{"text": content}]
    """
    if isinstance(content, str):
        return [Content(text=content)]
    else:
        contents = []
        for item in content:
            if isinstance(item, str):
                contents.append(Content(text=item))
            elif isinstance(item, dict) and item.get("text") is not None:
                contents.append(Content(text=item.get("text")))
        return contents


def _convert_image_url_to_base64(image_url: str) -> str | None:
    """将图片 URL 转换为 Base64 编码（如果是分享链接）

    如果是分享链接，则转换为 Base64 编码；否则保持原样

    Args:
        image_url: 图片 URL

    Returns:
        转换后的 URL 或 Base64 编码字符串
    """
    result = FileShareLinkGenerator.extract_path_from_share_link(image_url)
    if result:
        user_id, path = result
        try:
            file_path = validate_path(path, user_id)
            if file_path.exists():
                return FileShareLinkGenerator.encode_file_to_base64(file_path)
            else:
                return None
        except Exception:
            # 如果转换失败，返回原链接
            return image_url
    return image_url


def _convert_content_images_to_base64(content: list[dict]) -> list[dict]:
    """将 content 列表中的图片链接转为 Base64

    Args:
        content: content 字典列表

    Returns:
        转换后的 content 列表
    """
    result = []
    for item in content:
        new_item = dict(item)
        if "image" in new_item and new_item["image"]:
            image = _convert_image_url_to_base64(new_item["image"])
            if image is not None:
                new_item["image"] = image
                result.append(new_item)
        else:
            result.append(new_item)
    return result


def _convert_content_for_openai(content: list[Content]) -> list:
    """从列表格式的 content 中提取文本

    Args:
        content: 列表格式的 content [{"text": "..."}, ...]

    Returns:
        拼接后的字符串
    """
    list = []
    for item in content:
        if item.text is not None:
            list.append({"type": "text", "text": item.text})
        elif item.image is not None:
            image_url = _convert_image_url_to_base64(item.image)
            if image_url is not None:
                list.append({"type": "image_url", "image_url": {"url": image_url}})
        elif item.video is not None:
            list.append({"type": "video_url", "video_url": {"url": item.video}})
    return list


def convert_messages_for_openai(messages: list[Message]) -> list[dict]:
    """将 Message 列表转换为 OpenAI 模型调用所需的字典格式

    Args:
        messages: Message 对象列表

    Returns:
        转换后的消息字典列表，content 为字符串格式
    """
    converted_messages = []
    for msg in messages:
        msg_dict: dict = {
            "role": msg.role,
            "content": _convert_content_for_openai(msg.content),
            "reasoning_content": msg.reasoning_content,
        }

        if msg.tool_calls:
            msg_dict["tool_calls"] = [tc.to_dict() for tc in msg.tool_calls]

        if msg.tool_call_id:
            msg_dict["tool_call_id"] = msg.tool_call_id

        converted_messages.append(msg_dict)

    return converted_messages


def convert_messages_for_dashscope(messages: list[Message]) -> list[dict]:
    """将 Message 列表转换为 DashScope 模型调用所需的字典格式

    Args:
        messages: Message 对象列表

    Returns:
        转换后的消息字典列表，content 为列表格式
    """
    converted_messages = []
    for msg in messages:
        msg_dict = msg.to_dict()
        # 将 content 中的图片链接转为 Base64
        if msg_dict.get("content"):
            msg_dict["content"] = _convert_content_images_to_base64(msg_dict["content"])
        converted_messages.append(msg_dict)

    return converted_messages
