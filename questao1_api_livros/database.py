from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./banco.db"


# Classe base da qual todos os modelos (tabelas) devem herdar.
class Base(DeclarativeBase):
    pass


sql_lite_engine = create_async_engine(
    url=DATABASE_URL,
    echo=True,  # Loga o SQL executado no console; útil para debug.
    connect_args={"check_same_thread": False},  # Necessário para SQLite
)

# Fábrica de sessões assíncronas ligada ao engine acima.
AsyncSessionLocal = async_sessionmaker(
    bind=sql_lite_engine, expire_on_commit=False, class_=AsyncSession
)


# Dependency do FastAPI: abre uma sessão por requisição e garante
# que ela seja fechada automaticamente ao final (via "async with").
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
