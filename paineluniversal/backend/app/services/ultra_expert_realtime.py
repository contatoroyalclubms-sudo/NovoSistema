"""
Ultra-Expert Real-time Dashboard System
Sistema de Dashboard Enterprise em Tempo Real
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import websockets
from fastapi import WebSocket
import redis.asyncio as redis
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class MetricType(Enum):
    REAL_TIME = "real_time"
    BUSINESS = "business"
    TECHNICAL = "technical"
    USER_ACTIVITY = "user_activity"
    FINANCIAL = "financial"

@dataclass
class RealTimeMetric:
    metric_id: str
    metric_type: MetricType
    value: Any
    timestamp: datetime
    metadata: Dict[str, Any]
    tags: List[str]

@dataclass
class DashboardUpdate:
    dashboard_id: str
    metrics: List[RealTimeMetric]
    alerts: List[Dict[str, Any]]
    timestamp: datetime

class ConnectionManager:
    """Gerenciador de conexões WebSocket enterprise"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_subscriptions: Dict[str, Set[str]] = {}
        self.dashboard_subscribers: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str, dashboard_types: List[str] = None):
        """Conecta cliente WebSocket"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        if dashboard_types:
            self.user_subscriptions[client_id] = set(dashboard_types)
            for dashboard_type in dashboard_types:
                if dashboard_type not in self.dashboard_subscribers:
                    self.dashboard_subscribers[dashboard_type] = set()
                self.dashboard_subscribers[dashboard_type].add(client_id)
        
        logger.info(f"Cliente {client_id} conectado com dashboards: {dashboard_types}")
    
    def disconnect(self, client_id: str):
        """Desconecta cliente"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        if client_id in self.user_subscriptions:
            dashboard_types = self.user_subscriptions[client_id]
            for dashboard_type in dashboard_types:
                if dashboard_type in self.dashboard_subscribers:
                    self.dashboard_subscribers[dashboard_type].discard(client_id)
            del self.user_subscriptions[client_id]
        
        logger.info(f"Cliente {client_id} desconectado")
    
    async def send_personal_message(self, message: str, client_id: str):
        """Envia mensagem para cliente específico"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem para {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast_to_dashboard(self, message: str, dashboard_type: str):
        """Broadcast para todos os clientes de um dashboard"""
        if dashboard_type in self.dashboard_subscribers:
            clients = list(self.dashboard_subscribers[dashboard_type])
            await asyncio.gather(
                *[self.send_personal_message(message, client_id) for client_id in clients],
                return_exceptions=True
            )

class UltraExpertRealtime:
    """Sistema de Dashboard Enterprise em Tempo Real"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.connection_manager = ConnectionManager()
        self.redis_client = None
        self.metrics_cache: Dict[str, List[RealTimeMetric]] = {}
        self.is_monitoring = False
        self.monitoring_tasks: List[asyncio.Task] = []
        
        # Configurações de performance
        self.UPDATE_INTERVAL = 1.0  # 1 segundo
        self.BATCH_SIZE = 100
        self.MAX_METRICS_CACHE = 1000
        
    async def initialize(self):
        """Inicializa o sistema de tempo real"""
        try:
            self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
            await self.redis_client.ping()
            logger.info("Redis conectado para sistema real-time")
        except Exception as e:
            logger.warning(f"Redis não disponível, usando cache local: {e}")
        
        # Iniciar monitoramento
        await self.start_monitoring()
    
    async def start_monitoring(self):
        """Inicia monitoramento em tempo real"""
        if not self.is_monitoring:
            self.is_monitoring = True
            
            # Tasks de monitoramento
            self.monitoring_tasks = [
                asyncio.create_task(self._monitor_business_metrics()),
                asyncio.create_task(self._monitor_technical_metrics()),
                asyncio.create_task(self._monitor_user_activity()),
                asyncio.create_task(self._monitor_financial_metrics()),
                asyncio.create_task(self._process_alerts()),
            ]
            
            logger.info("Sistema de monitoramento em tempo real iniciado")
    
    async def stop_monitoring(self):
        """Para monitoramento"""
        self.is_monitoring = False
        
        for task in self.monitoring_tasks:
            task.cancel()
        
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        self.monitoring_tasks.clear()
        
        logger.info("Sistema de monitoramento parado")
    
    async def _monitor_business_metrics(self):
        """Monitora métricas de negócio"""
        while self.is_monitoring:
            try:
                metrics = await self._collect_business_metrics()
                await self._broadcast_metrics("business_dashboard", metrics)
                await asyncio.sleep(self.UPDATE_INTERVAL * 5)  # 5 segundos para business
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no monitoramento de negócio: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_technical_metrics(self):
        """Monitora métricas técnicas"""
        while self.is_monitoring:
            try:
                metrics = await self._collect_technical_metrics()
                await self._broadcast_metrics("technical_dashboard", metrics)
                await asyncio.sleep(self.UPDATE_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no monitoramento técnico: {e}")
                await asyncio.sleep(2)
    
    async def _monitor_user_activity(self):
        """Monitora atividade de usuários"""
        while self.is_monitoring:
            try:
                metrics = await self._collect_user_activity_metrics()
                await self._broadcast_metrics("activity_dashboard", metrics)
                await asyncio.sleep(self.UPDATE_INTERVAL * 2)  # 2 segundos
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no monitoramento de atividade: {e}")
                await asyncio.sleep(3)
    
    async def _monitor_financial_metrics(self):
        """Monitora métricas financeiras"""
        while self.is_monitoring:
            try:
                metrics = await self._collect_financial_metrics()
                await self._broadcast_metrics("financial_dashboard", metrics)
                await asyncio.sleep(self.UPDATE_INTERVAL * 10)  # 10 segundos para financeiro
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no monitoramento financeiro: {e}")
                await asyncio.sleep(5)
    
    async def _process_alerts(self):
        """Processa e envia alertas em tempo real"""
        while self.is_monitoring:
            try:
                alerts = await self._check_for_alerts()
                if alerts:
                    await self._broadcast_alerts(alerts)
                await asyncio.sleep(self.UPDATE_INTERVAL * 3)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no processamento de alertas: {e}")
                await asyncio.sleep(5)
    
    async def _collect_business_metrics(self) -> List[RealTimeMetric]:
        """Coleta métricas de negócio"""
        now = datetime.now()
        
        return [
            RealTimeMetric(
                metric_id="total_events",
                metric_type=MetricType.BUSINESS,
                value=127,  # Simulado - integrar com banco de dados real
                timestamp=now,
                metadata={"growth": "+12%", "period": "month"},
                tags=["events", "total", "growth"]
            ),
            RealTimeMetric(
                metric_id="active_participants",
                metric_type=MetricType.BUSINESS,
                value=2847,
                timestamp=now,
                metadata={"online": 1204, "in_person": 1643},
                tags=["participants", "active", "real_time"]
            ),
            RealTimeMetric(
                metric_id="revenue_today",
                metric_type=MetricType.BUSINESS,
                value=45680.50,
                timestamp=now,
                metadata={"currency": "BRL", "target": 50000.00, "progress": "91.4%"},
                tags=["revenue", "daily", "financial"]
            ),
            RealTimeMetric(
                metric_id="conversion_rate",
                metric_type=MetricType.BUSINESS,
                value=23.4,
                timestamp=now,
                metadata={"unit": "percentage", "benchmark": 20.0, "trend": "up"},
                tags=["conversion", "percentage", "sales"]
            ),
            RealTimeMetric(
                metric_id="satisfaction_score",
                metric_type=MetricType.BUSINESS,
                value=4.7,
                timestamp=now,
                metadata={"scale": "5.0", "responses": 342, "trend": "stable"},
                tags=["satisfaction", "nps", "feedback"]
            )
        ]
    
    async def _collect_technical_metrics(self) -> List[RealTimeMetric]:
        """Coleta métricas técnicas"""
        now = datetime.now()
        
        return [
            RealTimeMetric(
                metric_id="api_response_time",
                metric_type=MetricType.TECHNICAL,
                value=125.5,
                timestamp=now,
                metadata={"unit": "ms", "threshold": 200, "status": "healthy"},
                tags=["api", "performance", "response_time"]
            ),
            RealTimeMetric(
                metric_id="active_connections",
                metric_type=MetricType.TECHNICAL,
                value=len(self.connection_manager.active_connections),
                timestamp=now,
                metadata={"websockets": True, "max_capacity": 1000},
                tags=["connections", "websocket", "real_time"]
            ),
            RealTimeMetric(
                metric_id="error_rate",
                metric_type=MetricType.TECHNICAL,
                value=0.12,
                timestamp=now,
                metadata={"unit": "percentage", "threshold": 1.0, "status": "good"},
                tags=["errors", "rate", "health"]
            ),
            RealTimeMetric(
                metric_id="memory_usage",
                metric_type=MetricType.TECHNICAL,
                value=68.5,
                timestamp=now,
                metadata={"unit": "percentage", "available": 31.5, "status": "normal"},
                tags=["memory", "system", "resources"]
            ),
            RealTimeMetric(
                metric_id="database_connections",
                metric_type=MetricType.TECHNICAL,
                value=45,
                timestamp=now,
                metadata={"max_pool": 100, "active": 45, "idle": 55},
                tags=["database", "connections", "pool"]
            )
        ]
    
    async def _collect_user_activity_metrics(self) -> List[RealTimeMetric]:
        """Coleta métricas de atividade de usuários"""
        now = datetime.now()
        
        return [
            RealTimeMetric(
                metric_id="online_users",
                metric_type=MetricType.USER_ACTIVITY,
                value=234,
                timestamp=now,
                metadata={"peak_today": 456, "peak_time": "14:30"},
                tags=["users", "online", "activity"]
            ),
            RealTimeMetric(
                metric_id="new_registrations",
                metric_type=MetricType.USER_ACTIVITY,
                value=18,
                timestamp=now,
                metadata={"period": "hour", "daily_total": 89},
                tags=["registrations", "new_users", "growth"]
            ),
            RealTimeMetric(
                metric_id="page_views",
                metric_type=MetricType.USER_ACTIVITY,
                value=1247,
                timestamp=now,
                metadata={"unique_views": 892, "bounce_rate": "23.4%"},
                tags=["page_views", "traffic", "engagement"]
            ),
            RealTimeMetric(
                metric_id="check_ins_minute",
                metric_type=MetricType.USER_ACTIVITY,
                value=12,
                timestamp=now,
                metadata={"hourly_rate": 720, "trend": "increasing"},
                tags=["checkins", "real_time", "events"]
            )
        ]
    
    async def _collect_financial_metrics(self) -> List[RealTimeMetric]:
        """Coleta métricas financeiras"""
        now = datetime.now()
        
        return [
            RealTimeMetric(
                metric_id="total_revenue",
                metric_type=MetricType.FINANCIAL,
                value=125470.80,
                timestamp=now,
                metadata={"currency": "BRL", "period": "month", "growth": "+18.5%"},
                tags=["revenue", "total", "monthly"]
            ),
            RealTimeMetric(
                metric_id="pending_payments",
                metric_type=MetricType.FINANCIAL,
                value=8450.30,
                timestamp=now,
                metadata={"count": 23, "oldest": "2 days", "status": "normal"},
                tags=["payments", "pending", "cash_flow"]
            ),
            RealTimeMetric(
                metric_id="refund_rate",
                metric_type=MetricType.FINANCIAL,
                value=2.1,
                timestamp=now,
                metadata={"unit": "percentage", "benchmark": 3.0, "status": "good"},
                tags=["refunds", "rate", "quality"]
            ),
            RealTimeMetric(
                metric_id="average_ticket",
                metric_type=MetricType.FINANCIAL,
                value=245.60,
                timestamp=now,
                metadata={"currency": "BRL", "trend": "up", "target": 250.00},
                tags=["ticket", "average", "sales"]
            )
        ]
    
    async def _broadcast_metrics(self, dashboard_type: str, metrics: List[RealTimeMetric]):
        """Envia métricas para dashboards específicos"""
        if not metrics:
            return
        
        update = DashboardUpdate(
            dashboard_id=dashboard_type,
            metrics=metrics,
            alerts=[],
            timestamp=datetime.now()
        )
        
        message = json.dumps({
            "type": "metrics_update",
            "data": {
                "dashboard_id": update.dashboard_id,
                "metrics": [asdict(metric) for metric in update.metrics],
                "timestamp": update.timestamp.isoformat()
            }
        }, default=str)
        
        await self.connection_manager.broadcast_to_dashboard(message, dashboard_type)
        
        # Cache no Redis se disponível
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"dashboard:{dashboard_type}:latest",
                    30,  # TTL de 30 segundos
                    message
                )
            except Exception as e:
                logger.error(f"Erro ao cachear no Redis: {e}")
    
    async def _check_for_alerts(self) -> List[Dict[str, Any]]:
        """Verifica e gera alertas"""
        alerts = []
        
        # Simular alguns alertas baseados nas métricas
        now = datetime.now()
        
        # Alert de alta taxa de erro
        alerts.append({
            "id": f"error_rate_{now.timestamp()}",
            "type": "warning",
            "severity": "medium",
            "title": "Taxa de erro aumentou",
            "message": "Taxa de erro API está em 0.12%, próximo do limite de 0.15%",
            "timestamp": now.isoformat(),
            "dashboard": "technical_dashboard",
            "action_required": True,
            "metadata": {"threshold": 0.15, "current": 0.12}
        })
        
        # Alert de novo recorde de usuários online
        if datetime.now().hour == 14 and datetime.now().minute < 5:
            alerts.append({
                "id": f"peak_users_{now.timestamp()}",
                "type": "success",
                "severity": "low",
                "title": "Novo recorde de usuários online!",
                "message": "456 usuários simultâneos - novo recorde diário!",
                "timestamp": now.isoformat(),
                "dashboard": "activity_dashboard",
                "action_required": False,
                "metadata": {"record": 456, "previous_record": 423}
            })
        
        return alerts
    
    async def _broadcast_alerts(self, alerts: List[Dict[str, Any]]):
        """Envia alertas para todos os dashboards relevantes"""
        for alert in alerts:
            message = json.dumps({
                "type": "alert",
                "data": alert
            }, default=str)
            
            dashboard = alert.get("dashboard", "all")
            if dashboard == "all":
                # Enviar para todos os dashboards
                for dash_type in self.connection_manager.dashboard_subscribers:
                    await self.connection_manager.broadcast_to_dashboard(message, dash_type)
            else:
                await self.connection_manager.broadcast_to_dashboard(message, dashboard)
    
    async def get_dashboard_snapshot(self, dashboard_type: str) -> Dict[str, Any]:
        """Retorna snapshot atual do dashboard"""
        try:
            if self.redis_client:
                cached = await self.redis_client.get(f"dashboard:{dashboard_type}:latest")
                if cached:
                    return json.loads(cached)
            
            # Gerar snapshot em tempo real
            if dashboard_type == "business_dashboard":
                metrics = await self._collect_business_metrics()
            elif dashboard_type == "technical_dashboard":
                metrics = await self._collect_technical_metrics()
            elif dashboard_type == "activity_dashboard":
                metrics = await self._collect_user_activity_metrics()
            elif dashboard_type == "financial_dashboard":
                metrics = await self._collect_financial_metrics()
            else:
                metrics = []
            
            return {
                "dashboard_id": dashboard_type,
                "metrics": [asdict(metric) for metric in metrics],
                "timestamp": datetime.now().isoformat(),
                "status": "live"
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar snapshot do dashboard: {e}")
            return {
                "dashboard_id": dashboard_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    async def register_custom_metric(self, metric: RealTimeMetric):
        """Registra métrica customizada"""
        dashboard_type = f"custom_{metric.metric_type.value}_dashboard"
        await self._broadcast_metrics(dashboard_type, [metric])
    
    @asynccontextmanager
    async def websocket_connection(self, websocket: WebSocket, client_id: str, dashboard_types: List[str]):
        """Context manager para conexões WebSocket"""
        try:
            await self.connection_manager.connect(websocket, client_id, dashboard_types)
            
            # Enviar snapshot inicial
            for dashboard_type in dashboard_types:
                snapshot = await self.get_dashboard_snapshot(dashboard_type)
                await self.connection_manager.send_personal_message(
                    json.dumps({"type": "initial_snapshot", "data": snapshot}),
                    client_id
                )
            
            yield self.connection_manager
            
        finally:
            self.connection_manager.disconnect(client_id)

# Instância global
ultra_expert_realtime = UltraExpertRealtime()

# Função para inicialização
async def initialize_realtime_system():
    """Inicializa o sistema de tempo real"""
    await ultra_expert_realtime.initialize()
    logger.info("Sistema Ultra-Expert Real-time inicializado")

# Função para parar o sistema
async def shutdown_realtime_system():
    """Para o sistema de tempo real"""
    await ultra_expert_realtime.stop_monitoring()
    logger.info("Sistema Ultra-Expert Real-time finalizado")