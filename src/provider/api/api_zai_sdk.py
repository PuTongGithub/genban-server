"""智谱AI API封装"""

from zai import ZhipuAiClient
from src.config.config import env_config, app_config
from src.common.logger import get_logger

logger = get_logger(__name__)

# 智谱接口文档：https://docs.bigmodel.cn/cn/guide/start/introduction

client = ZhipuAiClient(api_key=env_config.get("ZHIPU_API_KEY"))


def web_search(
    search_query: str, count: int = 10, search_recency_filter: str = "noLimit"
):
    """执行网络搜索"""
    search_engine = app_config.get("tools")["zhipu_search_engine"]
    try:
        response = client.web_search.web_search(
            search_engine=search_engine,
            search_query=search_query,
            count=count,  # 返回结果的条数，范围1-50，默认10
            search_recency_filter=search_recency_filter,  # 搜索指定日期范围内的内容
        )
        return response.search_result
    except Exception:
        logger.exception(f"网络搜索失败，query: {search_query}")
        raise
