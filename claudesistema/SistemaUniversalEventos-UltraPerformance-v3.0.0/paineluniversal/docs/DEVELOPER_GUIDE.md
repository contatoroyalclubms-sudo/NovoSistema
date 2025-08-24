# 🔧 GUIA COMPLETO DO DESENVOLVEDOR

## 🎯 **Visão Geral da Arquitetura**

O Sistema Universal de Eventos é construído com uma arquitetura moderna e escalável, seguindo as melhores práticas de desenvolvimento.

### 🏗️ **Stack Tecnológico**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Frontend    │    │     Backend     │    │    Database     │
│   React + TS    │ ←→ │    FastAPI      │ ←→ │  PostgreSQL     │
│   Tailwind CSS  │    │    Python       │    │   + Redis       │
│      Vite       │    │   SQLAlchemy    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ↑                       ↑                       ↑
         │              ┌─────────────────┐              │
         └─────────────→│   WebSocket     │←─────────────┘
                        │   Real-time     │
                        └─────────────────┘
```

### 🎨 **Padrões Arquiteturais**

- **🏗️ Clean Architecture** - Separação clara de responsabilidades
- **📦 Domain Driven Design** - Modelagem baseada no domínio
- **🔄 CQRS** - Separação de comandos e consultas
- **⚡ Event Sourcing** - Para auditoria e rastreamento
- **🛡️ Repository Pattern** - Abstração de acesso a dados
- **🏭 Factory Pattern** - Criação de objetos complexos

---

## 📁 **Estrutura Detalhada do Projeto**

```
NovoSistema/
├── 📋 .projeto-management/           # Gestão do projeto
├── 📚 docs/                         # Documentação oficial
├── 🛠️ scripts/                     # Scripts organizados
│   ├── installation/               # Instalação e setup
│   ├── database/                   # Migração e backup
│   ├── development/                # Desenvolvimento
│   ├── production/                 # Deploy e produção
│   └── utilities/                  # Utilitários gerais
├── 🏢 paineluniversal/             # Sistema principal
│   ├── backend/                    # FastAPI Backend
│   │   ├── app/                    # Aplicação principal
│   │   │   ├── main.py            # Entry point (744 linhas)
│   │   │   ├── core/              # Configurações core
│   │   │   │   ├── config.py      # Configurações
│   │   │   │   ├── database.py    # Setup do banco
│   │   │   │   ├── security.py    # JWT e autenticação
│   │   │   │   └── exceptions.py  # Exceções customizadas
│   │   │   ├── models/            # Modelos SQLAlchemy
│   │   │   │   ├── base.py        # Modelo base
│   │   │   │   ├── user.py        # Modelo de usuário
│   │   │   │   ├── event.py       # Modelo de evento
│   │   │   │   ├── checkin.py     # Modelo de check-in
│   │   │   │   └── gamification.py # Gamificação
│   │   │   ├── routers/           # Rotas da API (25+ arquivos)
│   │   │   │   ├── auth.py        # Autenticação
│   │   │   │   ├── eventos.py     # Gestão de eventos
│   │   │   │   ├── usuarios.py    # Gestão de usuários
│   │   │   │   ├── checkins.py    # Sistema de check-in
│   │   │   │   ├── pdv.py         # Ponto de venda
│   │   │   │   ├── gamificacao.py # Sistema de gamificação
│   │   │   │   ├── analytics.py   # Analytics e relatórios
│   │   │   │   ├── whatsapp.py    # Integração WhatsApp
│   │   │   │   ├── n8n.py         # Automação N8N
│   │   │   │   └── ... (15+ outros)
│   │   │   ├── services/          # Lógica de negócio
│   │   │   │   ├── event_service.py
│   │   │   │   ├── user_service.py
│   │   │   │   ├── checkin_service.py
│   │   │   │   ├── gamification_service.py
│   │   │   │   ├── notification_service.py
│   │   │   │   ├── analytics_service.py
│   │   │   │   └── monitoring.py
│   │   │   ├── schemas/           # Pydantic schemas
│   │   │   │   ├── user.py
│   │   │   │   ├── event.py
│   │   │   │   ├── checkin.py
│   │   │   │   └── responses.py
│   │   │   ├── utils/             # Utilitários
│   │   │   │   ├── email.py
│   │   │   │   ├── whatsapp.py
│   │   │   │   ├── qr_code.py
│   │   │   │   ├── validators.py
│   │   │   │   └── helpers.py
│   │   │   ├── middleware/        # Middleware customizado
│   │   │   │   ├── performance.py
│   │   │   │   ├── logging.py
│   │   │   │   ├── cors.py
│   │   │   │   └── rate_limiting.py
│   │   │   └── tests/             # Testes automatizados
│   │   │       ├── test_auth.py
│   │   │       ├── test_events.py
│   │   │       ├── test_checkins.py
│   │   │       └── ...
│   │   ├── alembic/               # Migrações do banco
│   │   ├── requirements.txt       # Dependências Python
│   │   └── .env.example          # Variáveis de ambiente
│   └── frontend/                  # React Frontend
│       ├── src/
│       │   ├── components/        # Componentes reutilizáveis
│       │   │   ├── ui/           # Componentes base
│       │   │   ├── forms/        # Formulários
│       │   │   ├── charts/       # Gráficos
│       │   │   └── layout/       # Layout components
│       │   ├── pages/            # Páginas da aplicação
│       │   │   ├── auth/         # Login/Register
│       │   │   ├── dashboard/    # Dashboard principal
│       │   │   ├── events/       # Gestão de eventos
│       │   │   ├── checkin/      # Check-in interface
│       │   │   ├── pdv/          # Interface PDV
│       │   │   └── admin/        # Painel administrativo
│       │   ├── services/         # Serviços de API
│       │   │   ├── api.ts        # Cliente HTTP base
│       │   │   ├── auth.ts       # Serviços de auth
│       │   │   ├── events.ts     # Serviços de eventos
│       │   │   └── websocket.ts  # WebSocket client
│       │   ├── hooks/            # React hooks customizados
│       │   ├── utils/            # Utilitários frontend
│       │   ├── types/            # TypeScript types
│       │   ├── store/            # Estado global (Zustand)
│       │   └── styles/           # Estilos Tailwind
│       ├── public/               # Assets estáticos
│       ├── package.json          # Dependências Node.js
│       └── vite.config.ts        # Configuração Vite
├── 🐳 docker-compose.yml         # Orquestração Docker
├── 📄 requirements.txt           # Dependências globais
└── 🔧 .env.example              # Variáveis de ambiente
```

---

## ⚙️ **Configuração do Ambiente de Desenvolvimento**

### 1️⃣ **Pré-requisitos**

```bash
# Versões recomendadas
python --version    # 3.11+
node --version      # 18+
npm --version       # 9+
git --version       # 2.0+
```

### 2️⃣ **Setup Inicial**

```bash
# Clone e configuração
git clone <repository>
cd NovoSistema

