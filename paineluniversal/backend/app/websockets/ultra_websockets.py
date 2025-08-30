"""
Ultra-High Performance WebSocket System
Enterprise-grade real-time communication with connection pooling
Target: 10,000+ concurrent connections, sub-millisecond messaging
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import weakref

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ConnectionType(str, Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    PARTICIPANT = "participant"
    POS = "pos"
    MONITOR = "monitor"

class MessageType(str, Enum):
    SYSTEM = "system"
    EVENT_UPDATE = "event_update"
    CHECKIN = "checkin"
    SALE = "sale"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"

class WebSocketMessage(BaseModel):
    type: MessageType
    data: Dict[str, Any]
    timestamp: datetime
    sender_id: Optional[str] = None
    target_users: Optional[List[str]] = None
    target_rooms: Optional[List[str]] = None

class UltraWebSocketConnection:
    """High-performance WebSocket connection wrapper"""
    
    def __init__(self, websocket: WebSocket, connection_type: ConnectionType, user_id: str):
        self.websocket = websocket
        self.connection_type = connection_type
        self.user_id = user_id
        self.connection_id = f"{user_id}_{int(time.time() * 1000)}"
        self.connected_at = datetime.now()
        self.last_heartbeat = time.time()
        self.rooms: Set[str] = set()
        self.is_active = True
        self.message_count = 0
        self.bytes_sent = 0
        self.bytes_received = 0
    
    async def send_json(self, data: Dict[str, Any]) -> bool:
        """Send JSON data with error handling"""
        if not self.is_active:
            return False
        
        try:
            message = json.dumps(data, separators=(',', ':'), default=str)
            await self.websocket.send_text(message)
            self.message_count += 1
            self.bytes_sent += len(message)
            return True
        except Exception as e:
            logger.error(f"Send error for {self.connection_id}: {e}")
            self.is_active = False
            return False
    
    async def receive_json(self) -> Optional[Dict[str, Any]]:
        """Receive JSON data with error handling"""
        try:
            message = await self.websocket.receive_text()
            self.bytes_received += len(message)
            self.last_heartbeat = time.time()
            return json.loads(message)
        except Exception as e:
            logger.error(f"Receive error for {self.connection_id}: {e}")
            self.is_active = False
            return None
    
    def join_room(self, room: str):
        """Join a room for targeted messaging"""
        self.rooms.add(room)
    
    def leave_room(self, room: str):
        """Leave a room"""
        self.rooms.discard(room)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        uptime = (datetime.now() - self.connected_at).total_seconds()
        return {
            'connection_id': self.connection_id,
            'user_id': self.user_id,
            'connection_type': self.connection_type,
            'uptime_seconds': round(uptime, 2),
            'message_count': self.message_count,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'rooms': list(self.rooms),
            'is_active': self.is_active,
            'last_heartbeat': self.last_heartbeat
        }

class UltraWebSocketManager:
    """Enterprise WebSocket connection manager"""
    
    def __init__(self):
        # Connection pools by type for optimized routing
        self.connections: Dict[ConnectionType, Dict[str, UltraWebSocketConnection]] = {
            ConnectionType.ADMIN: {},
            ConnectionType.ORGANIZER: {},
            ConnectionType.PARTICIPANT: {},
            ConnectionType.POS: {},
            ConnectionType.MONITOR: {}
        }
        
        # Room management
        self.rooms: Dict[str, Set[str]] = {}  # room_id -> set of connection_ids
        
        # Performance metrics
        self.stats = {
            'total_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'bytes_transferred': 0,
            'connection_errors': 0,
            'start_time': datetime.now()
        }
        
        # Background tasks
        self._heartbeat_task = None
        self._cleanup_task = None
    
    async def connect(self, websocket: WebSocket, connection_type: ConnectionType, user_id: str) -> UltraWebSocketConnection:
        """Accept new WebSocket connection with optimization"""
        try:
            await websocket.accept()
            
            connection = UltraWebSocketConnection(websocket, connection_type, user_id)
            
            # Store in appropriate pool
            self.connections[connection_type][connection.connection_id] = connection
            
            # Auto-join type-specific room
            await self._join_room(connection.connection_id, f"type_{connection_type}")
            
            self.stats['total_connections'] += 1
            
            logger.info(f"✅ WebSocket connected: {connection.connection_id} ({connection_type})")
            
            # Send welcome message
            await connection.send_json({
                'type': 'system',
                'data': {
                    'message': 'Connected to Ultra Performance WebSocket',
                    'connection_id': connection.connection_id,
                    'server_time': datetime.now().isoformat()
                }
            })
            
            return connection
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.stats['connection_errors'] += 1
            raise
    
    async def disconnect(self, connection_id: str):
        """Handle WebSocket disconnection"""
        connection = self._find_connection(connection_id)
        if connection:
            connection.is_active = False
            
            # Remove from all rooms
            for room_id in list(connection.rooms):
                await self._leave_room(connection_id, room_id)
            
            # Remove from connection pool
            for pool in self.connections.values():
                if connection_id in pool:
                    del pool[connection_id]
                    break
            
            logger.info(f"🔌 WebSocket disconnected: {connection_id}")
    
    def _find_connection(self, connection_id: str) -> Optional[UltraWebSocketConnection]:
        """Find connection across all pools"""
        for pool in self.connections.values():
            if connection_id in pool:
                return pool[connection_id]
        return None
    
    async def send_to_user(self, user_id: str, message: WebSocketMessage) -> int:
        """Send message to specific user (all their connections)"""
        sent_count = 0
        message_data = {
            'type': message.type,
            'data': message.data,
            'timestamp': message.timestamp.isoformat(),
            'sender_id': message.sender_id
        }
        
        for pool in self.connections.values():
            for connection in pool.values():
                if connection.user_id == user_id and connection.is_active:
                    if await connection.send_json(message_data):
                        sent_count += 1
        
        if sent_count > 0:
            self.stats['messages_sent'] += sent_count
        
        return sent_count
    
    async def send_to_type(self, connection_type: ConnectionType, message: WebSocketMessage) -> int:
        """Send message to all connections of specific type"""
        sent_count = 0
        message_data = {
            'type': message.type,
            'data': message.data,
            'timestamp': message.timestamp.isoformat(),
            'sender_id': message.sender_id
        }
        
        connections = self.connections.get(connection_type, {})
        for connection in connections.values():
            if connection.is_active:
                if await connection.send_json(message_data):
                    sent_count += 1
        
        if sent_count > 0:
            self.stats['messages_sent'] += sent_count
        
        return sent_count
    
    async def send_to_room(self, room_id: str, message: WebSocketMessage) -> int:
        """Send message to all connections in a room"""
        sent_count = 0
        
        if room_id not in self.rooms:
            return 0
        
        message_data = {
            'type': message.type,
            'data': message.data,
            'timestamp': message.timestamp.isoformat(),
            'sender_id': message.sender_id
        }
        
        for connection_id in self.rooms[room_id]:
            connection = self._find_connection(connection_id)
            if connection and connection.is_active:
                if await connection.send_json(message_data):
                    sent_count += 1
        
        if sent_count > 0:
            self.stats['messages_sent'] += sent_count
        
        return sent_count
    
    async def broadcast(self, message: WebSocketMessage) -> int:
        """Broadcast message to all active connections"""
        sent_count = 0
        message_data = {
            'type': message.type,
            'data': message.data,
            'timestamp': message.timestamp.isoformat(),
            'sender_id': message.sender_id
        }
        
        for pool in self.connections.values():
            for connection in pool.values():
                if connection.is_active:
                    if await connection.send_json(message_data):
                        sent_count += 1
        
        if sent_count > 0:
            self.stats['messages_sent'] += sent_count
        
        return sent_count
    
    async def _join_room(self, connection_id: str, room_id: str):
        """Add connection to room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        
        self.rooms[room_id].add(connection_id)
        
        connection = self._find_connection(connection_id)
        if connection:
            connection.join_room(room_id)
    
    async def _leave_room(self, connection_id: str, room_id: str):
        """Remove connection from room"""
        if room_id in self.rooms:
            self.rooms[room_id].discard(connection_id)
            
            # Clean up empty rooms
            if not self.rooms[room_id]:
                del self.rooms[room_id]
        
        connection = self._find_connection(connection_id)
        if connection:
            connection.leave_room(room_id)
    
    async def start_background_tasks(self):
        """Start background maintenance tasks"""
        if not self._heartbeat_task:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats and check connection health"""
        while True:
            try:
                await asyncio.sleep(30)  # Every 30 seconds
                
                current_time = time.time()
                dead_connections = []
                
                # Check all connections
                for pool in self.connections.values():
                    for connection_id, connection in pool.items():
                        # Check if connection is stale (no heartbeat in 60 seconds)
                        if current_time - connection.last_heartbeat > 60:
                            dead_connections.append(connection_id)
                        elif connection.is_active:
                            # Send heartbeat
                            await connection.send_json({
                                'type': 'heartbeat',
                                'data': {'timestamp': datetime.now().isoformat()}
                            })
                
                # Clean up dead connections
                for connection_id in dead_connections:
                    await self.disconnect(connection_id)
                
                if dead_connections:
                    logger.info(f"Cleaned up {len(dead_connections)} stale connections")
                    
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
    
    async def _cleanup_loop(self):
        """Periodic cleanup and optimization"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Clean up empty rooms
                empty_rooms = [room_id for room_id, connections in self.rooms.items() if not connections]
                for room_id in empty_rooms:
                    del self.rooms[room_id]
                
                if empty_rooms:
                    logger.info(f"Cleaned up {len(empty_rooms)} empty rooms")
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive WebSocket statistics"""
        active_connections = sum(
            len([c for c in pool.values() if c.is_active])
            for pool in self.connections.values()
        )
        
        uptime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'active_connections': active_connections,
            'total_connections': self.stats['total_connections'],
            'connections_by_type': {
                conn_type.value: len([c for c in pool.values() if c.is_active])
                for conn_type, pool in self.connections.items()
            },
            'room_count': len(self.rooms),
            'messages_sent': self.stats['messages_sent'],
            'messages_received': self.stats['messages_received'],
            'connection_errors': self.stats['connection_errors'],
            'uptime_seconds': round(uptime, 2),
            'messages_per_second': round(self.stats['messages_sent'] / max(uptime, 1), 2)
        }
    
    async def stop_background_tasks(self):
        """Stop all background tasks"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()

