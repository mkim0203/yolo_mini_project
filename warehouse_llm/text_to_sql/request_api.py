import httpx
from langchain.tools import tool
from config import APP_CONFIG

WAREHOUSE_API_URL = APP_CONFIG.WAREHOUSE_API_URL


@tool
def request_rule_registration(
    rule_name: str,
    category: str,
    target_tables: list[str],
    rule_content: str
):
    """
    새로운 비즈니스 룰 등록을 요청합니다.

    Args:
        rule_name: 규칙의 목적을 명확하게 표현한 이름
        category: 규칙 분류
        target_tables: 규칙이 적용되는 실제 DB 테이블명 목록
        rule_content: 사용자가 요청한 규칙의 구체적인 내용.
            반드시 규칙의 조건, 적용 기준, 처리 방법을 상세하게 작성합니다.
            "새로운 비즈니스 룰 등록이 필요합니다."와 같은
            일반적인 안내 문구를 입력하면 안 됩니다.

    신규 등록된 룰은 pending 상태로 저장되며
    관리자 승인이 필요합니다.
    """

    payload = {
        "rule_name": rule_name,
        "category": category,
        "target_tables": target_tables,
        "rule_content": rule_content
    }

    try:
        response = httpx.post(
            f"{WAREHOUSE_API_URL}/business-rules",
            json=payload,
            timeout=10.0
        )

        response.raise_for_status()

        return {
            "success": True,
            "message": "룰 등록 요청이 완료되었습니다. 관리자 승인이 필요합니다.",
            "data": response.json()
        }

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "message": f"룰 등록 API 오류: HTTP {e.response.status_code}"
        }

    except httpx.RequestError:
        return {
            "success": False,
            "message": "warehouse_api에 연결할 수 없습니다."
        }