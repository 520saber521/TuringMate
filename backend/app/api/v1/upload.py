"""File upload API - 图片/文件上传."""
from fastapi import APIRouter, UploadFile, File
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/image")
async def upload_image(image: UploadFile = File(...)):
    """上传图片.

    前端直传 COS（通过后端签名 URL）或先传到后端再转存。
    MVP 阶段先保存到本地 uploads 目录。
    """
    file_ext = image.filename.rsplit(".", 1)[-1] if "." in image.filename else "png"
    file_name = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    content = await image.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "url": f"/api/v1/uploads/{file_name}",
        "filename": file_name,
        "size": len(content),
        "content_type": image.content_type,
    }
