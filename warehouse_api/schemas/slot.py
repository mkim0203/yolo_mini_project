from pydantic import BaseModel
from typing import List
from datetime import datetime


class SlotDetail(BaseModel):
    slot_id: int
    slot_info: str
    image_type: str | None=None
    image_data: str | None=None
    request_id: int | None=None
    expiry_date: datetime | None=None
    food_score: float | None=None
    processing_status: str | None=None
