from fastapi import APIRouter, Depends, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone
from database.connection import get_db
from database.models import StorageInfo, ReleaseRequest, StorageHistory, Warehouse, WarehouseSlot
from schemas.storage import ReleaseResponse, HistoryResponse, ExpriyResponse

import base64

router = APIRouter(
    prefix="/storage",
    tags=["storage"]
)

@router.post("/{slot_id}/test")
async def test(
    slot_id: int,
    request_id: int | None = Form(None),
    info: str | None = Form(None),
    expiry_date: datetime = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    이미지 넣기 테스트..
    """
    # 이미지 타입 확인
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="이미지 파일만 업로드할 수 있습니다."
        )

    # 이미지 바이너리 읽기
    image_data = await image.read()

    if not image_data:
        raise HTTPException(
            status_code=400,
            detail="이미지 데이터가 비어 있습니다."
        )

    # 기존 슬롯 데이터 확인
    storage = db.query(StorageInfo).filter(
        StorageInfo.slot_id == slot_id
    ).first()

    if storage:
        # 기존 데이터 수정
        storage.request_id = request_id
        storage.info = info
        storage.image_type = image.content_type
        storage.image_data = image_data
        storage.expiry_date = expiry_date
    else:
        # 신규 데이터 등록
        storage = StorageInfo(
            slot_id=slot_id,
            request_id=request_id,
            info=info,
            image_type=image.content_type,
            image_data=image_data,
            expiry_date=expiry_date
        )

        db.add(storage)

    try:
        db.commit()
        db.refresh(storage)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"저장 실패: {str(e)}"
        )

    return {
        "message": "저장 완료",
        "storage_id": storage.storage_id,
        "slot_id": storage.slot_id,
        "image_type": storage.image_type,
        "filename": image.filename
    }


@router.get("/history", description="적재 및 반출 이력 조회")
async def search_history(
    find_text: str = "",
    option: str = "7d",
    max_row: int = Query(200, ge=30, le=200),
    db: Session = Depends(get_db)
):
    """
    option:
        7d  : 최근 7일
        30d : 최근 30일
        all : 전체
    max_row:
        최대 조회 건수
    """
    print(f"{find_text} / {option} / {max_row}")

    if max_row < 30:
        max_row = 30
    elif max_row > 200:
        max_row = 200

    query = (
        db.query(
            StorageHistory.history_id,
            Warehouse.dong,
            WarehouseSlot.line_code,
            WarehouseSlot.column_no,
            WarehouseSlot.floor,
            StorageHistory.info,
            StorageHistory.expiry_date,
            StorageHistory.storage_request_id,
            StorageHistory.release_request_id,
            StorageHistory.input_date,
            StorageHistory.output_date,
            StorageHistory.create_date
        )
        .outerjoin(
            Warehouse,
            StorageHistory.warehouse_id == Warehouse.warehouse_id
        )
        .outerjoin(
            WarehouseSlot,
            StorageHistory.slot_id == WarehouseSlot.slot_id
        )
    )

    # 1. 날짜 조건
    now = datetime.now(timezone.utc)

    if option == "7d":
        start_date = now - timedelta(days=7)
        query = query.filter(StorageHistory.create_date >= start_date)

    elif option == "30d":
        start_date = now - timedelta(days=30)
        query = query.filter(StorageHistory.create_date >= start_date)

    elif option != "all":
        raise HTTPException(status_code=400, detail="잘못된 조회 기간입니다.")

    # 2. 검색어 조건
    if find_text.strip():
        query = query.filter(
            StorageHistory.info.ilike(f"%{find_text.strip()}%")
        )

    # 3. 정렬 및 최대 조회 건수
    result = (
        query
        .order_by(StorageHistory.history_id.desc())
        .limit(max_row)
        .all()
    )

    items = [
        HistoryResponse(**row._mapping)
        for row in result
    ]

    return items
    


@router.get("/expiry", description="유통 기한 만료 예정인 항목들 조회")
async def search_expiry(
    option: int = Query(7, le=30),
    db: Session = Depends(get_db)
):
    """
    select 
        w.dong
        , s.line_code
        , s.column_no
        , s.floor
        , i.storage_id
        , i.slot_id
        , i.info
        , i.expiry_date
    from storage_info i
    left outer join warehouse_slot s on i.slot_id = s.slot_id
    left outer join warehouse w on s.warehouse_id = w.warehouse_id
    """
    
    query = (
        db.query(
            Warehouse.dong,
            WarehouseSlot.line_code,
            WarehouseSlot.column_no,
            WarehouseSlot.floor,
            StorageInfo.storage_id,
            StorageInfo.slot_id,
            StorageInfo.info,
            StorageInfo.expiry_date
        )
        .select_from(StorageInfo)
        .outerjoin(
            WarehouseSlot,
            StorageInfo.slot_id == WarehouseSlot.slot_id
        )
        .outerjoin(
            Warehouse,
            WarehouseSlot.warehouse_id == Warehouse.warehouse_id
        )
    )

    # 1. 날짜 조건
    now = datetime.now(timezone.utc)
    target_date = now + timedelta(days=option)
    query = query.filter(StorageInfo.expiry_date <= target_date)

    # 3. 정렬
    result = (
        query
        .order_by(StorageInfo.expiry_date.desc())
        .all()
    )

    items = [
        ExpriyResponse(**row._mapping)
        for row in result
    ]

    return items



@router.get("/{id}", description="창고 적재 확인. option에 따라 구분하여 조회함.")
async def search_storage(id:int, option:str = "request", db: Session = Depends(get_db)):
    query = db.query(
        StorageInfo.slot_id,
        StorageInfo.info,
        StorageInfo.image_type,
        StorageInfo.image_data,
        StorageInfo.expiry_date
    )

    if option == "request":
        query = query.filter(StorageInfo.request_id == id)
    elif option == "storage":
        query = query.filter(StorageInfo.storage_id == id)
    elif option == "slot":
        query = query.filter(StorageInfo.slot_id == id)
    else:
        raise HTTPException(
            status_code=400,
            detail="잘못된 조회 옵션입니다."
        )

    result = query.first()

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="정보를 찾을수 없습니다."
        )

    # 이미 등록된 slot id인지 확인
    target_slot_id = result.slot_id
    check_result = db.query(ReleaseRequest.release_id).filter(ReleaseRequest.slot_id == target_slot_id).first()


    return ReleaseResponse(
        release_requested=False if check_result is None else True,
        info=result.info,
        slot_id=result.slot_id,
        image_type=result.image_type,
        image_data=(
            base64.b64encode(result.image_data).decode("utf-8")
            if result.image_data else None
        ),
        expiry_date=result.expiry_date
    )
