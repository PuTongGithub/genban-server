"""自定义异常类"""


class EnvConfigNotFoundException(Exception):
    """环境配置未找到异常"""

    def __init__(self, key: str):
        super().__init__(f"env config:{key} not found")


class ModelConfigNotFoundException(Exception):
    """模型配置未找到异常"""

    def __init__(self, model_name: str):
        super().__init__(f"model config:{model_name} not found")


class ConfigNotFoundException(Exception):
    """配置文件未找到异常"""

    def __init__(self, path: str):
        super().__init__(f"config file not found: {path}")
