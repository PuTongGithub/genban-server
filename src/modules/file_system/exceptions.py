"""FileSystem 模块异常类"""


class PathNotAllowedException(Exception):
    """路径不在允许范围内异常"""

    def __init__(self, path: str):
        super().__init__(f"无权访问该路径: {path}")


class FileNotFoundException(Exception):
    """文件不存在异常"""

    def __init__(self, path: str):
        super().__init__(f"文件不存在: {path}")


class LineNumberOutOfRangeException(Exception):
    """行号超出范围异常"""

    def __init__(self, line_num: int, total_lines: int):
        super().__init__(f"行号 {line_num} 超出范围，文件共 {total_lines} 行")
