# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Visão geral

Monorepo full stack para turismo: `backend/` (FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL, gerenciado com Poetry, `package-mode = false`) e `frontend/` (React 19 + Vite + Tailwind 4 + TypeScript, ainda praticamente um esqueleto). A documentação e as mensagens de commit do projeto são escritas em PT-BR.

## Comandos

Todos os comandos `make` são executados a partir da raiz (`make help` lista todos). Eles fazem `cd backend && poetry run ...` ou `cd frontend && npm run ...` internamente.

```bash
make install            # poetry install + npm ci
make up / make rebuild  # sobe db, backend e frontend via Docker Compose
make back-dev           # uvicorn app.main:app --reload (porta 8000, Swagger em /docs)
make front-dev          # Vite (porta 5173)

make lint / make format / make check-all
make back-check         # ruff check + ruff format --check (o mesmo que o CI roda)
make front-check        # biome check .

make test               # pytest + vitest
make test-all           # inclui Playwright E2E (inicia o Vite automaticamente)
make back-test-migrate  # aplica as migrations no banco de TEST_DATABASE_URL; make back-test não executa migrations

make back-migration m="create users table"   # autogenerate + renomeia para 0002_create_users_table.py
make back-migrate                            # alembic upgrade head
make back-migrate-down                       # alembic downgrade -1
```

Executar um único teste:

```bash
cd backend && poetry run pytest tests/integration/tourism/test_establishments.py::test_create_establishment
cd frontend && npx vitest run src/App.test.tsx -t "nome do teste"
cd frontend && npx playwright test tests/e2e/home.spec.ts
```

Observação: o README cita `make front-fix`, mas o alvo real é `make front-lint-fix`.

## Configuração e banco de dados

- `backend/app/core/config.py` usa `pydantic-settings` lendo `backend/.env` (copiar de `.env.example`). `DATABASE_URL` e `SECRET_KEY` são obrigatórios; importar qualquer módulo de `app` sem eles falha.
- No Docker Compose, `DATABASE_URL` é sobrescrito para apontar para o host `db`.
- **Testes exigem um PostgreSQL real**: `tests/conftest.py` aborta se `TEST_DATABASE_URL` não estiver definido ou se o nome do banco não terminar em `_test`. Como o conftest é carregado em toda a suíte, até `test_health.py` depende disso. O banco de teste precisa existir e estar migrado: use `make back-test-migrate` (o CI faz o equivalente com `alembic upgrade head`).
- O fixture `db_session` usa sessões reais com commit e faz limpeza ao final com `DELETE` explícito por tabela. **Ao criar um novo model, adicione a limpeza da tabela correspondente no `db_session`**, senão os dados vazam entre testes. O fixture `client` substitui `get_db` via `app.dependency_overrides`.

## Arquitetura do backend

- `app/main.py` cria o app, expõe `GET /health` e monta `api_router` em `/api/v1`.
- `app/api/v1/router.py` agrega os routers de cada domínio com prefixo e tag. Estão registrados `tourism`, `users` e `indicators`; `auth` e `reports` continuam planejados e comentados — o padrão é um pacote por domínio em `app/<dominio>/`.
- Cada domínio segue camadas fixas (ver `app/tourism/`):
  - `models.py` — models SQLAlchemy 2 (`Mapped`/`mapped_column`) herdando de `app.core.database.Base`.
  - `schemas.py` — Pydantic: `XCreate`, `XUpdate`, `XResponse` (`from_attributes=True`).
  - `repository.py` — acesso a dados puro; recebe `Session`, faz `commit`/`refresh`.
  - `service.py` — regras de negócio; chama o repository e lança exceções de domínio, sem depender de FastAPI/HTTP. Elas herdam de `NotFoundError`/`ConflictError` (`app/core/errors.py`), ficam em `exceptions.py` do domínio com um `code` estável (ex.: `user.not_found`), e o handler global as converte em 404/409. As mensagens HTTP (PT-BR) ficam centralizadas em `app/core/messages.py`. `tourism` ainda usa `HTTPException` diretamente (padrão antigo); Users e Indicators seguem o padrão de exceções de domínio.
  - `router.py` — endpoints finos que recebem `db: DbSession` (de `app/core/dependencies.py`) e delegam ao service.
