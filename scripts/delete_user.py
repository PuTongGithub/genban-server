#!/usr/bin/env python3
"""
删除用户脚本
用法: python scripts/delete_user.py
"""

import sys
from pathlib import Path
from src.user.db.user_db import user_db
from src.user.db.user_state_db import user_state_db

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def delete_user():
    print("=== 删除用户 ===\n")

    # 输入用户ID
    user_id = input("请输入要删除的用户ID: ").strip()
    if not user_id:
        print("错误: 用户ID不能为空")
        return

    # 检查用户是否存在
    existing_user = user_db.get_user_by_id(user_id)
    if not existing_user:
        print(f"错误: 用户 {user_id} 不存在")
        return

    # 确认删除
    confirm = input(
        f"确定要删除用户 {user_id} 吗？此操作不可恢复！请输入 'yes' 确认: "
    ).strip()
    if confirm != "yes":
        print("已取消删除操作")
        return

    # 删除用户状态
    state_deleted = user_state_db.delete(user_id)
    if not state_deleted:
        print(f"⚠ 用户 {user_id} 的状态删除失败或不存在")

    # 删除用户
    user_deleted = user_db.delete(user_id)
    if not user_deleted:
        print(f"\n✗ 用户 {user_id} 删除失败")
        return

    print(f"\n✓ 用户 {user_id} 删除成功！")


if __name__ == "__main__":
    delete_user()
