# Makefile para Sistema de Gestão de Eventos
# Facilita comandos comuns de desenvolvimento e deploy

.PHONY: help install dev build test clean docker-build docker-dev docker-prod backup restore

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Default target
help: ## 📋 Mostra esta ajuda
	@echo "$(BLUE)Sistema de Gestão de Eventos - Comandos Disponíveis$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

install: ## 📦 Instala todas as dependências
	@echo "$(BLUE)Instalando dependências...$(RESET)"
	@cd backend && poetry install --with dev
	@cd frontend && npm install
	@echo "$(GREEN)✅ Dependências instaladas$(RESET)"

dev: ## 🚀 Inicia desenvolvimento (backend + frontend)
	@echo "$(BLUE)Iniciando desenvolvimento...$(RESET)"
	@powershell -ExecutionPolicy Bypass -File "start-dev.ps1"

dev-backend: ## 🐍 Inicia apenas o backend
	@echo "$(BLUE)Iniciando backend...$(RESET)"
	@cd backend && poetry run uvicorn app.main:app --reload

dev-frontend: ## ⚛️ Inicia apenas o frontend
	@echo "$(BLUE)Iniciando frontend...$(RESET)"
	@cd frontend && npm run dev

build: ## 🔨 Build para produção
	@echo "$(BLUE)Construindo para produção...$(RESET)"
	@cd frontend && npm run build
	@echo "$(GREEN)✅ Build concluído$(RESET)"

test: ## 🧪 Executa todos os testes
	@echo "$(BLUE)Executando testes...$(RESET)"
	@cd backend && poetry run pytest
	@cd frontend && npm run test
	@echo "$(GREEN)✅ Testes concluídos$(RESET)"

test-backend: ## 🐍 Testes do backend
	@cd backend && poetry run pytest -v

test-frontend: ## ⚛️ Testes do frontend
	@cd frontend && npm run test

type-check: ## 🔍 Verificação de tipos TypeScript
	@echo "$(BLUE)Verificando tipos TypeScript...$(RESET)"
	@cd frontend && npm run type-check

lint: ## 🧹 Linting do código
	@echo "$(BLUE)Executando linting...$(RESET)"
	@cd backend && poetry run flake8 app/
	@cd frontend && npm run lint

format: ## ✨ Formatar código
	@echo "$(BLUE)Formatando código...$(RESET)"
	@cd backend && poetry run black app/
	@cd backend && poetry run isort app/
	@cd frontend && npm run format

clean: ## 🧹 Limpa arquivos temporários
	@echo "$(BLUE)Limpando arquivos temporários...$(RESET)"
	@cd backend && rm -rf __pycache__ .pytest_cache .coverage
	@cd frontend && rm -rf node_modules/.cache dist
	@echo "$(GREEN)✅ Limpeza concluída$(RESET)"

reset: ## 🔄 Reseta ambiente de desenvolvimento
	@echo "$(BLUE)Resetando ambiente...$(RESET)"
	@powershell -ExecutionPolicy Bypass -File "reset-env.ps1"

# Docker commands
docker-build: ## 🐳 Build das imagens Docker
	@echo "$(BLUE)Construindo imagens Docker...$(RESET)"
	@docker-compose build
	@echo "$(GREEN)✅ Imagens construídas$(RESET)"

docker-dev: ## 🐳 Inicia ambiente Docker para desenvolvimento
	@echo "$(BLUE)Iniciando Docker (desenvolvimento)...$(RESET)"
	@docker-compose up --build

docker-dev-detached: ## 🐳 Inicia Docker em background
	@echo "$(BLUE)Iniciando Docker em background...$(RESET)"
	@docker-compose up -d --build

docker-prod: ## 🐳 Inicia ambiente Docker para produção
	@echo "$(BLUE)Iniciando Docker (produção)...$(RESET)"
	@docker-compose -f docker-compose.prod.yml up --build

docker-down: ## 🐳 Para containers Docker
	@docker-compose down

docker-logs: ## 🐳 Mostra logs dos containers
	@docker-compose logs -f

docker-clean: ## 🐳 Remove containers e volumes
	@docker-compose down -v --remove-orphans
	@docker system prune -f

# Database commands
db-backup: ## 💾 Backup do banco de dados
	@echo "$(BLUE)Criando backup do banco...$(RESET)"
	@powershell -ExecutionPolicy Bypass -File "backup-db.ps1"

db-migrate: ## 🗄️ Executa migrações do banco
	@echo "$(BLUE)Executando migrações...$(RESET)"
	@cd backend && poetry run alembic upgrade head

db-migration: ## 🗄️ Cria nova migração
	@echo "$(BLUE)Criando nova migração...$(RESET)"
	@cd backend && poetry run alembic revision --autogenerate -m "$(msg)"

db-reset: ## ⚠️ Reseta banco de dados (CUIDADO!)
	@echo "$(RED)⚠️ ATENÇÃO: Isso irá apagar todos os dados!$(RESET)"
	@read -p "Digite 'CONFIRMO' para continuar: " confirm && [ "$$confirm" = "CONFIRMO" ]
	@cd backend && poetry run python scripts/reset_database.py

# Monitoring
logs: ## 📊 Mostra logs da aplicação
	@tail -f backend/logs/*.log 2>/dev/null || echo "Nenhum log encontrado"

monitor: ## 📊 Abre ferramentas de monitoramento
	@echo "$(BLUE)Abrindo ferramentas de monitoramento...$(RESET)"
	@echo "Grafana: http://localhost:3001"
	@echo "Prometheus: http://localhost:9090"

# Security
security-check: ## 🔒 Verifica vulnerabilidades
	@echo "$(BLUE)Verificando vulnerabilidades...$(RESET)"
	@cd backend && poetry run safety check
	@cd frontend && npm audit

# Deployment
deploy-staging: ## 🚀 Deploy para staging
	@echo "$(BLUE)Deploy para staging...$(RESET)"
	@echo "$(YELLOW)⚠️ Implemente comandos de deploy específicos$(RESET)"

deploy-prod: ## 🚀 Deploy para produção
	@echo "$(RED)⚠️ Deploy para produção$(RESET)"
	@echo "$(YELLOW)⚠️ Implemente comandos de deploy específicos$(RESET)"

# Health checks
health: ## 🏥 Verifica saúde do sistema
	@echo "$(BLUE)Verificando saúde do sistema...$(RESET)"
	@curl -f http://localhost:8000/health || echo "❌ Backend não está respondendo"
	@curl -f http://localhost:3000 || echo "❌ Frontend não está respondendo"

# Documentation
docs: ## 📚 Gera documentação
	@echo "$(BLUE)Gerando documentação...$(RESET)"
	@cd backend && poetry run python -m pydoc -w app/
	@echo "$(GREEN)✅ Documentação gerada$(RESET)"

# Setup inicial
setup: install ## ⚡ Setup inicial completo do projeto
	@echo "$(BLUE)Executando setup inicial...$(RESET)"
	@powershell -ExecutionPolicy Bypass -File "setup.ps1"
	@echo "$(GREEN)✅ Setup concluído$(RESET)"
