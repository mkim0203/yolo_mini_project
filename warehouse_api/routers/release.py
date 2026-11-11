from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session

from datetime import datetime
from database.connection import get_db
from database.models import StorageInfo, ReleaseRequest
from schemas.release import ViewReleaseRequest, ViewReleaseItem, ViewReleaseResponse

from sqlalchemy import text

router = APIRouter(
    prefix="/releases",
    tags=["releases"]
)

@router.get("", description="반출 목록 조회")
async def search_release(db: Session = Depends(get_db)):
    result = (
        db.query(
            ReleaseRequest.release_id,
            ReleaseRequest.slot_id,
            ReleaseRequest.info,
            ReleaseRequest.create_date
        )
        .order_by(
            ReleaseRequest.release_id.desc()
        )
        .all()
    )
    
    items = [
        ViewReleaseItem(**row._mapping)
        for row in result
    ]

    return ViewReleaseResponse(
            total=len(items),
            items=items
    )


@router.post("/release", description="반출 요청 등록")
async def release_request_id(model: ViewReleaseRequest, db: Session = Depends(get_db)):
    # request_id 기준으로 storage 에 등록된 정보 조회
    find = db.query(StorageInfo).filter(StorageInfo.slot_id == model.slot_id).first()

    if find is None:
        raise HTTPException(
            status_code=404,
            detail=f"해당 id로 적재된 정보가 없습니다."
        )

    # 반출 테이블에 데이터 저장
    add_data = ReleaseRequest()
    add_data.info = find.info
    add_data.slot_id = find.slot_id
    db.add(add_data)

    try:
        db.commit()
        db.refresh(add_data)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"저장 실패: {str(e)}"
        )

    return {
        "message": "반출 요청 완료",
        "release_id": add_data.release_id,
    }



@router.delete("/{release_id}/slot", description="반출 진행")
async def ouput_slot(release_id:int, db: Session = Depends(get_db)):
    print(release_id)
    # 적재 요청 테이블에서 확인
    target = db.query(ReleaseRequest).filter(ReleaseRequest.release_id == release_id).first()
    
    if target is None:
        raise HTTPException(
            status_code=404,
            detail=f"해당 id로 적재된 정보가 없습니다."
        )
    print(target)
    result = db.execute(
        text("SELECT output_slot(:release_id)"),
        {"release_id": release_id}
    )

    slot_id = result.scalar()
    print(slot_id)
    db.commit()

    return { "slot_id" : slot_id }

