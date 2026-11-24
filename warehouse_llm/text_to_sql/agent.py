from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from config import APP_CONFIG

from text_to_sql.llm_tools import (
    get_database_schema,
    get_database_relationships,
    execute_readonly_sql,
    get_approved_rules
)

from text_to_sql.request_api import request_rule_registration

from text_to_sql.prompt import V1, V2, V3, V4

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

system_prompt = V4

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)


def ask_agent(question, client_ip):
    # Short-term Memory 사용하여 현재 대화의 질문과 답변 기억, 대화 세션별로 저장함
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