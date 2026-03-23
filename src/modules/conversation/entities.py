from dataclasses import dataclass


@dataclass
class CompressionResult:
    summary: str
    end_chat_id: str
    end_chat_time: int
