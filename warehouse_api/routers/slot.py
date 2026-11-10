
from fastapi import APIRouter, Depends
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
def get_lines(slot_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(
            StorageInfo.slot_id,
            StorageInfo.info,
            StorageInfo.image_type,
            StorageInfo.image_data,
            StorageInfo.request_id,
            StorageInfo.expiry_date
        )
        .filter(StorageInfo.slot_id == slot_id)
        .all()
    )
    
    if len(result) == 0:
        return None

    items = [
        SlotDetail(
            slot_id=item.slot_id,
            slot_info=item.info,
            image_type=item.image_type,
            #image_data=item.image_data,
            image_data = base64.b64encode(item.image_data).decode("utf-8") if item.image_data else None,
            request_id = item.request_id,
            expiry_date=item.expiry_date
        )
        for item in result
    ]

    return items[0]