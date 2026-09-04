# SRS Tour --- Backend

Backend da aplicação SRS Tour desenvolvido com FastAPI.

## Tecnologias

-   Python 3.12
-   FastAPI
-   Poetry
-   PostgreSQL
-   Ruff
-   Pytest
-   HTTPX / TestClient

## Pré-requisitos

Para execução local:

-   Python 3.12+
-   Poetry 2+

Alternativamente, o backend pode ser executado utilizando Docker a
partir da raiz do projeto.

## Instalação

A partir da raiz:

``` bash
make install-back
```

Ou diretamente na pasta `backend`:

``` bash
cd backend
poetry install
```

O Poetry é utilizado para gerenciar as dependências e o ambiente virtual
do backend.

O projeto utiliza `package-mode = false`, pois o backend é tratado como
uma aplicação e não como um pacote Python distribuível.

## Executando localmente

A partir da raiz:

``` bash
make back-dev
```

Ou diretamente:

``` bash
cd backend
poetry run uvicorn app.main:app --reload
```

A aplicação ficará disponível em `http://localhost:8000`.

A documentação interativa do FastAPI estará disponível em
`http://localhost:8000/docs`.

## Executando com Docker

A partir da raiz do projeto:

``` bash
make up
```

Ou utilizando Docker Compose diretamente:

``` bash
docker compose up
```

O backend será executado junto com os demais serviços definidos no
`compose.yml`.

## Qualidade de código

### Lint

``` bash
make back-lint
```

Equivalente a:

``` bash
cd backend
poetry run ruff check .
```

### Formatação

``` bash
make back-format
```

Equivalente a:

``` bash
cd backend
poetry run ruff format .
```

## Testes

``` bash
make back-test
```

Ou:

``` bash
cd backend
poetry run pytest
```

Os testes do backend utilizam Pytest. Requisições HTTP à aplicação podem
ser testadas através do `TestClient` do FastAPI/Starlette, utilizando
HTTPX.
