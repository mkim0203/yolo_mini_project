from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import APP_CONFIG

_common_conn = f"{APP_CONFIG.DB_USER}:{APP_CONFIG.DB_PW}@{APP_CONFIG.DB_HOST}:{APP_CONFIG.DB_PORT}/{APP_CONFIG.DB_DATABASE}"
DB_CONN = f"postgresql+psycopg://{_common_conn}"
VECTORDB_CONN = f"postgresql+psycopg://{_common_conn}"

# DB Engine
engine = create_engine(
    DB_CONN,
    pool_pre_ping=True
)

# DB Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ORM Base
Base = declarative_base()

# API 요청별 DB 세션 생성
def get_db():
    
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def create_tables():
    # ORM 통해서 테이블 생성 진행
    Base.metadata.create_all(bind=engine)        