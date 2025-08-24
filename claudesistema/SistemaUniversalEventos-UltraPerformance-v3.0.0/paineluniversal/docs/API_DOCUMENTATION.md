# 📡 DOCUMENTAÇÃO COMPLETA DA API

## 🎯 **Visão Geral da API**

O Sistema Universal de Gestão de Eventos possui uma API RESTful robusta construída com FastAPI, oferecendo 25+ endpoints organizados em módulos especializados.

**Base URL:** `http://localhost:8000`  
**Documentação Interativa:** `http://localhost:8000/docs`  
**Especificação OpenAPI:** `http://localhost:8000/openapi.json`

---

## 🔐 **Autenticação**

### JWT Bearer Authentication

Todos os endpoints (exceto login e registro) requerem autenticação JWT.

**Header necessário:**

```
Authorization: Bearer <your-jwt-token>
```

### Endpoints de Autenticação

#### `POST /auth/login`

Realiza login no sistema

**Request:**

```json
{
  "email": "admin@sistema.com",
  "password": "admin123"
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "admin@sistema.com",
    "nome": "Administrador",
    "tipo": "admin",
    "ativo": true
  }
}
```

#### `POST /auth/register`

Registra um novo usuário

**Request:**

```json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "password": "senha123",
  "telefone": "+5511999999999",
  "tipo": "participante"
}
```

#### `POST /auth/refresh`

Renova o token JWT

**Headers:** `Authorization: Bearer <token>`

#### `POST /auth/logout`

Realiza logout (invalidar token)

---

## 🎪 **Módulo de Eventos**

### `GET /eventos`

Lista todos os eventos

**Parâmetros de Query:**

- `skip`: int = 0 - Paginação
- `limit`: int = 100 - Limite de resultados
- `status`: str = "todos" - Filtro por status
- `categoria`: str - Filtro por categoria
- `data_inicio`: date - Filtro por data

**Response:**

```json
{
  "eventos": [
    {
      "id": 1,
      "nome": "Conference Tech 2025",
      "descricao": "Grande conferência de tecnologia",
      "data_inicio": "2025-08-25T09:00:00",
      "data_fim": "2025-08-25T18:00:00",
      "local": "Centro de Convenções",
      "categoria": "tecnologia",
      "status": "ativo",
      "max_participantes": 500,
      "participantes_atual": 150,
      "valor_ingresso": 99.9,
      "organizador_id": 1,
      "configuracoes": {
        "check_in_automatico": true,
        "gamificacao_ativa": true,
        "whatsapp_notifications": true
      },
      "created_at": "2025-08-20T10:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1
}
```

### `POST /eventos`

Cria um novo evento

**Request:**

```json
{
  "nome": "Meu Evento",
  "descricao": "Descrição do evento",
  "data_inicio": "2025-08-25T09:00:00",
  "data_fim": "2025-08-25T18:00:00",
  "local": "Local do evento",
  "categoria": "categoria",
  "max_participantes": 100,
  "valor_ingresso": 50.0,
  "configuracoes": {
    "check_in_automatico": true,
    "gamificacao_ativa": true
  }
}
```

### `GET /eventos/{evento_id}`

Obtém detalhes de um evento específico

### `PUT /eventos/{evento_id}`

Atualiza um evento

### `DELETE /eventos/{evento_id}`

Remove um evento

### `POST /eventos/{evento_id}/participar`

Inscreve usuário em evento

### `GET /eventos/{evento_id}/participantes`

Lista participantes do evento

---

## 👥 **Módulo de Usuários**

### `GET /usuarios`

Lista usuários do sistema

**Parâmetros:**

- `tipo`: str - Filtro por tipo de usuário
- `ativo`: bool - Filtro por status ativo
- `search`: str - Busca por nome ou email

### `POST /usuarios`

Cria novo usuário

### `GET /usuarios/{user_id}`

Obtém usuário específico

### `PUT /usuarios/{user_id}`

Atualiza usuário

### `POST /usuarios/{user_id}/activate`

Ativa/desativa usuário

---

## ✅ **Módulo de Check-ins**

### `POST /checkins`

Realiza check-in de participante

