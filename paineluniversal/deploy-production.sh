#!/bin/bash

echo "🚀 DEPLOY AUTOMÁTICO - SISTEMA DE EVENTOS"
echo "=========================================="

# Configurações
FRONTEND_PATH="C:\Users\User\OneDrive\Desktop\projetos github\claudesistema\SistemaUniversalEventos-UltraPerformance-v3.0.0\paineluniversal\frontend"
BACKEND_PATH="C:\Users\User\OneDrive\Desktop\projetos github\claudesistema\SistemaUniversalEventos-UltraPerformance-v3.0.0\paineluniversal\backend"
DEPLOY_HOST="production.eventos.com"
DEPLOY_USER="deploy"
DEPLOY_PATH="/var/www/eventos"

# Build Frontend
echo "📦 Building Frontend..."
cd $FRONTEND_PATH
npm ci
npm run build

# Build Backend
echo "📦 Building Backend..."
cd $BACKEND_PATH
docker build -t evento-backend:latest .

# Deploy Frontend
echo "🚀 Deploying Frontend..."
rsync -avz --delete $FRONTEND_PATH/dist/ $DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH/frontend/

# Deploy Backend
echo "🚀 Deploying Backend..."
docker save evento-backend:latest | ssh $DEPLOY_USER@$DEPLOY_HOST docker load
ssh $DEPLOY_USER@$DEPLOY_HOST "cd $DEPLOY_PATH && docker-compose up -d backend"

# Run Migrations
echo "🔧 Running Migrations..."
ssh $DEPLOY_USER@$DEPLOY_HOST "cd $DEPLOY_PATH && docker-compose run --rm backend alembic upgrade head"

# Health Check
echo "❤️ Health Check..."
curl -f http://$DEPLOY_HOST/api/health || exit 1

echo "✅ DEPLOY COMPLETO COM SUCESSO!"
