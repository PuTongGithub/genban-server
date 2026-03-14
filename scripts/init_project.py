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

    print("✓ RSA 密钥对已生成")


def check_system_dependencies() -> None:
    """检查系统依赖（Pandoc、LibreOffice、Node.js）"""
    is_windows = sys_util.is_mswindows()
    missing_deps = []

    # 检查 Pandoc
    if not check_command(["pandoc", "--version"]):
        missing_deps.append(
            (
                "Pandoc",
                "winget install --id JohnMacFarlane.Pandoc -e --silent"
                if is_windows
                else "sudo apt-get install pandoc",
            )
        )

    # 检查 LibreOffice
    libreoffice_cmd = (
        ["soffice", "--version"] if is_windows else ["libreoffice", "--version"]
    )
    if not check_command(libreoffice_cmd):
        install_cmd = (
            "winget install --id TheDocumentFoundation.LibreOffice -e --silent"
        )
        missing_deps.append(("LibreOffice", install_cmd))

    # 检查 Node.js
    if not check_command(["node", "--version"]):
        install_cmd = (
            "winget install --id OpenJS.NodeJS -e --silent"
            if is_windows
            else "sudo apt-get install nodejs npm"
        )
        missing_deps.append(("Node.js", install_cmd))

    # 输出需要用户处理的依赖
    if missing_deps:
        print("\n=== 需要安装的系统依赖 ===")
        for name, cmd in missing_deps:
            print(f"\n✗ {name} 未安装")
            print(f"  安装命令: {cmd}")
        print("\n提示：安装完成后请重启终端")


def install_python_dependencies() -> None:
    """安装 Python 系统依赖（供 subprocess 调用）"""
    packages = ["defusedxml", "pypdf", "pdfplumber", "pypdfium2"]

    for package in packages:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            print(f"✗ {package} 安装失败，请手动安装: pip install {package}")


def install_node_dependencies() -> None:
    """安装 Node.js 依赖"""
    # 检查 npm 是否可用
    if not check_command(["npm", "--version"]):
        return

    packages = ["docx", "pptxgenjs"]
    failed_packages = []

    for package in packages:
        try:
            use_shell = sys.platform == "win32"
            subprocess.run(
                ["npm", "install", "-g", package],
                check=True,
                capture_output=True,
                shell=use_shell,
            )
        except subprocess.CalledProcessError:
            failed_packages.append(package)

    if failed_packages:
        print(f"\n✗ Node.js 包安装失败: {', '.join(failed_packages)}")
        print(f"  请手动安装: npm install -g {' '.join(failed_packages)}")


def check_env_file() -> None:
    """检查 .env 文件是否存在"""
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    if not env_file.exists():
        print("✗ .env 文件不存在")
        print(f"  提示: 复制 {env_example.name} 为 .env 并配置")


def main() -> None:
    """主函数"""
    print("=== 项目初始化 ===\n")

    check_env_file()
    init_rsa_keys()
    install_python_dependencies()
    check_system_dependencies()
    install_node_dependencies()

    print("\n✓ 项目初始化完成")


if __name__ == "__main__":
    main()
