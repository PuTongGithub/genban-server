#!/usr/bin/env python3
"""
生成RSA密钥对脚本
用法: python scripts/generate_rsa_keys.py
输出: 密钥保存到项目根目录/keys/文件夹下
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.common.utils.rsa_util import generate_key_pair


def main():
    print("=== 生成RSA密钥对 ===\n")

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
    print("# 公钥内容（给前端使用）：\n")
    print(public_key)

    print("\n" + "=" * 60)
    print("⚠ 警告：私钥请妥善保管，不要泄露给他人！")


if __name__ == "__main__":
    main()
