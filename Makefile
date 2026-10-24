# ==========================================
# SRS Tour - Makefile
# ==========================================
# Requer GNU Make e um shell POSIX (Git Bash no Windows).
# Convenção: cada alvo público tem um comentário `## descrição` na mesma linha
# e aparece em `make help`. Alvos internos ficam sem `##`.
# Semântica: *-check = verificação somente leitura (lint + formato);
# *-lint-fix e *-format = corrigem os arquivos.
#
# Acentos: o make nativo do Windows corrompe caracteres não ASCII passados a
# comandos de receita (`echo "não"` sai com mojibake). Mensagens com acento usam
# $(error)/$(info), que o make imprime direto, ou scripts Python (com
# PYTHONUTF8=1). Dentro de `echo`, escreva só ASCII.

.DEFAULT_GOAL := help

.PHONY: \
	help check check-pins versions setup env require-env \
	install install-back install-front \
	up down restart build rebuild logs logs-back logs-front logs-db ps \
	db-create-test \
	back-dev back-lock back-lint back-lint-fix back-format back-format-check \
	back-check back-test back-test-verbose \
	back-migration back-migrate back-migrate-down back-migrations \
	back-test-migrate back-test-migrate-only \
	back-migration-current back-migration-heads back-migration-check \
	seed \
	front-dev front-lint front-lint-fix front-format front-format-check \
	front-check front-build front-install-browsers \
	front-test front-test-watch front-e2e front-visual front-visual-update \
	lint lint-fix format format-check check-all test test-all \
	clean clean-back clean-front clean-all db-reset


# ------------------------------------------
# Variáveis
# ------------------------------------------

BACKEND_DIR := backend
FRONTEND_DIR := frontend

# Evita mojibake na saída dos scripts Python no Git Bash (stdout padrão é cp1252).
export PYTHONUTF8 := 1

PYTHON ?= python
POETRY := cd $(BACKEND_DIR) && poetry
BACK_RUN := cd $(BACKEND_DIR) && poetry run
FRONT_RUN := cd $(FRONTEND_DIR) && npm run

DB_USER ?= postgres
TEST_DB_NAME ?= srs_tour_test

# Argumentos extras do `playwright install`; no Linux/CI: --with-deps
PLAYWRIGHT_INSTALL_ARGS ?=

# Argumentos extras repassados aos alvos de teste: make back-test ARGS="-k nome"
ARGS ?=

# Confirmação exigida pelos alvos destrutivos: make clean-all CONFIRM=1
CONFIRM ?=

# Falha com mensagem se CONFIRM=1 não foi informado.
# $(1) alvo, $(2) o que será destruído (sem vírgulas).
define require_confirm
$(if $(filter 1,$(CONFIRM)),,$(error Erro: 'make $(1)' é destrutivo: $(2). Se é isso mesmo que você quer: make $(1) CONFIRM=1))
endef


##!
##! SRS Tour - comandos disponíveis
##! Primeiro dia: make setup && make up

##@ Ambiente

help: ## Lista os comandos disponíveis
	@awk 'BEGIN { FS = ":.*## " } \
		/^##!/ { print substr($$0, 5) } \
		/^##@/ { printf "\n%s\n", substr($$0, 5) } \
		/^[a-zA-Z0-9_-]+:.*## / { printf "  make %-24s %s\n", $$1, $$2 } \
		END { print "" }' \
		$(MAKEFILE_LIST)

check: ## Valida ferramentas e versões mínimas (.python-version, .nvmrc, requires-poetry)
	$(if $(shell command -v $(PYTHON) 2>/dev/null),,$(error Erro: Python não encontrado no PATH (mínimo 3.12)))
	@$(PYTHON) $(BACKEND_DIR)/scripts/check_env.py

check-pins: ## Confere se .nvmrc, .python-version, Dockerfiles e CI usam as mesmas versões
	@$(PYTHON) $(BACKEND_DIR)/scripts/check_pins.py

versions: ## Exibe versões do ambiente e das dependências
	@echo "=========================================="
	@echo " Ambiente"
	@echo "=========================================="
	@docker --version
	@$(PYTHON) --version
	@poetry --version
	@node --version
	@npm --version
	@echo ""
	@echo "=========================================="
	@echo " Backend"
	@echo "=========================================="
	@$(BACK_RUN) python --version
	@$(POETRY) show fastapi
	@$(POETRY) show sqlalchemy
	@$(POETRY) show alembic
	@$(POETRY) show pydantic-settings
	@$(POETRY) show uvicorn
	@$(POETRY) show ruff
	@$(POETRY) show pytest
	@$(POETRY) show httpx2
	@echo ""
	@echo "=========================================="
	@echo " Frontend"
	@echo "=========================================="
	@cd $(FRONTEND_DIR) && npm list --depth=0 \
		react \
		react-dom \
		vite \
		typescript \
		tailwindcss \
		@tailwindcss/vite \
		@biomejs/biome \
		vitest \
		@playwright/test \
		@testing-library/react \
		@testing-library/jest-dom \
		jsdom

