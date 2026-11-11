from datetime import datetime
from pydantic import BaseModel
from typing import List

class ViewReleaseRequest(BaseModel):
    slot_id: int

class ViewReleaseItem(BaseModel):
    release_id: int 
    slot_id: int | None=None
    info: str | None=None
    create_date: datetime

class ViewReleaseResponse(BaseModel):
    total: int
    items: List[ViewReleaseItem]