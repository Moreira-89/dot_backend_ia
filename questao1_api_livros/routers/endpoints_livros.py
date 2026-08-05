from database import get_async_session
from fastapi import APIRouter, Depends
from models import Livro
from schemas import LivroCreateSchema, LivroResponseSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/livros", tags=["Livros"])


# Cria um livro novo a partir do payload validado por LivroCreateSchema e
# devolve o registro já com o "id" gerado pelo banco (LivroResponseSchema).
@router.post("/", response_model=LivroResponseSchema, status_code=201)
async def criar_livro(
    livro: LivroCreateSchema, session: AsyncSession = Depends(get_async_session)
):
    novo_livro = Livro(**livro.model_dump())
    session.add(novo_livro)
    await session.commit()
    await session.refresh(novo_livro)  # Recarrega o objeto para trazer o "id" gerado.
    return novo_livro


# Lista os livros cadastrados, com filtros opcionais e case-insensitive
# (ilike) por título e/ou autor via query params.
@router.get("/", response_model=list[LivroResponseSchema])
async def listar_livros(
    titulo: str | None = None,
    autor: str | None = None,
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Livro)
    if titulo is not None:
        query = query.where(Livro.titulo.ilike(f"%{titulo}%"))
    if autor is not None:
        query = query.where(Livro.autor.ilike(f"%{autor}%"))
    result = await session.execute(query)
    return result.scalars().all()