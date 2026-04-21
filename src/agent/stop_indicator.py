"""停止指示器模块"""

import threading


class StopIndicator:
    """停止指示器，用于在模型生成过程中传递停止信号"""

    def __init__(self) -> None:
        self._stopped = False
        self._lock = threading.Lock()

    def is_stopped(self) -> bool:
        """检查是否已被置为停止状态"""
        with self._lock:
            return self._stopped

    def stop(self) -> None:
        """将指示器置为停止状态"""
        with self._lock:
            self._stopped = True
