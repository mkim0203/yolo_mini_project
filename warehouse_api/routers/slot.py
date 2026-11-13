
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import StorageInfo, WarehouseSlot, Warehouse
from schemas.slot import SlotDetail, SlotStatusRequest, EnumSlotStatus

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
            status_code=404,
            detail="정보를 찾을수 없습니다."
        )

    slot_info = db.query(WarehouseSlot).filter(WarehouseSlot.slot_id == slot_id).first()
    dong_info = db.query(Warehouse).filter(Warehouse.warehouse_id == slot_info.warehouse_id).first()

    return SlotDetail(
        slot_id=result.slot_id,
        slot_info=result.info,
        dong= dong_info.dong,
        line_code=slot_info.line_code,
        column_no=slot_info.column_no,
        floor=slot_info.floor,
        image_type=result.image_type,
        #image_data=item.image_data,
        image_data = base64.b64encode(result.image_data).decode("utf-8") if result.image_data else None,
        request_id = result.request_id,
        expiry_date=result.expiry_date,
        food_score=result.food_score,
        processing_status=result.processing_status
    )

@router.put("/{slot_id}/status", description="slot 상태 변경. 'empty' 또는  'maintenance'")
async def set_slot_status(slot_id: int, data:SlotStatusRequest, db: Session = Depends(get_db)):
    target = db.query(WarehouseSlot).filter(WarehouseSlot.slot_id == slot_id).first()

    if target is None:
        raise HTTPException(
            status_code=404,
            detail="정보를 찾을수 없습니다."
        )

    print(f"DB : {target.status} // 요청 {data.status}")

    request_status = data.status.value

    if target.status == "maintenance" and request_status == "empty":
        target.status = request_status

    elif target.status == "empty" and request_status == "maintenance":
        target.status = request_status

    else:
        raise HTTPException(
            status_code=400,
            detail="status 설정이 잘못되었습니다."
        )

    db.commit()

    return { "status" : target.status }