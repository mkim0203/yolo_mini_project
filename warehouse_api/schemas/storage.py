from datetime import datetime
from pydantic import BaseModel
from typing import List

class StorageRequestItem(BaseModel):
    request_id: int
    info: str
    image_type: str| None=None
    expiry_date: datetime | None=None
    create_date: datetime | None=None

class StorageRequestResponse(BaseModel):
    total: int
    items: List[StorageRequestItem]

class StorageRequestDetail(BaseModel):
    request_id: int
    info: str
    image_type: str | None=None
    image_data: str | None=None
    expiry_date: datetime | None=None
    create_date: datetime | None=None