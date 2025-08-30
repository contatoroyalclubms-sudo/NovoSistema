# Sistema Universal de Eventos - Frontend

## 🚀 Stack Tecnológica

- **React 18.3.1** - UI Library
- **TypeScript** - Type Safety
- **Vite** - Build Tool
- **Tailwind CSS** - Styling
- **Radix UI** - Component Library
- **TanStack Query** - Data Fetching
- **React Router v6** - Routing

## 📦 Instalação

```bash
# Instalar dependências
npm install

# Desenvolvimento
npm run dev

# Build produção
npm run build

# Testes
npm run test
```

## 🏗️ Arquitetura

### Estrutura de Diretórios

```
src/
├── components/      # Componentes reutilizáveis
│   ├── auth/       # Autenticação
│   ├── dashboard/  # Dashboard
│   ├── eventos/    # Gestão de eventos
│   ├── pdv/        # Ponto de venda
│   └── ui/         # Componentes UI base
├── contexts/       # React Contexts
├── hooks/          # Custom Hooks
├── pages/          # Páginas/Rotas
├── services/       # API Services
├── types/          # TypeScript Types
└── utils/          # Utilitários
```

## 🎨 Componentes Principais

### Dashboard
- Métricas em tempo real
- Gráficos interativos
- KPIs do evento

### Sistema de Eventos
- CRUD completo
- Templates personalizáveis
- QR Code generation

### PDV (Ponto de Venda)
- Carrinho de compras
- Múltiplas formas de pagamento
- Controle de estoque

### Check-in
- Leitura de QR Code
- Validação por CPF
- Histórico em tempo real

## 🔧 Configuração

### Variáveis de Ambiente

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENABLE_MOCK=false
```

## 🚀 Performance

- Code Splitting automático
- Lazy Loading de componentes
- Bundle optimization com Rollup
- PWA Ready com Service Worker

## 📱 Responsividade

- Mobile-first design
- Breakpoints Tailwind
- Touch gestures support

## 🧪 Testes

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage
npm run test:coverage
```

## 📊 Métricas de Performance

- Lighthouse Score: 95+
- First Contentful Paint: < 1s
- Time to Interactive: < 2s
- Bundle Size: < 300KB gzipped

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

MIT License - veja LICENSE para detalhes
