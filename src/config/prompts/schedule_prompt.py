"""日程提示词模板"""

SCHEDULE_PROMPT = """
当前启用的所有日程：
{schedule_list}
"""

EXPIRED_SCHEDULES_PROMPT = """

今日已过期的日程（最多展示5个）：
{expired_schedules}
"""

FUTURE_SCHEDULES_PROMPT = """

近期将触发的日程（最多展示5个）：
{future_schedules}
"""
