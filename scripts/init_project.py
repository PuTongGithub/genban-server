#!/usr/bin/env python3
"""
项目初始化脚本
用法: python scripts/init_project.py
功能:
  1. 生成 RSA 密钥对
  2. 拷贝系统 Skills 到运行时目录
"""

import sys
from pathlib import Path


def init_rsa_keys() -> None:
    """生成 RSA 密钥对"""
    print("=== 生成 RSA 密钥对 ===\n")

    # 添加项目根目录到路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    from src.common.utils.rsa_util import generate_key_pair

    private_key, public_key = generate_key_pair()

    # 创建keys目录
    keys_dir = project_root / "keys"
    keys_dir.mkdir(exist_ok=True)

    # 保存私钥
    private_key_path = keys_dir / "private_key.pem"
    with open(private_key_path, "w") as f:
        f.write(private_key)

    # 保存公钥
    public_key_path = keys_dir / "public_key.pem"
    with open(public_key_path, "w") as f:
        f.write(public_key)

    print(f"✓ 私钥已保存到: {private_key_path}")
    print(f"✓ 公钥已保存到: {public_key_path}")

    print("\n" + "=" * 60)
    print("⚠ 警告：私钥请妥善保管，不要泄露给他人！")


def main() -> None:
    """主函数"""
    print("=== 项目初始化 ===\n")

    init_rsa_keys()

    print("\n" + "=" * 60)
    print("✓ 项目初始化完成")


if __name__ == "__main__":
    main()
