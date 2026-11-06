import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass(frozen=True)
class AppConfig:
    DB_HOST=os.getenv("DB_HOST")
    DB_PORT=os.getenv("DB_PORT")
    DB_DATABASE=os.getenv("DB_DATABASE")
    DB_USER=os.getenv("DB_USER")
    DB_PW=os.getenv("DB_PW")

    RAG_EMB_MODEL=os.getenv("RAG_EMB_MODEL")

    RAG_LLM_MODEL=os.getenv("RAG_LLM_MODEL")
    RAG_LLM_TEMPERATURE=os.getenv("RAG_LLM_TEMPERATURE")
    RAG_PROMPT_VER=os.getenv("RAG_PROMPT_VER")
    
    

    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        if not cls.RAG_DB_PW:
            raise ValueError("RAG_DB_PW가 설정되지 않았습니다.")
        
APP_CONFIG = AppConfig()


if __name__ == "__main__":
    print(APP_CONFIG.DB_HOST)
    print(APP_CONFIG.RAG_EMB_MODEL)