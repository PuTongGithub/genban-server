#!/usr/bin/env python3
"""
项目初始化脚本
用法: python scripts/init_project.py
功能:
  1. 生成 RSA 密钥对
  2. 检查并安装系统依赖（Pandoc、LibreOffice）
  3. 安装 Python 依赖
  4. 安装 Node.js 依赖
"""

import subprocess
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.common.utils import sys_util


def check_command(command: list[str]) -> bool:
    """检查命令是否可用"""
    try:
        # Windows 上需要使用 shell=True 来正确解析某些命令
        use_shell = sys.platform == "win32" and command[0] in ("npm", "node")
        subprocess.run(command, capture_output=True, check=True, shell=use_shell)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


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


def check_system_dependencies() -> None:
    """检查系统依赖（Pandoc、LibreOffice）"""
    print("\n=== 检查系统依赖 ===\n")

    is_windows = sys_util.is_mswindows()

    # 检查 Pandoc
    has_pandoc = check_command(["pandoc", "--version"])
    if has_pandoc:
        print("✓ Pandoc 已安装")
    else:
        print("✗ Pandoc 未安装")
        if is_windows:
            print("  安装命令: winget install --id JohnMacFarlane.Pandoc -e --silent")
        else:
            print("  Debian/Ubuntu: sudo apt-get install pandoc")
            print("  CentOS/RHEL:   sudo dnf install pandoc")
            print("  Arch:          sudo pacman -S pandoc")
        print("  提示：安装完成后如命令不可用，请重启终端")

    # 检查 LibreOffice
    if is_windows:
        has_libreoffice = check_command(["soffice", "--version"])
        install_cmd = (
            "winget install --id TheDocumentFoundation.LibreOffice -e --silent"
        )
    else:
        has_libreoffice = check_command(["libreoffice", "--version"])
        install_cmd = (
            "sudo apt-get install libreoffice  (Debian/Ubuntu)\n"
            "sudo dnf install libreoffice      (CentOS/RHEL)\n"
            "sudo pacman -S libreoffice-still  (Arch)"
        )

    if has_libreoffice:
        print("✓ LibreOffice 已安装")
    else:
        print("✗ LibreOffice 未安装")
        print(f"  安装命令: {install_cmd}")
        if is_windows:
            print("  提示：如安装后命令仍不可用，请添加 PATH:")
            print(
                r'  [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\LibreOffice\program", "User")'
            )
        print("  提示：安装完成后如命令不可用，请重启终端")

    # 检查 Node.js
    has_node = check_command(["node", "--version"])
    if has_node:
        print("✓ Node.js 已安装")
    else:
        print("✗ Node.js 未安装")
        if is_windows:
            print("  安装命令: winget install --id OpenJS.NodeJS -e --silent")
        else:
            print("  Debian/Ubuntu: sudo apt-get install nodejs npm")
            print("  CentOS/RHEL:   sudo dnf install nodejs npm")
            print("  Arch:          sudo pacman -S nodejs npm")

    # 检查 npm
    has_npm = check_command(["npm", "--version"])
    if has_npm:
        print("✓ npm 已安装")
    else:
        print("✗ npm 未安装（通常随 Node.js 一起安装）")


def install_node_dependencies() -> None:
    """安装 Node.js 依赖"""
    print("\n=== 安装 Node.js 依赖 ===\n")

    packages = [
        "docx",
        "pptxgenjs",
    ]

    for package in packages:
        print(f"安装 {package}...")
        try:
            # Windows 上需要使用 shell=True
            use_shell = sys.platform == "win32"
            subprocess.run(
                ["npm", "install", "-g", package],
                check=True,
                capture_output=True,
                shell=use_shell,
            )
            print(f"  ✓ {package} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ {package} 安装失败: {e}")
        except FileNotFoundError:
            print(f"  ✗ npm 未找到，跳过 {package} 安装")
            break


def check_env_file() -> None:
    """检查 .env 文件是否存在"""
    print("=== 检查环境配置文件 ===\n")

    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    if env_file.exists():
        print("✓ .env 文件已存在\n")
    else:
        print("✗ .env 文件不存在")
        if env_example.exists():
            print(f"  提示: 可参考 {env_example.name} 文件创建 .env 文件")
            print(f"  命令: cp {env_example.name} .env")
        else:
            print("  提示: 请创建 .env 文件并配置必要的环境变量")
        print()


def main() -> None:
    """主函数"""
    print("=== 项目初始化 ===\n")

    check_env_file()
    init_rsa_keys()
    check_system_dependencies()
    install_node_dependencies()

    print("\n" + "=" * 60)
    print("✓ 项目初始化完成")


if __name__ == "__main__":
    main()
