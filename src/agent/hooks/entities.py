from dataclasses import dataclass


@dataclass
class ModelConfig:
    """模型配置"""

    model_key: str = ""  # 模型 key
    enable_thinking: bool = False  # 是否启用思考模式
