"""
Sistema Universal de Gestão de Eventos - VERSÃO COMPLETA
FastAPI Application - FASE 3: FUNCIONALIDADES AVANÇADAS

Sistema completo com todas as funcionalidades:
- Todos os 23+ routers ativos
- OpenAI e IA integração
- Monitoring e analytics avançados
- WebSocket tempo real
- Redis cache performático
- Sistema de backup automático
"""

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import logging
import os
import time
import uvicorn
from datetime import datetime
from typing import Dict, List, Any
import json
import uuid

# Core imports
from app.database import create_tables
from app.dependencies import get_current_user, get_openai_service

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ROUTERS - IMPORTAÇÃO SEGURA
try:
    # Core routers (básicos)
    from app.routers import auth, usuarios, eventos
    CORE_ROUTERS = [auth, usuarios, eventos]
    logger.info("✅ Core routers importados com sucesso")
except ImportError as e:
    logger.error(f"❌ Erro ao importar core routers: {e}")
    CORE_ROUTERS = []

try:
    # Business routers (negócio)
    from app.routers import (
        pdv, financeiro, estoque, empresas, 
        checkins, transacoes, cupons
    )
    BUSINESS_ROUTERS = [pdv, financeiro, estoque, empresas, checkins, transacoes, cupons]
    logger.info("✅ Business routers importados com sucesso")
except ImportError as e:
    logger.error(f"⚠️ Alguns business routers falharam: {e}")
    BUSINESS_ROUTERS = []

try:
    # Advanced routers (avançados)
    from app.routers import (
        dashboard, analytics, relatorios, relatorios_avancados,
        gamificacao, qr_codes, backup, listas
    )
    ADVANCED_ROUTERS = [dashboard, analytics, relatorios, relatorios_avancados, 
                       gamificacao, qr_codes, backup, listas]
    logger.info("✅ Advanced routers importados com sucesso")
except ImportError as e:
    logger.error(f"⚠️ Alguns advanced routers falharam: {e}")
    ADVANCED_ROUTERS = []

try:
    # AI & Expert routers (IA e expert)
    from app.routers import (
        ai_intelligence, ia_avancada, auth_ultra_expert,
        monitoramento, cache_inteligente
    )
    AI_ROUTERS = [ai_intelligence, ia_avancada, auth_ultra_expert, 
                 monitoramento, cache_inteligente]
    logger.info("✅ AI routers importados com sucesso")
except ImportError as e:
    logger.error(f"⚠️ Alguns AI routers falharam: {e}")
    AI_ROUTERS = []

try:
    # Integration routers (integrações)
    from app.routers import whatsapp, n8n, utils
    INTEGRATION_ROUTERS = [whatsapp, n8n, utils]
    logger.info("✅ Integration routers importados com sucesso")
except ImportError as e:
    logger.error(f"⚠️ Alguns integration routers falharam: {e}")
    INTEGRATION_ROUTERS = []

# SERVICES - IMPORTAÇÃO SEGURA
try:
    from app.services.monitoring import (
        monitoring_system, 
        alerting_system, 
        health_check_background
    )
    MONITORING_AVAILABLE = True
    logger.info("✅ Monitoring services disponíveis")
except ImportError as e:
    logger.error(f"⚠️ Monitoring services não disponível: {e}")
    MONITORING_AVAILABLE = False

try:
    from app.services.websocket_events import websocket_event_manager
    WEBSOCKET_AVAILABLE = True
    logger.info("✅ WebSocket services disponíveis")
except ImportError as e:
    logger.error(f"⚠️ WebSocket services não disponível: {e}")
    WEBSOCKET_AVAILABLE = False

try:
    from app.services.redis_cache import init_redis_cache, close_redis_cache
    REDIS_AVAILABLE = True
    logger.info("✅ Redis cache disponível")
