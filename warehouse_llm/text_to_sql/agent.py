from langchain_openai import ChatOpenAI
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from typing import Any
from config import APP_CONFIG

from log import logger

from text_to_sql.llm_tools import (
    get_database_schema,
    get_database_relationships,
    execute_readonly_sql,
    get_approved_rules
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
    get_database_schema,
    get_database_relationships,
    execute_readonly_sql,
    get_approved_rules,
    request_rule_registration
]

system_prompt = V5

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

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=checkpointer,
    middleware=[trim_old_messages]  # 2. 미들웨어 연결
)


def ask_agent(question, client_ip):
    config = {
        "configurable": {
            "thread_id": client_ip
        }
    }

    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": question}
            ]
        }, 
        config
    )

    return result["messages"][-1].content
