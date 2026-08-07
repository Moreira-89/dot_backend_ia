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

| Decisão | Escolha | Justificativa |
|---|---|---|
| Fonte dos documentos | Fixos, embutidos no repositório (não scraping externo) | Reprodutibilidade — o avaliador roda sem depender de internet/estrutura de site externo, que pode mudar ou cair. |
| Modelo de embeddings | OpenAI `text-embedding-3-small` | Já havia integração e chave de API configurada na Questão 2; evita dependência pesada (`torch`/`sentence-transformers`) só para uma etapa do teste. O enunciado sugere `transformers` como dica, não obrigação. |
| Vector store | FAISS | Citado explicitamente no enunciado ("FAISS ou Milvus"); é biblioteca local (sem servidor), mais simples de rodar que Milvus (que exige infraestrutura via Docker) — adequado ao escopo de um teste técnico. |
| Persistência do índice | Reconstruído a cada execução (não salvo em disco) | Volume pequeno de documentos fixos torna o custo de reprocessamento aceitável; evita a complexidade extra de salvar/carregar o índice do FAISS do disco. |

## Estrutura de arquivos

```
questao3_busca_semantica/
├── documentos.py       # Conjunto fixo de documentos (Documento: titulo + conteudo)
├── indexador.py        # construir_indice(): gera embeddings e monta o índice FAISS
├── busca.py            # buscar(): função de busca semântica (ResultadoBusca)
├── main.py             # Ponto de entrada: constrói o índice e roda consultas de exemplo
└── .env.example         # Modelo de variáveis de ambiente (OPENAI_API_KEY)
```

Não há testes automatizados neste exercício (mesma decisão da Questão 2).

## Como funciona

### `documentos.py` — Base de documentos

Define `DOCUMENTOS`, uma lista fixa de 8 posts curtos de blog técnico, cada um como um `Documento` (dataclass com `titulo` e `conteudo`). Os temas foram escolhidos deliberadamente distintos entre si (Python, orientação a objetos, banco de dados, APIs REST, embeddings, ambientes virtuais, testes, Docker) para que a busca semântica tenha o que diferenciar — por exemplo, "listas em Python" e "índices em banco de dados" não devem ser confundidos apesar de ambos mencionarem "dados".

### `indexador.py` — Geração de embeddings e montagem do índice

```python
def construir_indice() -> FAISS:
    documentos_langchain = [
        Document(page_content=documento.conteudo, metadata={"titulo": documento.titulo})
        for documento in DOCUMENTOS
    ]
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return FAISS.from_documents(documentos_langchain, embeddings)
```

Cada `Documento` fixo vira um `Document` do LangChain, guardando o título no `metadata` (para exibição posterior) e o conteúdo como `page_content` (o texto que efetivamente vira embedding). `FAISS.from_documents(...)` chama o modelo de embeddings para cada documento e monta o índice vetorial em memória — sem servidor externo, sem persistência em disco.

### `busca.py` — Função de busca semântica

```python
def buscar(indice: FAISS, consulta: str, k: int = 3) -> list[ResultadoBusca]:
    resultados = indice.similarity_search_with_score(consulta, k=k)
    return [
        ResultadoBusca(titulo=doc.metadata["titulo"], trecho=doc.page_content, pontuacao=pontuacao)
        for doc, pontuacao in resultados
    ]
```

`similarity_search_with_score` gera o embedding da consulta e calcula a distância L2 entre ele e os embeddings dos documentos indexados — **quanto menor a pontuação, mais similar (mais relevante) o documento**. `buscar()` é o ponto único de integração com o índice, retornando uma lista de `ResultadoBusca` (título, trecho e pontuação) já pronta para exibição, em vez de expor os objetos internos do LangChain a quem chama a função.

### `main.py` — Demonstração no terminal

1. Carrega `OPENAI_API_KEY` do `.env` e valida sua presença antes de importar os módulos que dependem dela (mesmo padrão de guard usado na Questão 2).
2. Chama `construir_indice()` uma única vez.
3. Roda uma lista de consultas de exemplo (`CONSULTAS_EXEMPLO`) contra o índice, imprimindo os 3 documentos mais relevantes de cada uma em uma tabela (`rich.table.Table`).

As consultas de exemplo usam vocabulário **deliberadamente diferente** do vocabulário dos documentos (ex.: "coleção de dados" em vez de "lista", "tabela grande" em vez de "índice") — o objetivo é evidenciar que a busca é por significado, e não por correspondência de palavra-chave.

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

Execução real de `python -m questao3_busca_semantica.main`, mostrando os 3 documentos mais relevantes retornados para cada consulta (pontuação = distância L2; menor é mais relevante). Em todas as 5 consultas, o documento correto ficou em primeiro lugar mesmo sem repetir o vocabulário exato do texto original.

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

## Decisões de projeto e limitações conhecidas

- **Índice em memória, reconstruído a cada execução.** Sem persistência em disco (`FAISS.save_local`/`load_local`) — aceitável para 8 documentos fixos; em produção, com uma base maior, o índice seria persistido e apenas atualizado incrementalmente.
- **Documentos fixos no código, não um dataset externo.** O enunciado sugere "um conjunto de artigos ou posts de um blog"; optou-se por embutir os textos em `documentos.py` em vez de fazer scraping de um blog real, para que o exercício rode de forma determinística e sem depender de rede ou de conteúdo que pode mudar.
- **Distância L2, não similaridade de cosseno.** `similarity_search_with_score` do FAISS (índice padrão `IndexFlatL2`) retorna distância euclidiana entre os vetores — por isso a interpretação é "quanto menor, mais relevante", ao contrário de uma pontuação de similaridade tradicional (onde maior é melhor).
- **`k` fixo em 3 nas consultas de exemplo.** `buscar()` aceita `k` como parâmetro (documentos mais relevantes a retornar), mas `main.py` sempre usa `k=3` para a demonstração.
- **Sem testes automatizados.** Mesma decisão tomada na Questão 2: o exercício prioriza a demonstração end-to-end no terminal; `buscar()` e `construir_indice()` foram mantidos como funções isoladas justamente para serem testáveis no futuro (ex. usando um índice FAISS pequeno construído em memória durante o teste).

---

⬅ [Questão 2 — Chatbot com LangChain](questao2_chatbot_langchain.md)
