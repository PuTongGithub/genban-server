#!/usr/bin/env python3
"""查询 conversation_memories 表数据

用法:
    python scripts/query_conversation_memories.py
    python scripts/query_conversation_memories.py --user-id <用户ID>
    python scripts/query_conversation_memories.py --limit 50
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text  # noqa: E402

from src.storage.sqlite.database import SessionLocal  # noqa: E402


def format_timestamp(ts: int) -> str:
    """将时间戳格式化为可读字符串"""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 200) -> str:
    """截断长文本，保留前 max_length 个字符"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def query_all(limit: int = 20) -> None:
    """查询所有对话记忆数据"""
    with SessionLocal() as db:
        result = db.execute(
            text("""
                SELECT id, user_id, end_chat_id, end_chat_time, summary, created_at
                FROM conversation_memories
                ORDER BY updated_at DESC
                LIMIT :limit
            """),
            {"limit": limit},
        )
        rows = result.fetchall()

        if not rows:
            print("conversation_memories 表中没有数据")
            return

        print(f"\n{'=' * 80}")
        print(f"  conversation_memories 表数据 (共 {len(rows)} 条)")
        print(f"{'=' * 80}")

        for row in rows:
            print(f"\n  ID:           {row[0]}")
            print(f"  用户ID:       {row[1]}")
            print(f"  最后对话ID:   {row[2]}")
            print(f"  最后对话时间: {format_timestamp(row[3])}")
            print(f"  创建时间:     {format_timestamp(row[5])}")
            print("  摘要内容:")
            print(f"  {truncate_text(row[4], 300)}")
            print(f"  {'-' * 76}")


def query_by_user_id(user_id: str) -> None:
    """根据用户ID查询对话记忆"""
    with SessionLocal() as db:
        result = db.execute(
            text("""
                SELECT id, user_id, end_chat_id, end_chat_time, summary, created_at
                FROM conversation_memories
                WHERE user_id = :user_id
            """),
            {"user_id": user_id},
        )
        row = result.fetchone()

        if not row:
            print(f"用户 {user_id} 没有对话记忆数据")
            return

        print(f"\n{'=' * 80}")
        print(f"  用户 {user_id} 的对话记忆")
        print(f"{'=' * 80}")
        print(f"\n  ID:           {row[0]}")
        print(f"  用户ID:       {row[1]}")
        print(f"  最后对话ID:   {row[2]}")
        print(f"  最后对话时间: {format_timestamp(row[3])}")
        print(f"  创建时间:     {format_timestamp(row[5])}")
        print("\n  摘要内容:")
        print(f"  {'-' * 76}")
        # 打印完整摘要，按行分割
        for line in row[4].split("\n"):
            print(f"  {line}")


def query_stats() -> None:
    """查询统计信息"""
    with SessionLocal() as db:
        # 总记录数
        result = db.execute(text("SELECT COUNT(*) FROM conversation_memories"))
        total_count = result.scalar()

        # 获取所有用户ID
        result = db.execute(text("SELECT user_id FROM conversation_memories ORDER BY user_id"))
        user_ids = [row[0] for row in result.fetchall()]

        print(f"\n{'=' * 60}")
        print("  conversation_memories 表统计信息")
        print(f"{'=' * 60}")
        print(f"  总记录数: {total_count}")
        print("\n  用户列表:")
        for uid in user_ids:
            print(f"    - {uid}")


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="查询 conversation_memories 表数据")
    parser.add_argument("--user-id", type=str, help="指定用户ID查询")
    parser.add_argument("--limit", type=int, default=20, help="限制返回记录数 (默认: 20)")
    parser.add_argument("--stats", action="store_true", help="只显示统计信息")

    args = parser.parse_args()

    try:
        if args.stats:
            query_stats()
        elif args.user_id:
            query_by_user_id(args.user_id)
        else:
            query_all(args.limit)
    except Exception as e:
        print(f"查询失败: {e}")
        raise


if __name__ == "__main__":
    main()
