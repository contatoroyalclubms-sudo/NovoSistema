#!/bin/bash

echo "🚀 Deploy PDV Digital Inteligente - Sistema de Gestão de Eventos"

cd backend
echo "📦 Instalando dependências backend..."
poetry install

echo "🗄️ Criando tabelas do banco..."
poetry run python -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('✅ Tabelas PDV criadas com sucesso!')
"

echo "🧪 Executando testes..."
poetry run pytest --cov=app --cov-report=html -v

if [ $? -ne 0 ]; then
    echo "❌ Testes falharam! Verifique os erros acima."
    exit 1
fi

echo "🚀 Iniciando servidor backend..."
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd ../frontend
echo "📦 Instalando dependências frontend..."
npm install

echo "🏗️ Build do frontend..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build do frontend falhou!"
    kill $BACKEND_PID
    exit 1
fi

echo "🚀 Iniciando servidor frontend..."
npm run preview &
FRONTEND_PID=$!

echo ""
echo "✅ Deploy PDV concluído com sucesso!"
echo ""
echo "🔧 Serviços rodando:"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:4173"
echo ""
echo "📚 Documentação API: http://localhost:8000/docs"
echo "🌐 Interface PDV: http://localhost:4173/pdv"
echo "📊 Dashboard PDV: http://localhost:4173/pdv/dashboard"
echo ""
echo "Para parar os serviços:"
echo "kill $BACKEND_PID $FRONTEND_PID"

read -p "Pressione Enter para parar os serviços..."
kill $BACKEND_PID $FRONTEND_PID
echo "Serviços parados."