# Configure ambiente Python
cd paineluniversal/backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instale dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dependências de desenvolvimento

# Configure Node.js
cd ../frontend
npm install
npm run build  # Primeira build

# Volte para raiz
cd ../../
```

### 3️⃣ **Configuração de Banco de Dados**

```bash
# PostgreSQL (Recomendado para produção)
createdb eventos_dev
createdb eventos_test

# Execute migrações
cd paineluniversal/backend
alembic upgrade head

# Popule dados de desenvolvimento
python scripts/seed_dev_data.py
```

### 4️⃣ **Variáveis de Ambiente**

**.env (Backend):**

```env
# Desenvolvimento
DEBUG=True
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://user:pass@localhost/eventos_dev
TEST_DATABASE_URL=postgresql://user:pass@localhost/eventos_test

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# External APIs
WHATSAPP_API_TOKEN=
N8N_WEBHOOK_URL=

# Monitoring
PROMETHEUS_ENABLED=True
SENTRY_DSN=
```

**.env.local (Frontend):**

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENVIRONMENT=development
VITE_DEBUG=true
```

---

## 🏗️ **Arquitetura do Backend**

### 🔧 **FastAPI Application (main.py)**

```python
"""
Estrutura principal do main.py (744 linhas)
"""

# 1. Imports e configurações (linhas 1-50)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# ... outros imports

# 2. Middleware stack (linhas 51-150)
app.add_middleware(UltraPerformanceMiddleware)
app.add_middleware(ResponseCompressionMiddleware)
app.add_middleware(CORSMiddleware, ...)

# 3. Routers registration (linhas 151-300)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(eventos.router, prefix="/eventos", tags=["eventos"])
# ... 23+ routers

# 4. WebSocket setup (linhas 301-400)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Implementação WebSocket

# 5. Monitoring endpoints (linhas 401-500)
@app.get("/health")
async def health_check():
    # Health check implementation

# 6. Error handlers (linhas 501-600)
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    # Error handling

# 7. Startup/shutdown events (linhas 601-744)
@app.on_event("startup")
async def startup_event():
    # Initialization code
```

