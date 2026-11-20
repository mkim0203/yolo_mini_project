-- read_llm 권한 부여
-- 스키마 및 get_db_table_relationships 테이블이 조회 안될경우 아래 권한 부여 진행


GRANT USAGE ON SCHEMA public TO read_llm;

GRANT SELECT ON ALL TABLES
IN SCHEMA public
TO read_llm;	