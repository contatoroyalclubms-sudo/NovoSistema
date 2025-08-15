# 🚀 Sistema Universal de Gestão de Eventos

Sistema completo para gestão de eventos, check-ins, PDV e gamificação.

## 📁 Estrutura do Projeto

```
paineluniversal/
├── backend/          # API Python FastAPI
├── frontend/         # Interface React + TypeScript
└── deploy-pdv.sh    # Script de deploy
```

## 🛠️ Tecnologias

### Backend
- Python 3.12+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Poetry

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Shadcn/ui

## 🚀 Como Executar

### Desenvolvimento Local

1. **Backend:**
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

2. **Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Deploy Completo
```bash
./deploy-pdv.sh
```

## 📊 Funcionalidades

- ✅ Autenticação JWT
- ✅ Gestão de usuários e eventos
- ✅ Check-in inteligente com QR Code
- ✅ PDV completo
- ✅ Dashboard em tempo real
- ✅ Sistema de gamificação
- ✅ Relatórios financeiros
- ✅ WebSocket para atualizações em tempo real

## 🔧 Configuração

1. Copie .env.example para .env no backend
2. Configure as variáveis de ambiente necessárias
3. Execute as migrações do banco de dados

## 📦 Estrutura de Módulos

### Backend
- pp/routers/ - Endpoints da API
- pp/services/ - Lógica de negócio
- pp/models.py - Modelos do banco de dados
- pp/schemas.py - Schemas Pydantic

### Frontend
- src/components/ - Componentes React
- src/services/ - Serviços de API
- src/contexts/ - Contextos React
- src/hooks/ - Hooks customizados

## 📜 Licença

MIT License
