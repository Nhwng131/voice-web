from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base

from app.api.routes_auth import router as auth_router
from app.api.routes_users import router as users_router

app = FastAPI(title="FastAPI + PostgreSQL + JWT")

@app.on_event("startup")
async def on_startup():
    # import models để metadata đầy đủ
    import app.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth_router)
app.include_router(users_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
