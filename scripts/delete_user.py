#!/usr/bin/env python3
"""
删除用户脚本
用法: python scripts/delete_user.py
"""

import shutil
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.common.utils.path_util import get_user_dir
from src.user.db.user_db import user_db
from src.user.db.user_state_db import user_state_db


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

    # 删除用户相关文件
    user_dir = get_user_dir(user_id)
    if user_dir.exists():
        try:
            shutil.rmtree(user_dir)
            print(f"✓ 用户目录已删除: {user_dir}")
        except Exception as e:
            print(f"⚠ 用户目录删除失败: {e}")
    else:
        print(f"ℹ 用户目录不存在: {user_dir}")

    print(f"\n✓ 用户 {user_id} 删除成功！")


if __name__ == "__main__":
    delete_user()
