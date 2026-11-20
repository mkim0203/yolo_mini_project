# uvicorn main:app --host 192.168.0.2 --port 28000 --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import APP_CONFIG
APP_CONFIG.validate()

from routers import (
    ask,
    
)



app = FastAPI(
    title="Warehouse LLM API",
    version="1.0.0",
    docs_url="/swagger"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mkim0203.github.io",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "null"
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)



app.include_router(ask.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}