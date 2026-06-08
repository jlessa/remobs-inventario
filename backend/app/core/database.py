from __future__ import annotations

import ssl
from collections.abc import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(
    naming_convention=naming_convention,
    schema=settings.database_schema or None,
)


class Base(DeclarativeBase):
    metadata = metadata


def table_ref(table: str, column: str = "id") -> str:
    if settings.database_schema:
        return f"{settings.database_schema}.{table}.{column}"
    return f"{table}.{column}"


connect_args: dict[str, object] = {}
if settings.database_url.startswith(("postgresql+asyncpg://", "postgresql://")):
    connect_args["statement_cache_size"] = 0
    if settings.database_ssl_required:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_context

engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    connect_args=connect_args,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
