# ==========================================
# SRS Tour - Makefile
# ==========================================

.DEFAULT_GOAL := help

.PHONY: \
	help check versions \
	install install-back install-front \
	up down restart build rebuild logs logs-back logs-front logs-db ps \
	back-dev back-lock back-lint back-lint-fix back-format back-format-check \
	back-check back-test back-test-verbose back-test-coverage \
	back-migration back-migrate back-migrate-down back-migrations \
	back-migration-current back-migration-heads back-migration-check \
	front-dev front-lint front-lint-fix front-format front-format-check \
	front-check front-build front-test front-test-watch front-e2e \
	lint lint-fix format format-check check-all test test-all \
	clean clean-back clean-front


# ------------------------------------------
# Variáveis
# ------------------------------------------

BACKEND_DIR := backend
FRONTEND_DIR := frontend

POETRY := cd $(BACKEND_DIR) && poetry
BACK_RUN := cd $(BACKEND_DIR) && poetry run
FRONT_RUN := cd $(FRONTEND_DIR) && npm run


# ==========================================
# Ajuda
# ==========================================

help:
	@echo ""
	@echo "SRS Tour - comandos disponíveis"
	@echo ""
	@echo "Ambiente"
	@echo "  make check                Verifica ferramentas principais"
	@echo "  make versions             Exibe versões do ambiente e dependências"
	@echo "  make install              Instala backend e frontend"
	@echo "  make install-back         Instala dependências do backend"
	@echo "  make install-front        Instala dependências do frontend"
	@echo ""
	@echo "Docker"
	@echo "  make up                   Sobe os containers em background"
	@echo "  make down                 Derruba os containers"
	@echo "  make restart              Reinicia os containers"
	@echo "  make build                Faz build das imagens"
	@echo "  make rebuild              Rebuilda e sobe os containers"
	@echo "  make logs                 Acompanha todos os logs"
	@echo "  make logs-back            Acompanha logs do backend"
	@echo "  make logs-front           Acompanha logs do frontend"
	@echo "  make logs-db              Acompanha logs do PostgreSQL"
	@echo "  make ps                   Lista os containers"
	@echo ""
	@echo "Backend"
	@echo "  make back-dev             Inicia FastAPI localmente"
	@echo "  make back-lock            Atualiza poetry.lock"
	@echo "  make back-lint            Verifica lint com Ruff"
	@echo "  make back-lint-fix        Corrige problemas de lint"
	@echo "  make back-format          Formata código com Ruff"
	@echo "  make back-format-check    Verifica formatação sem alterar arquivos"
	@echo "  make back-check           Executa lint e format check"
	@echo "  make back-test            Executa testes"
	@echo "  make back-test-verbose    Executa testes detalhados"
	@echo "  make back-migration       Cria migration (m=\"mensagem\")"
	@echo "  make back-migrate         Aplica migrations"
	@echo "  make back-migrate-down    Reverte última migration"
	@echo "  make back-migrations      Exibe histórico de migrations"
	@echo ""
	@echo "Frontend"
	@echo "  make front-dev            Inicia Vite localmente"
	@echo "  make front-lint           Verifica lint com Biome"
	@echo "  make front-lint-fix       Corrige problemas com Biome"
	@echo "  make front-format         Formata código com Biome"
	@echo "  make front-format-check   Verifica formatação sem alterar arquivos"
	@echo "  make front-check          Executa verificações do Biome"
	@echo "  make front-build          Gera build de produção"
	@echo "  make front-test           Executa Vitest"
	@echo "  make front-test-watch     Executa Vitest em watch mode"
	@echo "  make front-e2e            Executa Playwright"
	@echo ""
	@echo "Projeto"
	@echo "  make lint                 Executa lint no backend e frontend"
	@echo "  make lint-fix             Corrige lint no backend e frontend"
	@echo "  make format               Formata backend e frontend"
	@echo "  make format-check         Verifica formatação do projeto"
	@echo "  make check-all            Executa todas as verificações estáticas"
	@echo "  make test                 Executa testes backend + frontend"
	@echo "  make test-all             Executa testes incluindo E2E"
	@echo "  make clean                Remove caches e arquivos gerados"
	@echo ""


# ==========================================
# Ambiente
# ==========================================

check:
	@echo "Verificando ferramentas..."
	@docker --version
	@python --version
	@poetry --version
	@node --version
	@npm --version
	@echo ""
	@echo "Ambiente OK."


versions:
	@echo "=========================================="
	@echo " Ambiente"
	@echo "=========================================="
	@docker --version
	@python --version
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


# ==========================================
# Instalação
# ==========================================

install: install-back install-front

install-back:
	@$(POETRY) install

install-front:
	@cd $(FRONTEND_DIR) && npm ci


# ==========================================
# Docker
# ==========================================

up:
	@docker compose up -d

down:
	@docker compose down

restart:
	@docker compose restart

build:
	@docker compose build

rebuild:
	@docker compose up -d --build

logs:
	@docker compose logs -f

logs-back:
	@docker compose logs -f backend

logs-front:
	@docker compose logs -f frontend

logs-db:
	@docker compose logs -f db

ps:
	@docker compose ps


# ==========================================
# Backend - Desenvolvimento
# ==========================================

back-dev:
	@$(BACK_RUN) uvicorn app.main:app --reload

back-lock:
	@$(POETRY) lock


# ==========================================
# Backend - Qualidade
# ==========================================

back-lint:
	@$(BACK_RUN) ruff check .

back-lint-fix:
	@$(BACK_RUN) ruff check --fix .

back-format:
	@$(BACK_RUN) ruff format .

back-format-check:
	@$(BACK_RUN) ruff format --check .

back-check: back-lint back-format-check


# ==========================================
# Backend - Testes
# ==========================================

back-test:
	@$(BACK_RUN) pytest

back-test-verbose:
	@$(BACK_RUN) pytest -v


# ==========================================
# Backend - Banco de dados / Alembic
# ==========================================

back-migration:
	@if [ -z "$(m)" ]; then \
		echo 'Erro: informe a mensagem da migration.'; \
		echo 'Exemplo: make back-migration m="create users table"'; \
		exit 1; \
	fi
	@$(BACK_RUN) python scripts/create_migration.py "$(m)"

back-migrate:
	@$(BACK_RUN) alembic upgrade head

back-migrate-down:
	@$(BACK_RUN) alembic downgrade -1

back-migrations:
	@$(BACK_RUN) alembic history

back-migration-current:
	@$(BACK_RUN) alembic current

back-migration-heads:
	@$(BACK_RUN) alembic heads

back-migration-check:
	@$(BACK_RUN) alembic check


# ==========================================
# Frontend - Desenvolvimento
# ==========================================

front-dev:
	@$(FRONT_RUN) dev


# ==========================================
# Frontend - Qualidade
# ==========================================

front-lint:
	@$(FRONT_RUN) lint

front-lint-fix:
	@$(FRONT_RUN) lint:fix

front-format:
	@$(FRONT_RUN) format

front-format-check:
	@cd $(FRONTEND_DIR) && npx biome format .

front-check:
	@cd $(FRONTEND_DIR) && npx biome check .


# ==========================================
# Frontend - Build
# ==========================================

front-build:
	@$(FRONT_RUN) build


# ==========================================
# Frontend - Testes
# ==========================================

front-test:
	@$(FRONT_RUN) test:run

front-test-watch:
	@$(FRONT_RUN) test

front-e2e:
	@$(FRONT_RUN) test:e2e


# ==========================================
# Projeto - Qualidade
# ==========================================

lint: back-lint front-lint

lint-fix: back-lint-fix front-lint-fix

format: back-format front-format

format-check: back-format-check front-format-check

check-all: back-check front-check


# ==========================================
# Projeto - Testes
# ==========================================

test: back-test front-test

test-all: back-test front-test front-e2e


# ==========================================
# Limpeza
# ==========================================

clean: clean-back clean-front
	@echo "Limpeza concluída."


clean-back:
	@echo "Limpando arquivos do backend..."
	@find $(BACKEND_DIR) -type d -name "__pycache__" -prune -exec rm -rf {} +
	@find $(BACKEND_DIR) -type f -name "*.pyc" -delete
	@find $(BACKEND_DIR) -type f -name "*.pyo" -delete
	@rm -rf $(BACKEND_DIR)/.pytest_cache
	@rm -rf $(BACKEND_DIR)/.ruff_cache
	@rm -rf $(BACKEND_DIR)/htmlcov
	@rm -f $(BACKEND_DIR)/.coverage


clean-front:
	@echo "Limpando arquivos do frontend..."
	@rm -rf $(FRONTEND_DIR)/dist
	@rm -rf $(FRONTEND_DIR)/coverage
	@rm -rf $(FRONTEND_DIR)/test-results
	@rm -rf $(FRONTEND_DIR)/playwright-report