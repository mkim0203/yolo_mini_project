from pydantic import BaseModel
from typing import List
from datetime import datetime
from enum import Enum

class EnumSlotStatus(str, Enum):
    empty = "empty"
    used = "used"
    maintenance = "maintenance"


class SlotDetail(BaseModel):
    slot_id: int
    slot_info: str
    dong:str
    line_code: str
    column_no: int
    floor:int
    image_type: str | None=None
    image_data: str | None=None
    request_id: int | None=None
    expiry_date: datetime | None=None
    food_score: float | None=None
    processing_status: str | None=None


class SlotStatusRequest(BaseModel):
    status:EnumSlotStatus


