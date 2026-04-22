"""智谱AI API封装"""

from zai import ZhipuAiClient

from src.common.logger import get_logger
from src.config.config import app_config, env_config

logger = get_logger(__name__)

client = ZhipuAiClient(api_key=env_config.get("ZHIPU_API_KEY"))


def web_search(search_query: str, count: int = 10, search_recency_filter: str = "noLimit"):
    """执行网络搜索"""
    search_engine = app_config.get("tools", {}).get("zhipu_search_engine", "search-std")
    try:
        response = client.web_search.web_search(
            search_engine=search_engine,
            search_query=search_query,
            count=count,
            search_recency_filter=search_recency_filter,
        )
        return response.search_result
    except Exception:
        logger.exception(f"网络搜索失败，query: {search_query}")
        raise
