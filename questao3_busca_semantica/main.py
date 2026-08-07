import os
import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    sys.exit(
        "Erro: variável de ambiente OPENAI_API_KEY não definida.\n"
        "Copie .env.example para .env e informe sua chave da OpenAI."
    )

from questao3_busca_semantica.busca import ResultadoBusca, buscar
from questao3_busca_semantica.indexador import construir_indice

console = Console()

CONSULTAS_EXEMPLO = [
    "Como faço para adicionar um elemento em uma coleção de dados em Python?",
    "O que é herança em classes?",
    "Como acelerar consultas em uma tabela grande?",
    "O que são vetores que representam o significado de um texto?",
    "Como isolar as dependências de um projeto?",
]


def mostrar_resultados(console: Console, consulta: str, resultados: list[ResultadoBusca]) -> None:
    tabela = Table(title=f'Consulta: "{consulta}"', show_lines=True)
    tabela.add_column("Documento", style="bold cyan", no_wrap=True)
    tabela.add_column("Distância", justify="right", style="magenta")
    tabela.add_column("Trecho", style="white")

    for resultado in resultados:
        trecho = resultado.trecho
        if len(trecho) > 160:
            trecho = trecho[:160].rstrip() + "..."
        tabela.add_row(resultado.titulo, f"{resultado.pontuacao:.4f}", trecho)

    console.print(tabela)
    console.print()


def main() -> None:
    """Constrói o índice vetorial e demonstra a busca semântica com consultas de exemplo.

    As consultas de exemplo usam vocabulário deliberadamente diferente do dos
    documentos (ex.: "coleção de dados" em vez de "lista") para evidenciar que
    a busca é por significado, não por palavra-chave.
    """
    console.print("[bold]Busca Semântica com FAISS + Embeddings.[/bold]")
    console.print("Gerando embeddings e construindo o índice vetorial...\n")

    indice = construir_indice()

    for consulta in CONSULTAS_EXEMPLO:
        resultados = buscar(indice, consulta, k=3)
        mostrar_resultados(console, consulta, resultados)


if __name__ == "__main__":
    main()
