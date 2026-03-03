"""JSON工具函数"""

import json


def to_json(data: dict) -> str:
    """字典转JSON字符串"""
    return json.dumps(data, ensure_ascii=False)


def from_json(json_str: str) -> dict:
    """JSON字符串转字典"""
    return json.loads(json_str)
