#from langgraph.prebuilt import create_react_agent   # 버전에 따라 langchain.agents.create_agent
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from typing import Any
from config import APP_CONFIG


from text_to_sql.llm_tools import (
    execute_readonly_sql
)
from text_to_sql.request_api import request_rule_registration
from text_to_sql.prompt import V1, V2, V3, V4, V5

llm = ChatOpenAI(
    model=APP_CONFIG.LLM_MODEL,
    temperature=APP_CONFIG.LLM_TEMPERATURE,
    timeout=30,
    max_retries=1
)

tools = [
    execute_readonly_sql
]


DATA_PROMPT = """당신은 창고 관리 시스템(WMS) 데이터를 조회·분석하는 AI 에이전트입니다.

[작업 규칙]
1. 데이터 질문은 반드시 execute_readonly_sql로 조회한 결과에 근거해 답하세요.
   룰 내용을 데이터 조회 결과 대신 답변으로 출력하지 마세요.
2. 아래 [적용 중인 룰]은 SQL 작성과 답변 가공 방식을 정하는 지침입니다.
   조회하는 테이블이 룰의 대상 테이블에 포함되거나 대상이 '전체'인 룰만 적용하세요.
3. 사용자가 룰/규칙 자체를 물으면 [적용 중인 룰]을 정리해서 답하세요. (SQL 불필요)
4. 용어: 적재 요청=storage_request, 출고 요청=release_request,
   현재 적재 중인 물품=storage_info, 적재 이력=storage_history.
   "적재 요청 ID: N"은 storage_request.request_id = N 입니다.
5. SELECT만 사용하세요. SELECT * 는 쓰지 말고, 이미지 데이터(image_data)는 요청이 없으면 조회하지 마세요.
6. 조회 결과가 0건이면 "조건에 해당하는 데이터가 없습니다"라고 답하고,
   SQL 오류가 나면 원인을 간단히 설명하세요.
7. 요청 유형(적재/출고)이 불분명하면 추측하지 말고 되물으세요.
8. 룰을 추가/변경해 달라는 요청은 여기서 처리하지 말고,
   "'앞으로 ~해줘' 형태로 요청해 주세요"라고 안내하세요.

[적용 중인 룰]
{rules}

[DB 스키마]
{schema}
"""


# 1. 유지할 최근 메시지 개수 설정 (예: 최근 10개 메시지)
KEEP_LAST_N = 10

@before_model
def trim_old_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    #logger.info(state)
    messages = state["messages"]

    # 전체 메시지가 설정한 개수 이하면 아무것도 하지 않음
    if len(messages) <= KEEP_LAST_N:
        return None

    # 최근 N개 메시지 추출
    recent_messages = messages[-KEEP_LAST_N:]

    # [중요] 잘린 지점의 첫 메시지가 ToolMessage나 AI의 tool_calls 응답이면 
    # OpenAI API 규격 오류(짝 불일치)가 나므로, 가장 가까운 HumanMessage(사용자 질문)부터 시작하도록 보정
    while recent_messages and recent_messages[0].type != "human":
        recent_messages.pop(0)

    # 보정 후 남는 메시지가 없다면 초기화 방지
    if not recent_messages:
        return None

    # 기존 메시지를 모두 지우고 보정된 최근 메시지들만 다시 저장
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *recent_messages
        ]
    }


checkpointer = InMemorySaver()

def format_rules(rules: list[dict]) -> str:
    if not rules:
        return "(없음)"
    return "\n".join(
        f"- [{r['rule_name']}] 대상: {r['target_tables'] or '전체'} / {r['rule_content']}"
        for r in rules
    )


def format_schema(rows: list[dict]) -> str:
    """rows: table_name, column_name, data_type, is_nullable, table_comment, column_comment"""
    tables: dict[str, list[str]] = {}
    for r in rows:
        if r["data_type"] == "bytea":          # 이미지 바이너리 컬럼은 프롬프트에서 제외
            continue
        head = f"[{r['table_name']}] {r['table_comment']}"
        tables.setdefault(head, []).append(
            f"  - {r['column_name']} ({r['data_type']}): {r['column_comment']}"
        )
    return "\n".join(h + "\n" + "\n".join(cols) for h, cols in tables.items())


def run_data_agent(question: str, session_id: str, rules: list[dict], schema_rows: list[dict]) -> str:
    agent = create_agent(
        model=llm,
        tools=tools,                     # 조회 Tool만. 등록/룰조회/스키마 Tool 제거
        system_prompt=DATA_PROMPT.format(rules=format_rules(rules), schema=format_schema(schema_rows)),
        checkpointer=checkpointer,                        # 기존 checkpointer 재사용 (모듈 전역)
        middleware=[trim_old_messages]  # 2. 미들웨어 연결
    )
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        {"configurable": {"thread_id": session_id}},
    )
    return result["messages"][-1].content