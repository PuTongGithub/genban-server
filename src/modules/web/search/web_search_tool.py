"""网络搜索工具"""

from typing import Any

from src.agent.chat_factory import chat_factory
from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolParameter
from src.common.logger import get_logger
from src.modules.web.search.search_result_compressor import search_result_compressor
from src.provider.api.api_zai_sdk import web_search

logger = get_logger(__name__)

search_count_enum = [10, 20, 30, 40, 50]
search_recency_filter_enum = ["oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"]


class WebSearchTool(BaseTool):
    """网络搜索工具"""

    name = "web_search"
    description = "执行网络搜索，返回搜索结果"
    parameters = [
        ToolParameter(
            name="search_query",
            type="string",
            description="搜索关键词。建议：理解用户问题的真实意图，用多个词语确定搜索范围。例如：提问'北京明天穿羽绒服吗？'，搜索关键词‘北京 天气 最新’",
            required=True,
        ),
        ToolParameter(
            name="count",
            type="integer",
            description="返回结果数量，默认值：10",
            required=False,
            enum=search_count_enum,
        ),
        ToolParameter(
            name="search_recency_filter",
            type="string",
            description="时间过滤，默认值：noLimit(无限制)",
            required=False,
            enum=search_recency_filter_enum,
        )
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行网络搜索

        Args:
            context: Agent 执行上下文
            search_query: 搜索关键词
            count: 返回结果数量，默认10
            search_recency_filter: 时间过滤，默认noLimit

        Returns:
            格式化的搜索结果字符串
        """
        search_query = kwargs.get("search_query", "")
        count = kwargs.get("count", 10)
        search_recency_filter = kwargs.get("search_recency_filter", "noLimit")

        # 暂时屏蔽压缩功能
        # compress = kwargs.get("compress", True)
        compress = False

        if not search_query.strip():
            return chat_factory.create_system_remainder_str(content="错误：搜索关键词不能为空")

        # 确保count在有效范围内
        if count not in search_count_enum:
            count = search_count_enum[0]

        # 验证search_recency_filter
        if search_recency_filter not in search_recency_filter_enum:
            search_recency_filter = search_recency_filter_enum[0]

        try:
            result = web_search(
                search_query=search_query,
                count=count,
                search_recency_filter=search_recency_filter,
            )

            if isinstance(result, dict) and "error" in result:
                return chat_factory.create_system_remainder_str(
                    content=f"搜索失败：{result['error']}"
                )

            return self._format_result(context, search_query, result, compress)
        except Exception as e:
            logger.exception(f"网络搜索执行异常，user_id: {context.user_id}, query: {search_query}")
            return chat_factory.create_system_remainder_str(content=f"搜索执行异常：{str(e)}")

    def _format_result(
        self, context: AgentContext, search_query: str, result: list, compress: bool = True
    ) -> str:
        """格式化搜索结果为易读字符串，并使用LLM进行压缩

        Args:
            context: Agent 执行上下文
            search_query: 搜索查询
            result: 搜索结果数据
            compress: 是否压缩搜索结果，默认True

        Returns:
            格式化后的字符串
        """
        if not result:
            return "未找到相关搜索结果"

        if not compress:
            return self._format_result_original(result)

        try:
            compressed = search_result_compressor.compress(
                user_id=context.user_id,
                search_query=search_query,
                search_results=result,
            )
            return f"搜索结果（{len(result)}条）摘要：\n\n{compressed}"
        except Exception:
            logger.exception(
                f"搜索结果压缩失败，使用原始格式，user_id: {context.user_id}, query: {search_query}"
            )
            return self._format_result_original(result)

    def _format_result_original(self, items: list) -> str:
        """格式化原始搜索结果（未压缩版本）

        Args:
            items: 搜索结果列表

        Returns:
            格式化后的字符串
        """
        formatted_lines = []
        formatted_lines.append(f"找到 {len(items)} 条搜索结果：")
        formatted_lines.append("")

        for i, item in enumerate(items, 1):
            if isinstance(item, dict):
                title = item.get("title", "无标题")
                content = item.get("content", item.get("snippet", ""))
                url = item.get("link", "")
                media = item.get("media", "")
                publish_date = item.get("publish_date", "")

                formatted_lines.append(f"[{i}] {title}")
                if content:
                    formatted_lines.append(f"内容：{content}")
                if url:
                    formatted_lines.append(f"链接：{url}")
                if media:
                    formatted_lines.append(f"媒体：{media}")
                if publish_date:
                    formatted_lines.append(f"发布日期：{publish_date}")
                formatted_lines.append("")
            else:
                formatted_lines.append(f"[{i}] {str(item)}")
                formatted_lines.append("")

        return "\n".join(formatted_lines)