- **Novos models devem ser importados em `app/models.py`**: é esse módulo que `alembic/env.py` importa para que o autogenerate enxergue o metadata.
- Migrations usam numeração sequencial (`0001_...py`) gerada por `scripts/create_migration.py`; use `make back-migration` em vez de `alembic revision` direto.
- Exclusão de estabelecimentos é lógica (`DELETE` marca `is_active = False`).
- `app/core/security.py` já contém hash de senha (pwdlib/argon2) e criação de JWT (PyJWT), ainda não usados por nenhuma rota.
- Ruff: line-length 88, regras `E, F, I, UP, B`, alvo py312.

## Frontend

- Biome para lint/format (indentação com tabs, aspas duplas, organize imports). Não usar ESLint/Prettier.
- Vitest com jsdom e setup em `src/test/setup.ts`; testes E2E ficam em `tests/e2e/` e são excluídos do Vitest.

## CI e fluxo Git

- `.github/workflows/backend-ci.yml` roda em PRs/push para `main` e `develop` quando `backend/**` muda: ruff lint + format check, pytest contra um serviço Postgres (`srs_tour_test`) após `alembic upgrade head`, e build da imagem Docker. Não há CI de frontend ainda.
- `labeler.yml` rotula PRs automaticamente por área (`area: backend`, `area: frontend`, etc.).
- Commits seguem Conventional Commits com escopo e descrição em PT-BR (ex.: `feat(tourism): adiciona CRUD de estabelecimentos turisticos`). Branches no formato `mn/<tipo>/<descricao>`.

## Regras para alterações

- Antes de criar novos arquivos ou abstrações, verifique se já existe um padrão equivalente no projeto.
- Preserve a arquitetura existente; não introduza novas camadas, bibliotecas ou padrões sem necessidade explícita.
- Prefira alterações pequenas e focadas ao invés de refatorações amplas não solicitadas.
- Não altere arquivos fora do escopo da tarefa apenas para "melhorar" ou reorganizar código existente.
- Não adicione dependências sem justificar a necessidade.
- Não edite migrations já aplicadas/commitadas; crie uma nova migration.
- Não altere contratos públicos de endpoints existentes sem necessidade explícita.
- Ao modificar comportamento, adicione ou atualize os testes correspondentes.
- Execute os checks relevantes antes de considerar a tarefa concluída.

## Checklist antes de concluir uma alteração

Backend:

1. `make back-check`
2. `make back-test`
3. Se models foram alterados, verificar se existe migration correspondente.
4. Se uma migration foi criada, revisar manualmente o arquivo gerado.

Frontend:

1. `make front-check`
2. `make front-test`
3. Para alterações que afetam fluxos cobertos por E2E, executar os testes Playwright relevantes.

Alterações full stack:

1. `make check-all`
2. `make test-all`

Não considere uma tarefa concluída se algum check relevante estiver falhando. Não silencie ou remova testes para fazer a suíte passar.

## Convenções da API

- Todos os endpoints de domínio ficam sob `/api/v1`.
- Use substantivos no plural nos paths (`/establishments`, `/users`, `/reports`).
- Routers devem conter apenas responsabilidades HTTP: validação de entrada, dependências e delegação ao service.
- Regras de negócio pertencem ao service.
- Queries e persistência pertencem ao repository.
- Não acessar `Session` diretamente no router além de repassá-la às camadas apropriadas.
- Responses devem usar schemas Pydantic explícitos.
- Não retornar models SQLAlchemy diretamente sem schema de resposta.
- Use os status HTTP semanticamente apropriados (`201` para criação, `204` quando não houver corpo etc.).
- Erros esperados da aplicação devem possuir status HTTP e mensagem consistentes.

