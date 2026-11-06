from pydantic import BaseModel
from typing import List


class WarehouseItem(BaseModel):
    warehouse_id: int
    dong: str


class WarehouseListResponse(BaseModel):
    total: int
    items: List[WarehouseItem]