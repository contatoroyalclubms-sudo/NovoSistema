"""
Sistema de Monitoring Ultra-Expert
Sistema Universal de Gestão de Eventos - FASE 2 ULTRA-EXPERT

Implementação de métricas avançadas, alertas e observabilidade
"""

import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from fastapi import FastAPI, Request, Response
import asyncio
import logging

# ================================
# MÉTRICAS PERSONALIZADAS
# ================================

# Registry personalizado para métricas business
business_registry = CollectorRegistry()

# Contadores de negócio
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

# Histogramas de performance
tempo_processamento_checkin = Histogram(
    'checkin_tempo_processamento_segundos',
    'Tempo de processamento de check-in',
    ['evento_id'],
    registry=business_registry
)

tempo_processamento_venda = Histogram(
    'venda_tempo_processamento_segundos',
    'Tempo de processamento de venda',
    ['forma_pagamento'],
    registry=business_registry
)

# Gauges de sistema
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


# ================================
# SISTEMA DE MONITORING
# ================================

class UltraExpertMonitoring:
    """Sistema de monitoring ultra-avançado"""
    
    def __init__(self):
        self.start_time = time.time()
        self.logger = logging.getLogger("ultra-monitoring")
        self.system_metrics = {}
        self.business_metrics = {}
        
    def setup_instrumentator(self, app: FastAPI) -> Instrumentator:
        """Configura instrumentação automática do FastAPI"""
        
        # Configurar métricas customizadas do sistema
        self._setup_custom_metrics()
        
        instrumentator = Instrumentator(
            should_group_status_codes=False,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/docs", "/redoc", "/openapi.json", "/favicon.ico"],
            env_var_name="ENABLE_METRICS",
            inprogress_name="http_requests_inprogress",
            inprogress_labels=True,
        )
        
        # Adicionar métricas personalizadas
        instrumentator.add(
            metrics.request_size_and_response_size(
                should_include_handler=True,
                should_include_method=True,
                should_include_status=True,
                metric_namespace="eventos",
                metric_subsystem="http",
            )
        )
        
        instrumentator.add(
            metrics.latency(
                should_include_handler=True,
                should_include_method=True,
                should_include_status=True,
                metric_namespace="eventos",
                metric_subsystem="http",
            )
        )
        
        # Adicionar métricas de banco de dados
        instrumentator.add(self._database_metrics)
        
        # Adicionar métricas de negócio
        instrumentator.add(self._business_metrics_collector)
        
        # Adicionar métricas personalizadas
        instrumentator.add(
            metrics.info("system_info", "Informações do sistema", 
                        lambda: {"version": "2.0.0", "phase": "sprint_5"})
        )
        
        return instrumentator
    
    def _setup_custom_metrics(self):
        """Configura métricas personalizadas avançadas"""
        # Adicionar métricas específicas do domínio
        global checkins_realizados, vendas_pdv, receita_total
        
        # Registrar métricas no registry principal também
        from prometheus_client import REGISTRY
        try:
            REGISTRY.register(checkins_realizados)
            REGISTRY.register(vendas_pdv) 
            REGISTRY.register(receita_total)
            REGISTRY.register(eventos_criados)
            REGISTRY.register(usuarios_online)
            REGISTRY.register(eventos_ativos)
            REGISTRY.register(tempo_processamento_checkin)
            REGISTRY.register(tempo_processamento_venda)
        except ValueError:
            # Métricas já registradas - ignorar
            pass
    
    def _database_metrics(self, info: metrics.Info) -> None:
        """Coleta métricas de banco de dados"""
        try:
            # Simular coleta de métricas de DB
            # Em produção, conectaria ao banco para coletar estatísticas reais
            pass
        except Exception as e:
            self.logger.error(f"Erro coletando métricas de DB: {e}")
    
    def _business_metrics_collector(self, info: metrics.Info) -> None:
        """Coleta métricas de negócio em tempo real"""
        try:
            # Atualizar métricas de usuários online (simulado)
            usuarios_online.set(self._get_usuarios_online())
            
            # Atualizar eventos ativos (simulado)
            eventos_ativos.set(self._get_eventos_ativos())
            
        except Exception as e:
            self.logger.error(f"Erro coletando métricas de negócio: {e}")
    
    def _get_usuarios_online(self) -> int:
        """Obtém número de usuários online (implementar WebSocket tracking)"""
        # Placeholder - implementar tracking real de WebSocket
        return 42
    
    def _get_eventos_ativos(self) -> int:
        """Obtém número de eventos ativos"""
        # Placeholder - implementar query real ao banco
        return 15
    
    async def track_evento_criado(self, tipo_evento: str, organizador_tipo: str):
        """Tracked criação de evento"""
        eventos_criados.labels(
            tipo_evento=tipo_evento,
            organizador_tipo=organizador_tipo
        ).inc()
    
    async def track_checkin(self, evento_id: str, tipo_checkin: str, tempo_processamento: float):
        """Track check-in realizado"""
        checkins_realizados.labels(
            evento_id=evento_id,
            tipo_checkin=tipo_checkin
        ).inc()
        
        tempo_processamento_checkin.labels(
            evento_id=evento_id
        ).observe(tempo_processamento)
    
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
        
        tempo_processamento_venda.labels(
            forma_pagamento=forma_pagamento
        ).observe(tempo_processamento)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Obtém saúde geral do sistema"""
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
                    "usuarios_online": self._get_usuarios_online(),
                    "eventos_ativos": self._get_eventos_ativos()
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
        """Retorna métricas de negócio em formato Prometheus"""
        return generate_latest(business_registry)


# ================================
# MIDDLEWARE DE PERFORMANCE
# ================================

class PerformanceMiddleware:
    """Middleware para tracking de performance avançado"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        # Executar request
        response = await call_next(request)
        
        # Calcular tempo de processamento
        process_time = time.time() - start_time
        
        # Adicionar headers de performance
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Timestamp"] = str(int(time.time()))
        
        # Log para requests lentos (> 1 segundo)
        if process_time > 1.0:
            logging.warning(
                f"Slow request: {request.method} {request.url} took {process_time:.2f}s"
            )
        
        return response


