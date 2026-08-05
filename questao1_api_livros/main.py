from contextlib import asynccontextmanager

from database import Base, sql_lite_engine
from fastapi import FastAPI
from routers.endpoints_livros import router as livros_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas no banco de dados (se ainda não existirem).
    async with sql_lite_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # Aqui o FastAPI processa as requisições normalmente.

    await sql_lite_engine.dispose()  # Fecha o engine do SQLAlchemy ao final da aplicação.


app = FastAPI(
    title="API de Livros",
    description="API para gerenciar livros, permitindo criar e listar livros.",
    version="1.0.0",
    lifespan=lifespan,  # Registra o gerenciador de contexto de vida
)


# Registra as rotas de livros (POST/GET em /livros) definidas no router.
app.include_router(livros_router)