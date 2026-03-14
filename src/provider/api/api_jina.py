"""Jina AI API封装"""

import requests  # type: ignore
from src.config.config import env_config
from src.common.logger import get_logger

logger = get_logger(__name__)

# jina-ai接口文档：https://jina.ai/reader/#rate-limit

JINA_READER_URL = "https://r.jina.ai/"


def fetch_webpage(url: str) -> str:
    """调用Jina AI的reader接口获取网页内容

    Args:
        url: 目标网页URL

    Returns:
        网页内容文本，失败时返回空字符串
    """
    api_key = env_config.get("JINA_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(f"{JINA_READER_URL}{url}", headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception:
        logger.exception(f"获取网页内容失败，url: {url}")
        raise
