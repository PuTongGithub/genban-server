"""系统工具函数"""

try:
    import msvcrt
    _mswindows = True
except ModuleNotFoundError:
    _mswindows = False


def is_mswindows() -> bool:
    """判断是否Windows系统"""
    return _mswindows
