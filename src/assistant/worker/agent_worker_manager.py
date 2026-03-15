"""AgentWorkerManager - 管理所有用户的 Worker 和消息队列"""

import asyncio
from src.common.async_executor import AsyncExecutor
from src.modules.user_message.entities import QueueItem
from src.assistant.worker.user_agent_worker import UserAgentWorker


class AgentWorkerManager:
    """AgentWorker 管理器 - 管理消息队列和所有用户的 Worker"""

    def __init__(self) -> None:
        """初始化管理器"""
        self._executor = AsyncExecutor(name="AgentWorkerManager", on_stop=self._on_stop)
        self._workers: dict[str, UserAgentWorker] = {}
        self._queue: asyncio.Queue[QueueItem | None] | None = None
        self._running = True
        self._task = self._executor.submit(self._dispatch_loop())

    def _on_stop(self) -> None:
        """在管理器停止时调用，用于清理资源"""
        self.put(None)
        self._running = False
        self._task.result()

    def put(self, item: QueueItem | None) -> None:
        """同步方法，将消息放入队列（线程安全）"""
        if not self._running or self._queue is None:
            raise RuntimeError("AgentWorkerManager 未运行，无法放入消息")
        self._executor.submit(self._queue.put(item))

    async def _dispatch_loop(self) -> None:
        """消息分发主循环 - 从队列拉取消息并分发给对应的 UserAgentWorker"""
        self._queue = asyncio.Queue()
        while self._running:
            try:
                # 从队列获取消息（异步等待）
                item: QueueItem | None = await self._queue.get()
                if item is None:
                    break

                # 分发消息给对应的 Worker 处理
                await self._dispatch_message(item)

                # 标记任务完成
                self._queue.task_done()

            except Exception as e:
                # 处理异常，记录日志
                print(f"AgentWorkerManager 分发消息异常: {e}")
                await asyncio.sleep(0.1)  # 短暂休眠避免CPU空转

    async def _dispatch_message(self, item: QueueItem) -> None:
        """分发消息给指定用户的 Worker"""
        user_id = item.user_id
        chat = item.chat

        # 获取或创建用户的 Worker
        if user_id not in self._workers:
            self._workers[user_id] = UserAgentWorker(user_id)

        worker = self._workers[user_id]

        # 提交给 Worker 处理
        await worker.process_chat(chat)


# 全局单例（模块加载时初始化）
agent_worker_manager = AgentWorkerManager()
