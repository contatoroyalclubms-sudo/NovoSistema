# ⚡ FASE 5: Otimização e Performance

## 📋 Checklist de Implementação

### 1. Backend Performance Optimization

#### 1.1 Database Optimization
- [ ] **Arquivo:** `backend/app/database.py` (melhorias)
- [ ] Connection pooling configurado
- [ ] Índices otimizados
- [ ] Query optimization
- [ ] Lazy loading estratégico

#### 1.2 API Performance
- [ ] **Arquivo:** `backend/app/middleware/performance.py`
- [ ] Response time monitoring
- [ ] Request compression
- [ ] Rate limiting
- [ ] Caching headers

#### 1.3 Background Tasks
- [ ] **Pasta:** `backend/app/tasks/`
- [ ] Celery integration
- [ ] Email queue
- [ ] Report generation
- [ ] Data cleanup jobs

### 2. Frontend Performance

#### 2.1 Build Optimization
- [ ] **Arquivo:** `frontend/vite.config.ts` (melhorias)
- [ ] Code splitting
- [ ] Tree shaking
- [ ] Bundle analysis
- [ ] Asset optimization

#### 2.2 Runtime Performance
- [ ] **Pasta:** `frontend/src/hooks/performance/`
- [ ] useCallback optimization
- [ ] useMemo implementation
- [ ] Virtual scrolling
- [ ] Image lazy loading

### 3. Monitoring e Observabilidade

#### 3.1 Application Monitoring
- [ ] **Arquivo:** `backend/app/monitoring/metrics.py`
- [ ] Prometheus metrics
- [ ] Health checks
- [ ] Performance tracking
- [ ] Error monitoring

#### 3.2 Logging Enhancement
- [ ] **Arquivo:** `backend/app/logging/structured.py`
- [ ] Structured logging
- [ ] Log aggregation
- [ ] Error tracking
- [ ] Audit trails

## 🚀 Templates - Performance

### Database Optimization
```python
# backend/app/database.py (melhorias)
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
import logging

DATABASE_URL = os.getenv("DATABASE_URL")

# Engine otimizado com pool de conexões
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Desabilitar em produção
)

# Logging de queries lentas
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.5:  # Log queries > 500ms
        logging.warning(f"Slow query: {total:.3f}s - {statement[:100]}...")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency otimizada
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Cache de queries comuns
from functools import lru_cache

@lru_cache(maxsize=128)
def get_empresa_by_id(empresa_id: int, db_session):
    return db_session.query(Empresa).filter(Empresa.id == empresa_id).first()
```

### Performance Middleware
```python
# backend/app/middleware/performance.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Adicionar headers de cache para recursos estáticos
        if request.url.path.startswith('/static/'):
            response = await call_next(request)
            response.headers["Cache-Control"] = "public, max-age=31536000"  # 1 ano
            return response
        
        # Processar request
        response = await call_next(request)
        
        # Calcular tempo de resposta
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log requests lentos
        if process_time > 1.0:  # > 1 segundo
            logger.warning(
                f"Slow request: {request.method} {request.url.path} - {process_time:.3f}s"
            )
        
        # Adicionar headers de compressão
        if request.headers.get("accept-encoding", "").find("gzip") != -1:
            response.headers["Content-Encoding"] = "gzip"
        
        return response

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Aplicar rate limiting específico por endpoint
def rate_limit(per_minute: int = 60):
    return limiter.limit(f"{per_minute}/minute")
```

### Background Tasks com Celery
```python
# backend/app/tasks/celery_app.py
from celery import Celery
import os

# Configuração do Celery
celery_app = Celery(
    "eventos_tasks",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379"),
    include=["app.tasks.email_tasks", "app.tasks.report_tasks", "app.tasks.cleanup_tasks"]
)

# Configurações
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_routes={
        "app.tasks.email_tasks.*": {"queue": "email"},
        "app.tasks.report_tasks.*": {"queue": "reports"},
        "app.tasks.cleanup_tasks.*": {"queue": "cleanup"},
    }
)

# Tarefas periódicas
celery_app.conf.beat_schedule = {
    'cleanup-expired-tokens': {
        'task': 'app.tasks.cleanup_tasks.cleanup_expired_tokens',
        'schedule': 3600.0,  # A cada hora
    },
    'generate-daily-reports': {
        'task': 'app.tasks.report_tasks.generate_daily_reports',
        'schedule': 86400.0,  # Diário
    },
    'update-rankings': {
        'task': 'app.tasks.gamification_tasks.update_rankings',
        'schedule': 1800.0,  # A cada 30 minutos
    },
}

# Tasks de email
@celery_app.task
def send_welcome_email(user_email: str, user_name: str):
    """Enviar email de boas-vindas"""
    from app.services.email_service import email_service
    
    template_data = {
        "user_name": user_name,
        "login_url": "https://app.eventos.com/login"
    }
    
    return email_service.send_template_email(
        to_email=user_email,
        template_name="welcome",
        template_data=template_data
    )

@celery_app.task
def send_event_reminder(event_id: int):
    """Enviar lembrete de evento"""
    from app.models import Evento, Transacao
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        evento = db.query(Evento).filter(Evento.id == event_id).first()
        if not evento:
            return "Evento não encontrado"
        
        # Buscar participantes
        participantes = db.query(Transacao).filter(
            Transacao.evento_id == event_id,
            Transacao.status == 'aprovada'
        ).all()
        
        for transacao in participantes:
            send_event_reminder_email.delay(
                transacao.email_comprador,
                evento.nome,
                evento.data_evento.isoformat()
            )
        
        return f"Lembretes enviados para {len(participantes)} participantes"
    finally:
        db.close()
```

## 🎯 Frontend Performance

