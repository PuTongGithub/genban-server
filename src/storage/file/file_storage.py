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

    # 列出指定日期范围内的 JSONL 文件
    def list_jsonl_files(
        self, dir_path: Path, start_date: str, end_date: str
    ) -> List[Path]:
        if not dir_path.exists():
            return []

        files = []
        for file_path in dir_path.glob("*.jsonl"):
            date_str = file_path.stem
            if start_date <= date_str <= end_date:
                files.append(file_path)

        files.sort(key=lambda p: p.stem)
        return files


file_storage = _FileStorage()
