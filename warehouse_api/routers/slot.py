
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import StorageInfo
from schemas.slot import SlotDetail

import base64

router = APIRouter(
    prefix="/slots",
    tags=["slots"]
)

@router.get("/{slot_id}", description="'창고 현황' 선택한 slot 상세정보 조회")
def get_slot(slot_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(
            StorageInfo.slot_id,
            StorageInfo.info,
            StorageInfo.image_type,
            StorageInfo.image_data,
            StorageInfo.request_id,
            StorageInfo.expiry_date,
            StorageInfo.food_score,
            StorageInfo.processing_status
        )
        .filter(StorageInfo.slot_id == slot_id)
        .first()
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="정보를 찾을수 없습니다."
        )

    return SlotDetail(
        slot_id=result.slot_id,
        slot_info=result.info,
        image_type=result.image_type,
        #image_data=item.image_data,
        image_data = base64.b64encode(result.image_data).decode("utf-8") if result.image_data else None,
        request_id = result.request_id,
        expiry_date=result.expiry_date,
        food_score=result.food_score,
        processing_status=result.processing_status
    )