### Vite Config Optimization
```typescript
// frontend/vite.config.ts (melhorias)
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import { resolve } from 'path';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.eventos\.com\/api\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 // 24 hours
              }
            }
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-select'],
          charts: ['recharts'],
          utils: ['axios', 'date-fns']
        }
      }
    },
    chunkSizeWarningLimit: 1000,
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'axios']
  }
});
```

### Performance Hooks
```typescript
// frontend/src/hooks/performance/useVirtualizedList.tsx
import { useMemo, useState, useCallback } from 'react';

interface VirtualizedListProps<T> {
  items: T[];
  itemHeight: number;
  containerHeight: number;
  renderItem: (item: T, index: number) => React.ReactNode;
}

export function useVirtualizedList<T>({
  items,
  itemHeight,
  containerHeight,
  renderItem
}: VirtualizedListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);

  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length
    );

    return items.slice(startIndex, endIndex).map((item, index) => ({
      item,
      index: startIndex + index,
      top: (startIndex + index) * itemHeight
    }));
  }, [items, itemHeight, containerHeight, scrollTop]);

  const totalHeight = items.length * itemHeight;

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  return {
    visibleItems,
    totalHeight,
    handleScroll,
    renderItem
  };
}

// frontend/src/hooks/performance/useDebounce.tsx
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// frontend/src/hooks/performance/useInfiniteScroll.tsx
import { useState, useEffect, useCallback } from 'react';

interface UseInfiniteScrollProps {
  fetchMore: () => Promise<any>;
  hasMore: boolean;
  threshold?: number;
}

export function useInfiniteScroll({
  fetchMore,
  hasMore,
  threshold = 100
}: UseInfiniteScrollProps) {
  const [loading, setLoading] = useState(false);

  const handleScroll = useCallback(async () => {
    if (loading || !hasMore) return;

    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
    
    if (scrollTop + clientHeight >= scrollHeight - threshold) {
      setLoading(true);
      try {
        await fetchMore();
      } finally {
        setLoading(false);
      }
    }
  }, [loading, hasMore, threshold, fetchMore]);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  return { loading };
}
```

## 📊 Monitoring e Métricas

### Prometheus Metrics
```python
# backend/app/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from functools import wraps

# Métricas de API
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'websocket_connections_active',
    'Active WebSocket connections',
    ['event_id']
)

# Métricas de negócio
SALES_TOTAL = Counter(
    'sales_total',
    'Total sales processed',
    ['event_id', 'promoter_id']
)

CHECKINS_TOTAL = Counter(
    'checkins_total',
    'Total check-ins processed',
    ['event_id']
)

def track_request_metrics(func):
    """Decorator para tracking de métricas de request"""
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        start_time = time.time()
        
        try:
            response = await func(request, *args, **kwargs)
            status = response.status_code
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=status
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()
            raise
    
    return wrapper

def track_business_metrics(metric_type: str, **labels):
    """Track business metrics"""
    if metric_type == 'sale':
        SALES_TOTAL.labels(**labels).inc()
    elif metric_type == 'checkin':
        CHECKINS_TOTAL.labels(**labels).inc()

# Endpoint para métricas
from fastapi import APIRouter, Response

metrics_router = APIRouter()

@metrics_router.get("/metrics")
async def get_metrics():
    """Endpoint para Prometheus scraping"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### Performance Monitoring Component
```typescript
// frontend/src/components/monitoring/PerformanceMonitor.tsx
import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Activity, Zap, Clock, Users } from 'lucide-react';

interface PerformanceMetrics {
  responseTime: number;
  activeUsers: number;
  errorRate: number;
  uptime: number;
}

const PerformanceMonitor: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        // Simular carregamento de métricas
        const response = await fetch('/api/monitoring/metrics');
        const data = await response.json();
        setMetrics(data);
      } catch (error) {
        console.error('Erro ao carregar métricas:', error);
      } finally {
        setLoading(false);
      }
    };

    loadMetrics();
    const interval = setInterval(loadMetrics, 30000); // Atualizar a cada 30s

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div>Carregando métricas...</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Tempo de Resposta</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics?.responseTime}ms</div>
          <p className="text-xs text-muted-foreground">
            {metrics?.responseTime < 200 ? '🟢 Excelente' : 
             metrics?.responseTime < 500 ? '🟡 Bom' : '🔴 Lento'}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Usuários Ativos</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics?.activeUsers}</div>
          <p className="text-xs text-muted-foreground">
            Conectados agora
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Taxa de Erro</CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics?.errorRate}%</div>
          <p className="text-xs text-muted-foreground">
            {metrics?.errorRate < 1 ? '🟢 Baixa' : 
             metrics?.errorRate < 5 ? '🟡 Moderada' : '🔴 Alta'}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Uptime</CardTitle>
          <Zap className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics?.uptime}%</div>
          <p className="text-xs text-muted-foreground">
            Últimos 30 dias
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default PerformanceMonitor;
```

## 📊 Cronograma Fase 5

| Tarefa | Estimativa | Status |
|--------|------------|--------|
| Database optimization | 1 dia | ⏳ |
| API performance middleware | 1 dia | ⏳ |
| Background tasks Celery | 2 dias | ⏳ |
| Frontend build optimization | 1 dia | ⏳ |
| Performance hooks | 1 dia | ⏳ |
| Monitoring setup | 1 dia | ⏳ |

**Total:** 7 dias (1 semana)

## 🎯 Metas de Performance

- **API Response Time:** <200ms (95th percentile)
- **Frontend Load Time:** <3s (initial load)
- **Database Queries:** <100ms (average)
- **Memory Usage:** <512MB (backend)
- **Bundle Size:** <2MB (frontend)