setup: check env install front-install-browsers ## Primeiro dia: check + env + install + browsers do Playwright
	$(info Setup concluído. Próximo passo: make up)

env: ## Cria backend/.env com SECRET_KEY aleatória (não sobrescreve)
	@$(PYTHON) $(BACKEND_DIR)/scripts/init_env.py

# Interno: falha com mensagem clara se o backend/.env não existir.
require-env:
	$(if $(wildcard $(BACKEND_DIR)/.env),,$(error Erro: $(BACKEND_DIR)/.env não existe. Rode: make env))


# ==========================================
# Instalação
# ==========================================

install: install-back install-front ## Instala backend e frontend

install-back: ## Instala dependências do backend (Poetry)
	@$(POETRY) install

install-front: ## Instala dependências do frontend (npm ci)
	@cd $(FRONTEND_DIR) && npm ci


##@ Docker

up: require-env ## Sobe db, backend e frontend (o backend aplica as migrations ao iniciar)
	@docker compose up -d

down: ## Derruba os containers
	@docker compose down

restart: ## Reinicia os containers (o backend reaplica as migrations)
	@docker compose restart

build: ## Faz build das imagens
	@docker compose build

rebuild: require-env ## Rebuilda as imagens e sobe os containers (renova o node_modules do frontend)
	@docker compose up -d --build --renew-anon-volumes

logs: ## Acompanha todos os logs
	@docker compose logs -f

logs-back: ## Acompanha os logs do backend
	@docker compose logs -f backend

logs-front: ## Acompanha os logs do frontend
	@docker compose logs -f frontend

logs-db: ## Acompanha os logs do PostgreSQL
	@docker compose logs -f db

ps: ## Lista os containers
	@docker compose ps

db-create-test: ## Cria o banco de teste no container db (idempotente)
	$(if $(findstring db,$(shell docker compose ps --status running --services 2>/dev/null)),,$(error Erro: o container 'db' não está rodando. Suba o ambiente com: make up))
	@if docker compose exec -T db psql -U $(DB_USER) -tAc \
		"SELECT 1 FROM pg_database WHERE datname = '$(TEST_DB_NAME)'" | grep -q 1; then \
		echo "Banco '$(TEST_DB_NAME)' ja existe."; \
	else \
		docker compose exec -T db createdb -U $(DB_USER) $(TEST_DB_NAME) \
			&& echo "Banco '$(TEST_DB_NAME)' criado."; \
	fi


##@ Backend

back-dev: require-env ## Inicia o FastAPI localmente (uvicorn --reload)
	@$(BACK_RUN) uvicorn app.main:app --reload

back-lock: ## Atualiza o poetry.lock
	@$(POETRY) lock

back-lint: ## Lint com Ruff (somente leitura)
	@$(BACK_RUN) ruff check .

back-lint-fix: ## Corrige problemas de lint com Ruff
	@$(BACK_RUN) ruff check --fix .

back-format: ## Formata o código com Ruff
	@$(BACK_RUN) ruff format .

back-format-check: ## Verifica a formatação sem alterar arquivos
	@$(BACK_RUN) ruff format --check .

back-check: back-lint back-format-check ## Verificação somente leitura: lint + formato

back-test: ## Executa os testes (ARGS="-k nome")
	@$(BACK_RUN) pytest $(ARGS)

back-test-verbose: ## Executa os testes com saída detalhada (ARGS="-k nome")
	@$(BACK_RUN) pytest -v $(ARGS)

back-migration: ## Cria migration numerada (m="create x table")
	$(if $(m),,$(error Erro: informe a mensagem da migration. Exemplo: make back-migration m="create users table"))
	@$(BACK_RUN) python scripts/create_migration.py "$(m)"

back-migrate: ## Aplica as migrations no banco de desenvolvimento
	@$(BACK_RUN) alembic upgrade head

back-migrate-down: ## Reverte a última migration
	@$(BACK_RUN) alembic downgrade -1

back-test-migrate: db-create-test back-test-migrate-only ## Cria (se preciso) e migra o banco de teste

back-test-migrate-only: ## Migra o banco de teste sem criá-lo (CI, onde o Postgres não é o Compose)
	@$(BACK_RUN) python -m scripts.migrate_test_db

back-migrations: ## Exibe o histórico de migrations
	@$(BACK_RUN) alembic history

back-migration-current: ## Exibe a revisão atual do banco
	@$(BACK_RUN) alembic current

back-migration-heads: ## Exibe as heads das migrations
	@$(BACK_RUN) alembic heads

back-migration-check: ## Verifica se os models divergem das migrations
	@$(BACK_RUN) alembic check

seed: ## Popula o banco de desenvolvimento (estrutura pronta, sem dados ainda)
	@$(BACK_RUN) python -m scripts.seed


##@ Frontend