# Global WebSocket manager
ultra_websocket_manager = UltraWebSocketManager()

# Convenience functions
async def init_websocket_system():
    """Initialize WebSocket system"""
    await ultra_websocket_manager.start_background_tasks()
    logger.info("✅ Ultra WebSocket system initialized")

async def websocket_connect(websocket: WebSocket, connection_type: str, user_id: str):
    """Connect WebSocket endpoint"""
    return await ultra_websocket_manager.connect(
        websocket, 
        ConnectionType(connection_type), 
        user_id
    )

async def websocket_disconnect(connection_id: str):
    """Disconnect WebSocket endpoint"""
    await ultra_websocket_manager.disconnect(connection_id)

async def send_event_update(event_id: str, event_data: Dict[str, Any]):
    """Send event update to relevant users"""
    message = WebSocketMessage(
        type=MessageType.EVENT_UPDATE,
        data={'event_id': event_id, **event_data},
        timestamp=datetime.now()
    )
    
    # Send to organizers and participants
    organizer_count = await ultra_websocket_manager.send_to_type(ConnectionType.ORGANIZER, message)
    participant_count = await ultra_websocket_manager.send_to_room(f"event_{event_id}", message)
    
    return organizer_count + participant_count

async def send_checkin_notification(user_id: str, event_id: str, checkin_data: Dict[str, Any]):
    """Send check-in notification"""
    message = WebSocketMessage(
        type=MessageType.CHECKIN,
        data={'event_id': event_id, **checkin_data},
        timestamp=datetime.now()
    )
    
    # Send to organizers and POS systems
    organizer_count = await ultra_websocket_manager.send_to_type(ConnectionType.ORGANIZER, message)
    pos_count = await ultra_websocket_manager.send_to_type(ConnectionType.POS, message)
    
    return organizer_count + pos_count

async def get_websocket_stats():
    """Get WebSocket system statistics"""
    return ultra_websocket_manager.get_stats()