"""Função de busca semântica sobre o índice vetorial."""

from dataclasses import dataclass

from langchain_community.vectorstores import FAISS


@dataclass(frozen=True)
class ResultadoBusca:
    titulo: str
    trecho: str
    pontuacao: float


def buscar(indice: FAISS, consulta: str, k: int = 3) -> list[ResultadoBusca]:
    """Retorna os `k` documentos mais relevantes para `consulta`.

    Usa `similarity_search_with_score`, que gera o embedding da consulta e
    calcula a distância L2 entre ele e os embeddings dos documentos
    indexados: quanto menor a pontuação, mais similar (mais relevante) o
    documento é em relação à consulta.
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
