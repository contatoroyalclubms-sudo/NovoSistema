"""
Advanced WebSocket Event System - Sprint 5
Sistema Universal de Gestão de Eventos

Sistema estruturado de eventos WebSocket para:
- Notificações em tempo real
- Updates de dashboards
- Comunicação inter-usuários
- Sincronização de dados
- Alertas do sistema
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from enum import Enum
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Tipos de eventos WebSocket estruturados"""
    # Sistema
    SYSTEM_ALERT = "system_alert"
    SYSTEM_MAINTENANCE = "system_maintenance"
    
    # Gamificação
    POINTS_AWARDED = "points_awarded"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    LEADERBOARD_UPDATE = "leaderboard_update"
    BADGE_EARNED = "badge_earned"
    STREAK_MILESTONE = "streak_milestone"
    
    # Eventos
    EVENT_CREATED = "event_created"
    EVENT_UPDATED = "event_updated"
    EVENT_STARTED = "event_started"
    EVENT_ENDED = "event_ended"
    EVENT_CANCELLED = "event_cancelled"
    
    # Check-in
    CHECKIN_SUCCESS = "checkin_success"
    CHECKIN_FAILED = "checkin_failed"
    CHECKIN_QUEUE_UPDATE = "checkin_queue_update"
    CHECKOUT_SUCCESS = "checkout_success"
    ATTENDANCE_UPDATE = "attendance_update"
    
    # PDV/Vendas
    SALE_COMPLETED = "sale_completed"
    SALE_CANCELLED = "sale_cancelled"
    PAYMENT_RECEIVED = "payment_received"
    INVENTORY_LOW = "inventory_low"
    REVENUE_MILESTONE = "revenue_milestone"
    
    # Usuários
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    USER_ONLINE = "user_online"
    USER_OFFLINE = "user_offline"
    
    # Chat/Comunicação
    MESSAGE_RECEIVED = "message_received"
    NOTIFICATION_SENT = "notification_sent"
    ANNOUNCEMENT = "announcement"
    
    # Analytics
    DASHBOARD_UPDATE = "dashboard_update"
    METRIC_THRESHOLD = "metric_threshold"
    REPORT_GENERATED = "report_generated"


class EventPriority(str, Enum):
    """Prioridades de eventos para controle de entrega"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class WebSocketEvent:
    """Classe que representa um evento WebSocket estruturado"""
    
    def __init__(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
        target_users: Optional[Set[str]] = None,
        target_events: Optional[Set[str]] = None,
        target_roles: Optional[Set[str]] = None,
        expires_at: Optional[datetime] = None,
        requires_ack: bool = False
    ):
        self.id = str(uuid4())
        self.event_type = event_type
        self.data = data
        self.priority = priority
        self.target_users = target_users or set()
        self.target_events = target_events or set()
        self.target_roles = target_roles or set()
        self.created_at = datetime.utcnow()
        self.expires_at = expires_at
        self.requires_ack = requires_ack
        
    def to_dict(self) -> Dict[str, Any]:
        """Converte o evento para dicionário para serialização"""
        return {
            "id": self.id,
            "type": self.event_type.value,
            "data": self.data,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "requires_ack": self.requires_ack
        }
        
    def is_expired(self) -> bool:
        """Verifica se o evento expirou"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


