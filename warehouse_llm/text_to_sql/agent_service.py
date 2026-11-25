from text_to_sql.llm_tools import get_db_schema, get_db_table_relationships, get_db_business_rules
from text_to_sql.request_api import request_rule_registration
from text_to_sql.rule_flow import classify_intent, draft_rule, format_proposal
from text_to_sql.data_agent import format_rules, run_data_agent
from log import logger

pending_rules: dict[str, dict] = {}   # session_id -> RuleDraft(dict). 운영에서는 DB/Redis 권장

def _normalize(text: str) -> str:
    return text.strip().strip("'\"“”‘’.").strip()


def ask_agent(question: str, client_ip: str) -> str:
    session_id = client_ip

    # ① 승인: LLM을 거치지 않고 코드로 처리
    if _normalize(question) == "등록 승인":
        draft = pending_rules.pop(session_id, None)
        if draft is None:
            return "승인할 대기 중인 비즈니스 룰 제안이 없습니다."
        try:
            #register_business_rule_impl(draft)   # 기존 등록 Tool 내부 로직을 일반 함수로 호출
            request_rule_registration(**draft)
        except Exception as e:
            pending_rules[session_id] = draft    # 실패 시 다시 승인할 수 있도록 복구
            return f"룰 등록에 실패했습니다. 사유: {e}"
        return "룰 등록이 접수되었습니다. 관리자 승인 후 적용됩니다."

    #rules = fetch_active_rules()                 # 기존 get_approved_rules 내부 로직 (status=approved, is_active=Y)
    #schema_rows = fetch_schema_rows()            # 기존 get_database_schema 내부 로직 (캐시 가능)
    rules = get_db_business_rules()
    schema_rows = get_db_schema()

    result_classify = classify_intent(question, has_pending=session_id in pending_rules)
    logger.info(result_classify)
    # ② 룰 변경 요청: 초안만 작성하고 서버에 저장
    if result_classify == "rule_change":
        draft = draft_rule(question, format_rules(rules), pending_rules.get(session_id))
        pending_rules[session_id] = draft.model_dump()
        return format_proposal(draft)

    # ③ 그 외: 조회 에이전트
    return run_data_agent(question, session_id, rules, schema_rows)