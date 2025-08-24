"""
Sistema Universal de Gestão de Eventos - Versão Simplificada
FastAPI Backend com funcionalidades básicas
"""

from fastapi import FastAPI, Request, Response
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

# Routers principais
from app.routers import (
    auth, usuarios, eventos, checkin,
    pdv, gamificacao, listas,
    analytics, financeiro, ranking
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    try:
        # Inicialização
        logger.info("🚀 Iniciando Sistema Universal de Gestão de Eventos...")
        
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
    title="Sistema Universal de Gestão de Eventos",
    description="API completa para gestão de eventos, check-in, PDV e gamificação",
    version="2.0.0",
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
# ROUTERS
# =============================================================================

# Autenticação
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])

# Usuários
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuários"])

# Eventos
app.include_router(eventos.router, prefix="/api/eventos", tags=["Eventos"])

# Check-in
app.include_router(checkin.router, prefix="/api/checkin", tags=["Check-in"])

# PDV
app.include_router(pdv.router, prefix="/api/pdv", tags=["PDV"])

# Gamificação
app.include_router(gamificacao.router, prefix="/api/gamificacao", tags=["Gamificação"])

# Listas
app.include_router(listas.router, prefix="/api/listas", tags=["Listas"])

# Analytics
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# Financeiro
app.include_router(financeiro.router, prefix="/api/financeiro", tags=["Financeiro"])

# Ranking
app.include_router(ranking.router, prefix="/api/ranking", tags=["Ranking"])

# =============================================================================
# ENDPOINTS ROOT
# =============================================================================

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Sistema Universal de Gestão de Eventos",
        "version": "2.0.0",
        "status": "active",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde básica"""
    return {
        "status": "healthy",
        "message": "API funcionando corretamente"
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
        "app.main_simples:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
