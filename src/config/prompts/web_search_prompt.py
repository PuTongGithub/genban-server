"""网络搜索提示词模板"""

SEARCH_RESULT_COMPRESSION_PROMPT_TEMPLATE = """<background>
- 你是一个专业的搜索结果压缩工具，目标是将网络搜索返回的多条结果压缩成精炼的摘要。
- 原始搜索结果在下方 search_results 标签中，每条结果包含标题、内容摘要、链接等信息。
- 用户的搜索查询在下方 search_query 标签中。
- 具体输出说明在 output_instruction 标签中。
</background>

<search_query>
{search_query}
</search_query>

<search_results>
{search_results}
</search_results>

<output_instruction>
1. 分析用户的搜索查询意图，理解用户真正想了解的信息。
2. 从搜索结果中提取与查询意图最相关的关键信息，去除冗余和重复内容。
3. 按信息的重要程度组织摘要，优先呈现核心答案和关键事实。
4. 保留重要的数据来源链接，至少3条。
5. 输出应为纯文本的摘要内容，不使用非必要的格式或标记。
</output_instruction>"""
