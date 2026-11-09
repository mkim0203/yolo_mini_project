from fastapi import APIRouter, Depends, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from datetime import datetime
from database.connection import get_db
from database.models import StorageInfo


import base64

router = APIRouter(
    prefix="/storage",
    tags=["storage"]
)

@router.post("/{slot_id}/test")
async def test(
    slot_id: int,
    request_id: int | None = Form(None),
    info: str | None = Form(None),
    expiry_date: datetime = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 이미지 타입 확인
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="이미지 파일만 업로드할 수 있습니다."
        )

    # 이미지 바이너리 읽기
    image_data = await image.read()

    if not image_data:
        raise HTTPException(
            status_code=400,
            detail="이미지 데이터가 비어 있습니다."
        )

    # 기존 슬롯 데이터 확인
    storage = db.query(StorageInfo).filter(
        StorageInfo.slot_id == slot_id
    ).first()

    if storage:
        # 기존 데이터 수정
        storage.request_id = request_id
        storage.info = info
        storage.image_type = image.content_type
        storage.image_data = image_data
        storage.expiry_date = expiry_date
    else:
        # 신규 데이터 등록
        storage = StorageInfo(
            slot_id=slot_id,
            request_id=request_id,
            info=info,
            image_type=image.content_type,
            image_data=image_data,
            expiry_date=expiry_date
        )

        db.add(storage)

    try:
        db.commit()
        db.refresh(storage)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"저장 실패: {str(e)}"
        )

    return {
        "message": "저장 완료",
        "storage_id": storage.storage_id,
        "slot_id": storage.slot_id,
        "image_type": storage.image_type,
        "filename": image.filename
    }
