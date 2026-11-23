
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import BusinessRules

from schemas.business_rules import (
    BusinessRuleCreate,
    BusinessRuleStatusUpdate,
    BusinessRuleActiveUpdate,
    BusinessRuleResponse
)

router = APIRouter(
    prefix="/business-rules",
    tags=["Business Rules"]
)


# =====================================================
# 1. 규칙 조회
# =====================================================

@router.get("", response_model=list[BusinessRuleResponse])
def get_business_rules(
    rule_id: int | None = None,
    category: str | None = None,
    status: str | None = None,
    is_active: str | None = None,
    target_table: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(BusinessRules)

    if rule_id is not None:
        query = query.filter(
            BusinessRules.rule_id == rule_id
        )

    if category is not None:
        query = query.filter(
            BusinessRules.category == category
        )

    if status is not None:
        query = query.filter(
            BusinessRules.status == status
        )

    if is_active is not None:
        query = query.filter(
            BusinessRules.is_active == is_active
        )

    if target_table is not None:
        query = query.filter(
            BusinessRules.target_tables.contains([target_table])
        )

    return query.order_by(
        BusinessRules.rule_id.desc()
    ).all()


# =====================================================
# 2. 규칙 추가
# =====================================================

@router.post(
    "",
    response_model=BusinessRuleResponse,
    status_code=201
)
def create_business_rule(
    data: BusinessRuleCreate,
    db: Session = Depends(get_db)
):
    rule = BusinessRules(
        rule_name=data.rule_name,
        category=data.category,
        target_tables=data.target_tables,
        rule_content=data.rule_content,
        status="pending",
        is_active="Y"
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    return rule


# =====================================================
# 3. 규칙 삭제
# =====================================================

@router.delete("/{rule_id}")
def delete_business_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    rule = db.query(BusinessRules).filter(
        BusinessRules.rule_id == rule_id
    ).first()

    if rule is None:
        raise HTTPException(
            status_code=404,
            detail="규칙을 찾을 수 없습니다."
        )

    db.delete(rule)
    db.commit()

    return {
        "message": "규칙이 삭제되었습니다.",
        "rule_id": rule_id
    }


# =====================================================
# 4. 규칙 상태 변경
# =====================================================

@router.put(
    "/{rule_id}/status",
    response_model=BusinessRuleResponse
)
def update_business_rule_status(
    rule_id: int,
    data: BusinessRuleStatusUpdate,
    db: Session = Depends(get_db)
):
    rule = db.query(BusinessRules).filter(
        BusinessRules.rule_id == rule_id
    ).first()

    if rule is None:
        raise HTTPException(
            status_code=404,
            detail="규칙을 찾을 수 없습니다."
        )

    rule.status = data.status

    db.commit()
    db.refresh(rule)

    return rule


# =====================================================
# 5. 규칙 활성화 여부 변경
# =====================================================

@router.put(
    "/{rule_id}/active",
    response_model=BusinessRuleResponse
)
def update_business_rule_active(
    rule_id: int,
    data: BusinessRuleActiveUpdate,
    db: Session = Depends(get_db)
):
    rule = db.query(BusinessRules).filter(
        BusinessRules.rule_id == rule_id
    ).first()

    if rule is None:
        raise HTTPException(
            status_code=404,
            detail="규칙을 찾을 수 없습니다."
        )

    rule.is_active = data.is_active

    db.commit()
    db.refresh(rule)

    return rule
