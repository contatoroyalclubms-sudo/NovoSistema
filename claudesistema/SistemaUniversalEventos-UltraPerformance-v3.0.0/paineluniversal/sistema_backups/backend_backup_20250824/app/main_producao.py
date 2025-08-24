"""
Sistema Universal - FASE 4: VERSÃO DE PRODUÇÃO
Otimizações avançadas, documentação automática, performance e produção
"""

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import logging
import sys
import time
import json
import asyncio
import os
from pathlib import Path

# Database e funcionalidades existentes
from app.database_sqlite import (
    create_tables, get_all_usuarios, get_all_eventos, 
    get_all_produtos, get_dashboard_stats
)

# Importar router WhatsApp
from app.routers.whatsapp import router as whatsapp_router

# Importar router Analytics
from .routers.analytics import router as analytics_router

# Importar router BackupManager
from .routers.backup_manager import router as backup_manager_router

# Importar router Logs
from .routers.logs import router as logs_router

# Importar router QR Check-in
from .routers.qr_checkin import router as qr_checkin_router

# Importar router de Autenticação
from .routers.authentication import router as auth_router

# Importar router de Notificações
from .routers.notifications import router as notifications_router

# Importar BackupManager
from .backup_manager import backup_manager

# Importar LogManager
from .logging_manager import log_manager

# Importar AuthManager
from .auth_manager import auth_manager

# Configuração avançada de logging
log_manager.setup_logging()
logger = logging.getLogger(__name__)

# Cache em memória simples
CACHE = {}
CACHE_TTL = {}

def get_cache(key: str):
    """Sistema de cache simples"""
    if key in CACHE and key in CACHE_TTL:
        if datetime.now() < CACHE_TTL[key]:
            logger.info(f"[CACHE] Cache HIT: {key}")
            return CACHE[key]
        else:
            # Cache expirado
            del CACHE[key]
            del CACHE_TTL[key]
    return None

def set_cache(key: str, value, ttl_minutes: int = 10):
    """Define cache com TTL"""
    CACHE[key] = value
    CACHE_TTL[key] = datetime.now() + timedelta(minutes=ttl_minutes)
    logger.info(f"[CACHE] SET: {key} (TTL: {ttl_minutes}min)")

# Middleware de Performance e Logging
class PerformanceMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Processar request
            await self.app(scope, receive, send)
            
            # Calcular tempo de resposta
            process_time = time.time() - start_time
            
            # Log da performance
            method = scope["method"]
            path = scope["path"]
            logger.info(f"[PERF] {method} {path} - {process_time:.4f}s")
        else:
            await self.app(scope, receive, send)

# Sistema de backup automático
async def backup_database():
    """Backup automático do database"""
    try:
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"sistema_universal_backup_{timestamp}.db"
        
        # Simular backup (copiar arquivo SQLite)
        import shutil
        source_db = Path("app/sistema_universal.db")
        if source_db.exists():
            shutil.copy2(source_db, backup_file)
            logger.info(f"[BACKUP] Backup criado: {backup_file}")
            return str(backup_file)
        
    except Exception as e:
        logger.error(f"[ERROR] Erro no backup: {e}")
        return None

