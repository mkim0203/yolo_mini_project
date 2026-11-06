# routers/warehouse.py

from fastapi import APIRouter

router = APIRouter(
    prefix="/warehouses",
    tags=["Warehouses"]
)


@router.get("")
def get_warehouses():
    return {"message": "창고 목록 조회"}


@router.get("/{warehouse_id}/lines")
def get_lines(warehouse_id: int):
    return {"warehouse_id": warehouse_id}


@router.get("/{warehouse_id}/lines/{line_code}")
def get_line(warehouse_id: int, line_code: str):
    return {
        "warehouse_id": warehouse_id,
        "line_code": line_code
    }