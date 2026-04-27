import json
from pathlib import Path
from typing import List


# 文件存储底层操作类
class _FileStorage:
    # 追加写入 JSONL 文件
    def append_to_jsonl(self, file_path: Path, records: List[dict]) -> None:
        if not records:
            return

        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            for record in records:
                json_line = json.dumps(record, ensure_ascii=False)
                f.write(json_line + "\n")

    # 读取 JSONL 文件，解析错误抛异常
    def read_jsonl(self, file_path: Path) -> List[dict]:
        if not file_path.exists():
            return []

        records = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"JSONL parse error at {file_path}:{line_num}", e.doc, e.pos
                    )

        return records

    # 读取文本文件内容
    def read_text(self, file_path: Path) -> str:
        if not file_path.exists():
            return ""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # 读取文本文件内容为行列表
    def read_lines(self, file_path: Path) -> List[str]:
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()

    # 写入文本文件内容（覆盖）
    def write_text(self, file_path: Path, content: str) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    # 写入行列表到文本文件（覆盖）
    def write_lines(self, file_path: Path, lines: List[str]) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    # 列出目录内容
    def list_dir(self, dir_path: Path) -> List[Path]:
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        return list(dir_path.iterdir())

    # 检查路径是否存在
    def exists(self, path: Path) -> bool:
        return path.exists()

    # 检查路径是否是文件
    def is_file(self, path: Path) -> bool:
        return path.is_file()

    # 检查路径是否是目录
    def is_dir(self, path: Path) -> bool:
        return path.is_dir()

    # 写入二进制文件内容（覆盖）
    def write_bytes(self, file_path: Path, content: bytes) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)

    # 解析唯一的文件路径，处理文件名冲突
    def resolve_unique_path(self, directory: Path, filename: str) -> Path:
        """解析唯一的文件路径，处理文件名冲突

        如果目标文件已存在，会自动添加数字后缀（如 file_1.txt, file_2.txt）

        Args:
            directory: 目标目录路径
            filename: 原始文件名

        Returns:
            唯一的文件路径
        """
        file_path = directory / filename

        if not file_path.exists():
            return file_path

        # 处理文件名冲突
        counter = 1
        stem = file_path.stem
        suffix = file_path.suffix
        while file_path.exists():
            file_path = directory / f"{stem}_{counter}{suffix}"
            counter += 1

        return file_path

    # 保存文件，自动处理文件名冲突
    def write_bytes_with_conflict_resolution(
        self, directory: Path, filename: str, content: bytes
    ) -> Path:
        """保存文件，自动处理文件名冲突

        Args:
            directory: 目标目录路径
            filename: 原始文件名
            content: 文件内容

        Returns:
            最终保存的文件路径
        """
        file_path = self.resolve_unique_path(directory, filename)
        self.write_bytes(file_path, content)
        return file_path


file_storage = _FileStorage()
