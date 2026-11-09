from fastapi import APIRouter, Depends, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from datetime import datetime
from database.connection import get_db
from database.models import StorageRequest
from schemas.storage import StorageRequestItem, StorageRequestResponse, StorageRequestDetail

import base64

router = APIRouter(
    prefix="/requests",
    tags=["requests"]
)

@router.post("/request", description="적재 요청")
async def storage_request(
    info: str | None = Form(None),
    expiry_date: datetime = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    print(f"{info} / {expiry_date} / {image}")
    
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

    # return {
    #     "message": "임시 테스트",
    #     "request_id": -1,
    # }

    # 요청 테이블에 데이터 저장
    add_data = StorageRequest()
    add_data.info = info
    add_data.expiry_date = expiry_date
    add_data.image_type = image.content_type
    add_data.image_data = image_data
    db.add(add_data)

    try:
        db.commit()
        db.refresh(add_data)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"저장 실패: {str(e)}"
        )

    return {
        "message": "적재 요청 완료",
        "request_id": add_data.request_id,
    }

@router.get("", description="적재 요청 받은 목록 조회")
async def search_requests( db: Session = Depends(get_db)):
    result = (
        db.query(
            StorageRequest.request_id,
            StorageRequest.info,
            StorageRequest.image_type,
            StorageRequest.image_data,
            StorageRequest.expiry_date,
            StorageRequest.create_date
        )
        .order_by(
            StorageRequest.request_id.desc()
        )
        .all()
    )

    print(len(result))

    
    items = [
        StorageRequestItem(**row._mapping)
        for row in result
    ]

    return StorageRequestResponse(
            total=len(items),
            items=items
    )

@router.get("/{request_id}", description="적재 요청 ID 정보 조회")
async def search_requests(request_id:int, db: Session = Depends(get_db)):
    print(request_id)
    result = (
            db.query(
                StorageRequest.request_id,
                StorageRequest.info,
                StorageRequest.image_type,
                StorageRequest.image_data,
                StorageRequest.expiry_date
            )
            .filter(StorageRequest.request_id == request_id)
            .all()
        )
        
    if len(result) == 0:
        return None

    
    items = [
        StorageRequestDetail(
            request_id=item.request_id,
            info=item.info,
            image_type=item.image_type,
            #image_data=item.image_data,
            image_data = base64.b64encode(item.image_data).decode("utf-8") if item.image_data else None,
            expiry_date=item.expiry_date
        )
        for item in result
    ]
    

    return items[0]