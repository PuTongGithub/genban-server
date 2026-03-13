"""系统工具函数"""

try:
    import msvcrt

    _mswindows = True
except ModuleNotFoundError:
    _mswindows = False


def is_mswindows() -> bool:
    """判断是否Windows系统"""
    return _mswindows


def get_os() -> str:
    """获取操作系统"""
    if is_mswindows():
        return "Windows"
    else:
        return "Linux"
