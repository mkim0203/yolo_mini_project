from fastapi import APIRouter, Depends, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from datetime import datetime
from database.connection import get_db
from database.models import StorageRequest, WarehouseConfig
from schemas.storage import StorageRequestItem, StorageRequestResponse, StorageRequestDetail, UpdateRequestModel, EnumClassificationStatus

from sqlalchemy import text

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

    print(expiry_date.tzinfo)
    # 타임존 수정
    if expiry_date.tzinfo is None:
        expiry_date = expiry_date.replace(
            tzinfo=datetime.now().astimezone().tzinfo
        )
    else:
        expiry_date = expiry_date.astimezone()

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
            StorageRequest.food_score,
            StorageRequest.classification_status,
            StorageRequest.create_date
        )
        .order_by(
            StorageRequest.request_id.desc()
        )
        .all()
    )
    
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
    # print(request_id)
    result = (
        db.query(
            StorageRequest.request_id,
            StorageRequest.info,
            StorageRequest.image_type,
            StorageRequest.image_data,
            StorageRequest.expiry_date,
            StorageRequest.food_score,
            StorageRequest.classification_status,
        )
        .filter(StorageRequest.request_id == request_id)
        .first()
    )
        

    if result is None:
        return None

    
    return StorageRequestDetail(
        request_id=result.request_id,
        info=result.info,
        image_type=result.image_type,
        #image_data=item.image_data,
        image_data = base64.b64encode(result.image_data).decode("utf-8") if result.image_data else None,
        expiry_date=result.expiry_date,
        food_score=result.food_score,
        classification_status=result.classification_status
    )

@router.put("/{request_id}", description="적재 요청 정보 update")
async def update_requests(request_id:int, data:UpdateRequestModel, db: Session = Depends(get_db)):
    try:
        target = db.query(StorageRequest).filter(StorageRequest.request_id == request_id).first()
        if target is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"해당 id로 적재된 정보가 없습니다."
                )
        print(f"{request_id} / {data.classification_status} / {data.food_score}")

        target.classification_status = data.classification_status
        if data.food_score is not None:
            target.food_score = data.food_score

        # 변경사항을 먼저 DB에 반영
        db.flush()

        # ORM 세션에서 객체 분리
        db.expunge(target)    

        if data.classification_status == EnumClassificationStatus.completed:
            # 처리완료이면서 score 점수가 있으면 food_score_threshold 값보다 작으면 storage_info 테이블에 저장
            config_food_score_threshold = (
                db.query(WarehouseConfig)
                .filter(WarehouseConfig.config_key == "food_score_threshold")
                .first()
            )

            if config_food_score_threshold:
                food_score_threshold = float(config_food_score_threshold.config_value)
                if data.food_score <= food_score_threshold:
                    print(f"자동 적재 대상입니다. {data.food_score}")
                    db.execute(
                            text("SELECT input_slot(:request_id, 'auto_stored')"),
                            {"request_id": request_id}
                        )
        
        db.commit()

        return { "request_id" : request_id }
    except Exception as e:
        db.rollback()
        print(f"적재 처리 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail="적재 처리 중 오류가 발생했습니다."
        )

@router.delete("/{request_id}", description="적재 요청 제거")
async def delete_requests(request_id:int, db: Session = Depends(get_db)):
    target = db.query(StorageRequest).filter(StorageRequest.request_id == request_id).first()
    if target is None:
        raise HTTPException(
            status_code=404,
            detail=f"해당 id로 적재된 정보가 없습니다."
        )

    db.delete(target)
    db.commit()

@router.put("/{request_id}/slot", description="적재 요청 받은 항목을 slot에 수동 적재 진행.")
async def input_slot(request_id:int, db: Session = Depends(get_db)):
    print(request_id)
    # 적재 요청 테이블에서 확인
    target = db.query(StorageRequest).filter(StorageRequest.request_id == request_id).first()
    
    if target is None:
        raise HTTPException(
            status_code=404,
            detail=f"해당 id로 적재된 정보가 없습니다."
        )
    print(target)
    result = db.execute(
        text("SELECT input_slot(:request_id, 'manual_stored')"),
        {"request_id": request_id}
    )

    slot_id = result.scalar()
    print(slot_id)
    db.commit()

    return { "slot_id" : slot_id }

