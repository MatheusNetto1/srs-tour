# SRS Tour

Aplicação full stack voltada para turismo.

O projeto está organizado como um monorepo contendo aplicações independentes para backend e frontend, além da  infraestrutura necessária para execução local com Docker.

## Tecnologias

### Backend

-   Python 3.12
-   FastAPI
-   Poetry
-   PostgreSQL
-   Ruff
-   Pytest
-   httpx2 / TestClient

### Frontend

-   Node.js 24
-   TypeScript
-   React
-   Vite
-   Tailwind CSS
-   Biome
-   Vitest
-   Testing Library
-   Playwright

### Infraestrutura

-   Docker
-   Docker Compose
-   Make

## Estrutura do projeto

``` text
srs-tour/
├── backend/
│   └── README.md
├── docker/
│   └── postgres/init/   # scripts de inicialização do Postgres (banco de teste)
├── frontend/
│   └── README.md
├── compose.yml
├── Makefile
└── README.md
```

## Pré-requisitos

### Execução com Docker

Para executar todo o projeto utilizando containers:

-   Docker
-   Docker Compose
-   Make

### Execução local

Para executar as aplicações diretamente na máquina:

-   Python 3.12+
-   Poetry 2+
-   Node.js 24+
-   npm
-   Make

No Windows, use o Git Bash (Git for Windows) com GNU Make instalado
(por exemplo, `choco install make`). O PowerShell puro não é suportado
pelo Makefile.

## Instalação

Clone o repositório e acesse sua raiz:

``` bash
git clone https://github.com/MatheusNetto1/srs-tour
cd srs-tour
```

Antes de contribuir, leia o [CONTRIBUTING.md](CONTRIBUTING.md) (fluxo de branch, commit, PR e revisão).

Primeiro dia (o mesmo fluxo para todo o time, em Git Bash):

``` bash
make setup   # valida versões, cria backend/.env, instala dependências e browsers do Playwright
make up      # sobe banco, backend e frontend; as migrations rodam sozinhas
```

Pronto: o banco de desenvolvimento já tem as tabelas e o banco de teste
(`srs_tour_test`) já existe. Para rodar `make test`, aplique as migrations no
banco de teste uma vez com `make back-test-migrate`.

O `make setup` executa, em ordem, `make check` (versões mínimas de
`.python-version`, `.nvmrc` e `requires-poetry`, mais Docker), `make env` (copia `backend/.env.example` para
`backend/.env` com uma `SECRET_KEY` aleatória; nunca sobrescreve um `.env`
existente), `make install` e `make front-install-browsers`. Cada passo também
pode ser rodado separadamente.

Para instalar apenas as dependências:

``` bash
make install
```

## Executando com Docker

A maneira mais simples de iniciar todo o ambiente é:

``` bash
make up
```

Para realizar o build das imagens antes de iniciar:

``` bash
make rebuild
```

Os serviços ficam disponíveis em:

  Serviço      Endereço
  ------------ ------------------------------
  Frontend     `http://localhost:5173`
  Backend      `http://localhost:8000`
  Swagger      `http://localhost:8000/docs`
  PostgreSQL   `localhost:5432`

> Se a porta `5432` já estiver em uso na sua máquina, defina outra porta
> externa para o PostgreSQL, por exemplo `POSTGRES_HOST_PORT=5434 make up`
> (ou em um arquivo `.env` na raiz). Ajuste também `DATABASE_URL` e
> `TEST_DATABASE_URL` em `backend/.env` ao executar o backend fora do Docker.
> A comunicação entre containers continua usando `db:5432`.

Ao iniciar, o container do backend aplica `alembic upgrade head` no banco de
desenvolvimento. Depois de puxar migrations novas, rode `make restart` (ou
`make up`) para aplicá-las. `make back-migrate`, no host, também funciona e
migra o mesmo banco (via `localhost`).

O banco de teste `srs_tour_test` é criado automaticamente em volumes novos. Em
um volume antigo, crie-o com `make db-create-test` (idempotente; exige o
container `db` rodando).

Para encerrar os serviços:

``` bash
make down
```

Para acompanhar os logs:

