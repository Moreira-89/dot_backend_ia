"""Função de busca semântica sobre o índice vetorial."""

from dataclasses import dataclass

from langchain_community.vectorstores import FAISS


@dataclass(frozen=True)
class ResultadoBusca:
    titulo: str
    trecho: str
    pontuacao: float


def buscar(indice: FAISS, consulta: str, k: int = 3) -> list[ResultadoBusca]:
    """Retorna os k documentos mais relevantes pra consulta.

    A pontuação é distância L2 (via similarity_search_with_score), não
    similaridade — quanto menor, mais parecido.
    """
    resultados = indice.similarity_search_with_score(consulta, k=k)

    return [
        ResultadoBusca(
            titulo=documento.metadata["titulo"],
            trecho=documento.page_content,
            pontuacao=pontuacao,
        )
        for documento, pontuacao in resultados
    ]
