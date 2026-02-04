"""Main FastAPI application entry point."""
from fastapi import FastAPI

from app.api.routers import (
    accounts_router,
    admin_router,
    auth_router,
    payments_router,
    users_router,
)

app = FastAPI(
    title="Payment Service API", description="A simple payment system", version="1.0.0"
)


app.include_router(accounts_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(payments_router)
app.include_router(users_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
