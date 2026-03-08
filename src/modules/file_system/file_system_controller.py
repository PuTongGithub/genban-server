"""FileSystem 模块 HTTP 接口控制器"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, PlainTextResponse

from src.user.auth import get_current_user_id
from src.modules.file_system.path_validator import validate_path
from src.modules.file_system.exceptions import PathNotAllowedException
from src.modules.file_system.entities import (
    FileSystemItem,
    FileListResponse,
    FileUploadResponse,
)
from src.storage.file.file_storage import file_storage

router = APIRouter(prefix="/api/file_system", tags=["file_system"])


@router.get("/list")
async def list_directory(
    path: str = "",
    user_id: str = Depends(get_current_user_id),
) -> FileListResponse:
    """查看目录内容

    Args:
        path: 相对路径，默认为用户根目录
        user_id: 当前用户ID（由依赖注入）

    Returns:
        目录下的文件和子目录列表
    """
    try:
        dir_path = validate_path(path, user_id)
    except PathNotAllowedException as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not file_storage.exists(dir_path):
        raise HTTPException(status_code=404, detail="目录不存在")

    if not file_storage.is_dir(dir_path):
        raise HTTPException(status_code=400, detail="路径不是目录")

    items = []
    for item_path in file_storage.list_dir(dir_path):
        stat = item_path.stat()
        items.append(
            FileSystemItem(
                name=item_path.name,
                type="directory" if file_storage.is_dir(item_path) else "file",
                size=stat.st_size if file_storage.is_file(item_path) else None,
                modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            )
        )

    return FileListResponse(items=items)


@router.get("/preview")
async def preview_file(
    path: str,
    user_id: str = Depends(get_current_user_id),
):
    """预览文件内容（纯文本）

    Args:
        path: 文件相对路径
        user_id: 当前用户ID（由依赖注入）

    Returns:
        文件内容（纯文本）
    """
    try:
        file_path = validate_path(path, user_id)
    except PathNotAllowedException as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not file_storage.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    if not file_storage.is_file(file_path):
        raise HTTPException(status_code=400, detail="路径不是文件")

    try:
        content = file_storage.read_text(file_path)
        return PlainTextResponse(content)
    except UnicodeDecodeError:
        return "文件不是纯文本格式，暂不支持预览"


@router.get("/download")
async def download_file(
    path: str,
    user_id: str = Depends(get_current_user_id),
):
    """下载文件

    Args:
        path: 文件相对路径
        user_id: 当前用户ID（由依赖注入）

    Returns:
        文件下载流
    """
    try:
        file_path = validate_path(path, user_id)
    except PathNotAllowedException as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not file_storage.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    if not file_storage.is_file(file_path):
        raise HTTPException(status_code=400, detail="路径不是文件")

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream",
    )


@router.post("/upload")
async def upload_file(
    path: str,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
) -> FileUploadResponse:
    """上传文件

    Args:
        path: 目标相对路径（包含文件名）
        file: 上传的文件
        user_id: 当前用户ID（由依赖注入）

    Returns:
        上传结果
    """
    try:
        file_path = validate_path(path, user_id)
    except PathNotAllowedException as e:
        raise HTTPException(status_code=403, detail=str(e))

    # 保存文件（支持二进制文件）
    content = await file.read()
    file_storage.write_bytes(file_path, content)

    return FileUploadResponse(success=True, path=path, size=len(content))