front-dev: ## Inicia o Vite localmente
	@$(FRONT_RUN) dev

front-lint: ## Lint com Biome (somente leitura)
	@cd $(FRONTEND_DIR) && npx biome lint .

front-lint-fix: ## Corrige lint, formato e imports com Biome
	@$(FRONT_RUN) lint:fix

front-format: ## Formata o código com Biome
	@$(FRONT_RUN) format

front-format-check: ## Verifica a formatação sem alterar arquivos
	@cd $(FRONTEND_DIR) && npx biome format .

front-check: ## Verificação somente leitura: lint + formato + imports
	@cd $(FRONTEND_DIR) && npx biome check .

front-build: ## Gera o build de produção
	@$(FRONT_RUN) build

front-install-browsers: ## Instala o Chromium do Playwright (CI: PLAYWRIGHT_INSTALL_ARGS=--with-deps)
	@cd $(FRONTEND_DIR) && npx playwright install $(PLAYWRIGHT_INSTALL_ARGS) chromium

front-test: ## Executa o Vitest uma vez (ARGS="-t nome")
	@$(FRONT_RUN) test:run -- $(ARGS)

front-test-watch: ## Executa o Vitest em watch mode
	@$(FRONT_RUN) test

front-e2e: ## Executa o Playwright E2E (ARGS="tests/e2e/home.spec.ts")
	@$(FRONT_RUN) test:e2e -- $(ARGS)

front-visual: ## Compara com os snapshots visuais (só local, fora do CI)
	@$(FRONT_RUN) test:visual -- $(ARGS)

front-visual-update: ## Regera snapshots (exige VISUAL_BASE_URL e VISUAL_ROUTE_MODE)
	$(if $(and $(VISUAL_BASE_URL),$(VISUAL_ROUTE_MODE)),,$(error Erro: defina VISUAL_BASE_URL e VISUAL_ROUTE_MODE antes de regerar os snapshots. Sem elas o baseline seria sobrescrito com o app atual, não com o protótipo. Exemplo: VISUAL_BASE_URL=http://localhost:5199 VISUAL_ROUTE_MODE=hash make front-visual-update. Roteiro completo: frontend/tests/visual/README.md))
	@$(FRONT_RUN) test:visual:update


##@ Projeto

lint: back-lint front-lint ## Lint (somente leitura) no backend e no frontend

lint-fix: back-lint-fix front-lint-fix ## Corrige lint no backend e no frontend

format: back-format front-format ## Formata backend e frontend

format-check: back-format-check front-format-check ## Verifica a formatação do projeto

check-all: back-check front-check check-pins ## Todas as verificações estáticas (somente leitura)

test: back-test front-test ## Testes do backend + frontend (sem E2E)

test-all: back-test front-test front-e2e ## Testes incluindo E2E (sem visual, que é só local)


##@ Limpeza

clean: clean-back clean-front ## Remove caches e arquivos gerados
	$(info Limpeza concluída.)

clean-back: ## Remove caches do backend
	@echo "Limpando arquivos do backend..."
	@find $(BACKEND_DIR) -type d -name "__pycache__" -prune -exec rm -rf {} +
	@find $(BACKEND_DIR) -type f -name "*.pyc" -delete
	@find $(BACKEND_DIR) -type f -name "*.pyo" -delete
	@rm -rf $(BACKEND_DIR)/.pytest_cache
	@rm -rf $(BACKEND_DIR)/.ruff_cache
	@rm -rf $(BACKEND_DIR)/htmlcov
	@rm -f $(BACKEND_DIR)/.coverage

clean-front: ## Remove build e relatórios do frontend
	@echo "Limpando arquivos do frontend..."
	@rm -rf $(FRONTEND_DIR)/dist
	@rm -rf $(FRONTEND_DIR)/coverage
	@rm -rf $(FRONTEND_DIR)/test-results
	@rm -rf $(FRONTEND_DIR)/playwright-report

clean-all: ## DESTRUTIVO: clean + node_modules + .venv (exige CONFIRM=1)
	$(call require_confirm,clean-all,remove caches e builds mais $(FRONTEND_DIR)/node_modules e $(BACKEND_DIR)/.venv)
	@$(MAKE) --no-print-directory clean
	@rm -rf $(FRONTEND_DIR)/node_modules
	@rm -rf $(BACKEND_DIR)/.venv
	@echo "Pronto. Para reinstalar as dependencias: make install"

db-reset: ## DESTRUTIVO: recria o volume do banco, o banco de teste e as migrations (exige CONFIRM=1)
	$(call require_confirm,db-reset,apaga o volume do PostgreSQL e TODOS os dados locais)
	@docker compose down -v
	@docker compose up -d --wait db
	@$(MAKE) --no-print-directory db-create-test
	@$(MAKE) --no-print-directory back-migrate
	@$(MAKE) --no-print-directory back-test-migrate
	@echo "Banco recriado e migrado. Suba o restante com: make up"
