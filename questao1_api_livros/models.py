from datetime import date

from database import Base
from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column


# Modelo ORM que representa a tabela "livros" no banco de dados.
# Diferente dos schemas em schemas.py (usados pela API/Pydantic), esta
# classe é usada pelo SQLAlchemy para ler e gravar dados no banco.
class Livro(Base):
    __tablename__ = "livros"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    autor: Mapped[str] = mapped_column(String(100), nullable=False)
    data_publicacao: Mapped[date] = mapped_column(Date, nullable=False)
    resumo: Mapped[str] = mapped_column(Text, nullable=False)
