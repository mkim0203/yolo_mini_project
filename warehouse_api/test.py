from sqlalchemy import text

from database.connection import Base, DB_CONN, engine, create_tables
from database import models


if __name__ == "__main__":
    print(DB_CONN)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("DB 연결 성공:", result.scalar())

    except Exception as e:
        print("DB 연결 실패:", type(e).__name__, str(e))

    # 등록된 테이블 확인
    print("등록된 테이블:", Base.metadata.tables.keys())

    try:
        print('run create tables')
        create_tables()
        print('done create tables')
    except Exception as e:
        print(str(e))