### 📦 **Modelos de Dados (SQLAlchemy)**

```python
# models/base.py
class BaseModel(DeclarativeBase):
    """Modelo base com campos comuns"""
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(default=True)

# models/event.py
class Event(BaseModel):
    __tablename__ = "events"

    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str] = mapped_column(Text)
    data_inicio: Mapped[datetime] = mapped_column(nullable=False)
    data_fim: Mapped[datetime] = mapped_column(nullable=False)
    local: Mapped[str] = mapped_column(String(500))
    max_participantes: Mapped[int] = mapped_column(default=100)
    valor_ingresso: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    # Relacionamentos
    participantes: Mapped[List["UserEvent"]] = relationship(back_populates="event")
    checkins: Mapped[List["CheckIn"]] = relationship(back_populates="event")
    vendas: Mapped[List["Sale"]] = relationship(back_populates="event")
```

### 🎯 **Serviços de Negócio**

```python
# services/event_service.py
class EventService:
    def __init__(self, db: Session, cache: Redis):
        self.db = db
        self.cache = cache

    async def create_event(self, event_data: EventCreate, user_id: int) -> Event:
        """Criar novo evento com validações completas"""
        # 1. Validar dados
        await self._validate_event_data(event_data)

        # 2. Criar evento
        event = Event(**event_data.dict(), organizador_id=user_id)
        self.db.add(event)
        self.db.commit()

        # 3. Cache
        await self.cache.set(f"event:{event.id}", event.json())

        # 4. Notificações
        await self._send_event_created_notifications(event)

        return event

    async def get_events_with_analytics(self, filters: EventFilters) -> List[EventWithAnalytics]:
        """Buscar eventos com analytics incluído"""
        # Implementação com cache, filtros e agregações
        pass
```

### 🔌 **Sistema de Routers**

```python
# routers/eventos.py
router = APIRouter()

@router.get("/", response_model=List[EventResponse])
async def list_events(
    skip: int = 0,
    limit: int = 100,
    status: str = "all",
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """Listar eventos com filtros e paginação"""
    filters = EventFilters(skip=skip, limit=limit, status=status)
    events = await event_service.get_events(filters, current_user)
    return events

@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """Criar novo evento"""
    event = await event_service.create_event(event_data, current_user.id)
    return event
```

---

## 🌐 **Arquitetura do Frontend**

### ⚛️ **Estrutura React + TypeScript**

```typescript
// src/types/event.ts
export interface Event {
  id: number;
  nome: string;
  descricao: string;
  data_inicio: string;
  data_fim: string;
  local: string;
  categoria: string;
  status: "ativo" | "inativo" | "finalizado";
  max_participantes: number;
  participantes_atual: number;
  valor_ingresso: number;
  organizador_id: number;
  configuracoes: EventConfig;
  created_at: string;
}

export interface EventConfig {
  check_in_automatico: boolean;
  gamificacao_ativa: boolean;
  whatsapp_notifications: boolean;
  pdv_ativo: boolean;
}
```

### 🎣 **Hooks Customizados**

```typescript
// src/hooks/useEvents.ts
export const useEvents = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEvents = useCallback(async (filters?: EventFilters) => {
    setLoading(true);
    try {
      const response = await eventService.getEvents(filters);
      setEvents(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const createEvent = useCallback(async (eventData: EventCreate) => {
    const newEvent = await eventService.createEvent(eventData);
    setEvents((prev) => [...prev, newEvent]);
    return newEvent;
  }, []);

  return {
    events,
    loading,
    error,
    fetchEvents,
    createEvent,
    // ... outros métodos
  };
};
```

### 🏪 **Gerenciamento de Estado (Zustand)**

```typescript
// src/store/authStore.ts
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem("token"),
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    const response = await authService.login({ email, password });
    const { access_token, user } = response.data;

    localStorage.setItem("token", access_token);
    set({ token: access_token, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem("token");
    set({ token: null, user: null, isAuthenticated: false });
  },

  refreshToken: async () => {
    // Implementação refresh token
  },
}));
```

