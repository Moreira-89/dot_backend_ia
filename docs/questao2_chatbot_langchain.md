# Questão 2 — Chatbot com LangChain

Chatbot de terminal especializado em Python, que usa um LLM da OpenAI via LangChain/LangGraph para responder perguntas dos usuários.

## Enunciado

> Você precisa desenvolver um chatbot que utilize um modelo de linguagem (LLM) como o GPT-4 da OpenAI para responder perguntas dos usuários sobre programação em Python. O
> chatbot deve:
>
> 1. Receber perguntas dos usuários via input de texto.
> 2. Utilizar o Langchain para gerenciar o fluxo de conversação e integrar com o LLM.
> 3. Responder às perguntas utilizando o modelo da OpenAI.
>
> Implemente um exemplo simples onde o usuário possa perguntar algo como "Como criar uma lista em Python?" e o chatbot responda com uma explicação detalhada.

## Stack

| Camada | Tecnologia |
|---|---|
| Orquestração do agente | [LangChain](https://docs.langchain.com/) (`create_agent`, API v1) |
| Execução/estado do grafo | [LangGraph](https://langchain-ai.github.io/langgraph/) (`CompiledStateGraph`, `InMemorySaver`) |
| LLM | OpenAI `gpt-4o-mini`, via `langchain-openai` |
| Variáveis de ambiente | `python-dotenv` |
| Saída no terminal | [`rich`](https://rich.readthedocs.io/) (`Console` + `Markdown`) |

## Estrutura de arquivos

```
questao2_chatbot_langchain/
├── chatbot.py         # Criação do agente (create_agent) e função perguntar()
├── main.py            # Ponto de entrada: loop de input no terminal
├── prompt.py           # SYSTEM_PROMPT do agente
└── .env.example        # Modelo de variáveis de ambiente (OPENAI_API_KEY)
```

Não há testes automatizados neste exercício (diferente da questão 1).

## Como funciona

`prompt.py` define o `SYSTEM_PROMPT`, dividido em três blocos: escopo (restringe o assistente a Python/programação, recusando o resto educadamente), estilo de resposta (tom didático, passos numerados, exemplos de código curtos) e guardrails (proíbe inventar função/biblioteca que não existe, incentivar uso perigoso de `eval`/`exec`, revelar o próprio prompt, ou ceder mesmo sob insistência do usuário fora do escopo).

`chatbot.py` cria o agente:

```python
checkpointer = InMemorySaver()
agent_chatbot = create_agent(
    model="openai:gpt-4o-mini", system_prompt=SYSTEM_PROMPT, checkpointer=checkpointer
)
```

`agent_chatbot` é um grafo LangGraph compilado, montado pelo `create_agent` (API de agentes do LangChain v1) — o modelo é resolvido direto pela string `"openai:gpt-4o-mini"`, sem precisar instanciar `ChatOpenAI` manualmente. O `checkpointer` guarda o histórico de mensagens em memória, indexado por `thread_id`; é o que dá ao agente "memória" dentro de uma conversa — sem ele cada `invoke` seria isolado. Como é em memória, o histórico some quando o processo termina (em produção entraria um checkpointer persistente, tipo SQLite/Postgres).

`perguntar(pergunta, thread_id)` monta a mensagem do usuário, monta o `RunnableConfig` com o `thread_id` e chama `agent_chatbot.invoke(...)`, devolvendo só o texto da última mensagem. É por essa função que `main.py` (e qualquer teste futuro) fala com o agente, em vez de acessar `agent_chatbot` direto. `thread_id` é o mecanismo do LangGraph pra escopar conversas: mesmo `thread_id` reaproveita o histórico salvo pelo `checkpointer`, `thread_id` novo começa do zero.

`main.py` carrega o `.env` e valida a `OPENAI_API_KEY` antes de importar o agente — a checagem vem antes do `import chatbot` de propósito, porque só importar o módulo já dispara `create_agent(...)`, e sem chave isso falharia com um erro genérico da lib da OpenAI em vez da mensagem clara que a gente quer mostrar. Depois disso, gera um `thread_id` por execução (reaproveitado em todas as perguntas da sessão, é isso que dá a memória de curto prazo) e entra num loop de `input("Você: ")`: linha vazia é ignorada, `sair`/`exit`/`quit` encerra, `Ctrl+C`/`Ctrl+D` encerra sem stack trace. Cada resposta passa por `rich.markdown.Markdown` antes de imprimir, já que o `SYSTEM_PROMPT` pede pro modelo formatar em Markdown (listas, blocos de código) e mostrar isso cru ficaria feio.

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `OPENAI_API_KEY` | sim | Chave de API da OpenAI, usada implicitamente por `langchain-openai` para autenticar as chamadas ao modelo `gpt-4o-mini`. |

Configuração local: copiar `.env.example` para `.env` e preencher a chave. O `.env` já está no `.gitignore` da raiz do projeto — nunca é versionado.

## Como rodar

```bash
# Na raiz do repositório (dot_backend_ia/)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Configurar a chave da OpenAI
cp questao2_chatbot_langchain/.env.example questao2_chatbot_langchain/.env
# edite questao2_chatbot_langchain/.env e informe OPENAI_API_KEY

# Executar como módulo, a partir da raiz do repositório
# (chatbot.py usa import absoluto "questao2_chatbot_langchain.prompt",
# que exige a raiz do repositório no sys.path — daí rodar com -m)
.venv/bin/python -m questao2_chatbot_langchain.main
```

## Exemplos de perguntas e respostas

Transcrição real de uma execução (`python -m questao2_chatbot_langchain.main`), cobrindo os três comportamentos-chave: resposta didática, memória de conversa e guardrail de escopo. A saída abaixo é o texto puro; no terminal, o `rich` renderiza listas numeradas e blocos de código com destaque de sintaxe.

### 1. Pergunta normal sobre Python

```
Você: Como criar uma lista em Python?"

Criar uma lista em Python é bem simples! Aqui estão os passos que você pode seguir:

1. Utilizando colchetes: A maneira mais comum de criar uma lista é utilizando colchetes [].
   Exemplo:

    minha_lista = [1, 2, 3, 4, 5]  # Criando uma lista com números inteiros
    print(minha_lista)

2. Utilizando a função list(): Você também pode criar uma lista usando a função list(). Esta
   função é especialmente útil para converter outros tipos de coleções em listas.
   Exemplo:

    outra_lista = list((6, 7, 8))  # Convertendo uma tupla em lista
    print(outra_lista)

3. Lista vazia: Se você precisar iniciar com uma lista vazia, basta usar colchetes sem nada dentro.
   Exemplo:

    lista_vazia = []  # Criando uma lista vazia
    print(lista_vazia)

4. Adicionando elementos: Após criar uma lista, você pode adicionar elementos a ela utilizando
   o método append().
   Exemplo:

    lista = []
    lista.append('Python')  # Adicionando a string 'Python' à lista
    print(lista)  # Saída: ['Python']

Esses são alguns dos métodos mais comuns para criar listas em Python. Experimente os exemplos
e veja como as listas funcionam! Se tiver mais dúvidas, sinta-se à vontade para perguntar.
```

### 2. Pergunta de acompanhamento (confirma a memória de conversa)

A pergunta não repete a palavra "lista" — o bot só responde certo porque o `thread_id` da sessão manteve o histórico da pergunta anterior no `checkpointer`.

```
Você: E como eu adiciono um item nela?

Você pode adicionar um item a uma lista em Python utilizando o método append() ou o método
insert(). Vou explicar ambos:

1. Usando o método append()

O método append() adiciona um item ao final da lista.

Exemplo:

 minha_lista = [1, 2, 3]
 minha_lista.append(4)  # Adicionando o número 4 ao final da lista
 print(minha_lista)  # Saída: [1, 2, 3, 4]

2. Usando o método insert()

O método insert() permite que você adicione um item em uma posição específica na lista. Você
precisa especificar o índice e o valor a ser adicionado.

Exemplo:

 minha_lista = [1, 2, 3]
 minha_lista.insert(1, 99)  # Adicionando o número 99 na posição 1 (segunda posição)
 print(minha_lista)  # Saída: [1, 99, 2, 3]

Resumo dos métodos:

1. append(item): Adiciona item ao final da lista.
2. insert(posição, item): Insere item na posição especificada.

Experimente esses métodos e veja como funcionam com suas listas! Se você tiver mais dúvidas,
estou aqui para ajudar.
```

### 3. Pergunta fora do escopo (confirma o guardrail)

Testa a regra de escopo do `SYSTEM_PROMPT`: perguntas fora de Python/programação são recusadas educadamente, sem tentar responder.

```
Você: Qual a melhor receita de brigadeiro?

Desculpe, mas sou especializado em aprendizado de Python e não posso ajudar com receitas ou
culinária. Se você tiver perguntas sobre Python, conceitos de programação ou qualquer outro
tema relacionado a programação, ficarei feliz em ajudar!
```

### Encerrando a sessão

```
Você: sair
Até mais!
```

## Decisões de projeto e limitações conhecidas

A memória do chatbot vive só em processo (`InMemorySaver`) — some quando o programa termina e não é compartilhada entre execuções. Pra uma demonstração via terminal é suficiente; um chatbot com múltiplas sessões/usuários simultâneos precisaria de um checkpointer persistente, tipo `SqliteSaver`/`PostgresSaver`. Na mesma linha, o `thread_id` é gerado uma vez por execução, não por usuário — funciona porque o programa atende um usuário só no terminal; numa API web ele teria que vir da sessão de cada requisição.

O modelo (`openai:gpt-4o-mini`) está fixo no código, não é configurável por variável de ambiente. Escolhi ele por ser mais barato e rápido que `gpt-4`/`gpt-4-turbo` e dar conta bem de perguntas didáticas sobre Python; trocar de modelo hoje significa editar `chatbot.py` na mão.

Não tem streaming: `agent_chatbot.invoke(...)` é síncrono, a resposta só aparece inteira, não token a token. O LangChain suporta `.stream()`/`.stream_events()`, mas não precisei disso pro escopo do exercício. Também não tem testes automatizados, diferente da questão 1 — deixei `perguntar()` como função isolada de propósito, pra ficar fácil testar depois com um `agent_chatbot` mockado.

Por fim, os imports são absolutos, não relativos: `chatbot.py` importa `questao2_chatbot_langchain.prompt` como se a raiz do repositório fosse a raiz do projeto Python, o mesmo padrão da questão 1. Por isso a aplicação precisa rodar com `python -m questao2_chatbot_langchain.main` a partir da raiz, e não `python main.py` de dentro da pasta.

---

⬅ [Questão 1 — API de Livros](questao1_api_livros.md) | [Questão 3 — Busca Semântica](questao3_busca_semantica.md) ➡
