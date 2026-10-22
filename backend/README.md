# SRS Tour --- Backend

Backend da aplicação SRS Tour desenvolvido com FastAPI.

## Tecnologias

-   Python 3.12
-   FastAPI
-   Poetry
-   PostgreSQL
-   Ruff
-   Pytest
-   httpx2 / TestClient

## Pré-requisitos

Para execução local:

-   Python 3.12+
-   Poetry 2+

Alternativamente, o backend pode ser executado utilizando Docker a
partir da raiz do projeto.

## Instalação

A partir da raiz, o fluxo completo do primeiro dia é `make setup` (veja o
README da raiz). Só o backend:

``` bash
make env           # cria backend/.env com SECRET_KEY aleatória (não sobrescreve)
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
`compose.yml`. Ao iniciar, o container roda `alembic upgrade head` antes do
uvicorn; por isso, depois do `make up`, o banco de desenvolvimento já tem as
tabelas. Dentro do container, `DATABASE_URL` aponta para o host `db`; no host
(`make back-migrate`, `make back-dev`) ela usa `localhost`, e os dois acessam o
mesmo banco.

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

Os testes de integração usam um PostgreSQL real e exigem a variável
`TEST_DATABASE_URL` (veja `.env.example`) apontando para um banco cujo nome
termine em `_test`, por exemplo `srs_tour_test`.

O `srs_tour_test` é criado automaticamente em volumes novos do Docker
(`docker/postgres/init/`). Antes da primeira execução, e sempre que houver
novas migrations, prepare o banco de testes:

``` bash
make back-test-migrate
```

No CI o Postgres é um service do Actions (não o Compose); lá se usa
`make back-test-migrate-only`, que só migra. `make back-migration-check`
(`alembic check`) falha se algum model foi alterado sem migration.

Esse alvo depende de `make db-create-test`, que cria o banco no container `db`
se ele ainda não existir (idempotente) e falha com mensagem clara se o
container não estiver rodando.

Esse comando usa somente `TEST_DATABASE_URL`, nunca `DATABASE_URL`, e falha
se a variável não estiver configurada ou se o banco não terminar em `_test`.
O `make back-test` não executa migrations automaticamente.

Para executar os testes:

``` bash
make back-test
```

Para filtrar: `make back-test ARGS="-k nome"`. Ou:

``` bash
cd backend
poetry run pytest
```

## Seed

`make seed` executa `backend/scripts/seed.py`, que ainda não insere nada.
Veja a docstring do script para adicionar dados de forma idempotente.

Os testes do backend utilizam Pytest. Requisições HTTP à aplicação podem
ser testadas através do `TestClient` do FastAPI/Starlette, utilizando
httpx2.
