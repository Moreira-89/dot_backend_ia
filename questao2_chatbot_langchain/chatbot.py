from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver

from questao2_chatbot_langchain.prompt import SYSTEM_PROMPT

checkpointer = InMemorySaver()
agent_chatbot = create_agent(
    model="openai:gpt-4o-mini", system_prompt=SYSTEM_PROMPT, checkpointer=checkpointer
)


def perguntar(pergunta: str, thread_id: str) -> str:
    """Envia uma pergunta ao agente e retorna a resposta em texto.

    O histórico da conversa é mantido pelo `checkpointer` do agente e
    recuperado a partir do `thread_id`: chamadas com o mesmo `thread_id`
    reaproveitam o contexto das perguntas anteriores.
    """
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    result = agent_chatbot.invoke(
        {"messages": [{"role": "user", "content": pergunta}]},
        config=config,
    )

    return result["messages"][-1].content