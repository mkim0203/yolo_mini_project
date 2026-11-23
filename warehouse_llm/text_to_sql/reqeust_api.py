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
    새로운 비즈니스 룰 등록을 warehouse_api에 요청합니다.

    신규 업무 규칙이 필요하다고 판단되는 경우 사용합니다.
    등록된 룰은 pending 상태로 저장되며 관리자 승인이 필요합니다.
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