### 🔌 **Serviços de API**

```typescript
// src/services/api.ts
class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  setToken(token: string) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new ApiError(response.status, await response.text());
    }

    return response.json();
  }

  // Métodos HTTP
  get<T>(endpoint: string) {
    return this.request<T>(endpoint);
  }

  post<T>(endpoint: string, data: any) {
    return this.request<T>(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
}
```

---

## 🔄 **WebSocket Real-time**

### 🖥️ **Backend WebSocket Manager**

```python
# services/websocket_events.py
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.room_connections: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, room: str = None):
        """Conectar cliente WebSocket"""
        await websocket.accept()
        self.active_connections[client_id] = websocket

        if room:
            if room not in self.room_connections:
                self.room_connections[room] = set()
            self.room_connections[room].add(client_id)

    async def disconnect(self, client_id: str):
        """Desconectar cliente"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        # Remove de todas as salas
        for room_clients in self.room_connections.values():
            room_clients.discard(client_id)

    async def send_personal_message(self, message: dict, client_id: str):
        """Enviar mensagem para cliente específico"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_text(json.dumps(message))

    async def broadcast_to_room(self, message: dict, room: str):
        """Broadcast para sala específica"""
        if room in self.room_connections:
            for client_id in self.room_connections[room]:
                await self.send_personal_message(message, client_id)
```

### 🌐 **Frontend WebSocket Client**

```typescript
// src/services/websocket.ts
class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private eventHandlers: Map<string, Function[]> = new Map();

  connect(url: string, token: string) {
    this.ws = new WebSocket(`${url}?token=${token}`);

    this.ws.onopen = () => {
      console.log("WebSocket connected");
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.ws.onclose = () => {
      console.log("WebSocket disconnected");
      this.attemptReconnect(url, token);
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }

  private handleMessage(data: any) {
    const { type, payload } = data;
    const handlers = this.eventHandlers.get(type) || [];
    handlers.forEach((handler) => handler(payload));
  }

  on(eventType: string, handler: Function) {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)!.push(handler);
  }

  emit(eventType: string, payload: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: eventType, payload }));
    }
  }
}
```

---

## 🎮 **Sistema de Gamificação**

### 🏆 **Engine de Pontuação**

```python
# services/gamification_service.py
class GamificationEngine:
    """Engine completo de gamificação"""

    def __init__(self, db: Session, cache: Redis):
        self.db = db
        self.cache = cache
        self.rules = self._load_rules()

    async def process_event(self, event_type: str, user_id: int, context: dict):
        """Processa evento e calcula pontos/badges"""

        # 1. Calcular pontos baseado nas regras
        points = await self._calculate_points(event_type, context)

        # 2. Verificar badges conquistadas
        badges = await self._check_badges(user_id, event_type, context)

        # 3. Atualizar usuário
        await self._update_user_gamification(user_id, points, badges)

        # 4. Verificar mudança de nível
        level_change = await self._check_level_up(user_id)

        # 5. Notificar via WebSocket
        await self._notify_gamification_update(user_id, {
            'points': points,
            'badges': badges,
            'level_change': level_change
        })

        return {
            'points_earned': points,
            'badges_earned': badges,
            'level_change': level_change
        }

    async def _calculate_points(self, event_type: str, context: dict) -> int:
        """Calcula pontos baseado no tipo de evento"""
        base_points = self.rules.get(event_type, {}).get('points', 0)

        # Aplicar multiplicadores
        multiplier = 1.0
        if context.get('early_checkin'):
            multiplier += 0.5
        if context.get('first_time_event'):
            multiplier += 0.3

        return int(base_points * multiplier)
```

### 🏅 **Sistema de Badges**

```python
# models/gamification.py
class Badge(BaseModel):
    __tablename__ = "badges"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text)
    icon: Mapped[str] = mapped_column(String(100))
    criteria: Mapped[dict] = mapped_column(JSON)  # Critérios dinâmicos
    rarity: Mapped[str] = mapped_column(String(20))  # common, rare, epic, legendary
    points_reward: Mapped[int] = mapped_column(default=0)

class UserBadge(BaseModel):
    __tablename__ = "user_badges"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    badge_id: Mapped[int] = mapped_column(ForeignKey("badges.id"))
    earned_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    context: Mapped[dict] = mapped_column(JSON)  # Como foi conquistada
```

---

## 📊 **Sistema de Monitoring e Analytics**

### 📈 **Métricas Prometheus**

```python
# services/monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Métricas customizadas
REQUESTS_TOTAL = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_USERS = Gauge('active_users_total', 'Currently active users')
CHECKINS_TOTAL = Counter('checkins_total', 'Total check-ins', ['event_id'])
SALES_TOTAL = Counter('sales_total', 'Total sales', ['event_id'])

class MonitoringService:
    """Serviço de monitoramento e métricas"""

    @staticmethod
    def record_request(method: str, endpoint: str, status: int, duration: float):
        REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_DURATION.observe(duration)

    @staticmethod
    def record_checkin(event_id: int):
        CHECKINS_TOTAL.labels(event_id=str(event_id)).inc()

    @staticmethod
    def update_active_users(count: int):
        ACTIVE_USERS.set(count)

# Middleware de monitoring
class MonitoringMiddleware:
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        MonitoringService.record_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration
        )

        return response
```

### 📊 **Analytics Engine**

```python
# services/analytics_service.py
class AnalyticsEngine:
    """Engine de analytics e relatórios"""

    def __init__(self, db: Session, cache: Redis):
        self.db = db
        self.cache = cache

    async def get_event_analytics(self, event_id: int) -> EventAnalytics:
        """Analytics detalhado de um evento"""

        cache_key = f"analytics:event:{event_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return EventAnalytics.parse_raw(cached)

        # Calcular métricas
        analytics = EventAnalytics(
            total_participants=await self._count_participants(event_id),
            checkin_rate=await self._calculate_checkin_rate(event_id),
            sales_metrics=await self._get_sales_metrics(event_id),
            engagement_score=await self._calculate_engagement(event_id),
            hourly_checkins=await self._get_hourly_checkins(event_id),
            participant_demographics=await self._get_demographics(event_id),
            gamification_stats=await self._get_gamification_stats(event_id)
        )

        # Cache por 5 minutos
        await self.cache.set(cache_key, analytics.json(), ex=300)

        return analytics
```

---

## 🧪 **Testes Automatizados**

### 🎯 **Configuração de Testes**

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base

# Database de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### 🧪 **Testes de API**

```python
# tests/test_events.py
class TestEventAPI:
    """Testes para API de eventos"""

    def test_create_event_success(self, client, auth_headers):
        """Teste criação de evento com sucesso"""
        event_data = {
            "nome": "Test Event",
            "descricao": "Test Description",
            "data_inicio": "2025-08-25T09:00:00",
            "data_fim": "2025-08-25T18:00:00",
            "local": "Test Location",
            "max_participantes": 100,
            "valor_ingresso": 50.0
        }

        response = client.post("/eventos", json=event_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == event_data["nome"]
        assert data["max_participantes"] == event_data["max_participantes"]

    def test_list_events_with_filters(self, client, auth_headers, sample_events):
        """Teste listagem com filtros"""
        response = client.get("/eventos?status=ativo&limit=10", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "eventos" in data
        assert len(data["eventos"]) <= 10

    def test_update_event_unauthorized(self, client):
        """Teste atualização sem autenticação"""
        response = client.put("/eventos/1", json={"nome": "Updated"})
        assert response.status_code == 401
```

### 🎮 **Testes de Gamificação**

```python
# tests/test_gamification.py
class TestGamificationEngine:
    """Testes para engine de gamificação"""

    async def test_checkin_points_calculation(self, gamification_engine, sample_user):
        """Teste cálculo de pontos por check-in"""
        result = await gamification_engine.process_event(
            event_type="checkin",
            user_id=sample_user.id,
            context={"event_id": 1, "early_checkin": True}
        )

        assert result["points_earned"] == 15  # 10 base + 5 early bonus
        assert len(result["badges_earned"]) > 0

    async def test_badge_criteria_matching(self, badge_service, sample_user):
        """Teste critérios de badges"""
        badge = await badge_service.check_badge_earned(
            user_id=sample_user.id,
            badge_name="early_bird"
        )

        assert badge is not None
        assert badge.name == "early_bird"
```

---

## 🚀 **Deploy e Produção**

### 🐳 **Docker Configuration**

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

# Dockerfile.frontend
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy and build
COPY . .
RUN npm run build

# Serve with nginx
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

### 🔧 **Docker Compose Production**

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  backend:
    build:
      context: ./paineluniversal/backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/eventos
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=production
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs

  frontend:
    build:
      context: ./paineluniversal/frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: eventos
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
```

### 📈 **CI/CD Pipeline**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          cd paineluniversal/backend
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run tests
        run: |
          cd paineluniversal/backend
          pytest tests/ -v --cov=app --cov-report=xml

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Test frontend
        run: |
          cd paineluniversal/frontend
          npm ci
          npm run test
          npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Deploy to production
        run: |
          echo "Deploying to production server..."
          # Deploy commands here
```

---

## 📋 **Padrões de Desenvolvimento**

### 🎯 **Convenções de Código**

```python
# Python Code Style (PEP 8 + Black)

# 1. Imports organization
from __future__ import annotations  # Python 3.7+

import os
import sys
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.models import User, Event
from app.services import UserService

# 2. Class naming (PascalCase)
class EventService:
    """Service class documentation"""

    def __init__(self, db: Session):
        self.db = db

    async def create_event(self, event_data: EventCreate) -> Event:
        """Method documentation with type hints"""
        pass

# 3. Function naming (snake_case)
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Function documentation"""
    pass

# 4. Variable naming (snake_case)
event_count = 0
user_permissions = ["read", "write"]
is_active = True
```

```typescript
// TypeScript Code Style

// 1. Interface naming (PascalCase)
interface EventData {
  id: number;
  nome: string;
  dataInicio: string;
}

// 2. Function naming (camelCase)
const createEvent = async (eventData: EventCreate): Promise<Event> => {
  // Implementation
};

// 3. Component naming (PascalCase)
export const EventCard: React.FC<EventCardProps> = ({ event }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Component content */}
    </div>
  );
};

// 4. Hook naming (camelCase with 'use' prefix)
export const useEventData = (eventId: number) => {
  const [event, setEvent] = useState<Event | null>(null);
  // Hook logic
  return { event, setEvent };
};
```

### 📚 **Documentação de Código**

```python
# Docstring style (Google/NumPy style)
class EventService:
    """Serviço para gestão de eventos.

    Este serviço centraliza toda a lógica de negócio relacionada
    a eventos, incluindo criação, atualização, busca e analytics.

    Attributes:
        db: Sessão do banco de dados
        cache: Cliente Redis para cache
        notification_service: Serviço de notificações
    """

    async def create_event(
        self,
        event_data: EventCreate,
        user_id: int
    ) -> Event:
        """Cria um novo evento no sistema.

        Args:
            event_data: Dados do evento a ser criado
            user_id: ID do usuário organizador

        Returns:
            Event: Evento criado com ID atribuído

        Raises:
            ValueError: Se os dados do evento forem inválidos
            PermissionError: Se o usuário não tiver permissão

        Example:
            >>> event_data = EventCreate(nome="Meu Evento", ...)
            >>> event = await service.create_event(event_data, user_id=1)
            >>> print(event.id)
            1
        """
```

### 🔒 **Segurança**

```python
# Boas práticas de segurança

# 1. Validação de entrada
from pydantic import BaseModel, validator
from typing import Optional

class EventCreate(BaseModel):
    nome: str
    descricao: str
    max_participantes: int

    @validator('nome')
    def validate_nome(cls, v):
        if len(v) < 3:
            raise ValueError('Nome deve ter pelo menos 3 caracteres')
        if len(v) > 200:
            raise ValueError('Nome muito longo')
        return v.strip()

    @validator('max_participantes')
    def validate_max_participantes(cls, v):
        if v < 1:
            raise ValueError('Deve permitir pelo menos 1 participante')
        if v > 10000:
            raise ValueError('Limite máximo de 10.000 participantes')
        return v

# 2. Sanitização de dados
import html
import re

def sanitize_html(text: str) -> str:
    """Remove tags HTML perigosas"""
    # Remove scripts e outros elementos perigosos
    clean_text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
    clean_text = re.sub(r'<.*?>', '', clean_text)
    return html.escape(clean_text)

# 3. Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, user_data: UserLogin):
    # Login logic with rate limiting
    pass
```

---

## 🔧 **Utilitários e Ferramentas**

### 🛠️ **Scripts de Desenvolvimento**

