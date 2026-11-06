from pydantic import BaseModel
from typing import List


class WarehouseItem(BaseModel):
    warehouse_id: int
    dong: str


class WarehouseListResponse(BaseModel):
    total: int
    items: List[WarehouseItem]

class WarehouseInfoItem(BaseModel):
    warehouse_id: int
    dong: str
    line_code: str


class WarehouseInfoResponse(BaseModel):
    total: int
    items: List[WarehouseInfoItem]    


class WarehouseSlotItem(BaseModel):
    slot_id: int
    warehouse_id: int
    dong: str
    line_code: str
    column_no: int
    floor: int
    status: str


class WarehouseSlotListResponse(BaseModel):
    total: int
    items: List[WarehouseSlotItem]    