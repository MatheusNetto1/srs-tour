# AGENTS.md

Instruções para agentes de código neste repositório. Fonte única: não crie `CLAUDE.md`, `GEMINI.md` nem `CLAUDE.local.md`.

## Visão geral

Monorepo de turismo: `backend/` (FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, Poetry, Python 3.12, `package-mode = false`) e `frontend/` (React 19, Vite, Tailwind 4, TypeScript, React Router, Recharts, Node 24). Documentação, commits e mensagens HTTP em PT-BR.

## Comandos

Rode tudo a partir da raiz (`make help` lista todos; cada alvo se documenta com `## descrição` no Makefile).

```bash
make setup              # 1º dia: check + env (backend/.env) + install + browsers do Playwright
make up / make rebuild  # db, backend e frontend via Docker Compose (o backend aplica as migrations ao iniciar)
make back-dev           # uvicorn --reload (8000, Swagger em /docs)
make front-dev          # Vite (5173)
make check-all          # ruff (back) + biome (front) + check-pins, somente leitura
make lint-fix / make format
make test               # pytest + vitest
make test-all           # + Playwright E2E (o Vite sobe sozinho); visual fica de fora
make db-create-test     # cria srs_tour_test no container db (idempotente)
make back-test-migrate  # cria o banco de teste se faltar e aplica migrations nele (make back-test não migra)
make back-migration m="create x table"   # autogenerate + numeração 000N_
make back-migrate / make back-migrate-down
make front-api-types    # gera frontend/src/api/schema.d.ts do /openapi.json (exige make up; arquivo ignorado pelo git)
make seed               # estrutura pronta, sem dados ainda
make back-migration-single-head   # falha se houver mais de uma head do Alembic (sem banco; roda no CI)
make docker-seed / docker-back-test / docker-back-test-migrate / docker-back-migration m="..."   # o mesmo dentro do container backend (sem Poetry no host; exigem make up)
make db-reset CONFIRM=1 / make clean-all CONFIRM=1   # destrutivos: exigem CONFIRM=1
```

Dois fluxos para o backend: **Poetry no host** (`back-*`, `seed`) ou **tudo em container** (`docker-*`, que usam `docker compose exec` e falham com mensagem clara se o backend não estiver no ar; `docker-back-test*` usam `TEST_DATABASE_URL` com o host `db`). Aceitam `ARGS=`. O `compose.yml` não fixa `container_name`: para dois clones ao mesmo tempo, mude `COMPOSE_PROJECT_NAME` e as portas `POSTGRES_HOST_PORT`, `BACKEND_HOST_PORT` e `FRONTEND_HOST_PORT` (exemplo em `.env.example`). O frontend em container usa polling (`DEV_USE_POLLING=true`) porque o bind mount do Windows não propaga eventos de arquivo.

Convenção: `*-check` só lê (lint + formato); `*-lint-fix` e `*-format` corrigem. Alvos de teste aceitam `ARGS=` (`make back-test ARGS="-k nome"`). O `front-visual-update` exige `VISUAL_BASE_URL` e `VISUAL_ROUTE_MODE`.

No Makefile, o make nativo do Windows corrompe acento em `echo`: mensagens com acento vão em `$(error)`/`$(info)` ou em script Python; dentro de `echo`, só ASCII.

Teste isolado:

```bash
cd backend && poetry run pytest tests/integration/tourism/test_establishments.py::test_create_establishment
cd frontend && npx vitest run tests/integration/router.test.ts -t "nome"
cd frontend && npx playwright test tests/e2e/home.spec.ts
```

O alvo para corrigir o frontend é `make front-lint-fix`.

## Configuração e banco