class WebSocketEventManager:
    """Gerenciador avançado de eventos WebSocket"""
    
    def __init__(self):
        self.connections: Dict[str, Dict] = {}  # connection_id -> connection_info
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.event_connections: Dict[str, Set[str]] = {}  # event_id -> connection_ids
        self.role_connections: Dict[str, Set[str]] = {}  # role -> connection_ids
        
        # Queue para eventos prioritários
        self.event_queue: Dict[EventPriority, List[WebSocketEvent]] = {
            EventPriority.CRITICAL: [],
            EventPriority.HIGH: [],
            EventPriority.NORMAL: [],
            EventPriority.LOW: []
        }
        
        # Acknowledgments pendentes
        self.pending_acks: Dict[str, WebSocketEvent] = {}
        
        # Estatísticas
        self.stats = {
            "total_events_sent": 0,
            "events_by_type": {},
            "connections_count": 0,
            "failed_deliveries": 0
        }
        
        # Iniciado
        self.running = False
        
    async def start(self):
        """Inicia o gerenciador de eventos"""
        self.running = True
        
        # Iniciar task de processamento de eventos
        asyncio.create_task(self._process_event_queue())
        asyncio.create_task(self._cleanup_expired_events())
        
        logger.info("🚀 WebSocket Event Manager iniciado")
        
    async def stop(self):
        """Para o gerenciador de eventos"""
        self.running = False
        
        # Fechar todas as conexões
        for connection_id in list(self.connections.keys()):
            await self._disconnect(connection_id)
        
        logger.info("🛑 WebSocket Event Manager parado")
        
    async def register_connection(
        self,
        connection_id: str,
        websocket,
        user_id: Optional[str] = None,
        event_id: Optional[str] = None,
        role: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Registra uma nova conexão WebSocket"""
        try:
            # Aceitar conexão WebSocket
            await websocket.accept()
            
            # Registrar informações da conexão
            self.connections[connection_id] = {
                "websocket": websocket,
                "user_id": user_id,
                "event_id": event_id,
                "role": role,
                "connected_at": datetime.utcnow(),
                "last_ping": datetime.utcnow(),
                "metadata": metadata or {}
            }
            
            # Adicionar aos índices
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(connection_id)
                
            if event_id:
                if event_id not in self.event_connections:
                    self.event_connections[event_id] = set()
                self.event_connections[event_id].add(connection_id)
                
            if role:
                if role not in self.role_connections:
                    self.role_connections[role] = set()
                self.role_connections[role].add(connection_id)
            
            self.stats["connections_count"] += 1
            
            # Enviar evento de boas-vindas
            welcome_event = WebSocketEvent(
                event_type=EventType.USER_JOINED,
                data={
                    "connection_id": connection_id,
                    "message": "Conectado com sucesso ao sistema de eventos em tempo real",
                    "server_time": datetime.utcnow().isoformat(),
                    "features": [
                        "real_time_notifications",
                        "gamification_updates", 
                        "dashboard_sync",
                        "chat_support"
                    ]
                }
            )
            
            await self._send_to_connection(connection_id, welcome_event)
            
            logger.info(f"🔗 Nova conexão WebSocket registrada: {connection_id} (user: {user_id})")
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar conexão {connection_id}: {e}")
            await self._disconnect(connection_id)
            
    async def _disconnect(self, connection_id: str):
        """Remove uma conexão"""
        try:
            if connection_id not in self.connections:
                return
                
            connection_info = self.connections[connection_id]
            
            # Remover dos índices
            user_id = connection_info.get("user_id")
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
                    
            event_id = connection_info.get("event_id")
            if event_id and event_id in self.event_connections:
                self.event_connections[event_id].discard(connection_id)
                if not self.event_connections[event_id]:
                    del self.event_connections[event_id]
                    
            role = connection_info.get("role")
            if role and role in self.role_connections:
                self.role_connections[role].discard(connection_id)
                if not self.role_connections[role]:
                    del self.role_connections[role]
            
            # Fechar WebSocket
            try:
                websocket = connection_info["websocket"]
                await websocket.close()
            except:
                pass
            
            # Remover da lista de conexões
            del self.connections[connection_id]
            self.stats["connections_count"] -= 1
            
            logger.info(f"🔌 Conexão WebSocket removida: {connection_id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao desconectar {connection_id}: {e}")
            
    async def emit_event(self, event: WebSocketEvent):
        """Adiciona um evento à queue para processamento"""
        try:
            # Adicionar à queue baseado na prioridade
            self.event_queue[event.priority].append(event)
            
            # Atualizar estatísticas
            event_type_str = event.event_type.value
            if event_type_str not in self.stats["events_by_type"]:
                self.stats["events_by_type"][event_type_str] = 0
            self.stats["events_by_type"][event_type_str] += 1
            
            logger.debug(f"📤 Evento adicionado à queue: {event.event_type.value}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao emitir evento: {e}")
            
    async def _process_event_queue(self):
        """Processa a queue de eventos em background"""
        while self.running:
            try:
                # Processar eventos por prioridade
                for priority in [EventPriority.CRITICAL, EventPriority.HIGH, EventPriority.NORMAL, EventPriority.LOW]:
                    events = self.event_queue[priority]
                    
                    while events and self.running:
                        event = events.pop(0)
                        
                        # Verificar se o evento não expirou
                        if event.is_expired():
                            continue
                            
                        await self._deliver_event(event)
                
                # Pequena pausa para não sobrecarregar
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Erro no processamento da queue de eventos: {e}")
                await asyncio.sleep(1)
                
    async def _deliver_event(self, event: WebSocketEvent):
        """Entrega um evento para as conexões apropriadas"""
        try:
            target_connections = set()
            
            # Determinar conexões alvo
            if event.target_users:
                for user_id in event.target_users:
                    if user_id in self.user_connections:
                        target_connections.update(self.user_connections[user_id])
                        
            if event.target_events:
                for event_id in event.target_events:
                    if event_id in self.event_connections:
                        target_connections.update(self.event_connections[event_id])
                        
            if event.target_roles:
                for role in event.target_roles:
                    if role in self.role_connections:
                        target_connections.update(self.role_connections[role])
            
            # Se nenhum alvo específico, broadcast para todos
            if not target_connections and not (event.target_users or event.target_events or event.target_roles):
                target_connections = set(self.connections.keys())
            
            # Enviar para todas as conexões alvo
            delivery_tasks = []
            for connection_id in target_connections:
                if connection_id in self.connections:
                    task = asyncio.create_task(self._send_to_connection(connection_id, event))
                    delivery_tasks.append(task)
            
            # Aguardar todas as entregas
            if delivery_tasks:
                results = await asyncio.gather(*delivery_tasks, return_exceptions=True)
                
                # Contar sucessos e falhas
                successful_deliveries = sum(1 for result in results if result is True)
                failed_deliveries = len(results) - successful_deliveries
                
                self.stats["total_events_sent"] += successful_deliveries
                self.stats["failed_deliveries"] += failed_deliveries
                
                if failed_deliveries > 0:
                    logger.warning(f"⚠️ {failed_deliveries} entregas falharam para evento {event.event_type.value}")
                
                logger.debug(f"📨 Evento {event.event_type.value} entregue para {successful_deliveries} conexões")
            
        except Exception as e:
            logger.error(f"❌ Erro na entrega do evento {event.event_type.value}: {e}")
            
    async def _send_to_connection(self, connection_id: str, event: WebSocketEvent) -> bool:
        """Envia um evento para uma conexão específica"""
        try:
            if connection_id not in self.connections:
                return False
                
            websocket = self.connections[connection_id]["websocket"]
            message = json.dumps(event.to_dict())
            
            await websocket.send_text(message)
            
            # Se requer acknowledgment, adicionar à lista
            if event.requires_ack:
                self.pending_acks[event.id] = event
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar para conexão {connection_id}: {e}")
            # Remover conexão com problemas
            await self._disconnect(connection_id)
            return False
            
    async def handle_acknowledgment(self, connection_id: str, event_id: str):
        """Processa acknowledgment de evento"""
        try:
            if event_id in self.pending_acks:
                del self.pending_acks[event_id]
                logger.debug(f"✅ Acknowledgment recebido: {event_id} de {connection_id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar acknowledgment: {e}")
            
    async def _cleanup_expired_events(self):
        """Remove eventos expirados dos pending acknowledgments"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                expired_events = [
                    event_id for event_id, event in self.pending_acks.items()
                    if event.is_expired()
                ]
                
                for event_id in expired_events:
                    del self.pending_acks[event_id]
                
                if expired_events:
                    logger.info(f"🗑️ {len(expired_events)} eventos expirados removidos")
                
                # Cleanup a cada 5 minutos
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"❌ Erro no cleanup de eventos expirados: {e}")
                await asyncio.sleep(60)
                
    async def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de eventos"""
        return {
            "connections": {
                "total": self.stats["connections_count"],
                "by_user": len(self.user_connections),
                "by_event": len(self.event_connections),
                "by_role": len(self.role_connections)
            },
            "events": {
                "total_sent": self.stats["total_events_sent"],
                "failed_deliveries": self.stats["failed_deliveries"],
                "by_type": self.stats["events_by_type"],
                "pending_acks": len(self.pending_acks)
            },
            "queue_sizes": {
                priority.value: len(events) 
                for priority, events in self.event_queue.items()
            },
            "uptime": datetime.utcnow().isoformat() if self.running else None
        }


# Instância global do gerenciador de eventos
websocket_event_manager = WebSocketEventManager()


# Funções utilitárias para criar eventos comuns

async def emit_gamification_event(
    event_type: EventType,
    user_id: str,
    data: Dict[str, Any],
    priority: EventPriority = EventPriority.NORMAL
):
    """Emite evento de gamificação para usuário específico"""
    event = WebSocketEvent(
        event_type=event_type,
        data=data,
        priority=priority,
        target_users={user_id}
    )
    await websocket_event_manager.emit_event(event)


async def emit_event_update(
    event_type: EventType,
    event_id: str,
    data: Dict[str, Any],
    priority: EventPriority = EventPriority.NORMAL
):
    """Emite update de evento para todos os participantes"""
    event = WebSocketEvent(
        event_type=event_type,
        data=data,
        priority=priority,
        target_events={event_id}
    )
    await websocket_event_manager.emit_event(event)


async def emit_system_alert(
    message: str,
    level: str = "info",
    target_roles: Optional[Set[str]] = None
):
    """Emite alerta do sistema"""
    event = WebSocketEvent(
        event_type=EventType.SYSTEM_ALERT,
        data={
            "message": message,
            "level": level,
            "timestamp": datetime.utcnow().isoformat()
        },
        priority=EventPriority.HIGH if level in ["warning", "error"] else EventPriority.NORMAL,
        target_roles=target_roles or {"admin", "organizador"}
    )
    await websocket_event_manager.emit_event(event)