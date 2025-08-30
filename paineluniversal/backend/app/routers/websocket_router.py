"""
Ultra-Performance WebSocket Router
Sistema Universal de Gestão de Eventos - Real-time API
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.websockets.ultra_websockets import (
    ws_manager, ConnectionType, MessageType, WebSocketMessage,
    create_checkin_message, create_stats_message, create_payment_message
)

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)

# ================================
# WEBSOCKET ENDPOINTS
# ================================

@router.websocket("/ws/events/{event_id}")
async def websocket_event_endpoint(
    websocket: WebSocket,
    event_id: str,
    connection_type: str = Query("public", description="Connection type: admin, organizer, monitor, participant, pos, public"),
    user_id: Optional[str] = Query(None, description="User ID for authenticated connections"),
    token: Optional[str] = Query(None, description="Authentication token")
):
    """
    Ultra-performance WebSocket endpoint for event real-time updates.
    
    Connection Types:
    - admin: Full access to all events and system data
    - organizer: Event management access for owned events
    - monitor: Read-only dashboard access
    - participant: Participant-specific updates
    - pos: POS terminal updates
    - public: Public event information only
    """
    
    # Validate connection type
    try:
        conn_type = ConnectionType(connection_type.lower())
    except ValueError:
        await websocket.close(code=4000, reason="Invalid connection type")
        return
    
    # Authentication for protected connection types
    if conn_type in [ConnectionType.ADMIN, ConnectionType.ORGANIZER, ConnectionType.POS]:
        if not token or token != "ultra-performance-token":  # In production, validate JWT
            await websocket.close(code=4001, reason="Authentication required")
            return
    
    connection_id = None
    
    try:
        # Connect to WebSocket manager
        connection_id = await ws_manager.connect(
            websocket=websocket,
            connection_type=conn_type,
            user_id=user_id,
            event_id=event_id
        )
        
        logger.info(f"🔌 WebSocket connected: {connection_id} for event {event_id} ({connection_type})")
        
        # Handle incoming messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                
                # Parse message
                import orjson
                message_data = orjson.loads(data)
                
                # Create WebSocket message
                message = WebSocketMessage(
                    type=MessageType(message_data.get("type")),
                    data=message_data.get("data", {}),
                    event_id=event_id
                )
                
                # Queue message for processing
                await ws_manager.queue_message(message)
                
                logger.debug(f"📥 Message received from {connection_id}: {message.type.value}")
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"❌ Error handling message from {connection_id}: {e}")
                
                # Send error message back to client
                error_message = WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"error": f"Message processing failed: {str(e)}"}
                )
                await ws_manager.send_to_connection(connection_id, error_message)
    
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket connection error: {e}")
    finally:
        if connection_id:
            await ws_manager.disconnect(connection_id)

@router.websocket("/ws/admin/global")
async def websocket_admin_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="Admin authentication token")
):
    """
    Global admin WebSocket endpoint for system-wide monitoring.
    Receives updates from all events and system metrics.
    """
    
    # Validate admin token
    if not token or token != "ultra-admin-token":  # In production, validate admin JWT
        await websocket.close(code=4001, reason="Admin authentication required")
        return
    
    connection_id = None
    
    try:
        # Connect as admin (no specific event)
        connection_id = await ws_manager.connect(
            websocket=websocket,
            connection_type=ConnectionType.ADMIN,
            user_id="admin",
            event_id=None
        )
        
        logger.info(f"🔌 Admin WebSocket connected: {connection_id}")
        
        # Send initial system stats
        stats = await ws_manager.get_stats()
        welcome_message = WebSocketMessage(
            type=MessageType.NOTIFICATION,
            data={
                "message": "Connected to Admin Dashboard",
                "system_stats": stats,
                "timestamp": datetime.now().isoformat()
            }
        )
        await ws_manager.send_to_connection(connection_id, welcome_message)
        
        # Handle admin commands
        while True:
            try:
                data = await websocket.receive_text()
                
                import orjson
                command_data = orjson.loads(data)
                command = command_data.get("command")
                
                # Process admin commands
                if command == "get_stats":
                    stats = await ws_manager.get_stats()
                    response = WebSocketMessage(
                        type=MessageType.NOTIFICATION,
                        data={"system_stats": stats}
                    )
                    await ws_manager.send_to_connection(connection_id, response)
                
                elif command == "broadcast_message":
                    # Admin broadcast to specific event or all
                    message_type = MessageType(command_data.get("message_type", "notification"))
                    message_data_payload = command_data.get("data", {})
                    target_event = command_data.get("event_id")
                    
                    broadcast_message = WebSocketMessage(
                        type=message_type,
                        data=message_data_payload,
                        event_id=target_event
                    )
                    
                    if target_event:
                        await ws_manager.broadcast_to_event(target_event, broadcast_message)
                    else:
                        await ws_manager.broadcast_to_type(ConnectionType.MONITOR, broadcast_message)
                
                else:
                    logger.warning(f"Unknown admin command: {command}")
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"❌ Admin command error: {e}")
    
    except WebSocketDisconnect:
        logger.info(f"🔌 Admin WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"❌ Admin WebSocket error: {e}")
    finally:
        if connection_id:
            await ws_manager.disconnect(connection_id)

@router.websocket("/ws/pos/{pos_terminal_id}")
async def websocket_pos_endpoint(
    websocket: WebSocket,
    pos_terminal_id: str,
    event_id: str = Query(..., description="Event ID for POS terminal"),
    token: Optional[str] = Query(None, description="POS authentication token")
):
    """
    POS terminal WebSocket endpoint for real-time sales updates.
    Optimized for high-frequency transaction messages.
    """
    
    # Validate POS token
    if not token or token != "ultra-pos-token":  # In production, validate POS JWT
        await websocket.close(code=4001, reason="POS authentication required")
        return
    
    connection_id = None
    
    try:
        # Connect as POS terminal
        connection_id = await ws_manager.connect(
            websocket=websocket,
            connection_type=ConnectionType.POS,
            user_id=pos_terminal_id,
            event_id=event_id
        )
        
        logger.info(f"🔌 POS WebSocket connected: {connection_id} for terminal {pos_terminal_id}")
        
        # Handle POS messages (sales, inventory updates)
        while True:
            try:
                data = await websocket.receive_text()
                
                import orjson
                message_data = orjson.loads(data)
                
                # Create POS-specific message
                pos_message = WebSocketMessage(
                    type=MessageType(message_data.get("type")),
                    data={
                        "pos_terminal_id": pos_terminal_id,
                        **message_data.get("data", {})
                    },
                    event_id=event_id
                )
                
                # Queue for processing
                await ws_manager.queue_message(pos_message)
                
                # Immediate broadcast for critical POS events
                if pos_message.type in [MessageType.SALE_COMPLETED, MessageType.PAYMENT_STATUS]:
                    await ws_manager.broadcast_to_event(event_id, pos_message)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"❌ POS message error: {e}")
    
    except WebSocketDisconnect:
        logger.info(f"🔌 POS WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"❌ POS WebSocket error: {e}")
    finally:
        if connection_id:
            await ws_manager.disconnect(connection_id)

# ================================
# HTTP ENDPOINTS FOR WEBSOCKET MANAGEMENT
# ================================

@router.get("/api/v3/websocket/stats")
async def get_websocket_stats():
    """Get WebSocket system statistics"""
    return await ws_manager.get_stats()

@router.post("/api/v3/websocket/broadcast/{event_id}")
async def broadcast_to_event(
    event_id: str,
    message_type: str,
    message_data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    HTTP endpoint to broadcast message to WebSocket connections for specific event.
    Used by other services to trigger real-time updates.
    """
    
    # Validate authentication
    if not credentials or credentials.credentials != "ultra-performance-token":
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Create WebSocket message
        ws_message = WebSocketMessage(
            type=MessageType(message_type),
            data=message_data,
            event_id=event_id
        )
        
        # Broadcast to all connections for this event
        await ws_manager.broadcast_to_event(event_id, ws_message)
        
        return {
            "success": True,
            "message": f"Broadcast sent to event {event_id}",
            "message_type": message_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid message type: {str(e)}")
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        raise HTTPException(status_code=500, detail=f"Broadcast failed: {str(e)}")

@router.post("/api/v3/websocket/broadcast-global")
async def broadcast_global(
    connection_type: str,
    message_type: str,
    message_data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    HTTP endpoint to broadcast message to all connections of a specific type.
    """
    
    # Validate admin authentication
    if not credentials or credentials.credentials != "ultra-admin-token":
        raise HTTPException(status_code=401, detail="Admin authentication required")
    
    try:
        # Validate connection type
        conn_type = ConnectionType(connection_type.lower())
        
        # Create WebSocket message
        ws_message = WebSocketMessage(
            type=MessageType(message_type),
            data=message_data
        )
        
        # Broadcast to all connections of this type
        await ws_manager.broadcast_to_type(conn_type, ws_message)
        
        return {
            "success": True,
            "message": f"Global broadcast sent to {connection_type} connections",
            "message_type": message_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid type: {str(e)}")
    except Exception as e:
        logger.error(f"Global broadcast error: {e}")
        raise HTTPException(status_code=500, detail=f"Broadcast failed: {str(e)}")

@router.post("/api/v3/websocket/send-user/{user_id}")
async def send_to_user(
    user_id: str,
    message_type: str,
    message_data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    HTTP endpoint to send message to specific user's WebSocket connections.
    """
    
    # Validate authentication
    if not credentials or credentials.credentials != "ultra-performance-token":
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Create WebSocket message
        ws_message = WebSocketMessage(
            type=MessageType(message_type),
            data=message_data
        )
        
        # Send to user's connections
        await ws_manager.send_to_user(user_id, ws_message)
        
        return {
            "success": True,
            "message": f"Message sent to user {user_id}",
            "message_type": message_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid message type: {str(e)}")
    except Exception as e:
        logger.error(f"Send to user error: {e}")
        raise HTTPException(status_code=500, detail=f"Send failed: {str(e)}")

# ================================
# UTILITY ENDPOINTS FOR TESTING
# ================================

@router.post("/api/v3/websocket/test/checkin")
async def test_checkin_broadcast(
    event_id: str,
    participant_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Test endpoint to simulate check-in broadcast"""
    
    if not credentials or credentials.credentials != "ultra-performance-token":
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Create test check-in message
    checkin_message = create_checkin_message(
        participant_id=participant_id,
        event_id=event_id,
        checkin_data={
            "checkin_time": datetime.now().isoformat(),
            "status": "checked_in",
            "test_mode": True
        }
    )
    
    # Broadcast to event
    await ws_manager.broadcast_to_event(event_id, checkin_message)
    
    return {
        "success": True,
        "message": "Test check-in broadcast sent",
        "participant_id": participant_id,
        "event_id": event_id
    }

@router.post("/api/v3/websocket/test/stats")
async def test_stats_broadcast(
    event_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Test endpoint to simulate live stats broadcast"""
    
    if not credentials or credentials.credentials != "ultra-performance-token":
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Create test stats message
    stats_message = create_stats_message(
        event_id=event_id,
        stats={
            "total_participants": 150,
            "checked_in": 120,
            "check_in_rate": 80.0,
            "revenue": 15000.00,
            "last_update": datetime.now().isoformat(),
            "test_mode": True
        }
    )
    
    # Broadcast to monitors and admins
    await ws_manager.broadcast_to_type(ConnectionType.MONITOR, stats_message)
    await ws_manager.broadcast_to_type(ConnectionType.ADMIN, stats_message)
    
    return {
        "success": True,
        "message": "Test stats broadcast sent",
        "event_id": event_id
    }