- `backend/app/core/config.py` lê `backend/.env` (`make env` cria a partir de `backend/.env.example` com `SECRET_KEY` aleatória, sem sobrescrever). `DATABASE_URL` e `SECRET_KEY` são obrigatórios; importar `app` sem eles falha. `APP_ENV` assume `production`; somente `dev` aceita chave fraca, e os demais ambientes exigem ao menos 32 caracteres e rejeitam `change-me`. No Compose, `DATABASE_URL` aponta para o host `db`; no host, `localhost` (mesmo banco, via porta publicada). O backend do Compose roda `alembic upgrade head` antes do uvicorn.
- Versões: fonte única em `.python-version` e `.nvmrc` (raiz); o mínimo do Poetry é `requires-poetry` em `backend/pyproject.toml`. Workflows e `make check` leem desses arquivos; Dockerfiles repetem em `ARG`. Ao mudar um pin, rode `make check-pins`. O venv do backend é `backend/.venv` (`backend/poetry.toml`).
- Testes exigem PostgreSQL real: `tests/conftest.py` aborta sem `TEST_DATABASE_URL` ou se o nome do banco não terminar em `_test`. O `srs_tour_test` nasce com volume novo (`docker/postgres/init/`); em volume antigo, `make db-create-test`. Ele deve estar migrado: `make back-test-migrate` (o CI usa `alembic upgrade head`).
- `db_session` usa sessão real com commit e limpa cada tabela com `DELETE` no final. Novo model ⇒ adicione a tabela ao cleanup do `db_session`.

## Backend

- Um pacote por domínio em `app/<dominio>/`. `app/api/v1/router.py` registra `auth`, `users`, `indicators`, `reports` e `tourism` sob `/api/v1` e o namespace administrativo `/api/v1/admin/<recurso>`.
- Camadas: `models.py` (`Mapped`/`mapped_column`, herda `app.core.database.Base`), `schemas.py` (`XCreate`/`XUpdate`/`XResponse`, `from_attributes=True`), `repository.py` (acesso a dados, commit/refresh), `service.py` (regras de negócio, sem FastAPI/HTTP), `router.py` (HTTP fino, `db: DbSession` de `app/core/dependencies.py`).
- Erros: exceções de domínio em `exceptions.py` herdam de `NotFoundError`/`ConflictError`/`UnauthorizedError` (`app/core/errors.py`) com `code` estável (ex.: `user.not_found`); o handler global converte em 404/409/401. Mensagens HTTP em `app/core/messages.py`. Código novo usa esse padrão; `tourism` e `reports` ainda usam `HTTPException`/exceção local.
- Novo model: importe em `app/models.py` (usado por `alembic/env.py`) e gere a migration.
- Migrations: sempre `make back-migration`; revise o arquivo gerado; nunca edite migration já integrada (crie outra); nunca `Base.metadata.create_all()` no lugar do Alembic.
- Auth: hash e JWT em `app/core/security.py` (não reimplementar). `User.role` usa `UserRole`; o agrupador `/api/v1/admin` aplica `require_admin` em um único ponto. Rotas que precisam apenas de autenticação recebem `current_user: CurrentUser` (`app/auth/dependencies.py`). O admin inicial é criado de forma idempotente por `make seed`, usando `ADMIN_EMAIL` e `ADMIN_PASSWORD`.
- Soft delete: estabelecimentos usam `is_active`; `DELETE` só desativa; consultas públicas ignoram inativos; nunca reutilizar registro inativo implicitamente.
- Ruff: line-length 88, regras `E,F,I,UP,B`, alvo py312.

## API

Tudo sob `/api/v1`; paths no plural; router só valida entrada, injeta dependências e delega; regras no service, queries no repository; `Session` nunca é usada no router além de repassá-la. Responses com schema Pydantic explícito (nunca model SQLAlchemy); status semânticos (`201` criação, `204` sem corpo). Não altere contratos de endpoints existentes sem necessidade explícita.

## Testes

- Backend: integração em `backend/tests/integration/<dominio>/test_<recurso>.py`; unitários (sem banco) em `backend/tests/unit/<modulo>/`; health em `backend/tests/test_health.py`.
- Use apenas as fixtures `client`, `anonymous_client` e `db_session` de `tests/conftest.py`. `client` substitui `require_admin` por um admin fictício; `anonymous_client` mantém a autenticação real para testes 401/403. Proibido: SQLite, `Base.metadata.create_all()`/`drop_all()`, `TestClient(app)`, engines ou sessões próprias, mock do banco.
- Estilo: constante `BASE_URL`, helpers `create_<entidade>(client, ...)` em vez de fixtures de entidade, testes `(client: TestClient) -> None`, asserts com `status.HTTP_*` (nunca número literal). Cubra o sucesso e os principais erros esperados.
- Persistência (hash, normalização, exclusão lógica): confirme no banco via `db_session`; use `db_session.expire_all()` quando precisar reler do PostgreSQL. Testes independentes da ordem e repetíveis sem acumular dados.
- Frontend: Vitest + Testing Library em `frontend/tests/integration/` (helpers em `tests/utils/`, setup em `tests/setup/vitest.ts`), Playwright em `tests/e2e/`. Prefira `getByRole`/`getByLabelText`.

