"""Monta o índice FAISS a partir dos documentos fixos.

Reconstrói tudo a cada execução — com poucos documentos, não compensa a
complexidade de salvar/carregar o índice do disco.
"""

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from questao3_busca_semantica.documentos import DOCUMENTOS

EMBEDDING_MODEL = "text-embedding-3-small"


def construir_indice() -> FAISS:
    """Gera os embeddings e monta o índice FAISS.

    Título vai pro metadata do Document, só pra dar pra mostrar na busca depois.
    """
    documentos_langchain = [
        Document(page_content=documento.conteudo, metadata={"titulo": documento.titulo})
        for documento in DOCUMENTOS
    ]

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    return FAISS.from_documents(documentos_langchain, embeddings)