**Request:**

```json
{
  "evento_id": 1,
  "participante_id": 1,
  "qr_code": "QR123456789",
  "localizacao": {
    "latitude": -23.5505,
    "longitude": -46.6333
  }
}
```

**Response:**

```json
{
  "checkin_id": 1,
  "evento": "Conference Tech 2025",
  "participante": "João Silva",
  "timestamp": "2025-08-25T09:15:00",
  "status": "confirmado",
  "pontos_gamificacao": 10,
  "badges_conquistadas": ["early_bird"],
  "message": "Check-in realizado com sucesso!"
}
```

### `GET /checkins/{evento_id}`

Lista check-ins de um evento

### `GET /checkins/qr/{qr_code}`

Valida QR code para check-in

---

## 💰 **Módulo PDV (Ponto de Venda)**

### `POST /pdv/venda`

Registra nova venda

**Request:**

```json
{
  "evento_id": 1,
  "vendedor_id": 1,
  "cliente_id": 1,
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 2,
      "valor_unitario": 15.0
    }
  ],
  "forma_pagamento": "cartao",
  "desconto_percentual": 0
}
```

### `GET /pdv/vendas`

Lista vendas realizadas

### `GET /pdv/produtos`

Lista produtos disponíveis

### `POST /pdv/produtos`

Cadastra novo produto

---

## 🎮 **Módulo de Gamificação**

### `GET /gamificacao/ranking`

Ranking de participantes

**Response:**

```json
{
  "ranking": [
    {
      "posicao": 1,
      "participante": {
        "id": 1,
        "nome": "João Silva",
        "avatar": "https://avatar.url"
      },
      "pontos": 150,
      "badges": ["early_bird", "social_butterfly"],
      "nivel": "Gold",
      "eventos_participados": 5
    }
  ],
  "minha_posicao": 15,
  "meus_pontos": 85
}
```

### `GET /gamificacao/badges`

Lista badges disponíveis

### `POST /gamificacao/pontos`

Adiciona pontos para usuário

### `GET /gamificacao/usuario/{user_id}`

Perfil gamificação do usuário

---

## 📊 **Módulo de Analytics**

### `GET /analytics/dashboard`

Dados do dashboard principal

**Response:**

```json
{
  "resumo": {
    "total_eventos": 25,
    "total_participantes": 1250,
    "vendas_mes": 15000.00,
    "check_ins_hoje": 85
  },
  "eventos_populares": [...],
  "vendas_por_dia": [...],
  "check_ins_por_hora": [...]
}
```

### `GET /analytics/evento/{evento_id}`

Analytics específico de evento

### `GET /analytics/financeiro`

Relatório financeiro

### `GET /analytics/participacao`

Relatório de participação

---

## 💬 **Módulo WhatsApp**

### `POST /whatsapp/send`

Enviar mensagem WhatsApp

**Request:**

```json
{
  "numero": "+5511999999999",
  "mensagem": "Olá! Seu check-in foi confirmado.",
  "tipo": "texto"
}
```

### `POST /whatsapp/broadcast`

Envio em massa

### `GET /whatsapp/templates`

Lista templates de mensagens

---

## 🔄 **Módulo N8N (Automação)**

### `POST /n8n/trigger`

Dispara workflow N8N

### `GET /n8n/workflows`

Lista workflows disponíveis

### `POST /n8n/webhook`

Webhook para receber dados do N8N

---

## 📈 **Módulo de Relatórios**

### `GET /relatorios/eventos`

Relatório de eventos

### `GET /relatorios/vendas`

Relatório de vendas

### `GET /relatorios/participacao`

Relatório de participação

### `POST /relatorios/customizado`

Gerar relatório customizado

**Request:**

```json
{
  "tipo": "vendas",
  "periodo": {
    "inicio": "2025-08-01",
    "fim": "2025-08-31"
  },
  "filtros": {
    "evento_id": 1,
    "vendedor_id": null
  },
  "formato": "pdf"
}
```

---

## 🗄️ **Módulo de Estoque**

### `GET /estoque/produtos`

Lista produtos em estoque

### `POST /estoque/entrada`