``` bash
make logs
```

Para verificar os containers:

``` bash
make ps
```

## Executando localmente

Primeiro instale as dependências:

``` bash
make install
```

### Backend

``` bash
make back-dev
```

O backend ficará disponível em `http://localhost:8000`.

### Frontend

Em outro terminal:

``` bash
make front-dev
```

O frontend ficará disponível em `http://localhost:5173`.

> Ao executar as aplicações localmente, o PostgreSQL pode continuar
> sendo executado via Docker quando o backend passar a depender do banco
> de dados.

## Qualidade de código

Executar lint de todo o projeto:

``` bash
make lint
```

Formatar backend e frontend:

``` bash
make format
```

Convenção: `*-check` apenas verifica (lint + formato) e `*-lint-fix` /
`*-format` corrigem os arquivos. `make check-all` roda os dois `*-check` e o `make check-pins` (versões de Python, Node e Poetry em sincronia entre os arquivos de pin, Dockerfiles e CI).

Comandos específicos:

``` bash
make back-check
make back-lint-fix
make back-format

make front-check
make front-lint-fix
make front-format
```

## Testes

Executar os testes unitários do backend e frontend:

``` bash
make test
```

Executar todos os testes, incluindo E2E:

``` bash
make test-all
```

Ou executar individualmente, repassando argumentos com `ARGS=`:

``` bash
make back-test ARGS="-k nome"
make front-test ARGS="-t nome"
make front-e2e ARGS="tests/e2e/home.spec.ts"
make front-visual   # regressão visual: só local, fora do `test-all` e do CI
```

O banco de teste precisa estar migrado (`make back-test-migrate`). Os browsers
do Playwright são instalados pelo `make setup` (ou `make front-install-browsers`).

## Build

Build do frontend:

``` bash
make front-build
```

Build das imagens Docker:

``` bash
make build
```

## Verificando o ambiente

Para verificar as ferramentas principais instaladas:

``` bash
make check
```

Para visualizar as versões das principais ferramentas e dependências:

``` bash
make versions
```

Para visualizar todos os comandos disponíveis:

``` bash
make help
```

### Limpeza e reset

Comandos destrutivos exigem `CONFIRM=1`:

``` bash
make clean                 # caches e builds
make clean-all CONFIRM=1   # clean + node_modules + .venv
make db-reset CONFIRM=1    # apaga o volume do Postgres e recria banco, teste e migrations
```

`make seed` já existe, mas ainda não insere dados.

## CI

Todo PR (inclusive empilhado), push em `develop`/`main` e disparo manual rodam:

-   **Backend CI**: Ruff (`make back-check`), versões em sincronia (`make check-pins`), migrations no banco de teste, `alembic check` (falha se um model mudou sem migration), pytest e build da imagem Docker.
-   **Frontend CI**: Biome, Vitest, build e E2E (Playwright). O teste visual não roda no CI.
-   **PR Conventions**: o título do PR deve ser `[Área] [Tipo] Título` (Área: Backend, Frontend, Fullstack, Infra, Docs; Tipo: Feature, Fix, Refactor, Test, Docs, Chore, CI) e a branch `<iniciais>/<tipo>/<descricao-em-kebab-case>` (tipo: feat, fix, refactor, test, docs, chore, ci; iniciais com 2 ou 3 letras minúsculas).

Os workflows chamam os mesmos alvos `make` do uso local. Para rodar um workflow manualmente em qualquer branch:

``` bash
gh workflow run "Backend CI" --ref <branch>
gh workflow run "Frontend CI" --ref <branch>
gh run list --branch <branch>
```

## Agentes de código

O `AGENTS.md` da raiz é a fonte única de instruções para agentes de código (Claude Code, Codex CLI e Gemini CLI). Como confirmar a leitura em cada ferramenta e o que evitar: [CONTRIBUTING.md](CONTRIBUTING.md#agentes-de-código).

## Documentação específica

-   [Guia de contribuição](CONTRIBUTING.md): fluxo de branch, commit, PR, revisão e PRs empilhados
-   [Backend](backend/README.md)
-   [Frontend](frontend/README.md)
