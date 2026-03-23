"""数据库迁移脚本：简化 Conversation Memory 设计

变更内容：
1. 在 user_costs 表新增 type 字段（区分 assistant 和 conversation 类型）

执行方式：
    python scripts/migrate_simplify_conversation_memory.py
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from src.storage.sqlite.database import SessionLocal


def migrate_user_costs() -> None:
    """在 user_costs 表新增 type 字段"""
    with SessionLocal() as db:
        # 检查表是否存在
        result = db.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_costs'")
        )
        if not result.fetchone():
            print("user_costs 表不存在，跳过迁移")
            return

        # 检查 type 字段是否已存在
        result = db.execute(text("PRAGMA table_info(user_costs)"))
        columns = [row[1] for row in result.fetchall()]

        if "type" in columns:
            print("type 字段已存在，跳过迁移")
            return

        # 新增 type 字段，默认值为 assistant
        db.execute(
            text("ALTER TABLE user_costs ADD COLUMN type VARCHAR(32) NOT NULL DEFAULT 'assistant'")
        )
        db.commit()
        print("user_costs 表迁移完成：新增 type 字段")


def main() -> None:
    """主函数"""
    print("开始迁移数据库...")

    try:
        migrate_user_costs()
        print("\n迁移完成！")
    except Exception as e:
        print(f"迁移失败: {e}")
        raise


if __name__ == "__main__":
    main()
