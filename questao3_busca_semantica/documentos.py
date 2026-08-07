"""Documentos fixos usados na busca, embutidos aqui em vez de raspados de
algum blog real — assim o exercício roda sem depender de internet.

Os temas são bem diferentes entre si de propósito, pra dar pro embedding
algo de fato pra diferenciar.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Documento:
    titulo: str
    conteudo: str


DOCUMENTOS: list[Documento] = [
    Documento(
        titulo="Listas em Python",
        conteudo=(
            "Listas são uma das estruturas de dados mais usadas em Python. Elas são "
            "criadas com colchetes, como em numeros = [1, 2, 3], e podem conter "
            "elementos de tipos diferentes na mesma lista. É possível adicionar itens "
            "com o método append(), remover com remove() ou pop(), e acessar elementos "
            "por índice, incluindo índices negativos para contar a partir do fim. "
            "Listas também suportam slicing, permitindo extrair sublistas com a "
            "sintaxe lista[inicio:fim]. Por serem mutáveis, listas são a escolha padrão "
            "quando é preciso alterar uma coleção de dados ao longo do programa."
        ),
    ),
    Documento(
        titulo="Programação Orientada a Objetos em Python",
        conteudo=(
            "Python é uma linguagem multiparadigma que oferece suporte completo à "
            "programação orientada a objetos. Classes são definidas com a palavra-chave "
            "class, e o método especial __init__ funciona como construtor, inicializando "
            "os atributos de cada instância. Herança é implementada passando a classe "
            "base entre parênteses na definição da subclasse, permitindo reaproveitar e "
            "especializar comportamento. Conceitos como encapsulamento, polimorfismo e "
            "métodos mágicos (dunder methods, como __str__ e __eq__) tornam os objetos "
            "Python flexíveis e integrados à sintaxe nativa da linguagem."
        ),
    ),
    Documento(
        titulo="Índices em Bancos de Dados Relacionais",
        conteudo=(
            "Índices são estruturas auxiliares que aceleram consultas em bancos de "
            "dados relacionais, evitando que o motor precise varrer todas as linhas de "
            "uma tabela para encontrar um resultado. O tipo mais comum é a B-tree, que "
            "organiza os valores de forma ordenada e permite buscas em tempo "
            "logarítmico. Criar um índice tem custo: cada escrita na tabela (INSERT, "
            "UPDATE, DELETE) também precisa atualizar o índice, então índices em excesso "
            "podem piorar a performance de escrita. A escolha de quais colunas indexar "
            "geralmente segue os padrões de consulta mais frequentes da aplicação, como "
            "colunas usadas em cláusulas WHERE e JOIN."
        ),
    ),
    Documento(
        titulo="Introdução a APIs REST",
        conteudo=(
            "APIs REST expõem recursos através de URLs e utilizam os métodos HTTP "
            "(GET, POST, PUT, DELETE) para representar operações sobre esses recursos. "
            "Um princípio central do REST é o statelessness: cada requisição deve conter "
            "toda a informação necessária para ser processada, sem depender de estado "
            "guardado no servidor entre chamadas. Códigos de status HTTP comunicam o "
            "resultado da operação, como 200 para sucesso, 404 quando o recurso não é "
            "encontrado e 500 para erros internos do servidor. Frameworks como FastAPI "
            "e Flask facilitam a criação de APIs REST em Python, cuidando de roteamento, "
            "serialização e validação de dados automaticamente."
        ),
    ),
    Documento(
        titulo="Modelos de Linguagem e Embeddings",
        conteudo=(
            "Embeddings são representações numéricas de texto em vetores de alta "
            "dimensão, gerados por modelos treinados para capturar significado "
            "semântico. Textos com significados parecidos produzem vetores próximos no "
            "espaço vetorial, medidos por métricas como similaridade de cosseno ou "
            "distância euclidiana. Essa propriedade é a base da busca semântica: em vez "
            "de comparar palavras exatas como uma busca por palavra-chave tradicional, "
            "compara-se o significado das frases. Modelos de linguagem como os da "
            "família GPT também usam embeddings internamente para representar tokens "
            "antes de processá-los nas camadas de atenção do transformer."
        ),
    ),
    Documento(
        titulo="Gerenciamento de Ambientes Virtuais em Python",
        conteudo=(
            "Ambientes virtuais isolam as dependências de um projeto Python das "
            "dependências instaladas globalmente no sistema, evitando conflitos de "
            "versão entre projetos diferentes. O módulo venv, incluído na biblioteca "
            "padrão desde o Python 3.3, cria um ambiente isolado com o comando python -m "
            "venv .venv. Depois de ativado (source .venv/bin/activate no Linux/macOS), "
            "o comando pip install passa a instalar pacotes apenas dentro desse "
            "ambiente. Arquivos como requirements.txt ou pyproject.toml documentam as "
            "dependências do projeto, permitindo recriar o mesmo ambiente em outra "
            "máquina."
        ),
    ),
    Documento(
        titulo="Testes Automatizados com pytest",
        conteudo=(
            "pytest é um dos frameworks de testes mais populares do ecossistema "
            "Python, conhecido pela sintaxe simples baseada em funções e na palavra-"
            "chave assert, sem exigir classes ou métodos especiais como em unittest. "
            "Fixtures, declaradas com o decorador @pytest.fixture, permitem preparar e "
            "compartilhar recursos entre testes, como conexões de banco de dados ou "
            "clientes HTTP de teste. O pytest também suporta parametrização de testes "
            "com @pytest.mark.parametrize, executando a mesma função de teste várias "
            "vezes com conjuntos de dados diferentes, o que reduz duplicação de código "
            "em cenários de teste semelhantes."
        ),
    ),
    Documento(
        titulo="Docker e Containers para Desenvolvimento",
        conteudo=(
            "Docker permite empacotar uma aplicação junto com todas as suas "
            "dependências em uma imagem de container, garantindo que ela rode da mesma "
            "forma em qualquer ambiente, do notebook do desenvolvedor ao servidor de "
            "produção. Um Dockerfile descreve, passo a passo, como construir essa "
            "imagem: qual imagem base usar, quais arquivos copiar e quais comandos "
            "executar. Ferramentas como o Docker Compose facilitam orquestrar múltiplos "
            "containers relacionados, como uma aplicação web e seu banco de dados, "
            "definidos em um único arquivo YAML. Diferente de máquinas virtuais, "
            "containers compartilham o kernel do sistema operacional host, o que os "
            "torna significativamente mais leves e rápidos para iniciar."
        ),
    ),
]
