# Questão 3 — Busca Semântica com Vector Stores e Embeddings

Sistema de busca semântica sobre um conjunto fixo de documentos, usando embeddings da OpenAI e um índice vetorial FAISS.

## Enunciado

> Você deve criar um sistema de busca semântica de documentos utilizando embeddings e
> vector stores. Para isso, siga as etapas abaixo:
>
> 1. Utilize um conjunto de documentos de texto (pode ser um conjunto de artigos ou
>    posts de um blog).
> 2. Gere embeddings para esses documentos utilizando um modelo de embeddings.
> 3. Armazene esses embeddings em uma vector store como FAISS ou Milvus.
> 4. Implemente uma função de busca que, dado um texto de consulta, retorne os
>    documentos mais relevantes com base na similaridade semântica.

## Stack

| Camada | Tecnologia |
|---|---|
| Modelo de embeddings | OpenAI `text-embedding-3-small`, via `langchain-openai` |
| Vector store | [FAISS](https://faiss.ai/) (`faiss-cpu`), via `langchain-community` |
| Variáveis de ambiente | `python-dotenv` |
| Saída no terminal | [`rich`](https://rich.readthedocs.io/) (`Console` + `Table`) |

## Decisões de projeto

Os documentos são fixos, embutidos em `documentos.py`, em vez de raspados de um blog real — o enunciado permite qualquer conjunto de textos, e usar algo fixo evita que o exercício dependa de internet ou de uma página que pode mudar de conteúdo (ou sair do ar) depois de entregue.

Pra embeddings, usei o `text-embedding-3-small` da OpenAI. Já tinha chave e integração configuradas por causa da Questão 2, então não fazia sentido puxar `torch`/`sentence-transformers` só pra essa etapa — o enunciado cita `transformers` como sugestão, não como exigência.

FAISS entra porque o próprio enunciado já dá as duas opções (FAISS ou Milvus), e FAISS roda local, sem precisar subir infraestrutura via Docker como o Milvus pede. Pra um teste técnico, isso poupa tempo de setup sem abrir mão do que o enunciado pede.

O índice é reconstruído a cada execução, sem salvar em disco. Com 8 documentos o reprocessamento é instantâneo, então não valia a pena a complexidade extra do `save_local`/`load_local` do FAISS.

Vale registrar que `similarity_search_with_score` do FAISS retorna distância L2, não similaridade de cosseno — então, ao contrário do que a intuição sugere, quanto **menor** a pontuação, mais relevante o resultado (é assim que a coluna "Distância" nos exemplos abaixo deve ser lida).

## Estrutura de arquivos

```
questao3_busca_semantica/
├── documentos.py       # Conjunto fixo de documentos (Documento: titulo + conteudo)
├── indexador.py        # construir_indice(): gera embeddings e monta o índice FAISS
├── busca.py            # buscar(): função de busca semântica (ResultadoBusca)
├── main.py             # Ponto de entrada: constrói o índice e roda consultas de exemplo
└── .env.example         # Modelo de variáveis de ambiente (OPENAI_API_KEY)
```

Sem testes automatizados neste exercício, mesma decisão da Questão 2 — `buscar()` e `construir_indice()` ficaram como funções isoladas justamente pra dar pra testar depois, se precisar.

## Como funciona

`documentos.py` define `DOCUMENTOS`, uma lista de 8 posts curtos sobre temas técnicos bem distintos entre si (Python, POO, banco de dados, APIs REST, embeddings, ambientes virtuais, testes, Docker). A ideia de misturar temas tão diferentes é forçar a busca a diferenciar coisas que até compartilham palavras — "lista" e "índice", por exemplo, os dois remetem a "dados", mas são assuntos bem separados.

`indexador.py` transforma cada `Documento` num `Document` do LangChain (o texto vira `page_content`, o título vai pro `metadata`) e monta o índice:

```python
def construir_indice() -> FAISS:
    documentos_langchain = [
        Document(page_content=documento.conteudo, metadata={"titulo": documento.titulo})
        for documento in DOCUMENTOS
    ]
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return FAISS.from_documents(documentos_langchain, embeddings)
```

`busca.py` expõe `buscar()`, que embrulha o `similarity_search_with_score` do FAISS numa lista de `ResultadoBusca` (título, trecho, pontuação) — assim quem chama não precisa lidar com os objetos internos do LangChain:

```python
def buscar(indice: FAISS, consulta: str, k: int = 3) -> list[ResultadoBusca]:
    resultados = indice.similarity_search_with_score(consulta, k=k)
    return [
        ResultadoBusca(titulo=doc.metadata["titulo"], trecho=doc.page_content, pontuacao=pontuacao)
        for doc, pontuacao in resultados
    ]
```

`main.py` valida a `OPENAI_API_KEY` antes de importar qualquer coisa que dependa dela (mesmo guard da Questão 2), constrói o índice uma vez e roda uma lista de consultas de exemplo, imprimindo os 3 resultados mais relevantes de cada uma numa tabela `rich`. As consultas de exemplo usam palavras diferentes das dos documentos — "coleção de dados" em vez de "lista", "tabela grande" em vez de "índice" — justamente pra mostrar que a busca funciona por significado, não por bater palavra-chave.

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `OPENAI_API_KEY` | sim | Chave de API da OpenAI, usada por `langchain-openai` para gerar os embeddings (`text-embedding-3-small`). |

Configuração local: copiar `.env.example` para `.env` e preencher a chave. O `.env` já está no `.gitignore` da raiz — nunca é versionado.

## Como rodar

```bash
# Na raiz do repositório (dot_backend_ia/)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Configurar a chave da OpenAI
cp questao3_busca_semantica/.env.example questao3_busca_semantica/.env
# edite questao3_busca_semantica/.env e informe OPENAI_API_KEY

# Executar como módulo, a partir da raiz do repositório
.venv/bin/python -m questao3_busca_semantica.main
```

## Exemplos de consulta e resultados

Saída real de `python -m questao3_busca_semantica.main`, com os 3 documentos mais relevantes de cada consulta (lembrando: distância menor = mais relevante). Nas 5 consultas o documento certo ficou em primeiro, mesmo sem repetir o vocabulário do texto original.

### 1. "Como faço para adicionar um elemento em uma coleção de dados em Python?"

| # | Documento | Distância |
|---|---|---|
| 1 | Listas em Python | 0.7993 |
| 2 | Programação Orientada a Objetos em Python | 1.2175 |
| 3 | Testes Automatizados com pytest | 1.4058 |

### 2. "O que é herança em classes?"

| # | Documento | Distância |
|---|---|---|
| 1 | Programação Orientada a Objetos em Python | 1.1777 |
| 2 | Índices em Bancos de Dados Relacionais | 1.4459 |
| 3 | Modelos de Linguagem e Embeddings | 1.4887 |

### 3. "Como acelerar consultas em uma tabela grande?"

| # | Documento | Distância |
|---|---|---|
| 1 | Índices em Bancos de Dados Relacionais | 0.8222 |
| 2 | Introdução a APIs REST | 1.5466 |
| 3 | Docker e Containers para Desenvolvimento | 1.5583 |

### 4. "O que são vetores que representam o significado de um texto?"

| # | Documento | Distância |
|---|---|---|
| 1 | Modelos de Linguagem e Embeddings | 0.7926 |
| 2 | Índices em Bancos de Dados Relacionais | 1.4047 |
| 3 | Listas em Python | 1.5188 |

### 5. "Como isolar as dependências de um projeto?"

| # | Documento | Distância |
|---|---|---|
| 1 | Gerenciamento de Ambientes Virtuais em Python | 0.8505 |
| 2 | Docker e Containers para Desenvolvimento | 1.0281 |
| 3 | Testes Automatizados com pytest | 1.4180 |

## Limitações conhecidas

`k` fica fixo em 3 nas consultas de exemplo, embora `buscar()` aceite qualquer valor. E, como já comentei, o índice não persiste em disco — numa base de documentos maior isso teria que mudar, com o índice sendo salvo e atualizado incrementalmente em vez de reconstruído do zero a cada execução.

---

⬅ [Questão 2 — Chatbot com LangChain](questao2_chatbot_langchain.md)
