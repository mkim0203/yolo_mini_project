from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List

class ViewConfigItem(BaseModel):
    config_id: int 
    config_key: str
    config_value: str | None=None
    info: str | None=None
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)

class ViewConfigResponse(BaseModel):
    total: int
    items: List[ViewConfigItem]