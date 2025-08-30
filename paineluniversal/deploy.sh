#!/bin/bash

# ================================
# SCRIPT DE DEPLOY - SISTEMA UNIVERSAL DE EVENTOS
# Ultra Performance Deploy Script
# ================================

set -e

echo "🚀 INICIANDO DEPLOY DO SISTEMA UNIVERSAL DE EVENTOS..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado!"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose não está instalado!"
    exit 1
fi

print_status "Docker e Docker Compose encontrados"

# Verificar se arquivo .env existe
if [ ! -f .env ]; then
    print_warning "Arquivo .env não encontrado. Copiando .env.example..."
    cp .env.example .env
    print_warning "Por favor, edite o arquivo .env com suas configurações antes de continuar"
    echo "Pressione Enter para continuar ou Ctrl+C para cancelar..."
    read -r
fi

print_status "Carregando variáveis de ambiente..."
source .env

# Parar containers existentes
print_status "Parando containers existentes..."
docker-compose down --remove-orphans

# Limpar imagens antigas (opcional)
read -p "Deseja remover imagens antigas? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Removendo imagens antigas..."
    docker system prune -f
fi

# Construir e subir os serviços
print_status "Construindo e iniciando serviços..."
docker-compose up --build -d

# Aguardar serviços ficarem saudáveis
print_status "Aguardando serviços ficarem prontos..."

# Aguardar PostgreSQL
echo "📊 Aguardando PostgreSQL..."
timeout 60 bash -c 'until docker-compose exec postgres pg_isready -U $DB_USER; do sleep 2; done'

# Aguardar Redis
echo "🔴 Aguardando Redis..."
timeout 30 bash -c 'until docker-compose exec redis redis-cli ping; do sleep 2; done'

# Aguardar Backend
echo "⚡ Aguardando Backend..."
timeout 120 bash -c 'until curl -f http://localhost:${BACKEND_PORT}/health; do sleep 5; done'

# Aguardar Frontend
echo "🌐 Aguardando Frontend..."
timeout 60 bash -c 'until curl -f http://localhost:${FRONTEND_PORT}/health; do sleep 3; done'

print_status "Todos os serviços estão rodando!"

# Executar migrações do banco
print_status "Executando migrações do banco de dados..."
docker-compose exec backend python -m alembic upgrade head || print_warning "Migrações não executadas (pode ser normal na primeira instalação)"

# Mostrar status final
echo ""
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo ""
echo "📋 SERVIÇOS ATIVOS:"
docker-compose ps

echo ""
echo "🔗 URLS DE ACESSO:"
echo "   Frontend: http://localhost:${FRONTEND_PORT}"
echo "   Backend API: http://localhost:${BACKEND_PORT}"
echo "   Documentação API: http://localhost:${BACKEND_PORT}/docs"
echo "   Banco PostgreSQL: localhost:${DB_PORT}"
echo "   Redis Cache: localhost:${REDIS_PORT}"

echo ""
echo "📊 PARA MONITORAR LOGS:"
echo "   docker-compose logs -f"
echo "   docker-compose logs -f backend"
echo "   docker-compose logs -f frontend"

echo ""
echo "🛑 PARA PARAR O SISTEMA:"
echo "   docker-compose down"

echo ""
print_status "Sistema pronto para uso!"