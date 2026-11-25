from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from text_to_sql.agent_service import ask_agent
from log import logger

router = APIRouter(
    prefix="",
    tags=["Text-to-SQL"]
)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str


@router.post("/ask", response_model=AskResponse)
def ask(base_request: Request, request: AskRequest):

    try:
        ip=base_request.client.host
        logger.info(f"{ip} => {request.question}")
        answer = ask_agent(request.question, ip)
        

        logger.info(answer)
        return AskResponse(
            question=request.question,
            answer=answer
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )