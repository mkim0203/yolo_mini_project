from datetime import datetime
from pydantic import BaseModel
from typing import List

class StorageRequestItem(BaseModel):
    request_id: int
    info: str
    image_type: str| None=None
    expiry_date: datetime | None=None
    food_score: float | None=None,
    classification_status: str | None=None,
    create_date: datetime | None=None

class StorageRequestResponse(BaseModel):
    total: int
    items: List[StorageRequestItem]

class StorageRequestDetail(BaseModel):
    request_id: int| None=None
    info: str
    image_type: str | None=None
    image_data: str | None=None
    expiry_date: datetime | None=None
    food_score: float | None=None,
    classification_status: str | None=None,
    create_date: datetime | None=None

class ReleaseResponse(BaseModel):
    release_requested: bool
    slot_id: int
    info: str
    image_type: str | None=None
    image_data: str | None=None
    expiry_date: datetime | None=None
    create_date: datetime | None=None

class HistoryResponse(BaseModel):
    history_id: int
    dong: str | None=None
    line_code: str | None=None
    column_no: int | None=None
    floor: int | None=None
    info: str | None=None
    expiry_date: datetime | None=None
    storage_request_id: int | None=None
    release_request_id: int | None=None
    input_date: datetime | None=None
    food_score: float | None=None
    processing_status: str | None=None
    output_date: datetime | None=None
    create_date: datetime | None=None

class ExpriyResponse(BaseModel):
    """
    w.dong
    , s.line_code
    , s.column_no
    , s.floor
    , i.storage_id
    , i.slot_id
    , i.info
    , i.expiry_date
    """
    dong: str | None=None
    line_code: str | None=None
    column_no: int | None=None
    floor: int | None=None
    storage_id: int
    slot_id: int
    info: str | None=None
    expiry_date: datetime | None=None