"""QQ 机器人测试程序

使用 ThreadExecutor 运行 botpy 客户端
支持接收消息、记录 user_openid、发送消息
"""

import sys
from pathlib import Path

import botpy
from botpy.message import C2CMessage
from botpy.types.message import MarkdownPayload

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.common.async_executor import AsyncExecutor
from src.common.logger import get_logger

logger = get_logger(__name__)
intents = botpy.Intents(public_messages=True)


class QQBotClient(botpy.Client):
    """QQ 机器人客户端"""

    def __init__(self) -> None:
        super().__init__(intents=intents, is_sandbox=True)
        self._user_openid: str | None = None

    async def on_ready(self) -> None:
        """机器人就绪回调"""
        print(f"机器人 「{self.robot.name}」 已就绪!")

    async def on_c2c_message_create(self, message: C2CMessage) -> None:
        """收到 C2C 消息回调"""
        print(f"收到消息：{message.content}")
        print(f"发送者 user_openid: {message.author.user_openid}")

        if not self._user_openid:
            self._user_openid = message.author.user_openid

        await message._api.post_c2c_message(
            openid=message.author.user_openid,
            msg_type=0,
            msg_id=message.id,
            content=f"我收到了你的消息：{message.content}",
        )

    async def send_message(self, content: str) -> None:
        """发送消息给记录的 user"""
        if not self._user_openid:
            print("尚未记录 user_openid，无法发送消息")
            return

        markdown = MarkdownPayload(content=content)
        try:
            await self.api.post_c2c_message(openid=self._user_openid, msg_type=2, markdown=markdown)
            print(f"消息发送成功: {content}")
        except Exception as e:
            print(f"消息发送失败: {e}")
            raise e


class QQBotRunner:
    """QQ 机器人运行类，整合客户端和运行管理"""

    def __init__(self, app_id: str, app_secret: str) -> None:
        self._app_id = app_id
        self._app_secret = app_secret
        self._client: QQBotClient | None = None
        self._executor: AsyncExecutor = AsyncExecutor(name="QQBotRunner")

    async def _run_client(self) -> None:
        """在线程中运行机器人客户端"""
        self._client = QQBotClient()
        async with self._client:
            await self._client.start(appid=self._app_id, secret=self._app_secret)

    def begin(self) -> None:
        """启动机器人"""
        self._executor.submit(self._run_client())
        print("机器人启动中...")

    def end(self) -> None:
        """停止机器人"""
        self._executor.stop()
        print("机器人已停止")

    def send_message(self, content: str) -> None:
        """发送消息给记录的 user"""
        if not self._client:
            print("机器人未启动，无法发送消息")
            return
        self._executor.submit(self._client.send_message(content))

    def is_running(self) -> bool:
        """检查是否运行中"""
        return self._executor.is_running()


def main() -> None:
    """主函数"""
    runner = QQBotRunner(app_id="102830734", app_secret="1FUjzFWn5NgzJdyJf1OmAZyOoFg8a3W0")

    try:
        runner.begin()
        print("\n=== 输入消息内容发送给机器人，输入 'quit' 退出 ===\n")

        while runner.is_running():
            try:
                content = input("> ").strip()
                if content.lower() == "quit":
                    print("\n收到退出信号，正在退出...")
                    runner.end()
                    break
                if content:
                    runner.send_message(content)
            except KeyboardInterrupt:
                print("\n收到中断信号，正在退出...")
                runner.end()
                break
            except Exception as e:
                print(f"输入处理异常: {e}")

    except Exception as e:
        logger.exception(f"程序异常: {e}")
    finally:
        runner.end()
        print("程序已退出")


if __name__ == "__main__":
    main()
