"""Construção do índice vetorial (FAISS) a partir dos documentos fixos.

O índice é reconstruído a cada execução do programa: dado o volume pequeno de documentos fixos, o custo de reprocessar os embeddings é aceitável e evita a complexidade extra de salvar/carregar o índice do disco.
"""

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from questao3_busca_semantica.documentos import DOCUMENTOS

EMBEDDING_MODEL = "text-embedding-3-small"


def construir_indice() -> FAISS:
    """Gera embeddings para os documentos fixos e monta o índice FAISS.

    Cada `Documento` vira um `Document` do LangChain, guardando o título no
    metadata (`titulo`) para que a busca possa exibi-lo junto do trecho de
    conteúdo relevante.
    """
    documentos_langchain = [
        Document(page_content=documento.conteudo, metadata={"titulo": documento.titulo})
        for documento in DOCUMENTOS
    ]

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    return FAISS.from_documents(documentos_langchain, embeddings)