## Frontend

- Biome para lint e format (tabs, aspas duplas, organize imports); não use ESLint nem Prettier.
- `tsconfig.tests.json` faz `tsc -b` (e `npm run build`) checar `src/` e `tests/`. Rotas em `src/routes/router.tsx` (`createBrowserRouter`).
- Acesso à API só por `src/api/client.ts` (`request`, único ponto de `fetch`); erros chegam como `ApiError` (aceita o envelope `detail`+`code`+`errors` e o formato antigo). O Vite faz proxy de `/api` (`API_PROXY_TARGET`). Dados em componentes: `useApiQuery` + `LoadingState`/`ErrorState`/`EmptyState`. `src/api/schema.d.ts` é gerado e ignorado pelo git. O `overrides` do `openapi-typescript` no `package.json` está explicado em `frontend/README.md`.
- Teste visual (`tests/visual/`) roda só local, fora do CI. Nunca rode `test:visual:update` sem `VISUAL_BASE_URL` e `VISUAL_ROUTE_MODE`: veja [`frontend/tests/visual/README.md`](frontend/tests/visual/README.md).

## Git, PRs e CI

- Branch: `<iniciais>/<tipo>/<descricao-em-kebab-case>`, tipo ∈ `feat | fix | refactor | test | docs | chore | ci`.
- Commit na branch: Conventional Commits em PT-BR, mesmos tipos, escopo opcional (ex.: `feat(tourism): adiciona CRUD de estabelecimentos`).
- Título do PR (vira o commit em `develop` por squash): `[Área] [Tipo] Título`, Área ∈ `Backend | Frontend | Fullstack | Infra | Docs`, Tipo ∈ `Feature | Fix | Refactor | Test | Docs | Chore | CI`.
- **Nunca adicione linha de atribuição a IA** (`Co-Authored-By`, "Generated with…" etc.) em commits, PRs ou descrições, mesmo que a ferramenta tenha esse comportamento por padrão.
- `.gitattributes` mantém LF; CRLF faz o Biome acusar `␍`. Nunca commite `.env`, secrets ou tokens.
- CI: todo PR (qualquer base, inclusive empilhado), push em `main`/`develop` e `workflow_dispatch`; sem filtro de `paths` (checks obrigatórios não podem ficar pendentes). Os workflows chamam alvos `make`, a mesma definição do uso local.
  - `backend-ci.yml`: job `Backend` (`back-check`, `back-migration-single-head`, `back-test-migrate-only`, `back-migration-check`, `back-test`; Postgres é service do Actions, por isso não usa `back-test-migrate`) e `Backend Docker Build`.
  - `frontend-ci.yml`: `Frontend` (`front-check`, `front-test`, `front-build`) e `Frontend E2E` (Playwright; só precisa do Vite). Visual fica fora do CI.
  - `pr-conventions.yml`: reprova PR para `develop`/`main` com título ou branch fora do padrão acima (ignora bots).
  - Disparo manual: `gh workflow run "Backend CI" --ref <branch>` (idem `"Frontend CI"`).

## Regras para alterações

- Procure padrão equivalente no projeto antes de criar arquivos ou abstrações; preserve a arquitetura.
- Alterações pequenas e focadas; não mexa em arquivos fora do escopo; não adicione dependências sem justificar.
- Mudou comportamento ⇒ adicione ou atualize testes. Não silencie nem remova testes para a suíte passar.
- Segurança: não confie em IDs, roles ou permissões vindos do cliente; senhas só via `app/core/security.py`; não exponha stack traces ou detalhes de banco pela API.
- Antes de concluir, rode e confirme: backend `make back-check` e `make back-test`; frontend `make front-check` e `make front-test` (E2E relevante se o fluxo for coberto); full stack `make check-all` e `make test-all`. Model alterado exige migration.
