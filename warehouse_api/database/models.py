# ORM 작업시 Comment를 달아작업.
# 해당 Comment 기준으로 llm에서 정보를 수집할수 있도록 하기 위함.


from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    CHAR,
    Float,
    LargeBinary,
    ForeignKey,
    UniqueConstraint,
    text
)
from sqlalchemy.dialects.postgresql import JSONB

from database.connection import Base


class Warehouse(Base):
    __tablename__ = "warehouse"

    __table_args__ = {
        "comment": "창고 및 동 정보"
    }

    warehouse_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="창고 ID"
    )

    warehouse_name = Column(
        String(100),
        nullable=True,
        comment="창고 이름"
    )

    dong = Column(
        String(20),
        nullable=False,
        comment="창고 동"
    )

    status = Column(
        String(20),
        nullable=True,
        comment="창고 상태"
    )

    create_date = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

class WarehouseSlot(Base):
    __tablename__ = "warehouse_slot"

    # 중복 적재칸 방지
    __table_args__ = (
        UniqueConstraint(
            "warehouse_id",
            "line_code",
            "column_no",
            "floor",
            name="uq_warehouse_slot_location"
        ),
        {
            "comment": "창고 내 개별 적재 칸(slot) 정보"
        }
    )

    slot_id = Column(Integer, primary_key=True, autoincrement=True, comment="적재칸(slot) ID")

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouse.warehouse_id"),
        nullable=False,
        comment="창고 ID"
    )

    line_code = Column(CHAR(1), nullable=False, comment="적재칸 라인 코드 (A, B, C 등)")
    column_no = Column(Integer, nullable=False, comment="적재칸 열 번호")
    floor = Column(Integer, nullable=False, comment="적재칸 층 수")

    status = Column(String(20), nullable=False, comment="적재칸 상태 (used, empty, maintenance)")

    create_date = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

class WarehouseConfig(Base):
    __tablename__ = "warehouse_config"

    __table_args__ = {
        "comment": "창고 설정 정보"
    }
    
    config_id = Column(Integer, primary_key=True, autoincrement=True, comment="설정 ID")
    config_key = Column(String(50), nullable=False, comment="설정 키")
    config_value = Column(String(50), nullable=True, comment="설정 값")
    info = Column(String(100), nullable=True, comment="설정 정보")
    create_date = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

class StorageInfo(Base):
    __tablename__ = "storage_info"

    __table_args__ = (
        UniqueConstraint(
            "slot_id",
            name="uq_storage_slot_id"
        ),
        {
            "comment": "창고 적재 정보"
        }
    )

    storage_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="적재 정보 ID"
    )

    slot_id = Column(
        Integer,
        ForeignKey("warehouse_slot.slot_id"),
        nullable=False,
        comment="적재칸(slot) ID"
    )

    request_id = Column(Integer, nullable=True, comment="적재 요청 ID")

    info = Column(String(100), nullable=True, comment="적재 요청 정보")

    image_type = Column(String(50), nullable=False, comment="이미지 유형")

    image_data = Column(LargeBinary, nullable=True, comment="이미지 데이터")

    expiry_date = Column(DateTime(timezone=True), nullable=False, comment="유통기한 만료 날짜")

    food_score = Column(Float, nullable=True, comment="음식(food/non_food) 점수. 0~1 사이의 값으로, 0에 가까울수록 음식일 확률이 높음")
    classification_result = Column(JSONB, nullable=True, comment="AI 분류 결과. 음식 유형 및 분류 점수 저장")
    processing_status = Column(String(20), nullable=True, comment="음식 분류 후 처리 상태(auto_stored, manual_stored)")

    create_date = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

class StorageHistory(Base):
    __tablename__ = "storage_history"

    __table_args__ = {
        "comment": "창고 적재 이력 정보. 적재 완료된 정보만 기록"
    }

    # 기본키
    history_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="적재 이력 ID"
    )

    warehouse_id = Column(Integer, nullable=False, comment="창고 ID")

    slot_id = Column(Integer, nullable=False, comment="적재칸(slot) ID")

    storage_id = Column(Integer, nullable=False, comment="적재 정보 ID")

    info = Column(String(100), nullable=True, comment="적재 요청 정보")

    expiry_date = Column(DateTime(timezone=True), nullable=False, comment="유통기한 만료 날짜")

    storage_request_id = Column(Integer, nullable=True, comment="적재 요청 ID")

    release_request_id = Column(Integer, nullable=True, comment="출고 요청 ID")

    food_score = Column(Float, nullable=True, comment="음식(food/non_food) 점수. 0~1 사이의 값으로, 0에 가까울수록 음식일 확률이 높음")
    classification_result = Column(JSONB, nullable=True, comment="AI 분류 결과. 음식 유형 및 분류 점수 저장")
    processing_status = Column(String(20), nullable=True, comment="음식 분류 후 처리 상태(auto_stored, manual_stored)")

    input_date = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="적재 완료 날짜"
    )

    output_date = Column(DateTime(timezone=True), nullable=True, comment="출고 완료 날짜")

    create_date = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

class StorageRequest(Base):
    __tablename__ = "storage_request"

    __table_args__ = {
        "comment": "창고 적재 요청 정보"
    }

    request_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="적재 요청 ID"
    )

    info = Column(String(100), nullable=True, comment="적재 요청 정보")

    expiry_date = Column(DateTime(timezone=True), nullable=False, comment="유통기한 만료 날짜")

    image_type = Column(String(50), nullable=True, comment="이미지 유형")

    image_data = Column(LargeBinary, nullable=True, comment="이미지 데이터")

    food_score = Column(Float, nullable=True, comment="음식(food/non_food) 점수. 0~1 사이의 값으로, 0에 가까울수록 음식일 확률이 높음")
    classification_status = Column(String(20), nullable=True, comment="AI 분류 상태(pending, processing, completed, failed)")

    classification_result = Column(JSONB, nullable=True, comment="AI 분류 결과. 음식 유형 및 분류 점수 저장")

    create_date = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )


class ReleaseRequest(Base):
    __tablename__ = "release_request"

    __table_args__ = {
        "comment": "창고 출고 요청 정보"
    }

    release_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="출고 요청 ID"
    )

    slot_id = Column(Integer, nullable=False, comment="적재칸(slot) ID")

    info = Column(String(100), nullable=True, comment="적재 요청시 입력한 정보")

    create_date = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

class BusinessRules(Base):
    __tablename__ = "business_rules"

    __table_args__ = {
        "comment": "창고 운영 관련 비즈니스 규칙"
    }

    rule_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="규칙 ID"
    )

    rule_name = Column(String(100), nullable=False, comment="규칙 이름")
    category = Column(String(30), nullable=False, comment="규칙 카테고리(BUSINESS, SYSTEM 등)")
    target_tables = Column(JSONB, nullable=True, comment="규칙 적용 대상 테이블")
    rule_content = Column(String(1024), nullable=True, comment="규칙 설명")
    status = Column(String(20), nullable=True, comment="규칙 상태 (pending, approved, rejected)")
    is_active = Column(CHAR(1), nullable=False, server_default=text("'Y'"), comment="규칙 활성화 여부 (Y/N)")

    create_date = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )