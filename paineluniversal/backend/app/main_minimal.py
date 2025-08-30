"""
FastAPI MINIMAL para testes
Sistema Universal de Gestão de Eventos - FASE 2 ULTRA-EXPERT
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging
from datetime import datetime

# Importações do sistema de monitoring ultra-expert
try:
    from app.services.monitoring import (
        monitoring_system, 
        alerting_system, 
        health_check_background,
        PerformanceMiddleware
    )
    from prometheus_client import generate_latest
    MONITORING_AVAILABLE = True
except ImportError as e:
    print(f"Monitoring não disponível: {e}")
    MONITORING_AVAILABLE = False

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida da aplicação"""
    logger.info("🚀 Iniciando Sistema ULTRA-EXPERT...")
    
    if MONITORING_AVAILABLE:
        # Inicializar sistema de monitoring
        instrumentator = monitoring_system.setup_instrumentator(app)
        instrumentator.instrument(app).expose(app)
        logger.info("✅ Monitoring ultra-expert inicializado")
    
    yield
    
    logger.info("👋 Aplicação finalizada")

# Aplicação FastAPI
app = FastAPI(
    title="Sistema Universal de Gestão de Eventos - ULTRA-EXPERT",
    description="Sistema com monitoring avançado e performance ultra-otimizada",
    version="2.1.0-ULTRA-EXPERT",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance Middleware
if MONITORING_AVAILABLE:
    app.add_middleware(PerformanceMiddleware)

# Timestamp de início
start_time = time.time()

# ================================
# ENDPOINTS BÁSICOS
# ================================

@app.get("/")
async def root():
    return {
        "message": "Sistema Universal de Gestão de Eventos",
        "version": "2.1.0-ULTRA-EXPERT", 
        "status": "online",
        "features": ["monitoring", "performance", "ultra-expert"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check com métricas ultra-expert"""
    response = {
        "status": "healthy",
        "version": "2.1.0-ULTRA-EXPERT",
        "environment": "development",
        "uptime_seconds": time.time() - start_time,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if MONITORING_AVAILABLE:
        system_health = monitoring_system.get_system_health()
        response["system_metrics"] = system_health
    
    return response

@app.get("/api/v1/system/info")
async def system_info():
    return {
        "name": "Sistema Universal de Gestão de Eventos",
        "version": "2.1.0-ULTRA-EXPERT",
        "phase": "ULTRA-EXPERT",
        "features": [
            "Monitoring Ultra-Expert",
            "Performance Optimization",
            "Real-time Metrics",
            "Business Intelligence",
            "Alerting System"
        ],
        "monitoring_enabled": MONITORING_AVAILABLE,
        "timestamp": datetime.utcnow().isoformat()
    }

# ================================
# ENDPOINTS DE MONITORING
# ================================

if MONITORING_AVAILABLE:
    
    @app.get("/metrics")
    async def prometheus_metrics():
        """Endpoint para métricas do Prometheus"""
        return generate_latest()

    @app.get("/api/v1/metrics/business")
    async def business_metrics():
        """Métricas de negócio"""
        from prometheus_client import CONTENT_TYPE_LATEST
        from fastapi.responses import Response
        
        metrics_data = monitoring_system.get_business_metrics()
        return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)

    @app.get("/api/v1/metrics/performance")
    async def performance_metrics():
        """Métricas de performance"""
        return monitoring_system.get_system_health()

    @app.get("/api/v1/monitoring/alerts")
    async def get_active_alerts():
        """Alertas ativos"""
        return {
            "active_alerts": list(alerting_system.alerts_active.values()),
            "total_alerts": len(alerting_system.alerts_active),
            "thresholds": alerting_system.thresholds,
            "timestamp": datetime.utcnow().isoformat()
        }

    @app.post("/api/v1/monitoring/test-alert")
    async def trigger_test_alert():
        """Dispara alerta de teste"""
        await alerting_system._trigger_alert("test_alert", "Alerta de teste Ultra-Expert")
        return {"status": "success", "message": "Test alert triggered"}

    # Endpoints de tracking
    @app.post("/api/v1/metrics/track/evento")
    async def track_evento_creation(tipo_evento: str = "workshop", organizador_tipo: str = "empresa"):
        await monitoring_system.track_evento_criado(tipo_evento, organizador_tipo)
        return {"status": "tracked", "tipo": tipo_evento}

    @app.post("/api/v1/metrics/track/checkin")
    async def track_checkin_event(evento_id: str = "test", tipo_checkin: str = "qr", tempo: float = 0.5):
        await monitoring_system.track_checkin(evento_id, tipo_checkin, tempo)
        return {"status": "tracked", "evento_id": evento_id}

    @app.post("/api/v1/metrics/track/venda")
    async def track_venda_pdv(evento_id: str = "test", forma_pagamento: str = "pix", valor: float = 25.0, tempo: float = 1.0):
        await monitoring_system.track_venda_pdv(evento_id, forma_pagamento, valor, tempo)
        return {"status": "tracked", "valor": valor}

# ================================
# MOCK ENDPOINTS PARA TESTES
# ================================

@app.get("/api/v1/auth/me")
async def auth_me():
    return JSONResponse(status_code=401, content={"error": "Unauthorized"})

@app.post("/api/v1/auth/login")
async def auth_login():
    return JSONResponse(status_code=422, content={"error": "Invalid credentials"})

@app.get("/api/v1/eventos/")
async def listar_eventos():
    return {"eventos": [], "total": 0, "message": "Sistema funcionando"}

@app.get("/api/v1/pdv/status")
async def pdv_status():
    return {"status": "online", "version": "ultra-expert"}

@app.get("/api/v1/gamificacao/ranking")
async def gamificacao_ranking():
    return {"ranking": [], "total": 0, "message": "Sistema funcionando"}

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando servidor Ultra-Expert...")
    
    uvicorn.run(
        "main_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )