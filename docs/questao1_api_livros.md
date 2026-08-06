# Questão 1 — API de Livros

API para cadastro e consulta de livros em uma biblioteca virtual.

## Enunciado

> Desenvolva uma API simples que permite aos usuários cadastrar e consultar livros em uma
> biblioteca virtual. A API deve incluir as seguintes funcionalidades:
>
> 1. Cadastro de livros com os campos: título, autor, data de publicação e resumo.
> 2. Consulta de livros por título ou autor.
> 3. Implemente a API utilizando um dos frameworks: Django, Flask ou FastAPI.
>
> Certifique-se de:
> - Criar endpoints claros e bem documentados.
> - Utilizar um banco de dados SQLite para armazenamento.
> - Implementar testes unitários para os endpoints criados.

## Stack

| Camada | Tecnologia |
|---|---|
| Framework web | [FastAPI](https://fastapi.tiangolo.com/) |
| Validação de dados | Pydantic v2 |
| ORM | SQLAlchemy 2.0 (estilo `Mapped`/`mapped_column`, assíncrono) |
| Banco de dados | SQLite, via driver assíncrono `aiosqlite` |
| Servidor ASGI | Uvicorn |
| Testes | pytest + pytest-asyncio + httpx (`AsyncClient`) |

## Estrutura de arquivos

```
questao1_api_livros/
├── main.py                       # Instância do FastAPI, lifespan, registro do router
├── database.py                   # Engine, Base declarativa, fábrica de sessões, dependency
├── models.py                     # Modelo ORM (tabela "livros")
├── schemas.py                    # Schemas Pydantic (entrada e saída da API)
├── banco.db                      # Arquivo SQLite (gerado em runtime, não versionar dados sensíveis)
├── routers/
│   └── endpoints_livros.py       # Endpoints REST de livros
└── tests/
    ├── __init__.py
    ├── conftest.py                # Fixtures: banco de teste + client HTTP
    └── test_livros.py             # Testes dos endpoints
```

## Modelo de dados

Tabela `livros` (`questao1_api_livros/models.py`):

| Coluna | Tipo | Restrições |
|---|---|---|
| `id` | `INTEGER` | chave primária, autoincremento |
| `titulo` | `VARCHAR(200)` | obrigatório |
| `autor` | `VARCHAR(100)` | obrigatório |
| `data_publicacao` | `DATE` | obrigatório |
| `resumo` | `TEXT` | obrigatório |

As tabelas são criadas automaticamente na inicialização da aplicação, via `Base.metadata.create_all` executado dentro do `lifespan` do FastAPI (`main.py`) — não há migrations (Alembic) neste exercício.

## Schemas (Pydantic)

- **`LivroCreateSchema`** — payload de entrada do `POST /livros/`: `titulo`, `autor`, `data_publicacao`, `resumo`. Não inclui `id` (gerado pelo banco). Tem `json_schema_extra` com um exemplo exibido no Swagger.
- **`LivroResponseSchema`** — payload de saída (herda de `LivroCreateSchema` e acrescenta `id`). Usa `model_config = ConfigDict(from_attributes=True)` para ser construído diretamente a partir do objeto ORM retornado pelo SQLAlchemy, sem precisar convertê-lo manualmente em dict.

## Endpoints

Prefixo: `/livros` (definido no `APIRouter`, tag `Livros` no Swagger).

### `POST /livros/` — Cadastrar livro

Cria um novo livro.

**Body** (`application/json`):
```json
{
  "titulo": "O Hobbit",
  "autor": "J.R.R. Tolkien",
  "data_publicacao": "1937-09-21",
  "resumo": "Bilbo Bolseiro é levado numa aventura por um mago e treze anões."
}
```

**Respostas:**
- `201 Created` — livro criado, corpo no formato `LivroResponseSchema` (inclui `id`).
- `409 Conflict` — já existe um livro cadastrado com o mesmo `titulo` e `autor`.
- `422 Unprocessable Entity` — payload inválido (campo faltando, tipo errado, `data_publicacao` fora do formato `YYYY-MM-DD` etc.), gerado automaticamente pela validação do Pydantic.

### `GET /livros/` — Consultar livros

Lista livros cadastrados, com filtros **opcionais** por título e/ou autor.

**Query params:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `titulo` | `string` | não | Busca parcial e case-insensitive (`ILIKE %titulo%`) |
| `autor` | `string` | não | Busca parcial e case-insensitive (`ILIKE %autor%`) |

Sem parâmetros, retorna todos os livros cadastrados. Os dois filtros podem ser combinados (aplicados com `AND`).

**Exemplos:**
```
GET /livros/                       -> lista completa
GET /livros/?titulo=hobbit         -> livros cujo título contém "hobbit"
GET /livros/?autor=tolkien         -> livros cujo autor contém "tolkien"
GET /livros/?titulo=o&autor=tolkien -> combina os dois filtros
```

**Resposta:** `200 OK`, lista de `LivroResponseSchema` (`[]` se nada for encontrado).

### Documentação interativa

Com a aplicação rodando, o FastAPI expõe automaticamente:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Schema OpenAPI cru: `http://127.0.0.1:8000/openapi.json`

## Banco de dados

- **Produção**: SQLite em arquivo, `questao1_api_livros/banco.db`, acessado via `sqlite+aiosqlite:///./banco.db` (driver assíncrono `aiosqlite`).
- **Sessão por requisição**: a dependency `get_async_session` (`database.py`) abre uma `AsyncSession` por request e garante o fechamento ao final via `async with`.
- **Testes**: cada teste usa um banco SQLite **em memória** (`sqlite+aiosqlite:///:memory:`), isolado do `banco.db` real — ver seção [Testes](#testes).

## Como rodar

```bash
# Na raiz do repositório (dot_backend_ia/)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Servidor precisa ser iniciado de dentro da pasta questao1_api_livros/,
# pois os módulos (database, models, schemas, routers) usam imports
# absolutos que assumem essa pasta como raiz.
cd questao1_api_livros
../.venv/bin/python -m uvicorn main:app --reload
```

Acesse `http://127.0.0.1:8000/docs` para testar os endpoints pela UI do Swagger.

## Testes

Testes de integração dos endpoints, usando `httpx.AsyncClient` (via `ASGITransport`, sem subir um servidor real) contra um banco SQLite em memória isolado por teste.

### Como funciona (`tests/conftest.py`)

- **`test_session`**: cria um engine SQLite `:memory:` com `poolclass=StaticPool` (necessário porque o banco `:memory:` só existe enquanto a conexão está aberta — sem `StaticPool`, cada checkout do pool abriria uma conexão nova e "esqueceria" os dados). Cria as tabelas antes do teste e as remove depois.
- **`client`**: sobrescreve a dependency `get_async_session` da aplicação com `app.dependency_overrides`, apontando para a sessão de teste — sem alterar nenhum código de produção. Devolve um `AsyncClient` que fala diretamente com a instância do FastAPI em memória.

Como o `lifespan` da aplicação (que cria as tabelas no `banco.db` real) só é acionado sob o protocolo ASGI de lifespan — que o `ASGITransport` não dispara — o banco de produção nunca é tocado pelos testes.

### Casos cobertos (`tests/test_livros.py`)

| Teste | O que valida |
|---|---|
| `test_criar_livro` | `POST /livros/` retorna `201` e o corpo com o `id` gerado |
| `test_criar_livro_duplicado_retorna_409` | Cadastrar o mesmo título+autor duas vezes retorna `409` |
| `test_listar_livros_vazio` | `GET /livros/` sem dados retorna lista vazia |
| `test_listar_livros_filtra_por_titulo` | Filtro por `titulo` (parcial, case-insensitive) retorna só o livro esperado |
| `test_listar_livros_filtra_por_autor` | Filtro por `autor` (parcial, case-insensitive) retorna só o livro esperado |

### Rodando os testes

```bash
# Na raiz do repositório
.venv/bin/python -m pytest -v
```

Configuração em `pyproject.toml`: `asyncio_mode = "auto"` (dispensa `@pytest.mark.asyncio` em cada teste) e `testpaths = ["questao1_api_livros/tests"]`.

## Decisões de projeto e limitações conhecidas

- **Prevenção de duplicatas é feita na aplicação, não no banco.** `criar_livro` faz um `SELECT` por `titulo`+`autor` antes do `INSERT`. Sob concorrência (duas requisições simultâneas para o mesmo livro), ainda é possível criar duplicatas, pois não há `UniqueConstraint` no banco garantindo isso. Suficiente para o escopo do exercício; em produção, o ideal seria adicionar a constraint e tratar o `IntegrityError`.
- **Sem paginação em `GET /livros/`.** A listagem devolve todos os resultados de uma vez; aceitável para o volume de dados deste exercício, mas não escalaria para uma tabela grande.
- **Sem migrations.** As tabelas são criadas via `create_all` no startup; qualquer mudança de schema em um banco já existente exigiria apagar o `banco.db` ou introduzir uma ferramenta como Alembic.
- **Imports absolutos ("soltos"), não relativos.** Módulos como `database`, `models`, `schemas` e `routers.endpoints_livros` são importados como se `questao1_api_livros/` fosse a raiz do projeto. Por isso a aplicação (e os testes) precisam ser executados com essa pasta no `sys.path` — daí o `cd questao1_api_livros` antes do `uvicorn` e o `tests/__init__.py`, que faz o pytest inserir automaticamente essa pasta no `sys.path`.