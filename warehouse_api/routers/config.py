from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from datetime import datetime
from database.connection import get_db
from database.models import WarehouseConfig
from schemas.config import ViewConfigItem, ViewConfigResponse


router = APIRouter(
    prefix="/configs",
    tags=["configs"]
)

@router.get("", description="설정 정보 조회")
async def search_configs(db: Session = Depends(get_db)):
    result = db.query(WarehouseConfig).all()

    items = [
            #ViewConfigItem(**row._mapping)
            ViewConfigItem.model_validate(row)
            for row in result
        ]
    
    return ViewConfigResponse(
            total=len(items),
            items=items
    )

@router.get("/config", description="설정 항목 조회")
async def get_config(key:str, db: Session = Depends(get_db)):
    result = db.query(WarehouseConfig).filter(WarehouseConfig.config_key == key).first()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"해당 id로 적재된 정보가 없습니다."
        )

    return ViewConfigItem.model_validate(result)
    