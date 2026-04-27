"""FileSystem 模块实体类"""

from typing import Optional

from pydantic import BaseModel


class FileSystemItem(BaseModel):
    """文件系统项（文件或目录）"""

    name: str
    type: str  # "directory" 或 "file"
    size: Optional[int] = None  # 文件大小（字节），目录为 None
    modified_at: str  # 修改时间（ISO 8601 格式）


class FileListResponse(BaseModel):
    """文件列表响应"""

    items: list[FileSystemItem]


class FileUploadResponse(BaseModel):
    """文件上传响应"""

    success: bool
    path: str
    size: int
    url: str | None = None  # 图片文件的分享链接，非图片为 None
