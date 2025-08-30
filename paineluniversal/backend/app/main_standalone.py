"""
FastAPI STANDALONE ULTRA-EXPERT
Sistema Universal de Gestão de Eventos
Versão independente com monitoring avançado
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
import time
import logging
import asyncio
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any

# Prometheus imports
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ================================
# SISTEMA DE MONITORING ULTRA-EXPERT STANDALONE
# ================================

# Registry personalizado
business_registry = CollectorRegistry()

# Métricas de negócio
eventos_criados = Counter(
    'eventos_criados_total', 
    'Total de eventos criados',
    ['tipo_evento', 'organizador_tipo'],
    registry=business_registry
)

checkins_realizados = Counter(
    'checkins_realizados_total',
    'Total de check-ins realizados', 
    ['evento_id', 'tipo_checkin'],
    registry=business_registry
)

vendas_pdv = Counter(
    'vendas_pdv_total',
    'Total de vendas PDV',
    ['evento_id', 'forma_pagamento'],
    registry=business_registry
)

receita_total = Counter(
    'receita_total_reais',
    'Receita total em reais',
    ['evento_id', 'tipo_transacao'], 
    registry=business_registry
)

usuarios_online = Gauge(
    'usuarios_online_atual',
    'Número atual de usuários online',
    registry=business_registry
)

eventos_ativos = Gauge(
    'eventos_ativos_atual', 
    'Número atual de eventos ativos',
    registry=business_registry
)

class StandaloneMonitoring:
    """Sistema de monitoring standalone"""
    
    def __init__(self):
        self.start_time = time.time()
        self.alerts_active = {}
        self.thresholds = {
            "cpu_percent": 80,
            "memory_percent": 85, 
            "disk_percent": 90
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Obtém saúde do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            uptime_seconds = time.time() - self.start_time
            
            return {
                "status": "healthy",
                "uptime_seconds": uptime_seconds,
                "uptime_human": str(timedelta(seconds=int(uptime_seconds))),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "disk_percent": disk.percent, 
                    "disk_free_gb": round(disk.free / (1024**3), 2)
                },
                "business": {
                    "usuarios_online": 42,  # Mock
                    "eventos_ativos": 15    # Mock
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_business_metrics(self) -> str:
        """Retorna métricas de negócio"""
        return generate_latest(business_registry)
    
    async def track_evento_criado(self, tipo_evento: str, organizador_tipo: str):
        """Track evento criado"""
        eventos_criados.labels(
            tipo_evento=tipo_evento,
            organizador_tipo=organizador_tipo
        ).inc()
    
    async def track_checkin(self, evento_id: str, tipo_checkin: str, tempo_processamento: float):
        """Track check-in"""
        checkins_realizados.labels(
            evento_id=evento_id,
            tipo_checkin=tipo_checkin
        ).inc()
    
    async def track_venda_pdv(self, evento_id: str, forma_pagamento: str, valor: float, tempo_processamento: float):
        """Track venda PDV"""
        vendas_pdv.labels(
            evento_id=evento_id,
            forma_pagamento=forma_pagamento
        ).inc()
        
        receita_total.labels(
            evento_id=evento_id,
            tipo_transacao="pdv"
        ).inc(valor)
    
    async def check_system_health(self):
        """Verifica saúde do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            if cpu_percent > self.thresholds["cpu_percent"]:
                await self._trigger_alert("high_cpu", f"CPU usage: {cpu_percent}%")
            
            if memory.percent > self.thresholds["memory_percent"]:
                await self._trigger_alert("high_memory", f"Memory usage: {memory.percent}%")
        except Exception as e:
            await self._trigger_alert("monitoring_error", f"Error: {e}")
    
    async def _trigger_alert(self, alert_type: str, message: str):
        """Dispara alerta"""
        alert_key = f"{alert_type}_{int(time.time() // 300)}"
        
        if alert_key not in self.alerts_active:
            self.alerts_active[alert_key] = {
                "type": alert_type,
                "message": message,
                "timestamp": datetime.now(),
                "count": 1
            }
            logger.critical(f"🚨 ALERT: {alert_type} - {message}")
        else:
            self.alerts_active[alert_key]["count"] += 1


