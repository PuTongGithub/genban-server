"""阿里云DashScope API封装"""

import dashscope
from dashscope.api_entities.dashscope_response import GenerationResponse
from src.config.config import env_config


def call(model, messages, tools, enable_thinking) -> GenerationResponse:
    """调用大模型生成接口"""
    kwargs = {
        'api_key': env_config.get('DASHSCOPE_API_KEY'),
        'model': model,
        'messages': messages,
        'tools': tools,
        'enable_thinking': enable_thinking,
        'result_format': 'message',
        'stream': False,
        'parallel_tool_calls': True
    }
    return dashscope.Generation.call(**kwargs)
