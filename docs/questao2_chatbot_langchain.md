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

### `prompt.py` — System prompt

Define `SYSTEM_PROMPT`, injetado no agente como instrução de sistema. Estrutura em três blocos:

- **Escopo**: restringe o assistente a perguntas sobre Python/programação; fora do escopo, ele recusa educadamente.
- **Estilo de resposta**: tom didático, respostas longas em passos numerados, exemplos de código curtos e comentados quando fizer sentido.
- **Guardrails**: proíbe inventar funções/bibliotecas inexistentes, proíbe incentivar más práticas de segurança (ex.: uso perigoso de `eval`/`exec`), proíbe revelar o próprio system prompt e proíbe responder sobre assuntos fora do escopo mesmo sob insistência do usuário.

### `chatbot.py` — Agente e função de pergunta

```python
checkpointer = InMemorySaver()
agent_chatbot = create_agent(
    model="openai:gpt-4o-mini", system_prompt=SYSTEM_PROMPT, checkpointer=checkpointer
)
```

- **`agent_chatbot`**: um grafo LangGraph compilado (`CompiledStateGraph`), criado por `create_agent` (API de agentes do LangChain v1). O modelo é resolvido pela string `"openai:gpt-4o-mini"` (provider `openai` + modelo `gpt-4o-mini`), sem necessidade de instanciar `ChatOpenAI` manualmente.
- **`checkpointer` (`InMemorySaver`)**: guarda o histórico de mensagens em memória, por `thread_id`. É o que permite ao agente "lembrar" de perguntas anteriores dentro da mesma conversa — sem ele, cada `invoke` seria uma conversa nova e isolada. Por ser em memória, o histórico se perde quando o processo termina (aceitável para este exercício; em produção usar-se-ia um checkpointer persistente, ex. SQLite/Postgres).
- **`perguntar(pergunta, thread_id)`**: função de conveniência que monta a mensagem do usuário, monta o `RunnableConfig` com o `thread_id` e chama `agent_chatbot.invoke(...)`, retornando apenas o texto da última mensagem da resposta (`result["messages"][-1].content`). É o ponto único de integração com o agente — tanto `main.py` quanto testes futuros chamariam essa função em vez de acessar `agent_chatbot` diretamente.

O `thread_id` é o mecanismo do LangGraph para escopar conversas: chamadas com o mesmo `thread_id` reaproveitam o histórico salvo pelo `checkpointer`; um `thread_id` diferente começa uma conversa do zero.

### `main.py` — Loop de conversa no terminal

Ponto de entrada da aplicação. Fluxo:

1. **Carrega variáveis de ambiente** com `load_dotenv()` (lê um arquivo `.env`, se existir).
2. **Valida `OPENAI_API_KEY`** antes de importar o agente: se a variável não estiver definida, o programa termina com `sys.exit(...)` e uma mensagem orientando a copiar `.env.example` para `.env`. Essa checagem é feita *antes* do `from questao2_chatbot_langchain.chatbot import perguntar` propositalmente — importar `chatbot.py` já dispara `create_agent(...)`, que falharia com um erro genérico da lib da OpenAI caso a chave não exista.
3. **Gera um `thread_id`** (`uuid.uuid4()`) uma única vez por execução do programa, e o reutiliza em todas as perguntas da sessão — é isso que dá ao chatbot memória de curto prazo durante a conversa.
4. **Loop de leitura**: `input("Você: ")` captura a pergunta do usuário.
   - Linha vazia: ignorada, volta a pedir input.
   - `sair` / `exit` / `quit` (case-insensitive): encerra o loop.
   - `Ctrl+C` (`KeyboardInterrupt`) ou EOF (`Ctrl+D`): encerra o loop de forma graciosa, sem stack trace.
5. **Resposta formatada**: cada resposta do agente é impressa com `rich.markdown.Markdown` via `Console.print`, renderizando negrito, listas, blocos de código etc. diretamente no terminal — em vez de mostrar o Markdown cru, já que o `SYSTEM_PROMPT` instrui o modelo a formatar respostas com listas e blocos de código.

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

Transcrição real de uma execução (`python -m questao2_chatbot_langchain.main`), demonstrando os três comportamentos-chave do chatbot: resposta didática, memória de conversa e guardrail de escopo. A saída abaixo é o texto puro; no terminal, o `rich` renderiza listas numeradas e blocos de código com destaque de sintaxe.

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

A pergunta não repete a palavra "lista" — o bot só consegue responder corretamente porque o `thread_id` da sessão manteve o histórico da pergunta anterior no `checkpointer` (ver [`chatbot.py`](#chatbotpy--agente-e-função-de-pergunta)).

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

- **Memória apenas em processo (`InMemorySaver`).** O histórico da conversa não sobrevive ao encerramento do programa nem é compartilhado entre execuções — suficiente para uma demonstração via terminal, mas não para um chatbot com múltiplas sessões/usuários simultâneos, que exigiria um checkpointer persistente (ex. `SqliteSaver`/`PostgresSaver`).
- **Um `thread_id` por execução, não por usuário.** Como o programa roda para um único usuário no terminal, um `thread_id` gerado no início do `main()` é suficiente. Numa aplicação com múltiplos usuários (ex. API web), o `thread_id` precisaria ser derivado da sessão/usuário de cada requisição.
- **Modelo fixo no código (`openai:gpt-4o-mini`).** Não é configurável via variável de ambiente. Escolhido por ser um modelo da família GPT-4 mais barato e rápido que o `gpt-4`/`gpt-4-turbo` originais, adequado para perguntas didáticas sobre Python; trocar de modelo hoje exige editar `chatbot.py`.
- **Sem streaming de resposta.** `agent_chatbot.invoke(...)` é síncrono e bloqueante — a resposta só aparece por completo, não token a token. O LangChain suporta streaming (`.stream()`/`.stream_events()`), mas não foi necessário para o escopo do exercício.
- **Sem testes automatizados.** Diferente da questão 1, este exercício não tem suíte de testes. A função `perguntar()` foi extraída de propósito para ser testável isoladamente (ex. usando um fake/mocked `agent_chatbot`), caso testes sejam adicionados no futuro.
- **Imports absolutos ("soltos"), não relativos.** Assim como na questão 1, `chatbot.py` importa `questao2_chatbot_langchain.prompt` como se a raiz do repositório fosse a raiz do projeto Python. Por isso a aplicação precisa ser executada com `python -m questao2_chatbot_langchain.main` a partir da raiz do repositório (e não `python main.py` de dentro da pasta).

---

⬅ [Questão 1 — API de Livros](questao1_api_livros.md)