## Convenções de testes

Backend:

- Testes devem espelhar o domínio testado.
- Prefira testes de comportamento observável ao invés de testar detalhes internos de implementação.
- Para endpoints, cubra pelo menos o caminho de sucesso e os principais erros esperados.
- Não mockar o banco nos testes de integração; eles usam PostgreSQL real através de `TEST_DATABASE_URL`.
- Todo teste deve ser independente da ordem de execução.
- Dados criados por um teste não podem ser necessários para outro teste.
- Organização: testes de integração ficam em `backend/tests/integration/<dominio>/test_<recurso>.py`; testes unitários (sem banco) em `backend/tests/unit/<modulo>/`. O teste de health fica em `backend/tests/test_health.py`.
- Testes de integração usam as fixtures compartilhadas `client` e `db_session` de `tests/conftest.py`. Não crie `TestClient(app)`, engines ou sessões próprias nos módulos de teste, e não use SQLite, `Base.metadata.create_all()` ou `drop_all()` no lugar do PostgreSQL migrado.
- O schema do banco de teste é aplicado separadamente por `make back-test-migrate`, que usa somente `TEST_DATABASE_URL` (nunca `DATABASE_URL`) e recusa bancos que não terminem em `_test`. O `make back-test` não executa migrations: rode `make back-test-migrate` depois de criar ou alterar migrations.
- Todo novo model deve entrar no cleanup do `db_session` (ver "Configuração e banco de dados"). `make back-test` deve poder ser executado várias vezes seguidas sem acumular dados.
- Asserts de status HTTP usam `from fastapi import status` e `status.HTTP_*` (por exemplo `status.HTTP_201_CREATED`, `status.HTTP_422_UNPROCESSABLE_CONTENT`), nunca números literais.
- Estilo dos módulos de integração: constante `BASE_URL` com o path do recurso, helpers de módulo (`create_<entidade>(client, ...)`) em vez de fixtures de entidade, e testes anotados com `client: TestClient` e `-> None`.
- Quando o comportamento envolve persistência (hash de senha, normalização, exclusão lógica), confirme também no banco via `db_session`. Como `client` e `db_session` compartilham a mesma sessão, use `db_session.expire_all()` quando o teste precisar garantir que observa o estado recarregado do PostgreSQL e não o identity map da sessão (não é obrigatório em toda releitura).

Frontend:

- Vitest/Testing Library para testes de componentes e integração.
- Playwright para fluxos completos observáveis pelo usuário.
- Prefira queries acessíveis do Testing Library (`getByRole`, `getByLabelText`, etc.) em vez de seletores ligados à implementação.

## Segurança

- Nunca commitar `.env`, secrets, tokens, senhas ou chaves privadas.
- Nunca incluir valores reais de secrets em testes, fixtures, logs ou documentação.
- Senhas nunca devem ser armazenadas ou comparadas em texto puro; use as funções de `app/core/security.py`.
- Não implementar criptografia, hashing ou JWT manualmente quando já existir utilitário no projeto.
- Não confiar em IDs, roles ou permissões enviados pelo cliente sem validação no backend.
- Não expor detalhes internos de exceções, banco ou stack traces através da API.

## Soft delete

Estabelecimentos usam exclusão lógica através de `is_active`.

- `DELETE` não remove fisicamente o registro.
- Queries públicas devem ignorar registros inativos por padrão.
- Não reutilizar registros inativos implicitamente.
- Testes de listagem/busca devem verificar que registros inativos não são retornados quando aplicável.

## Regras de migrations

- Nunca criar migrations manualmente quando `make back-migration` atender ao caso.
- Sempre revisar migrations autogeradas antes de executá-las.
- Não modificar uma migration já integrada ao histórico compartilhado; crie outra migration corretiva.
- Alterações em models persistidos devem incluir a migration correspondente.
- Não usar `Base.metadata.create_all()` como substituto para Alembic.
- Migrations devem ser determinísticas e não depender de estado externo à base.