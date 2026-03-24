"""搜索结果压缩服务"""

import json
from typing import Any

from src.agent.chat_factory import chat_factory
from src.common.logger import get_logger
from src.config.config import app_config
from src.config.prompts_loader import prompts_loader
from src.model.model_caller import model_caller
from src.user.user_cost.user_cost_manager import user_cost_manager

logger = get_logger(__name__)


class SearchResultCompressor:
    """搜索结果压缩器，使用轻量模型压缩搜索结果"""

    def compress(
        self,
        user_id: str,
        search_query: str,
        search_results: list,
    ) -> str:
        """压缩搜索结果

        Args:
            user_id: 用户 ID
            search_query: 搜索查询
            search_results: 原始搜索结果列表

        Returns:
            压缩后的摘要字符串
        """
        # 构造 prompt
        prompt = self._build_compression_prompt(search_query, search_results)

        # 调用轻量模型进行压缩
        response = self._call_compression_model(prompt)

        # 记录 token 用量
        self._record_compression_cost(user_id, response)

        # 提取压缩结果
        compressed_text = response.message.get_text_content()

        return compressed_text

    def _build_compression_prompt(
        self,
        search_query: str,
        search_results: list,
    ) -> str:
        """构造压缩 prompt

        Args:
            search_query: 搜索查询
            search_results: 原始搜索结果列表

        Returns:
            压缩 prompt
        """
        # 将搜索结果转为 JSON 字符串
        result_list = [item.to_dict() for item in search_results]
        search_results_str = json.dumps(result_list, ensure_ascii=False)

        return prompts_loader.get_search_compression_prompt(
            search_query=search_query,
            search_results=search_results_str,
        )

    def _call_compression_model(self, prompt: str) -> Any:
        """调用压缩模型

        Args:
            prompt: 压缩 prompt

        Returns:
            模型响应对象
        """
        # 构造简单的对话列表
        chats = [chat_factory.create_prompt_chat(prompt)]

        return model_caller.call(
            model_key=app_config.get_light_model_key(),
            chats=chats,
            enable_thinking=False,
        )

    def _record_compression_cost(self, user_id: str, response: Any) -> None:
        """记录压缩调用的 token 用量

        Args:
            user_id: 用户 ID
            response: 模型响应对象
        """
        user_cost_manager.record_cost(
            user_id=user_id,
            model_key=app_config.get_light_model_key(),
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            total_tokens=response.total_tokens,
            type="web_search",
        )


# 全局单例
search_result_compressor = SearchResultCompressor()
