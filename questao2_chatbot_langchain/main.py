import os
import sys
import uuid

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    sys.exit(
        "Erro: variável de ambiente OPENAI_API_KEY não definida.\n"
        "Copie .env.example para .env e informe sua chave da OpenAI."
    )

from questao2_chatbot_langchain.chatbot import perguntar

console = Console()


def main() -> None:
    """Roda o chatbot em loop no terminal, lendo perguntas via input de texto.

    Um único `thread_id` é gerado por execução do programa e reutilizado em
    todas as perguntas da sessão, para que o agente mantenha o histórico da
    conversa (veja `perguntar` em chatbot.py).
    """
    thread_id = str(uuid.uuid4())

    console.print("[bold]Chatbot de Python (LangChain + OpenAI).[/bold] Digite 'sair' para encerrar.\n")

    while True:
        try:
            question = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nAté mais!")
            break

        if not question:
            continue
        if question.lower() in {"sair", "exit", "quit"}:
            console.print("Até mais!")
            break

        answer = perguntar(question, thread_id)
        console.print()
        console.print(Markdown(answer))
        console.print()


if __name__ == "__main__":
    main()