except ImportError as e:
    logger.error(f"⚠️ Redis cache não disponível: {e}")
    REDIS_AVAILABLE = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager com inicialização segura"""
    logger.info("🚀 Iniciando Sistema Universal de Gestão...")
    
    # 1. Inicializar banco de dados
    try:
        create_tables()
        logger.info("✅ Database inicializado")
    except Exception as e:
        logger.error(f"❌ Erro na inicialização do database: {e}")
    
    # 2. Inicializar Redis (se disponível)
    if REDIS_AVAILABLE:
        try:
            await init_redis_cache()
            logger.info("✅ Redis cache inicializado")
        except Exception as e:
            logger.error(f"⚠️ Redis não inicializado: {e}")
    
    # 3. Inicializar Monitoring (se disponível)
    if MONITORING_AVAILABLE:
        try:
            asyncio.create_task(health_check_background())
            logger.info("✅ Monitoring iniciado")
        except Exception as e:
            logger.error(f"⚠️ Monitoring não iniciado: {e}")
    
    yield
    
    # Cleanup
    logger.info("🛑 Finalizando Sistema...")
    if REDIS_AVAILABLE:
        try:
            await close_redis_cache()
            logger.info("✅ Redis fechado")
        except Exception as e:
            logger.error(f"⚠️ Erro ao fechar Redis: {e}")

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema Universal de Gestão de Eventos - COMPLETO",
    description="Sistema completo com todas as funcionalidades avançadas",
    version="3.0.0",
    lifespan=lifespan
)

# MIDDLEWARE CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# ROUTER REGISTRATION - SEGURO E PROGRESSIVO
def register_routers():
    """Registra routers de forma segura"""
    registered_count = 0
    
    # Core routers (essenciais)
    for router in CORE_ROUTERS:
        try:
            app.include_router(router.router, prefix="/api")
            registered_count += 1
            logger.info(f"✅ Router registrado: {router.__name__}")
        except Exception as e:
            logger.error(f"❌ Erro ao registrar {router.__name__}: {e}")
    
    # Business routers
    for router in BUSINESS_ROUTERS:
        try:
            app.include_router(router.router, prefix="/api")
            registered_count += 1
            logger.info(f"✅ Router registrado: {router.__name__}")
        except Exception as e:
            logger.error(f"❌ Erro ao registrar {router.__name__}: {e}")
    
    # Advanced routers
    for router in ADVANCED_ROUTERS:
        try:
            app.include_router(router.router, prefix="/api")
            registered_count += 1
            logger.info(f"✅ Router registrado: {router.__name__}")
        except Exception as e:
            logger.error(f"❌ Erro ao registrar {router.__name__}: {e}")
    
    # AI routers
    for router in AI_ROUTERS:
        try:
            app.include_router(router.router, prefix="/api")
            registered_count += 1
            logger.info(f"✅ Router registrado: {router.__name__}")
        except Exception as e:
            logger.error(f"❌ Erro ao registrar {router.__name__}: {e}")
    
    # Integration routers
    for router in INTEGRATION_ROUTERS:
        try:
            app.include_router(router.router, prefix="/api")
            registered_count += 1
            logger.info(f"✅ Router registrado: {router.__name__}")
        except Exception as e:
            logger.error(f"❌ Erro ao registrar {router.__name__}: {e}")
    
    logger.info(f"🎯 Total de routers registrados: {registered_count}")
    return registered_count

# Registrar todos os routers
total_routers = register_routers()

# ENDPOINTS PRINCIPAIS
@app.get("/")
async def root():
    """Homepage com status do sistema"""
    return {
        "message": "Sistema Universal de Gestão de Eventos - VERSÃO COMPLETA",
        "version": "3.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "routers_registered": total_routers,
            "monitoring": MONITORING_AVAILABLE,
            "websocket": WEBSOCKET_AVAILABLE,
            "redis_cache": REDIS_AVAILABLE,
            "ai_integration": len(AI_ROUTERS) > 0
        }
    }

@app.get("/health")
async def health_check():
    """Health check detalhado"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "routers": total_routers,
            "monitoring": MONITORING_AVAILABLE,
            "websocket": WEBSOCKET_AVAILABLE,
            "redis": REDIS_AVAILABLE,
            "ai": len(AI_ROUTERS) > 0
        }
    }

@app.get("/status")
async def system_status():
    """Status completo do sistema"""
    return {
        "system": "Sistema Universal de Gestão",
        "version": "3.0.0",
        "status": "running",
        "components": {
            "core_routers": len(CORE_ROUTERS),
            "business_routers": len(BUSINESS_ROUTERS),
            "advanced_routers": len(ADVANCED_ROUTERS),
            "ai_routers": len(AI_ROUTERS),
            "integration_routers": len(INTEGRATION_ROUTERS),
            "total_routers": total_routers
        },
        "services": {
            "monitoring": MONITORING_AVAILABLE,
            "websocket": WEBSOCKET_AVAILABLE,
            "redis_cache": REDIS_AVAILABLE
        },
        "timestamp": datetime.now().isoformat()
    }

# WebSocket endpoint (se disponível)
if WEBSOCKET_AVAILABLE:
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint para comunicação em tempo real"""
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                await websocket.send_text(f"Echo: {data}")
        except WebSocketDisconnect:
            logger.info("Cliente WebSocket desconectado")

if __name__ == "__main__":
    uvicorn.run(
        "app.main_completo:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