# Lifespan com otimizações
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle com backup automático e otimizações"""
    logger.info("[SISTEMA] INICIANDO SISTEMA DE PRODUÇÃO v4.0...")
    
    # Inicializar LogManager
    log_manager.setup_logging()
    
    # Inicializar database
    create_tables()
    logger.info("[DATABASE] Database inicializado")
    
    # Backup inicial
    await backup_manager.create_backup("startup")
    
    # Iniciar agendador de backup automático
    backup_manager.start_scheduler()
    logger.info("[BACKUP] Sistema de backup automático iniciado")
    
    yield
    
    # Cleanup - backup final e parar scheduler
    backup_manager.stop_scheduler()
    final_backup = await backup_manager.create_backup("shutdown")
    final_backup_path = final_backup.path if final_backup else "Erro no backup"
    logger.info(f"[SISTEMA] Sistema finalizado. Backup final: {final_backup_path}")

# Custom OpenAPI para documentação
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Sistema Universal de Gestão - API v4.0",
        version="4.0.0-PRODUCTION",
        description="""
        ## Sistema Universal Completo - Versão de Produção
        
        Sistema completo de gestão de eventos com todas as funcionalidades:
        
        ### Funcionalidades Core
        - **Gestão de Usuários** - CRUD completo
        - **Gestão de Eventos** - Criação e controle
        - **PDV Integrado** - Vendas em tempo real
        - **Controle de Estoque** - Gestão de produtos
        
        ### Analytics & IA
        - **Dashboard Avançado** - Métricas em tempo real
        - **IA Preditiva** - Análises inteligentes
        - **Relatórios Automáticos** - Insights de negócio
        
        ### Segurança & Performance
        - **Autenticação JWT** - Segurança robusta
        - **Cache Inteligente** - Performance otimizada
        - **Backup Automático** - Dados protegidos
        - **Monitoring 24/7** - Sistema sempre online
        
        ### Integrações
        - **WhatsApp Business** - Comunicação direta
        - **APIs RESTful** - Integrações flexíveis
        - **WebSocket** - Atualizações em tempo real
        """,
        routes=app.routes,
    )
    
    # Adicionar informações extras
    openapi_schema["info"]["contact"] = {
        "name": "Sistema Universal Support",
        "email": "support@sistemauniversal.com"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    # Tags para organização
    openapi_schema["tags"] = [
        {"name": "Core", "description": "APIs principais do sistema"},
        {"name": "Business", "description": "APIs de negócio"},
        {"name": "Analytics", "description": "Análises e relatórios"},
        {"name": "AI", "description": "Inteligência Artificial"},
        {"name": "System", "description": "Sistema e monitoring"}
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Criar aplicação FastAPI otimizada
app = FastAPI(
    title="Sistema Universal v4.0 - PRODUÇÃO",
    description="Sistema completo otimizado para produção",
    version="4.0.0-PRODUCTION",
    lifespan=lifespan,
    docs_url=None,  # Desabilitar docs padrão para customizar
    redoc_url=None,
    openapi_url="/api/openapi.json"
)

# Configurar OpenAPI customizado
app.openapi = custom_openapi

# MIDDLEWARE STACK OTIMIZADO
app.add_middleware(PerformanceMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Configuração de arquivos estáticos (se existir)
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# INCLUIR ROUTERS
app.include_router(whatsapp_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(backup_manager_router, prefix="/api")
app.include_router(logs_router, prefix="/api")
app.include_router(qr_checkin_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")

# SISTEMA DE MÉTRICAS AVANÇADAS
METRICS = {
    "requests_total": 0,
    "requests_by_endpoint": {},
    "average_response_time": 0,
    "system_uptime": datetime.now(),
    "cache_hits": 0,
    "cache_misses": 0,
    "backup_count": 0
}

def update_metrics(endpoint: str, response_time: float):
    """Atualiza métricas do sistema"""
    METRICS["requests_total"] += 1
    METRICS["requests_by_endpoint"][endpoint] = METRICS["requests_by_endpoint"].get(endpoint, 0) + 1
    
    # Média móvel do tempo de resposta
    current_avg = METRICS["average_response_time"]
    total_requests = METRICS["requests_total"]
    METRICS["average_response_time"] = ((current_avg * (total_requests - 1)) + response_time) / total_requests

# DOCUMENTAÇÃO CUSTOMIZADA
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Documentação Swagger customizada"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Sistema Universal - API Docs",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Documentação ReDoc"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="Sistema Universal - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
    )

# ENDPOINTS PRINCIPAIS OTIMIZADOS
@app.get("/", tags=["Core"])
async def root():
    """Homepage do Sistema Universal v4.0"""
    uptime = datetime.now() - METRICS["system_uptime"]
    
    return {
        "message": "Sistema Universal v4.0 - PRODUÇÃO",
        "version": "4.0.0-PRODUCTION",
        "status": "ONLINE",
        "timestamp": datetime.now().isoformat(),
        "uptime": str(uptime),
        "features": {
            "total_requests": METRICS["requests_total"],
            "average_response_time": f"{METRICS['average_response_time']:.4f}s",
            "cache_efficiency": f"{(METRICS['cache_hits']/(METRICS['cache_hits']+METRICS['cache_misses']+1)*100):.1f}%",
            "documentation": "/docs",
            "metrics": "/metrics",
            "health": "/health"
        },
        "production_features": [
            "Performance Monitoring",
            "Cache Inteligente",
            "Backup Automático",
            "Documentação Completa",
            "Logs Estruturados",
            "Métricas Avançadas"
        ]
    }

@app.get("/health", tags=["System"])
async def health_check_advanced():
    """🔍 Health Check Avançado"""
    # Verificar cache
    cache_key = "health_check"
    cached_result = get_cache(cache_key)
    if cached_result:
        METRICS["cache_hits"] += 1
        return cached_result
    
    METRICS["cache_misses"] += 1
    
    # Verificar database
    try:
        stats = get_dashboard_stats()
        db_status = "🟢 Conectado"
    except Exception as e:
        db_status = f"🔴 Erro: {str(e)}"
    
    # Verificar arquivos de backup
    backup_dir = Path("backups")
    backup_files = list(backup_dir.glob("*.db")) if backup_dir.exists() else []
    
    result = {
        "status": "healthy",
        "version": "4.0.0-PRODUCTION",
        "timestamp": datetime.now().isoformat(),
        "uptime": str(datetime.now() - METRICS["system_uptime"]),
        "system": {
            "database": db_status,
            "cache": f"🟢 Ativo ({len(CACHE)} items)",
            "backup": f"🟢 {len(backup_files)} backups disponíveis",
            "performance": f"🟢 {METRICS['average_response_time']:.4f}s avg"
        },
        "metrics": {
            "total_requests": METRICS["requests_total"],
            "cache_efficiency": f"{(METRICS['cache_hits']/(METRICS['cache_hits']+METRICS['cache_misses']+1)*100):.1f}%"
        }
    }
    
    # Cache do resultado por 1 minuto
    set_cache(cache_key, result, 1)
    
    return result

@app.get("/metrics", tags=["System"])
async def system_metrics():
    """📊 Métricas Detalhadas do Sistema"""
    uptime = datetime.now() - METRICS["system_uptime"]
    
    return {
        "system_metrics": {
            "uptime": str(uptime),
            "total_requests": METRICS["requests_total"],
            "average_response_time": f"{METRICS['average_response_time']:.4f}s",
            "requests_per_minute": round(METRICS["requests_total"] / max(uptime.total_seconds() / 60, 1), 2)
        },
        "cache_metrics": {
            "cache_hits": METRICS["cache_hits"],
            "cache_misses": METRICS["cache_misses"],
            "cache_efficiency": f"{(METRICS['cache_hits']/(METRICS['cache_hits']+METRICS['cache_misses']+1)*100):.1f}%",
            "cached_items": len(CACHE)
        },
        "endpoint_stats": METRICS["requests_by_endpoint"],
        "timestamp": datetime.now().isoformat()
    }

# APIS COM CACHE OTIMIZADO
@app.get("/api/usuarios", tags=["Core"])
async def listar_usuarios_cached():
    """👥 Lista usuários com cache"""
    cache_key = "usuarios_list"
    cached_result = get_cache(cache_key)
    
    if cached_result:
        METRICS["cache_hits"] += 1
        return cached_result
    
    METRICS["cache_misses"] += 1
    usuarios = get_all_usuarios()
    
    result = {
        "usuarios": usuarios,
        "total": len(usuarios),
        "timestamp": datetime.now().isoformat(),
        "cached": False
    }
    
    # Cache por 5 minutos
    set_cache(cache_key, result, 5)
    return result

@app.get("/api/dashboard", tags=["Analytics"])
async def dashboard_cached():
    """📊 Dashboard com cache otimizado"""
    cache_key = "dashboard_stats"
    cached_result = get_cache(cache_key)
    
    if cached_result:
        METRICS["cache_hits"] += 1
        cached_result["from_cache"] = True
        return cached_result
    
    METRICS["cache_misses"] += 1
    stats = get_dashboard_stats()
    
    result = {
        "dashboard": stats,
        "performance": {
            "avg_response_time": f"{METRICS['average_response_time']:.4f}s",
            "total_requests": METRICS["requests_total"],
            "uptime": str(datetime.now() - METRICS["system_uptime"])
        },
        "timestamp": datetime.now().isoformat(),
        "from_cache": False
    }
    
    # Cache por 2 minutos
    set_cache(cache_key, result, 2)
    return result

# BACKUP MANUAL
@app.post("/api/backup", tags=["System"])
async def create_backup_manual(background_tasks: BackgroundTasks):
    """💾 Criar backup manual"""
    background_tasks.add_task(backup_database)
    METRICS["backup_count"] += 1
    
    return {
        "message": "Backup iniciado em background",
        "timestamp": datetime.now().isoformat(),
        "backup_count": METRICS["backup_count"]
    }

# LIMPEZA DE CACHE
@app.delete("/api/cache", tags=["System"])
async def clear_cache():
    """🧹 Limpar cache do sistema"""
    cache_count = len(CACHE)
    CACHE.clear()
    CACHE_TTL.clear()
    
    return {
        "message": f"Cache limpo ({cache_count} items removidos)",
        "timestamp": datetime.now().isoformat()
    }

# SISTEMA INFO AVANÇADO
@app.get("/system/info", tags=["System"])
async def system_info_advanced():
    """ℹ️ Informações avançadas do sistema"""
    return {
        "system": "Sistema Universal de Gestão",
        "version": "4.0.0-PRODUCTION",
        "python_version": sys.version,
        "uptime": str(datetime.now() - METRICS["system_uptime"]),
        "features": {
            "production_ready": True,
            "auto_backup": True,
            "performance_monitoring": True,
            "cache_system": True,
            "structured_logging": True,
            "api_documentation": True
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "metrics": "/metrics",
            "health": "/health",
            "backup": "/api/backup"
        },
        "timestamp": datetime.now().isoformat()
    }

logger.info("[SISTEMA] SISTEMA UNIVERSAL v4.0 - PRODUCAO ATIVADO")
logger.info("[PERF] Performance monitoring ativo")
logger.info("[BACKUP] Backup automatico configurado")
logger.info("[CACHE] Cache inteligente ativo")
logger.info("[DOCS] Documentacao disponivel em /docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_producao:app",
        host="0.0.0.0",
        port=8003,
        log_level="info",
        access_log=True
    )
