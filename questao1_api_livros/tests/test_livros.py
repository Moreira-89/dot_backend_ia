from httpx import AsyncClient

LIVRO_PAYLOAD = {
    "titulo": "O Hobbit",
    "autor": "J.R.R. Tolkien",
    "data_publicacao": "1937-09-21",
    "resumo": "Bilbo Bolseiro é levado numa aventura por um mago e treze anões.",
}


async def test_criar_livro(client: AsyncClient):
    response = await client.post("/livros/", json=LIVRO_PAYLOAD)

    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == LIVRO_PAYLOAD["titulo"]
    assert data["autor"] == LIVRO_PAYLOAD["autor"]
    assert "id" in data


async def test_criar_livro_duplicado_retorna_409(client: AsyncClient):
    await client.post("/livros/", json=LIVRO_PAYLOAD)
    response = await client.post("/livros/", json=LIVRO_PAYLOAD)

    assert response.status_code == 409


async def test_listar_livros_vazio(client: AsyncClient):
    response = await client.get("/livros/")

    assert response.status_code == 200
    assert response.json() == []


async def test_listar_livros_filtra_por_titulo(client: AsyncClient):
    await client.post("/livros/", json=LIVRO_PAYLOAD)
    await client.post(
        "/livros/",
        json={
            **LIVRO_PAYLOAD,
            "titulo": "O Senhor dos Anéis",
            "autor": "Outro Autor",
        },
    )

    response = await client.get("/livros/", params={"titulo": "hobbit"})

    assert response.status_code == 200
    resultados = response.json()
    assert len(resultados) == 1
    assert resultados[0]["titulo"] == "O Hobbit"


async def test_listar_livros_filtra_por_autor(client: AsyncClient):
    await client.post("/livros/", json=LIVRO_PAYLOAD)
    await client.post(
        "/livros/",
        json={
            **LIVRO_PAYLOAD,
            "titulo": "O Senhor dos Anéis",
            "autor": "Outro Autor",
        },
    )

    response = await client.get("/livros/", params={"autor": "tolkien"})

    assert response.status_code == 200
    resultados = response.json()
    assert len(resultados) == 1
    assert resultados[0]["autor"] == "J.R.R. Tolkien"
