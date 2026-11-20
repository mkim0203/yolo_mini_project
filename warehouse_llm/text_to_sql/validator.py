# sql 검증
import re

def validate_sql(sql: str):

    sql = sql.strip()

    # SELECT 또는 WITH만 허용
    if not re.match(r"^(SELECT|WITH)\b", sql, re.IGNORECASE):
        raise ValueError("SELECT 쿼리만 허용됩니다.")

    # 여러 SQL 문장 차단
    if ";" in sql.rstrip(";"):
        raise ValueError("여러 SQL 문장은 허용되지 않습니다.")

    # 쓰기 및 위험한 명령 차단
    forbidden = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "GRANT",
        "REVOKE"
    ]

    pattern = r"\b(" + "|".join(forbidden) + r")\b"

    if re.search(pattern, sql, re.IGNORECASE):
        raise ValueError("허용되지 않는 SQL 명령입니다.")

    return True