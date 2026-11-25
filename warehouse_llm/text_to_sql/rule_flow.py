# 룰 변경 요청 판별과 초안 작성

from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from config import APP_CONFIG

#small_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # 모델명은 사용 중인 것으로
small_llm = ChatOpenAI(
    model=APP_CONFIG.LLM_MODEL,
    temperature=APP_CONFIG.LLM_TEMPERATURE,
    timeout=30,
    max_retries=1
)


class Intent(BaseModel):
    intent: Literal["rule_change", "other"] = Field(
        description=(
            "rule_change: 사용자가 '앞으로의' 시스템 동작/규칙을 추가·변경·삭제하라고 명시적으로 지시하거나, "
            "대기 중인 룰 제안을 수정해 달라고 하는 경우. "
            "other: 데이터 조회, 룰 조회, '이번 결과만' 다시 계산해 달라는 요청 등 그 외 모두. "
            "애매하면 other."
        )
    )


class RuleDraft(BaseModel):
    rule_name: str = Field(description="핵심 기능을 요약한 룰 이름")
    category: Literal["BUSINESS"] = "BUSINESS"
    target_tables: list[str] = Field(description="전체 공통 규칙이면 [], 특정 테이블 한정이면 [\"테이블명\"]")
    rule_content: str = Field(description="AI가 이후 SQL 작성/답변 가공 시 따를 구체적 지침. SELECT 조회 범위 내에서만 작성")


def classify_intent(question: str, has_pending: bool) -> str:
    try:
        r = small_llm.with_structured_output(Intent).invoke(
            f"대기 중인 룰 제안 존재 여부: {has_pending}\n사용자 메시지: {question}"
        )
        return r.intent
    except Exception:
        return "other"  # 실패 시 안전한 쪽(조회)으로


def draft_rule(question: str, rules_text: str, pending: dict | None) -> RuleDraft:
    prompt = (
        "WMS 비즈니스 룰 초안을 작성하세요.\n"
        f"[이미 적용 중인 룰]\n{rules_text}\n\n"
        f"[대기 중인 제안(있다면 수정 요청일 수 있음)]\n{pending}\n\n"
        f"[사용자 요청]\n{question}\n\n"
        "기존 룰과 동일하면 그 룰의 target_tables만 확장하는 형태로 작성하세요."
    )
    return small_llm.with_structured_output(RuleDraft).invoke(prompt)


def format_proposal(d: RuleDraft) -> str:
    return (
        "비즈니스 룰 등록을 위해 다음과 같은 내용을 제안합니다:\n\n"
        f"* **룰 이름:** {d.rule_name}\n"
        f"* **카테고리:** {d.category}\n"
        f"* **대상 테이블:** {d.target_tables}\n"
        f"* **룰 내용:** {d.rule_content}\n\n"
        "위 내용대로 등록을 원하시면 **'등록 승인'**이라고 입력해 주세요."
    )