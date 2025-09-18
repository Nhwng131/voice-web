from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from urllib.parse import quote_plus
from app.core.config import settings

# --- DEBUG: in cấu hình đang dùng ---
masked_pw = "*" * len(settings.DB_PASSWORD) if settings.DB_PASSWORD else "(empty)"
print("DB EFFECTIVE ->",
      f"user={settings.DB_USER}, host={settings.DB_HOST}, port={settings.DB_PORT}, db={settings.DB_NAME}, pw={masked_pw}")
db_url = f"postgresql+asyncpg://{settings.DB_USER}:{quote_plus(settings.DB_PASSWORD)}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
print("DATABASE_URL (masked) ->", db_url.replace(settings.DB_PASSWORD, "****"))
# --- END DEBUG ---

engine = create_async_engine(
    db_url, echo=False, future=True, pool_pre_ping=True
)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session