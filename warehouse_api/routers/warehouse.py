# routers/warehouse.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Warehouse, WarehouseSlot, StorageInfo
from schemas.warehouse import WarehouseItem, WarehouseListResponse
from schemas.warehouse import WarehouseInfoItem, WarehouseInfoResponse
from schemas.warehouse import WarehouseSlotItem, WarehouseSlotListResponse


router = APIRouter(
    prefix="/warehouses",
    tags=["Warehouses"]
)


@router.get("", description="")
def get_warehouses(db: Session = Depends(get_db)):
    result = (
        db.query(Warehouse)
        .order_by(Warehouse.warehouse_id.asc())
        .all()
    )

    items = [
        WarehouseItem(
            warehouse_id=item.warehouse_id,
            dong=item.dong
        )
        for item in result
    ]

    return WarehouseListResponse(
        total=len(items),
        items=items
    )

@router.get("/info", description="'창고 현황' 데이터 조회, 창고 동, line 정보")
def get_warehouses(db: Session = Depends(get_db)):
    result = (
        db.query(
            Warehouse.warehouse_id,
            Warehouse.dong,
            WarehouseSlot.line_code
        )
        .outerjoin(
            WarehouseSlot,
            Warehouse.warehouse_id == WarehouseSlot.warehouse_id
        )
        .group_by(
            Warehouse.warehouse_id,
            Warehouse.dong,
            WarehouseSlot.line_code
        )
        .order_by(
            Warehouse.warehouse_id.asc(),
            WarehouseSlot.line_code.asc()
        )
        .all()
    )

    items = [
        WarehouseInfoItem(**row._mapping)
        for row in result
    ]

    return WarehouseInfoResponse(
        total=len(items),
        items=items
    )

@router.get("/{warehouse_id}/lines")
def get_lines(warehouse_id: int, db: Session = Depends(get_db)):
    
    result = (
        db.query(
            WarehouseSlot.slot_id,
            WarehouseSlot.warehouse_id,
            Warehouse.dong,
            WarehouseSlot.line_code,
            WarehouseSlot.column_no,
            WarehouseSlot.floor,
            WarehouseSlot.status
        )
        .join(
            Warehouse,
            WarehouseSlot.warehouse_id == Warehouse.warehouse_id
        )
        .filter(WarehouseSlot.warehouse_id == warehouse_id)
        .all()
    )

    items = [
        WarehouseSlotItem(**row._mapping)
        for row in result
    ]

    return WarehouseSlotListResponse(
            total=len(items),
            items=items
    )


@router.get("/{warehouse_id}/lines/{line_code}", description="'창고 현황' 창고 동, line 기준으로 slot 정보 조회")
def get_line(warehouse_id: int, line_code: str, db: Session = Depends(get_db)):
    
    result = (
        db.query(
            WarehouseSlot.slot_id,
            WarehouseSlot.warehouse_id,
            Warehouse.dong,
            WarehouseSlot.line_code,
            WarehouseSlot.column_no,
            WarehouseSlot.floor,
            WarehouseSlot.status,
        )
        .outerjoin(
            Warehouse,
            WarehouseSlot.warehouse_id == Warehouse.warehouse_id,
        )
        .filter(
            WarehouseSlot.warehouse_id == warehouse_id,
            WarehouseSlot.line_code == line_code
        )
        .all()
    )
    

    items = [
        WarehouseSlotItem(**row._mapping)
        for row in result
    ]

    return WarehouseSlotListResponse(
            total=len(items),
            items=items
    )