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

## Instalação

Clone o repositório e acesse sua raiz:

``` bash
git clone https://github.com/MatheusNetto1/srs-tour
cd srs-tour
```

Para instalar as dependências do backend e frontend localmente:

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

Comandos específicos:

``` bash
make back-lint
make back-format

make front-lint
make front-format
make front-lint-fix
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

Ou executar individualmente:

``` bash
make back-test
make front-test
make front-e2e
```

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

## Agentes de código

O `AGENTS.md` da raiz é a **fonte única** de instruções para agentes de código (Claude Code, Codex CLI e Gemini CLI). Edite só ele.

-   Não crie `CLAUDE.md`, `GEMINI.md` nem `CLAUDE.local.md`. O Claude Code só lê o `AGENTS.md` quando não existe nenhum `CLAUDE.md` (nem `CLAUDE.local.md`) no diretório de trabalho ou acima dele.
-   **Claude Code**: versão mínima v2.1.277. Confirme com `/memory` (ou pela linha `no CLAUDE.md found; AGENTS.md loaded: ...` no início da sessão).
-   **Codex CLI**: lê o `AGENTS.md` nativamente. Confirme com `codex --ask-for-approval never "Show which instruction files are active."`.
-   **Gemini CLI**: o `.gemini/settings.json` do repositório aponta `context.fileName` para o `AGENTS.md`. Confirme pelo contador de arquivos de contexto no rodapé ou com `/memory show`.
    -   Se o recurso de pastas confiáveis estiver ativo (`security.folderTrust.enabled`, desligado por padrão), o Gemini ignora o `.gemini/settings.json` de pastas não confiáveis. Confie na pasta do projeto com `/permissions` (ou em `~/.gemini/trustedFolders.json`).
-   Regra do time: nenhuma linha de atribuição a IA em commits e PRs. Está no `AGENTS.md` e, no Claude Code, em `.claude/settings.json`.

## Documentação específica

-   [Backend](backend/README.md)
-   [Frontend](frontend/README.md)
