from fastapi import FastAPI

from routers import (
    warehouse,
    # storage,
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

app.include_router(warehouse.router)
# app.include_router(storage.router)
# app.include_router(release.router)
# app.include_router(expiry.router)
# app.include_router(slot.router)
# app.include_router(dashboard.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}