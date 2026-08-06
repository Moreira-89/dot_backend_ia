from database import get_async_session
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models import Livro
from schemas import LivroCreateSchema, LivroResponseSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/livros", tags=["Livros"])


@router.post(
    "/",
    response_model=LivroResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar um novo livro",
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Já existe um livro cadastrado com o mesmo título e autor."
        }
    },
)
async def criar_livro(
    livro: LivroCreateSchema, session: AsyncSession = Depends(get_async_session)
):
    """Cadastra um livro novo a partir de título, autor, data de publicação e resumo.

    Retorna o registro criado, já com o `id` gerado pelo banco. Rejeita com
    `409 Conflict` se já existir um livro com o mesmo título e autor.
    """
    # Impede cadastro duplicado do mesmo título+autor.
    # OBS: checagem em duas etapas (SELECT depois INSERT) — sob concorrência
    # (duas requisições simultâneas para o mesmo livro), ainda é possível
    # criar duplicatas, pois nada garante a unicidade no nível do banco.
    # Uma UniqueConstraint(titulo, autor) no model seria a forma robusta.
    query = select(Livro).where(
        Livro.titulo == livro.titulo, Livro.autor == livro.autor
    )
    result = await session.execute(query)
    livro_existente = result.scalar_one_or_none()

    if livro_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"O livro '{livro.titulo}' do autor '{livro.autor}' já foi cadastrado.",
        )

    novo_livro = Livro(**livro.model_dump())
    session.add(novo_livro)
    await session.commit()
    await session.refresh(novo_livro)  # Recarrega o objeto para trazer o "id" gerado.
    return novo_livro


@router.get(
    "/",
    response_model=list[LivroResponseSchema],
    summary="Consultar livros por título e/ou autor",
)
async def listar_livros(
    titulo: str | None = Query(
        default=None, description="Filtra por título (busca parcial, case-insensitive)."
    ),
    autor: str | None = Query(
        default=None, description="Filtra por autor (busca parcial, case-insensitive)."
    ),
    session: AsyncSession = Depends(get_async_session),
):
    """Lista os livros cadastrados.

    Sem parâmetros, retorna todos os livros. Se `titulo` e/ou `autor` forem
    informados, filtra por correspondência parcial (`ILIKE %valor%`) em cada
    um; quando os dois são informados, os filtros são combinados com `AND`.
    """
    query = select(Livro)
    if titulo is not None:
        query = query.where(Livro.titulo.ilike(f"%{titulo}%"))
    if autor is not None:
        query = query.where(Livro.autor.ilike(f"%{autor}%"))
    result = await session.execute(query)
    return result.scalars().all()