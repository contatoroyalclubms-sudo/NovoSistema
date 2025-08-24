"""
FastAPI Application - Versão Simplificada para Inicialização
Sistema Universal de Gestão de Eventos - FASE 2
"""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

from app.core.database_minimal import init_db
from app.schemas_simple import HealthCheck

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds', 
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    print("Iniciando Sistema Universal de Gestao de Eventos...")
    await init_db()
    print("Banco de dados inicializado!")
    yield
    # Shutdown
    print("Encerrando sistema...")


# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema Universal de Gestão de Eventos",
    description="API completa para gestão de eventos, check-ins e PDV",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware para métricas Prometheus
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Registrar métricas
    duration = time.time() - start_time
    endpoint = request.url.path
    method = request.method
    status = str(response.status_code)
    
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    return response

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:4200", 
        "http://localhost:4201",
        "http://localhost:4202",
        "http://localhost:4203",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4200",
        "http://127.0.0.1:4201",
        "http://127.0.0.1:4202",
        "http://127.0.0.1:4203",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Sistema Universal de Gestão de Eventos",
        "version": "2.0.0",
        "status": "online",
        "docs": "/docs",
        "timestamp": datetime.now()
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check da aplicação"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version="2.0.0"
    )


@app.get("/api/v1/health")
async def api_health():
    """Health check da API"""
    return {
        "status": "healthy",
        "api_version": "v1",
        "timestamp": datetime.now(),
        "database": "connected"
    }

# Basic Auth Endpoints for Testing
@app.post("/api/v1/auth/login")
async def auth_login(credentials: dict):
    """Basic login endpoint for testing"""
    # Support both email/senha and username/password formats
    email = credentials.get("email", "") or credentials.get("username", "")
    senha = credentials.get("senha", "") or credentials.get("password", "")
    
    # Test credentials
    if email == "admin@eventos.com" and senha == "admin123":
        user_data = {
            "id": 1,
            "username": "admin",
            "email": "admin@eventos.com", 
            "full_name": "Administrador",
            "is_active": True,
            "is_superuser": True,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }
        tokens = {
            "access_token": "test-jwt-token-admin",
            "refresh_token": "test-refresh-token", 
            "token_type": "bearer"
        }
        return {
            **tokens,  # Include tokens at root level
            "user": user_data,
            "tokens": tokens  # Also include nested for compatibility
        }
    elif email == "user@eventos.com" and senha == "user123":
        user_data = {
            "id": 2,
            "username": "user",
            "email": "user@eventos.com",
            "full_name": "Usuario Teste", 
            "is_active": True,
            "is_superuser": False,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }
        tokens = {
            "access_token": "test-jwt-token-user",
            "refresh_token": "test-refresh-token",
            "token_type": "bearer"
        }
        return {
            **tokens,  # Include tokens at root level
            "user": user_data,
            "tokens": tokens  # Also include nested for compatibility
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos"
        )

@app.get("/api/v1/auth/me")
async def auth_me():
    """Get current user info - simplified for testing"""
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@eventos.com",
        "full_name": "Administrador",
        "is_active": True,
        "is_superuser": True,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }

@app.post("/api/v1/auth/logout")
async def auth_logout():
    """Logout endpoint"""
    return {
        "message": "Logout realizado com sucesso",
        "success": True
    }

@app.get("/metrics")
async def get_metrics():
    """Endpoint para métricas do Prometheus"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )