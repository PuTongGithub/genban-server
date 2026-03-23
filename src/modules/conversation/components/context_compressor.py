"""上下文压缩服务"""

import json

from src.agent.chat_factory import chat_factory
from src.agent.entities import Chat
from src.common.logger import get_logger
from src.config.config import app_config
from src.config.prompts_loader import prompts_loader
from src.model.entities import CallResponse
from src.model.model_caller import model_caller
from src.modules.conversation.entities import CompressionResult
from src.modules.conversation.exceptions import ContextCompressionError
from src.modules.module_manager import build_modules_prompt
from src.user.user_cost.user_cost_manager import user_cost_manager

logger = get_logger(__name__)


class ContextCompressor:
    """上下文压缩器，使用大模型压缩对话历史"""

    def compress(self, user_id: str, chats: list[Chat]) -> CompressionResult:
        """压缩对话历史

        Args:
            user_id: 用户 ID
            chats: 待压缩的 Chat 列表（按时间升序排列）

        Returns:
            压缩结果对象

        Raises:
            ContextCompressionError: 压缩失败时抛出
        """
        if not chats:
            raise ContextCompressionError("没有待压缩的对话内容")

        # 构造 prompt
        prompt = self._build_compression_prompt(chats)

        # 调用大模型进行压缩
        response = self._call_compression_model(prompt)

        # 记录 token 用量（type=conversation）
        self._record_compression_cost(user_id, response)

        # 解析 JSON 结果
        result = self._parse_compression_result(response, chats)

        logger.info(
            f"对话压缩完成: user_id={user_id}, "
            f"summary_length={len(result.summary)}, "
            f"end_chat_id={result.end_chat_id}, "
            f"end_chat_time={result.end_chat_time}"
        )

        return result

    def _build_compression_prompt(self, chats: list[Chat]) -> str:
        """构造压缩 prompt

        Args:
            chats: 待压缩的 Chat 列表

        Returns:
            压缩 prompt
        """
        # 延迟导入避免循环依赖
        from src.assistant.modules import ASSISTANT_MODULES

        chat_dicts = [chat.to_dict() for chat in chats]
        chat_history = json.dumps(chat_dicts, ensure_ascii=False)
        available_modules_prompt = build_modules_prompt(
            [m for m in ASSISTANT_MODULES if m.message_tag is not None]
        )
        return prompts_loader.get_conversation_compression_prompt(
            available_modules_prompt=available_modules_prompt,
            chat_history=chat_history,
        )

    def _call_compression_model(self, prompt: str) -> CallResponse:
        """调用压缩模型

        Args:
            prompt: 压缩 prompt

        Returns:
            模型响应对象
        """
        # 构造简单的对话列表
        chats = [chat_factory.create_prompt_chat(prompt)]

        return model_caller.call(
            model_key=app_config.get_memory_model_key(),
            chats=chats,
            tools=[],
            enable_thinking=True,
        )

    def _parse_compression_result(
        self, response: CallResponse, chats: list[Chat]
    ) -> CompressionResult:
        """解析压缩结果

        Args:
            response: 模型响应对象
            chats: 原始 Chat 列表，用于查找 end_chat_time

        Returns:
            压缩结果对象

        Raises:
            ContextCompressionError: 解析失败时抛出
        """
        try:
            # 提取文本内容
            text = response.message.get_text_content()

            # 解析 JSON
            result = json.loads(text)

            # 验证必要字段
            if "summary" not in result or "end_id" not in result:
                raise ContextCompressionError(f"压缩结果缺少必要字段: response={response}")

            end_chat_id = result["end_id"]

            # 从 chats 中查找 end_id 对应的时间
            end_chat_time = self._find_chat_time(chats, end_chat_id)
            if end_chat_time is None:
                raise ContextCompressionError(f"未找到 end_id 对应的 Chat: {end_chat_id}")

            return CompressionResult(
                summary=result["summary"],
                end_chat_id=end_chat_id,
                end_chat_time=end_chat_time,
            )

        except json.JSONDecodeError as e:
            raise ContextCompressionError(f"解析 JSON 失败: {e} response={response}") from e
        except ContextCompressionError:
            raise
        except Exception as e:
            raise ContextCompressionError(f"解析压缩结果失败: {e} response={response}") from e

    def _find_chat_time(self, chats: list[Chat], chat_id: str) -> int | None:
        """从 Chat 列表中查找指定 ID 的 Chat 时间

        Args:
            chats: Chat 列表
            chat_id: 要查找的 Chat ID

        Returns:
            Chat 时间戳，未找到返回 None
        """
        for chat in chats:
            if chat.id == chat_id:
                return chat.time
        return None

    def _record_compression_cost(self, user_id: str, response: CallResponse) -> None:
        """记录压缩调用的 token 用量

        Args:
            user_id: 用户 ID
            response: 模型响应对象
        """
        user_cost_manager.record_cost(
            user_id=user_id,
            model_key=app_config.get_memory_model_key(),
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            total_tokens=response.total_tokens,
            type="conversation",
        )


# 全局单例
context_compressor = ContextCompressor()