# Background task para health check
async def health_check_background():
    """Task background para health check"""
    while True:
        try:
            await monitoring_system.check_system_health()
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            await asyncio.sleep(300)

# Instância global
monitoring_system = StandaloneMonitoring()

# ================================
# APLICAÇÃO FASTAPI
# ================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida"""
    logger.info("🚀 Iniciando Sistema ULTRA-EXPERT Standalone...")
    
    # Iniciar background task
    asyncio.create_task(health_check_background())
    logger.info("✅ Health check background task iniciado")
    
    yield
    
    logger.info("👋 Aplicação finalizada")

app = FastAPI(
    title="Sistema Universal de Gestão de Eventos - ULTRA-EXPERT",
    description="Sistema standalone com monitoring avançado",
    version="2.1.0-STANDALONE-ULTRA-EXPERT",
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
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Timestamp"] = str(int(time.time()))
    
    if process_time > 1.0:
        logger.warning(f"Slow request: {request.method} {request.url} took {process_time:.2f}s")
    
    return response

# Timestamp de início
start_time = time.time()

# ================================
# ENDPOINTS BÁSICOS
# ================================

@app.get("/")
async def root():
    return {
        "message": "Sistema Universal de Gestão de Eventos - ULTRA-EXPERT",
        "version": "2.1.0-STANDALONE",
        "status": "online",
        "features": ["monitoring", "performance", "ultra-expert", "standalone"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check com métricas ultra-expert"""
    system_health = monitoring_system.get_system_health()
    return {
        "status": "healthy",
        "version": "2.1.0-STANDALONE-ULTRA-EXPERT",
        "environment": "development",
        "uptime_seconds": time.time() - start_time,
        "system_metrics": system_health,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/system/info")
async def system_info():
    return {
        "name": "Sistema Universal de Gestão de Eventos",
        "version": "2.1.0-STANDALONE-ULTRA-EXPERT",
        "phase": "ULTRA-EXPERT-STANDALONE",
        "features": [
            "Monitoring Ultra-Expert",
            "Performance Optimization",
            "Real-time Metrics",
            "Business Intelligence",
            "Alerting System",
            "Standalone Architecture"
        ],
        "monitoring_enabled": True,
        "timestamp": datetime.utcnow().isoformat()
    }

# ================================
# ENDPOINTS DE MONITORING
# ================================

@app.get("/metrics")
async def prometheus_metrics():
    """Endpoint para métricas do Prometheus"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/v1/metrics/business")
async def business_metrics():
    """Métricas de negócio"""
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
        "active_alerts": list(monitoring_system.alerts_active.values()),
        "total_alerts": len(monitoring_system.alerts_active),
        "thresholds": monitoring_system.thresholds,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/monitoring/test-alert")
async def trigger_test_alert():
    """Dispara alerta de teste"""
    await monitoring_system._trigger_alert("test_alert", "Alerta de teste Ultra-Expert Standalone")
    return {"status": "success", "message": "Test alert triggered"}

# ================================
# ENDPOINTS DE TRACKING
# ================================

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
    return {"eventos": [], "total": 0, "message": "Sistema Ultra-Expert funcionando"}

@app.get("/api/v1/pdv/status")
async def pdv_status():
    return {"status": "online", "version": "ultra-expert-standalone"}

@app.get("/api/v1/gamificacao/ranking")
async def gamificacao_ranking():
    return {"ranking": [], "total": 0, "message": "Sistema Ultra-Expert funcionando"}

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando servidor Ultra-Expert Standalone...")
    
    uvicorn.run(
        "main_standalone:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )