from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from config import APP_CONFIG

from text_to_sql.llm_tools import (
    get_database_schema,
    get_database_relationships,
    execute_readonly_sql
)

llm = ChatOpenAI(
    model=APP_CONFIG.LLM_MODEL,
    temperature=APP_CONFIG.LLM_TEMPERATURE
)

tools = [
    get_database_schema,
    get_database_relationships,
    execute_readonly_sql
]

system_prompt = """
당신은 PostgreSQL 데이터 분석 전문가입니다.

규칙:
1. 사용자의 질문을 SQL로 변환합니다.
2. SQL 실행 전에 반드시 get_database_schema Tool을 호출합니다.
3. 조회 가능한 테이블과 컬럼만 사용합니다.
4. 테이블 연결은 PK/FK 관계를 참고합니다.
5. SELECT 쿼리만 생성합니다.
6. SQL 실행 결과를 근거로 답변합니다.
7. 조회 결과에 없는 내용은 추측하지 않습니다.
8. SELECT * 사용을 금지합니다.
9. 사용자 질문에 답변하는 데 필요한 컬럼만 SELECT 절에 명시합니다.
10. image_data 컬럼은 이미지 확인 요청이 명시적으로 있는 경우에만 SELECT 절에 포함합니다.
11. 이미지 확인 요청이 아닌 경우 image_data 컬럼은 어떤 형태로든 조회하지 않습니다.
12. 대용량 데이터 컬럼은 별도 요청이 없는 한 조회하지 않습니다.
"""

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)


def ask_agent(question):

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    return result["messages"][-1].content