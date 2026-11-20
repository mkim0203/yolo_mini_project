from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from text_to_sql.agent import ask_agent

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
def ask(request: AskRequest):

    try:
        answer = ask_agent(request.question)

        return AskResponse(
            question=request.question,
            answer=answer
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )