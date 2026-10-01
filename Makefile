# ==========================================
# SRS Tour - Makefile
# ==========================================

.PHONY: help \
	check versions \
	install install-back install-front \
	up down build rebuild logs ps \
	back-dev front-dev \
	back-lint back-format back-test \
	front-lint front-format front-fix front-build front-test front-e2e \
	lint format test test-all clean

# ------------------------------------------
# Variáveis
# ------------------------------------------

BACKEND_DIR := backend
FRONTEND_DIR := frontend

# ------------------------------------------
# Ajuda
# ------------------------------------------

help:
	@echo "SRS Tour - comandos disponíveis"
	@echo ""
	@echo "Ambiente:"
	@echo "  make check         Verifica ferramentas principais"
	@echo "  make versions      Lista versões das ferramentas/dependências"
	@echo "  make install       Instala backend e frontend"
	@echo ""
	@echo "Docker:"
	@echo "  make up            Sobe os containers"
	@echo "  make down          Derruba os containers"
	@echo "  make build         Build dos containers"
	@echo "  make rebuild       Rebuild e sobe os containers"
	@echo "  make logs          Exibe os logs"
	@echo "  make ps            Lista os containers"
	@echo ""
	@echo "Backend:"
	@echo "  make back-dev      Sobe o backend localmente"
	@echo "  make back-lint     Executa Ruff"
	@echo "  make back-format   Formata com Ruff"
	@echo "  make back-test     Executa Pytest"
	@echo ""
	@echo "Frontend:"
	@echo "  make front-dev     Sobe o Vite"
	@echo "  make front-lint    Executa Biome"
	@echo "  make front-format  Formata com Biome"
	@echo "  make front-fix     Aplica correções do Biome"
	@echo "  make front-build   Build de produção"
	@echo "  make front-test    Executa Vitest"
	@echo "  make front-e2e     Executa Playwright"
	@echo ""
	@echo "Projeto:"
	@echo "  make lint          Executa lint no backend e frontend"
	@echo "  make format        Formata backend e frontend"
	@echo "  make test          Executa testes unitários"
	@echo "  make test-all      Executa todos os testes"
	@echo "  make clean         Remove arquivos gerados"

# ------------------------------------------
# Verificação do ambiente
# ------------------------------------------

check:
	@docker --version
	@python --version
	@poetry --version
	@node --version
	@npm --version

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
	@cd $(BACKEND_DIR) && poetry run python --version
	@cd $(BACKEND_DIR) && echo "FastAPI: $$(poetry show fastapi | grep 'version' | awk '{print $$3}')"
	@cd $(BACKEND_DIR) && echo "Uvicorn: $$(poetry show uvicorn | grep 'version' | awk '{print $$3}')"
	@cd $(BACKEND_DIR) && echo "Ruff: $$(poetry show ruff | grep 'version' | awk '{print $$3}')"
	@cd $(BACKEND_DIR) && echo "Pytest: $$(poetry show pytest | grep 'version' | awk '{print $$3}')"
	@cd $(BACKEND_DIR) && echo "HTTPX: $$(poetry show httpx | grep 'version' | awk '{print $$3}')"
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

# ------------------------------------------
# Instalação
# ------------------------------------------

install: install-back install-front

install-back:
	cd $(BACKEND_DIR) && poetry install

install-front:
	cd $(FRONTEND_DIR) && npm ci

# ------------------------------------------
# Docker
# ------------------------------------------

up:
	@docker compose up

down:
	@docker compose down

build:
	@docker compose build

rebuild:
	@docker compose up --build

logs:
	@docker compose logs -f

ps:
	@docker compose ps

# ------------------------------------------
# Backend
# ------------------------------------------

back-lock:
	@cd $(BACKEND_DIR) && poetry lock

back-dev:
	@cd $(BACKEND_DIR) && poetry run uvicorn app.main:app --reload

back-lint:
	@cd $(BACKEND_DIR) && poetry run ruff check .

back-lint-fix:
	cd backend && poetry run ruff check --fix .

back-format:
	@cd $(BACKEND_DIR) && poetry run ruff format .

back-format-check:
	cd backend && poetry run ruff format --check .

back-test:
	@cd $(BACKEND_DIR) && poetry run pytest

# ------------------------------------------
# Frontend
# ------------------------------------------

front-dev:
	@cd $(FRONTEND_DIR) && npm run dev

front-lint:
	@cd $(FRONTEND_DIR) && npm run lint

front-format:
	@cd $(FRONTEND_DIR) && npm run format

front-fix:
	@cd $(FRONTEND_DIR) && npm run lint:fix

front-build:
	@cd $(FRONTEND_DIR) && npm run build

front-test:
	@cd $(FRONTEND_DIR) && npm run test:run

front-e2e:
	@cd $(FRONTEND_DIR) && npm run test:e2e

# ------------------------------------------
# Comandos agregados
# ------------------------------------------

lint: back-lint front-lint

format: back-format front-format

test: back-test front-test

test-all: back-test front-test front-e2e

# ------------------------------------------
# Limpeza
# ------------------------------------------

clean:
	@rm -rf $(BACKEND_DIR)/.pytest_cache
	@rm -rf $(BACKEND_DIR)/.ruff_cache
	@rm -rf $(FRONTEND_DIR)/dist
	@rm -rf $(FRONTEND_DIR)/test-results
	@rm -rf $(FRONTEND_DIR)/playwright-report