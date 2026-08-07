from collections.abc import AsyncGenerator
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
AsyncSession,
async_sessionmaker,
create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings
settings.db_data_dir
async_engine = create_async_engine(
settings.DATABASE_URL,
echo=False,
connect_args={
"check_same_thread": False,
"timeout": 30,
},
)
@event.listens_for(async_engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-32000")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
class Base(DeclarativeBase):
    pass
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
async def create_all_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