Registra entrada de estoque

### `POST /estoque/saida`

Registra saída de estoque

### `GET /estoque/movimentacao`

Histórico de movimentação

---

## 🏢 **Módulo de Empresas**

### `GET /empresas`

Lista empresas/organizadores

### `POST /empresas`

Cadastra nova empresa

### `GET /empresas/{empresa_id}/eventos`

Eventos da empresa

---

## 🔍 **WebSocket Real-time**

### Conexão WebSocket

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Evento em tempo real:", data);
};
```

### Eventos Disponíveis

- `check_in_realizado` - Novo check-in
- `venda_realizada` - Nova venda
- `novo_participante` - Nova inscrição
- `badge_conquistada` - Nova badge
- `ranking_atualizado` - Atualização do ranking

---

## 📋 **Códigos de Status HTTP**

| Código | Significado                              |
| ------ | ---------------------------------------- |
| 200    | OK - Sucesso                             |
| 201    | Created - Recurso criado                 |
| 400    | Bad Request - Dados inválidos            |
| 401    | Unauthorized - Token inválido/expirado   |
| 403    | Forbidden - Sem permissão                |
| 404    | Not Found - Recurso não encontrado       |
| 422    | Unprocessable Entity - Erro de validação |
| 500    | Internal Server Error - Erro do servidor |

---

## 🛠️ **Middleware e Features**

### Rate Limiting

- 100 requests por minuto por IP
- 1000 requests por hora por usuário autenticado

### Compressão

- Gzip automático para responses > 1KB
- Headers de cache otimizados

### CORS

- Configurado para permitir frontend local
- Headers apropriados para APIs cross-origin

### Monitoring

- Métricas Prometheus em `/metrics`
- Health check em `/health`
- Status do sistema em `/status`

---

## 🧪 **Exemplos de Uso**

### Fluxo Completo de Check-in

```python
import requests

# 1. Login
login_response = requests.post('http://localhost:8000/auth/login', json={
    'email': 'admin@sistema.com',
    'password': 'admin123'
})
token = login_response.json()['access_token']

# 2. Headers com token
headers = {'Authorization': f'Bearer {token}'}

# 3. Buscar evento
eventos = requests.get('http://localhost:8000/eventos', headers=headers)
evento_id = eventos.json()['eventos'][0]['id']

# 4. Realizar check-in
checkin = requests.post('http://localhost:8000/checkins',
    headers=headers,
    json={
        'evento_id': evento_id,
        'participante_id': 1,
        'qr_code': 'QR123456789'
    }
)
```

### Integração JavaScript/Frontend

```javascript
class EventosAPI {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async get(endpoint) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      headers: {
        Authorization: `Bearer ${this.token}`,
        "Content-Type": "application/json",
      },
    });
    return response.json();
  }

  async post(endpoint, data) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    return response.json();
  }
}

// Uso
const api = new EventosAPI("http://localhost:8000", "seu-token-jwt");
const eventos = await api.get("/eventos");
```

---

## 🔧 **Configurações Avançadas**

### Variáveis de Ambiente

```env
# API Configuration
API_VERSION=v1
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@localhost/db
DATABASE_POOL_SIZE=10

# Redis Cache
REDIS_URL=redis://localhost:6379
REDIS_TTL=3600

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# External APIs
WHATSAPP_API_TOKEN=your-whatsapp-token
N8N_WEBHOOK_URL=your-n8n-webhook
```

### Headers Personalizados

```
X-Request-ID: UUID para tracking
X-User-Agent: Identificação da aplicação
X-API-Version: Versão da API utilizada
```

---

## 📞 **Suporte e Recursos**

- 📖 **Documentação Interativa:** http://localhost:8000/docs
- 🔍 **Redoc:** http://localhost:8000/redoc
- 📋 **OpenAPI Spec:** http://localhost:8000/openapi.json
- 💬 **Discord:** [Link do servidor]
- 🐛 **Issues:** [GitHub Issues](https://github.com/contatoroyalclubms-sudo/NovoSistema/issues)

---

**API desenvolvida com FastAPI - Performance e confiabilidade garantidas! ⚡**
