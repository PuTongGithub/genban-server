"""数据库迁移脚本：为已有表添加新字段

使用方式：
    python scripts/add_column.py

或指定参数：
    python scripts/add_column.py --table schedules --column onetime --type BOOLEAN --default false
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from src.storage.sqlite.database import SessionLocal


def add_column(
    table_name: str,
    column_name: str,
    column_type: str,
    default_value: str | None = None,
    nullable: bool = False,
) -> bool:
    """为指定表添加新字段

    Args:
        table_name: 表名
        column_name: 字段名
        column_type: 字段类型（如 BOOLEAN, VARCHAR(32), INTEGER 等）
        default_value: 默认值（可选）
        nullable: 是否允许为空

    Returns:
        是否成功添加
    """
    with SessionLocal() as db:
        # 检查表是否存在
        result = db.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"),
            {"table_name": table_name},
        )
        if not result.fetchone():
            print(f"错误：表 '{table_name}' 不存在")
            return False

        # 检查字段是否已存在
        result = db.execute(text(f"PRAGMA table_info({table_name})"))
        columns = [row[1] for row in result.fetchall()]

        if column_name in columns:
            print(f"字段 '{column_name}' 已存在，跳过迁移")
            return True

        # 构建 ALTER TABLE 语句
        if default_value is not None:
            # 字符串类型的默认值需要加引号
            if column_type.upper().startswith("VARCHAR") or column_type.upper() == "TEXT":
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {'NULL' if nullable else 'NOT NULL'} DEFAULT '{default_value}'"
            else:
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {'NULL' if nullable else 'NOT NULL'} DEFAULT {default_value}"
        else:
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {'NULL' if nullable else 'NOT NULL'}"

        db.execute(text(sql))
        db.commit()
        print(f"表 '{table_name}' 迁移完成：新增字段 '{column_name}' ({column_type})")
        return True


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="为数据库表添加新字段")
    parser.add_argument(
        "--table",
        type=str,
        default="schedules",
        help="表名（默认: schedules）",
    )
    parser.add_argument(
        "--column",
        type=str,
        default="onetime",
        help="字段名（默认: onetime）",
    )
    parser.add_argument(
        "--type",
        dest="column_type",
        type=str,
        default="BOOLEAN",
        help="字段类型（默认: BOOLEAN）",
    )
    parser.add_argument(
        "--default",
        dest="default_value",
        type=str,
        default="false",
        help="默认值（默认: false）",
    )
    parser.add_argument(
        "--nullable",
        action="store_true",
        help="允许为空（默认不允许）",
    )

    args = parser.parse_args()

    print(f"开始迁移：为表 '{args.table}' 添加字段 '{args.column}'...")
    success = add_column(
        table_name=args.table,
        column_name=args.column,
        column_type=args.column_type,
        default_value=args.default_value,
        nullable=args.nullable,
    )

    if success:
        print("迁移完成！")
        sys.exit(0)
    else:
        print("迁移失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
