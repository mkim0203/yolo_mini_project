from langchain.tools import tool
from sqlalchemy import text
from database.connection import SessionLocal
from text_to_sql.validator import validate_sql
import json
from log import logger

MAX_ROWS = 50         # LLM에게 넘길 최대 행 수
MAX_CHARS = 12000     # LLM에게 넘길 최대 글자 수 (한글/영문 혼합 기준 약 4,000~6,000 토큰 수준)

def get_db_schema(db = SessionLocal()):

    query = text("""
        SELECT
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            pg_catalog.obj_description(
                (quote_ident(c.table_schema) || '.' ||
                quote_ident(c.table_name))::regclass,
                'pg_class'
            ) AS table_comment,
            pg_catalog.col_description(
                (quote_ident(c.table_schema) || '.' ||
                quote_ident(c.table_name))::regclass,
                c.ordinal_position
            ) AS column_comment
        FROM information_schema.columns c
        WHERE c.table_schema = 'public'
        ORDER BY c.table_name, c.ordinal_position;
    """)

    rows = db.execute(query).mappings().all()

    return [dict(row) for row in rows]

def get_db_table_relationships(db = SessionLocal()):
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

def get_db_business_rules(db = SessionLocal()):
    query = text("""
        SELECT
            rule_id,
            rule_name,
            category,
            target_tables,
            rule_content
        FROM business_rules
        WHERE status = 'approved'
        AND is_active = 'Y'
        ORDER BY rule_id
    """)

    rows = db.execute(query).mappings().all()

    result = [dict(row) for row in rows]

    return result

@tool
def get_database_schema():
    """
    wharehouse 데이터베이스의 현재 테이블과 컬럼 구조를 조회합니다.
    """
    print("get_database_schema 호출됨")
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
    """
    wharehouse 데이터베이스의 현재 테이블 간 관계를 조회합니다.
    """
    print("get_database_relationships 호출됨")
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
    """wharehouse 데이터베이스에서 읽기 전용 SQL 쿼리를 실행합니다."""

    valid = validate_sql(sql_query);
    if not valid:
        return "허용되지 않은 SQL 쿼리입니다. SELECT 문만 허용됩니다."

    print("SQL 쿼리:", sql_query)
    db = SessionLocal()

    try:
        # SQL 쿼리 실행
        rows = db.execute(text(sql_query)).mappings().all()


        total_count = len(rows)

        logger.info(total_count)
        
        if total_count == 0:
            return "조회된 데이터가 없습니다."

        # 1. 행(Row) 개수 제한
        is_truncated = False
        if total_count > MAX_ROWS:
            rows = rows[:MAX_ROWS]
            is_truncated = True

        # 2. 결과 직렬화 및 전체 글자 수(토큰 폭발 방지) 제한
        result_str = json.dumps(rows, ensure_ascii=False, default=str)
        
        if len(result_str) > MAX_CHARS:
            result_str = result_str[:MAX_CHARS] + "...(데이터 길이 초과로 일부 생략됨)"
            is_truncated = True

        # 3. 잘렸을 경우 LLM이 인지하고 사용자에게 안내할 수 있도록 메타 정보 추가
        if is_truncated:
            notice = f"\n\n[시스템 안내: 전체 {total_count}건 중 토큰 제한으로 인해 상위 일부({len(rows)}건)만 표시되었습니다. 전체 통계가 필요하면 COUNT, SUM, GROUP BY 등 집계 쿼리를 사용하세요.]"
            return result_str + notice

        return result_str

    except Exception as e:
        print("DB 조회 오류:", type(e).__name__, str(e))
        # 오류 발생시 오류 메시지 llm에 전달하도록함.
        return f"DB 조회 오류: {type(e).__name__}, {str(e)}"

    finally:
        db.close()        


@tool
def get_approved_rules():
    """
    승인되고 활성화된 비즈니스 룰을 조회합니다.
    SQL 생성 및 데이터 분석 시 업무 규칙을 확인하기 위해 사용합니다.
    """
    print("get_approved_rules 호출됨")
    db = SessionLocal()

    try:
        result = get_db_business_rules(db)

        if not result:
            return {
                "success": True,
                "count": 0,
                "rules": []
            }

        return {
            "success": True,
            "count": len(result),
            "rules": result
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"비즈니스 룰 조회 실패: {str(e)}"
        }

    finally:
        db.close()