```powershell
# scripts/development/start-dev.ps1
# Script para iniciar ambiente de desenvolvimento

Write-Host "🚀 Iniciando ambiente de desenvolvimento..." -ForegroundColor Green

# 1. Verificar pré-requisitos
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python não encontrado. Instale Python 3.11+"
    exit 1
}

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js não encontrado. Instale Node.js 18+"
    exit 1
}

# 2. Ativar ambiente virtual
Set-Location "paineluniversal/backend"
if (-not (Test-Path "venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
}

& "venv\Scripts\Activate.ps1"

# 3. Instalar dependências
Write-Host "Instalando dependências Python..." -ForegroundColor Yellow
pip install -r requirements.txt

# 4. Executar migrações
Write-Host "Executando migrações..." -ForegroundColor Yellow
python -m alembic upgrade head

# 5. Iniciar backend em background
Write-Host "Iniciando backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "python -m uvicorn app.main:app --reload --port 8000"

# 6. Instalar dependências frontend
Set-Location "../frontend"
Write-Host "Instalando dependências Node.js..." -ForegroundColor Yellow
npm install

# 7. Iniciar frontend
Write-Host "Iniciando frontend..." -ForegroundColor Green
npm run dev

Write-Host "✅ Ambiente iniciado com sucesso!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
```

### 🧹 **Scripts de Limpeza**

```python
# scripts/utilities/clean_project.py
"""Script para limpeza de arquivos temporários e cache"""

import os
import shutil
from pathlib import Path

def clean_python_cache():
    """Remove cache Python"""
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
                print(f"Removido: {os.path.join(root, dir_name)}")

def clean_node_modules():
    """Remove node_modules"""
    for path in Path('.').rglob('node_modules'):
        if path.is_dir():
            shutil.rmtree(path)
            print(f"Removido: {path}")

def clean_build_artifacts():
    """Remove artefatos de build"""
    patterns = ['*.pyc', '*.pyo', '*.egg-info', 'dist/', 'build/']
    for pattern in patterns:
        for path in Path('.').rglob(pattern):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            print(f"Removido: {path}")

if __name__ == "__main__":
    print("🧹 Limpando projeto...")
    clean_python_cache()
    clean_node_modules()
    clean_build_artifacts()
    print("✅ Limpeza concluída!")
```

---

## 📞 **Suporte e Recursos**

### 📚 **Recursos Adicionais**

- **📖 FastAPI Docs:** https://fastapi.tiangolo.com/
- **⚛️ React Docs:** https://react.dev/
- **🎨 Tailwind CSS:** https://tailwindcss.com/docs
- **🗄️ SQLAlchemy:** https://docs.sqlalchemy.org/
- **📊 Prometheus:** https://prometheus.io/docs/

### 🔧 **Ferramentas Recomendadas**

**IDEs:**

- 🆚 Visual Studio Code + Python/TypeScript extensions
- 💎 PyCharm Professional
- 🌟 Cursor (AI-powered)

**Database Tools:**

- 🐘 pgAdmin (PostgreSQL)
- 📊 DBeaver (Universal)
- 🔍 Redis Commander

**API Testing:**

- 📮 Postman
- ⚡ Insomnia
- 🔧 HTTPie

**Monitoring:**

- 📊 Grafana
- 📈 Prometheus
- 🐛 Sentry

---

## 🎯 **Próximos Passos**

### 🚀 **Roadmap Técnico**

1. **🧪 Testes (Semana 1)**

   - Cobertura de testes > 90%
   - Testes de integração
   - Testes E2E com Playwright

2. **⚡ Performance (Semana 2)**

   - Otimização de queries
   - Cache avançado
   - CDN para assets

3. **🔒 Segurança (Semana 3)**

   - Auditoria de segurança
   - Penetration testing
   - Compliance LGPD

4. **📱 Mobile App (Semana 4-6)**
   - React Native
   - Push notifications
   - Offline support

### 🎓 **Processo de Contribuição**

1. **Fork** o repositório
2. **Clone** sua fork
3. **Crie** uma branch feature
4. **Implemente** suas mudanças
5. **Escreva** testes
6. **Execute** linting e testes
7. **Abra** um Pull Request

---

**🎉 Agora você tem todo o conhecimento necessário para contribuir e desenvolver o Sistema Universal de Eventos! Happy Coding! 🚀**
