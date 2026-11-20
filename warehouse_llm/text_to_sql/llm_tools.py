from langchain.tools import tool
from sqlalchemy import text
from database.connection import SessionLocal
from text_to_sql.validator import validate_sql


def get_db_schema(db):

    query = text("""
        SELECT
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """)

    rows = db.execute(query).mappings().all()

    return [dict(row) for row in rows]

def get_db_table_relationships(db):
    query = text("""
        SELECT
            n.nspname AS schema_name,
            c.relname AS table_name,
            con.conname AS constraint_name,
            CASE con.contype
                WHEN 'p' THEN 'PRIMARY KEY'
                WHEN 'f' THEN 'FOREIGN KEY'
            END AS constraint_type,
            pg_get_constraintdef(con.oid) AS constraint_definition
        FROM pg_constraint con
        JOIN pg_class c
            ON con.conrelid = c.oid
        JOIN pg_namespace n
            ON c.relnamespace = n.oid
        WHERE n.nspname = 'public'
          AND con.contype IN ('p', 'f')
        ORDER BY c.relname, con.contype;
    """)

    rows = db.execute(query).mappings().all()

    return [dict(row) for row in rows]


@tool
def get_database_schema():
    """PostgreSQL의 현재 테이블과 컬럼 구조를 조회합니다."""

    db = SessionLocal()

    try:
        items = get_db_schema(db)
        return items

    except Exception as e:
        print("DB 조회 오류:", type(e).__name__, str(e))
        raise

    finally:
        db.close()


@tool
def get_database_relationships():
    """PostgreSQL의 현재 테이블 간 관계를 조회합니다."""

    db = SessionLocal()

    try:
        items = get_db_table_relationships(db)

        return items

    except Exception as e:
        print("DB 조회 오류:", type(e).__name__, str(e))
        raise

    finally:
        db.close()

@tool
def execute_readonly_sql(sql_query: str):
    """PostgreSQL에서 읽기 전용 SQL 쿼리를 실행합니다."""

    valid = validate_sql(sql_query);
    if not valid:
        raise ValueError("허용되지 않은 SQL 쿼리입니다. SELECT 문만 허용됩니다.")

    print("SQL 쿼리:", sql_query)
    db = SessionLocal()

    try:
        # SQL 쿼리 실행
        result = db.execute(text(sql_query)).mappings().all()

        return [dict(row) for row in result]

    except Exception as e:
        print("DB 조회 오류:", type(e).__name__, str(e))
        raise

    finally:
        db.close()        