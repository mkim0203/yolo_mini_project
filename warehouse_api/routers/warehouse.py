# routers/warehouse.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Warehouse
from schemas.warehouse import WarehouseListResponse, WarehouseItem

router = APIRouter(
    prefix="/warehouses",
    tags=["Warehouses"]
)


@router.get("")
def get_warehouses(db: Session = Depends(get_db)):
    warehouses = (
        db.query(Warehouse)
        .order_by(Warehouse.warehouse_id.asc())
        .all()
    )

    items = [
        WarehouseItem(
            warehouse_id=item.warehouse_id,
            dong=item.dong
        )
        for item in warehouses
    ]

    return WarehouseListResponse(
        total=len(items),
        items=items
    )


@router.get("/{warehouse_id}/lines")
def get_lines(warehouse_id: int):
    return {"warehouse_id": warehouse_id}


@router.get("/{warehouse_id}/lines/{line_code}")
def get_line(warehouse_id: int, line_code: str):
    return {
        "warehouse_id": warehouse_id,
        "line_code": line_code
    }