# ================================
# ALERTING SYSTEM
# ================================

class AlertingSystem:
    """Sistema de alertas inteligente"""
    
    def __init__(self):
        self.alerts_active = {}
        self.thresholds = {
            "cpu_percent": 80,
            "memory_percent": 85,
            "disk_percent": 90,
            "response_time": 2.0,
            "error_rate": 5.0
        }
    
    async def check_system_health(self):
        """Verifica saúde do sistema e dispara alertas"""
        try:
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.thresholds["cpu_percent"]:
                await self._trigger_alert("high_cpu", f"CPU usage: {cpu_percent}%")
            
            # Memory check
            memory = psutil.virtual_memory()
            if memory.percent > self.thresholds["memory_percent"]:
                await self._trigger_alert("high_memory", f"Memory usage: {memory.percent}%")
            
            # Disk check
            disk = psutil.disk_usage('/')
            if disk.percent > self.thresholds["disk_percent"]:
                await self._trigger_alert("high_disk", f"Disk usage: {disk.percent}%")
                
        except Exception as e:
            await self._trigger_alert("monitoring_error", f"Error in health check: {e}")
    
    async def _trigger_alert(self, alert_type: str, message: str):
        """Dispara alerta"""
        alert_key = f"{alert_type}_{int(time.time() // 300)}"  # Group by 5min windows
        
        if alert_key not in self.alerts_active:
            self.alerts_active[alert_key] = {
                "type": alert_type,
                "message": message,
                "timestamp": datetime.now(),
                "count": 1
            }
            
            # Log crítico
            logging.critical(f"🚨 ALERT: {alert_type} - {message}")
            
            # Aqui integraria com Slack, email, SMS, etc.
            # await self._send_notification(alert_type, message)
        else:
            self.alerts_active[alert_key]["count"] += 1


# ================================
# INSTÂNCIA GLOBAL
# ================================

# Instância global do sistema de monitoring
monitoring_system = UltraExpertMonitoring()
alerting_system = AlertingSystem()

# Background task para verificação de saúde
async def health_check_background():
    """Task background para verificação contínua de saúde"""
    while True:
        try:
            await alerting_system.check_system_health()
            await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            logging.error(f"Error in health check background task: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes on error