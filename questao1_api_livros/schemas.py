from datetime import date

from pydantic import BaseModel, ConfigDict, Field


# Schema usado para receber os dados de um livro ao criá-lo (não tem "id",
# pois quem gera o id é o banco (SQLAlchemy), não quem envia a requisição).
class LivroCreateSchema(BaseModel):
    titulo: str = Field(..., description="Titulo do livro", min_length=1, max_length=200)
    autor: str = Field(..., description="Autor do livro", min_length=1, max_length=100)
    data_publicacao: date = Field(..., description="Data de publicacao do livro")
    resumo: str = Field(..., description="Resumo do livro")

    # json_schema_extra injeta um exemplo no schema OpenAPI (Swagger),
    # apenas para documentação — não afeta a validação dos dados.
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "titulo": "O Príncipe",
                "autor": "Nicolau Maquiavel",
                "data_publicacao": "1532-10-29",
                "resumo": "Um tratado político que analisa como os governantes devem conquistar e manter o poder, introduzindo uma visão pragmática onde as ações do Estado são separadas da moral tradicional."
            }
        }
    )


# Schema usado para devolver um livro na resposta da API, já com o "id"
# preenchido (herda os demais campos de LivroCreateSchema).
class LivroResponseSchema(LivroCreateSchema):
    id: int = Field(..., description="ID do livro")

    # from_attributes=True permite criar este schema a partir de um objeto
    # (ex.: modelo do banco/ORM) e não apenas de um dict, lendo os valores
    # via atributo (objeto.campo) em vez de chave (dict["campo"]).
    model_config = ConfigDict(from_attributes=True)