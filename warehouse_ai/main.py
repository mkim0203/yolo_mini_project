# uvicorn main:app --host 0.0.0.0 --port 18000 --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    predict,
)

app = FastAPI(
    title="Warehouse ai",
    version="1.0.0",
    docs_url="/swagger"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "null"
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


app.include_router(predict.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}