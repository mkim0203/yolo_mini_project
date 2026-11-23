import os
from dotenv import load_dotenv
from dataclasses import dataclass

if not os.getenv("DOCKER_ENV"):
    load_dotenv()

@dataclass(frozen=True)
class AppConfig:
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

    DB_HOST=os.getenv("DB_HOST")
    DB_PORT=os.getenv("DB_PORT")
    DB_DATABASE=os.getenv("DB_DATABASE")
    DB_USER=os.getenv("DB_USER")
    DB_PW=os.getenv("DB_PW")

    # RAG_EMB_MODEL=os.getenv("RAG_EMB_MODEL")

    LLM_MODEL=os.getenv("LLM_MODEL")
    LLM_TEMPERATURE=os.getenv("LLM_TEMPERATURE")
    # RAG_PROMPT_VER=os.getenv("RAG_PROMPT_VER")
    
    WAREHOUSE_API_URL=os.getenv("WAREHOUSE_API_URL")
    

    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        if not cls.DB_PW:
            raise ValueError("DB_PW가 설정되지 않았습니다.")
        
APP_CONFIG = AppConfig()

