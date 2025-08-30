"""
Sistema Universal de Gestão de Eventos - Versão Intermediária
FastAPI Backend com funcionalidades principais
"""

from fastapi import FastAPI, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import os

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base de dados
from app.database import create_tables

# Routers principais - importação individual para evitar conflitos
from app.routers.auth import router as auth_router
from app.routers.usuarios import router as usuarios_router
from app.routers.eventos import router as eventos_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    try:
        # Inicialização
        logger.info("🚀 Iniciando Sistema Universal - Versão Intermediária...")
        
        # Criar tabelas
        create_tables()
        logger.info("✅ Base de dados inicializada")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Erro no ciclo de vida: {e}")
        raise
    finally:
        logger.info("🔄 Finalizando aplicação...")

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema Universal de Gestão de Eventos - Intermediário",
    description="API com funcionalidades principais para gestão de eventos",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# =============================================================================
# MIDDLEWARES
# =============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compressão
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Hosts confiáveis
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app"]
)

# =============================================================================
# ROUTERS PRINCIPAIS
# =============================================================================

# Autenticação
app.include_router(auth_router, prefix="/api/auth", tags=["Autenticação"])

# Usuários
app.include_router(usuarios_router, prefix="/api/usuarios", tags=["Usuários"])

# Eventos
app.include_router(eventos_router, prefix="/api/eventos", tags=["Eventos"])

# =============================================================================
# ENDPOINTS ROOT
# =============================================================================

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Sistema Universal de Gestão de Eventos - Intermediário",
        "version": "2.1.0",
        "status": "active",
        "features": ["auth", "usuarios", "eventos"],
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde"""
    return {
        "status": "healthy",
        "message": "API funcionando com funcionalidades principais",
        "database": "connected",
        "features_active": ["authentication", "users", "events"]
    }

@app.get("/api/status")
async def api_status():
    """Status detalhado da API"""
    try:
        # Teste básico de banco
        from app.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        database_status = "connected"
    except Exception as e:
        database_status = f"error: {str(e)}"
    
    return {
        "api": "Sistema Universal de Eventos",
        "version": "2.1.0",
        "status": "operational",
        "database": database_status,
        "endpoints": {
            "auth": "/api/auth/",
            "usuarios": "/api/usuarios/",
            "eventos": "/api/eventos/",
            "docs": "/docs"
        }
    }

# =============================================================================
# HANDLERS DE ERRO
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {exc}")
    return Response(
        content=f"Erro interno do servidor: {str(exc)}",
        status_code=500
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_intermediario:app",
        host="127.0.0.1",
        port=8002,
        reload=True
    )
