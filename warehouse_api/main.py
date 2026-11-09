# uvicorn main:app --host 0.0.0.0 --port 8000 --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    warehouse,
    slot,
    storage,
    request,
    # release,
    # expiry,
    # slot,
    # dashboard
)

app = FastAPI(
    title="Warehouse API",
    version="1.0.0",
    docs_url="/swagger"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mkim0203.github.io",
        "null"
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


app.include_router(warehouse.router)
app.include_router(slot.router)
app.include_router(storage.router)
app.include_router(request.router)
# app.include_router(release.router)
# app.include_router(expiry.router)
# app.include_router(slot.router)
# app.include_router(dashboard.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}