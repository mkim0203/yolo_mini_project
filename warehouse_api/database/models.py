from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    CHAR,
    LargeBinary,
    ForeignKey,
    UniqueConstraint,
    text
)
from database.connection import Base


class Warehouse(Base):
    __tablename__ = "warehouse"

    warehouse_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    warehouse_name = Column(
        String(100),
        nullable=True
    )

    dong = Column(
        String(20),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=True
    )

    create_date = Column(
        DateTime,
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
    )

    slot_id = Column(Integer, primary_key=True, autoincrement=True)

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouse.warehouse_id"),
        nullable=False
    )

    line_code = Column(CHAR(1), nullable=False)
    column_no = Column(Integer, nullable=False)
    floor = Column(Integer, nullable=False)

    status = Column(String(20), nullable=False)

    create_date = Column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

class Storage(Base):
    __tablename__ = "storage"

    __table_args__ = (
        UniqueConstraint(
            "slot_id",
            name="uq_storage_slot_id"
        ),
    )

    storage_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    slot_id = Column(
        Integer,
        ForeignKey("warehouse_slot.slot_id"),
        nullable=False
    )

    request_id = Column(Integer, nullable=True)

    info = Column(String(100), nullable=True)

    image_type = Column(String(50), nullable=False)

    image_data = Column(LargeBinary, nullable=False)

    expiry_date = Column(DateTime, nullable=False)

    create_date = Column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

class StorageHistory(Base):
    __tablename__ = "storage_history"

    # 기본키
    history_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    warehouse_id = Column(Integer, nullable=False)

    slot_id = Column(Integer, nullable=False)

    storage_id = Column(Integer, nullable=False)

    info = Column(String(100), nullable=True)

    expiry_date = Column(DateTime, nullable=False)

    storage_request_id = Column(Integer, nullable=True)

    release_request_id = Column(Integer, nullable=True)

    input_date = Column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

    output_date = Column(DateTime, nullable=True)

    create_date = Column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

class ReleaseRequest(Base):
    __tablename__ = "release_request"

    release_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    slot_id = Column(Integer, nullable=False)

    info = Column(String(100), nullable=True)

    create_date = Column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )    