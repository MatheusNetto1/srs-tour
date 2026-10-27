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

Em ambientes diferentes de `dev`, a `SECRET_KEY` deve ter pelo menos 32
caracteres e não pode usar o valor `change-me`. O `make env` cria uma chave
forte automaticamente. O token de acesso expira em 480 minutos (8 horas) por
padrão.

Quem já possui um `backend/.env` antigo deve adicionar `APP_ENV=dev` para o
ambiente local e atualizar `ACCESS_TOKEN_EXPIRE_MINUTES=480`. Uma chave gerada
pelo `make env`, com mais de 32 caracteres, continua válida mesmo sem
`APP_ENV`.

O backend e o frontend têm `healthcheck` no Compose (`make ps` mostra
`healthy`). Sem Poetry no host, use os alvos que rodam dentro do container,
com o ambiente no ar (`make up`): `make docker-back-test-migrate`,
`make docker-back-test ARGS="-k nome"`, `make docker-seed` e
`make docker-back-migration m="create x table"`. Eles exportam
`TEST_DATABASE_URL` com o host `db`. Os alvos sem prefixo continuam rodando no
host, com Poetry.

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
(`alembic check`) falha se algum model foi alterado sem migration, e
`make back-migration-single-head` (sem banco; roda no CI antes das migrations)
falha se duas migrations partirem da mesma revisão: ajuste o `down_revision`
da que você criou.

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

`make seed` cria o administrador inicial quando `ADMIN_EMAIL` e
`ADMIN_PASSWORD` estão configurados no `backend/.env`. O seed é idempotente:
se o e-mail já existir, nenhum dado é alterado; um usuário inativo nunca é
reativado implicitamente. Dentro do container, use `make docker-seed`.

As operações de usuários ficam em `/api/v1/admin/users`. Todo endpoint sob
`/api/v1/admin` exige um token de usuário com papel `admin`; a antiga rota
`/api/v1/users` não está mais disponível.

Os testes do backend utilizam Pytest. Requisições HTTP à aplicação podem
ser testadas através do `TestClient` do FastAPI/Starlette, utilizando
httpx2.
