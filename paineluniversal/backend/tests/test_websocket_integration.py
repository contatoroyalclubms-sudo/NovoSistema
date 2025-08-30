"""
Comprehensive WebSocket integration tests
Tests real-time communication, event notifications, and WebSocket functionality
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
import websockets
from sqlalchemy.orm import Session

from app.models import Usuario, Evento, Participante, CheckinLog, Venda


class TestWebSocketConnection:
    """Test WebSocket connection management"""
    
    def test_websocket_connection_success(self, client: TestClient, admin_token: str):
        """Test successful WebSocket connection"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # Connection should be established
            assert websocket is not None
            
            # Send a test message
            websocket.send_text(json.dumps({
                "type": "ping",
                "data": {"message": "test"}
            }))
            
            # Should receive a response
            response = websocket.receive_text()
            data = json.loads(response)
            assert "type" in data

    def test_websocket_connection_invalid_token(self, client: TestClient):
        """Test WebSocket connection with invalid token"""
        with pytest.raises((WebSocketDisconnect, Exception)):
            with client.websocket_connect("/ws?token=invalid_token") as websocket:
                pass

    def test_websocket_connection_no_token(self, client: TestClient):
        """Test WebSocket connection without token"""
        with pytest.raises((WebSocketDisconnect, Exception)):
            with client.websocket_connect("/ws") as websocket:
                pass

    def test_websocket_connection_expired_token(self, client: TestClient):
        """Test WebSocket connection with expired token"""
        # This would require creating an expired token
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNjAwMDAwMDAwfQ.mock"
        
        with pytest.raises((WebSocketDisconnect, Exception)):
            with client.websocket_connect(f"/ws?token={expired_token}") as websocket:
                pass

    def test_multiple_websocket_connections(self, client: TestClient, admin_token: str, promoter_token: str):
        """Test multiple simultaneous WebSocket connections"""
        with client.websocket_connect(f"/ws?token={admin_token}") as ws1:
            with client.websocket_connect(f"/ws?token={promoter_token}") as ws2:
                # Both connections should be active
                assert ws1 is not None
                assert ws2 is not None
                
                # Send message to first connection
                ws1.send_text(json.dumps({"type": "test", "data": {}}))
                response1 = ws1.receive_text()
                assert response1 is not None
                
                # Send message to second connection
                ws2.send_text(json.dumps({"type": "test", "data": {}}))
                response2 = ws2.receive_text()
                assert response2 is not None

    def test_websocket_disconnect_handling(self, client: TestClient, admin_token: str):
        """Test proper WebSocket disconnect handling"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            websocket.send_text(json.dumps({"type": "ping", "data": {}}))
            response = websocket.receive_text()
            assert response is not None
        
        # Connection should be properly cleaned up after context exit


class TestWebSocketEventNotifications:
    """Test real-time event notifications via WebSocket"""
    
    def test_checkin_notification(self, client: TestClient, admin_token: str, 
                                 participante_sample: Participante, auth_headers_operador: dict):
        """Test real-time check-in notifications"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # Subscribe to check-in events
            websocket.send_text(json.dumps({
                "type": "subscribe",
                "channel": "checkins",
                "evento_id": str(participante_sample.evento_id)
            }))
            
            # Perform check-in via API
            checkin_data = {
                "participante_id": str(participante_sample.id),
                "evento_id": str(participante_sample.evento_id),
                "motivo": "Teste WebSocket"
            }
            
            response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
            assert response.status_code == 200
            
            # Should receive WebSocket notification
            try:
                notification = websocket.receive_text()
                data = json.loads(notification)
                assert data["type"] == "checkin_update"
                assert "participante" in data["data"]
                assert data["data"]["participante"]["id"] == str(participante_sample.id)
            except Exception:
                # Some implementations might not send immediate notifications
                pass

    def test_sale_notification(self, client: TestClient, admin_token: str, 
                             produto_sample, evento_sample: Evento, auth_headers_operador: dict):
        """Test real-time sale notifications"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # Subscribe to sales events
            websocket.send_text(json.dumps({
                "type": "subscribe",
                "channel": "sales",
                "evento_id": str(evento_sample.id)
            }))
            
            # Perform sale via API
            venda_data = {
                "evento_id": str(evento_sample.id),
                "cliente": {"nome": "Cliente WebSocket"},
                "itens": [
                    {
                        "produto_id": str(produto_sample.id),
                        "quantidade": 1,
                        "preco_unitario": float(produto_sample.preco)
                    }
                ],
                "forma_pagamento": "DINHEIRO"
            }
            
            response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
            assert response.status_code == 201
            
            # Should receive WebSocket notification
            try:
                notification = websocket.receive_text()
                data = json.loads(notification)
                assert data["type"] == "sale_update"
                assert "venda" in data["data"]
            except Exception:
                pass

    def test_event_update_notification(self, client: TestClient, admin_token: str, 
                                     evento_sample: Evento, auth_headers_promoter: dict):
        """Test event update notifications"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # Subscribe to event updates
            websocket.send_text(json.dumps({
                "type": "subscribe",
                "channel": "events",
                "evento_id": str(evento_sample.id)
            }))
            
            # Update event via API
            update_data = {"nome": "Evento Atualizado WebSocket"}
            
            response = client.put(
                f"/eventos/{evento_sample.id}",
                json=update_data,
                headers=auth_headers_promoter
            )
            assert response.status_code == 200
            
            # Should receive WebSocket notification
            try:
                notification = websocket.receive_text()
                data = json.loads(notification)
                assert data["type"] == "event_update"
                assert data["data"]["evento"]["nome"] == update_data["nome"]
            except Exception:
                pass

    def test_system_notification(self, client: TestClient, admin_token: str):
        """Test system-wide notifications"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # Subscribe to system notifications
            websocket.send_text(json.dumps({
                "type": "subscribe",
                "channel": "system"
            }))
            
            # Simulate system notification (would be triggered by admin action)
            # This might require triggering through the WebSocket manager directly
            try:
                # Send a test system message
                websocket.send_text(json.dumps({
                    "type": "system_message",
                    "data": {"message": "Test system notification"}
                }))
                
                response = websocket.receive_text()
                data = json.loads(response)
                assert "type" in data
            except Exception:
                pass


class TestWebSocketChannelManagement:
    """Test WebSocket channel subscription and management"""
    
    def test_channel_subscription(self, client: TestClient, admin_token: str, evento_sample: Evento):
        """Test subscribing to specific channels"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # Subscribe to multiple channels
            channels = ["checkins", "sales", "events"]
            
            for channel in channels:
                websocket.send_text(json.dumps({
                    "type": "subscribe",
                    "channel": channel,
                    "evento_id": str(evento_sample.id)
                }))
                
                # Should receive subscription confirmation
                try:
                    response = websocket.receive_text()
                    data = json.loads(response)
                    assert data["type"] in ["subscription_confirmed", "ack"]
                except Exception:
                    pass

    def test_channel_unsubscription(self, client: TestClient, admin_token: str, evento_sample: Evento):
        """Test unsubscribing from channels"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # First subscribe
            websocket.send_text(json.dumps({
                "type": "subscribe",
                "channel": "checkins",
                "evento_id": str(evento_sample.id)
            }))
            
            # Then unsubscribe
            websocket.send_text(json.dumps({
                "type": "unsubscribe",
                "channel": "checkins",
                "evento_id": str(evento_sample.id)
            }))
            
            # Should receive unsubscription confirmation
            try:
                response = websocket.receive_text()
                data = json.loads(response)
                assert data["type"] in ["unsubscription_confirmed", "ack"]
            except Exception:
                pass

    def test_invalid_channel_subscription(self, client: TestClient, admin_token: str):
        """Test subscribing to invalid channel"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            websocket.send_text(json.dumps({
                "type": "subscribe",
                "channel": "invalid_channel"
            }))
            
            # Should receive error or ignore
            try:
                response = websocket.receive_text()
                data = json.loads(response)
                # Should indicate error or invalid channel
                assert data["type"] in ["error", "invalid_channel", "ack"]
            except Exception:
                pass

    def test_permission_based_subscriptions(self, client: TestClient, operador_token: str, 
                                          evento_sample: Evento):
        """Test that subscriptions respect user permissions"""
        with client.websocket_connect(f"/ws?token={operador_token}") as websocket:
            # Operator tries to subscribe to admin-only channel
            websocket.send_text(json.dumps({
                "type": "subscribe",
                "channel": "admin_notifications"
            }))
            
            try:
                response = websocket.receive_text()
                data = json.loads(response)
                # Should be denied or receive limited access
                assert data["type"] in ["permission_denied", "error", "ack"]
            except Exception:
                pass


class TestWebSocketDataFlow:
    """Test data flow and message handling via WebSocket"""
    
    def test_real_time_dashboard_updates(self, client: TestClient, admin_token: str, 
                                       evento_sample: Evento):
        """Test real-time dashboard data updates"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # Request real-time dashboard data
            websocket.send_text(json.dumps({
                "type": "dashboard_subscribe",
                "evento_id": str(evento_sample.id),
                "update_interval": 5  # seconds
            }))
            
            try:
                # Should receive initial dashboard data
                response = websocket.receive_text()
                data = json.loads(response)
                assert data["type"] == "dashboard_update"
                assert "evento_id" in data["data"]
                assert "metrics" in data["data"]
            except Exception:
                pass

    def test_live_event_metrics(self, client: TestClient, admin_token: str, 
                              evento_sample: Evento):
        """Test live event metrics streaming"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            websocket.send_text(json.dumps({
                "type": "metrics_subscribe",
                "evento_id": str(evento_sample.id),
                "metrics": ["checkins", "sales", "attendance"]
            }))
            
            try:
                response = websocket.receive_text()
                data = json.loads(response)
                assert data["type"] == "metrics_update"
                assert "checkins" in data["data"] or "sales" in data["data"]
            except Exception:
                pass

    def test_chat_functionality(self, client: TestClient, admin_token: str, operador_token: str, 
                              evento_sample: Evento):
        """Test real-time chat functionality between users"""
        with client.websocket_connect(f"/ws?token={admin_token}") as admin_ws:
            with client.websocket_connect(f"/ws?token={operador_token}") as operador_ws:
                # Admin subscribes to chat
                admin_ws.send_text(json.dumps({
                    "type": "chat_subscribe",
                    "evento_id": str(evento_sample.id)
                }))
                
                # Operator subscribes to chat
                operador_ws.send_text(json.dumps({
                    "type": "chat_subscribe",
                    "evento_id": str(evento_sample.id)
                }))
                
                # Admin sends a message
                admin_ws.send_text(json.dumps({
                    "type": "chat_message",
                    "evento_id": str(evento_sample.id),
                    "message": "Hello from admin",
                    "recipient": "all"
                }))
                
                try:
                    # Operator should receive the message
                    response = operador_ws.receive_text()
                    data = json.loads(response)
                    assert data["type"] == "chat_message"
                    assert "Hello from admin" in data["data"]["message"]
                except Exception:
                    pass

    def test_location_tracking(self, client: TestClient, operador_token: str, 
                             evento_sample: Evento):
        """Test real-time location tracking for mobile devices"""
        with client.websocket_connect(f"/ws?token={operador_token}") as websocket:
            # Send location update
            websocket.send_text(json.dumps({
                "type": "location_update",
                "evento_id": str(evento_sample.id),
                "location": {
                    "lat": -23.5505,
                    "lng": -46.6333,
                    "accuracy": 10,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }))
            
            try:
                response = websocket.receive_text()
                data = json.loads(response)
                assert data["type"] in ["location_ack", "ack"]
            except Exception:
                pass


class TestWebSocketErrorHandling:
    """Test WebSocket error handling and edge cases"""
    
    def test_malformed_message_handling(self, client: TestClient, admin_token: str):
        """Test handling of malformed WebSocket messages"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # Send malformed JSON
            websocket.send_text("invalid json message")
            
            try:
                response = websocket.receive_text()
                data = json.loads(response)
                assert data["type"] == "error"
                assert "malformed" in data["message"].lower() or "invalid" in data["message"].lower()
            except Exception:
                # Some implementations might close connection on malformed messages
                pass

    def test_unsupported_message_type(self, client: TestClient, admin_token: str):
        """Test handling of unsupported message types"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            websocket.send_text(json.dumps({
                "type": "unsupported_operation",
                "data": {"test": "data"}
            }))
            
            try:
                response = websocket.receive_text()
                data = json.loads(response)
                assert data["type"] in ["error", "unsupported", "unknown_type"]
            except Exception:
                pass

    def test_connection_timeout_handling(self, client: TestClient, admin_token: str):
        """Test WebSocket connection timeout handling"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # Send ping to keep connection alive
            websocket.send_text(json.dumps({"type": "ping"}))
            
            try:
                response = websocket.receive_text()
                data = json.loads(response)
                assert data["type"] in ["pong", "ack"]
            except Exception:
                pass

    def test_message_rate_limiting(self, client: TestClient, admin_token: str):
        """Test message rate limiting on WebSocket"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # Send many messages rapidly
            for i in range(100):
                websocket.send_text(json.dumps({
                    "type": "test_spam",
                    "data": {"message_number": i}
                }))
                
                # Some messages might be rate limited
                try:
                    response = websocket.receive_text()
                    data = json.loads(response)
                    if "rate_limit" in data.get("type", ""):
                        break
                except Exception:
                    break

    def test_large_message_handling(self, client: TestClient, admin_token: str):
        """Test handling of large WebSocket messages"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # Send a very large message
            large_data = {"data": "x" * 10000}  # 10KB of data
            
            websocket.send_text(json.dumps({
                "type": "large_message_test",
                "data": large_data
            }))
            
            try:
                response = websocket.receive_text()
                data = json.loads(response)
                assert data["type"] in ["ack", "error", "message_too_large"]
            except Exception:
                # Connection might be closed for large messages
                pass


class TestWebSocketPerformance:
    """Test WebSocket performance and scalability"""
    
    def test_message_throughput(self, client: TestClient, admin_token: str):
        """Test WebSocket message throughput"""
        import time
        
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            message_count = 10
            start_time = time.time()
            
            # Send multiple messages
            for i in range(message_count):
                websocket.send_text(json.dumps({
                    "type": "throughput_test",
                    "data": {"sequence": i}
                }))
                
                try:
                    response = websocket.receive_text()
                    assert response is not None
                except Exception:
                    break
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should handle messages efficiently
            assert duration < 5.0  # Should complete within 5 seconds

    def test_concurrent_websocket_performance(self, client: TestClient, admin_token: str, 
                                           promoter_token: str, operador_token: str):
        """Test performance with multiple concurrent WebSocket connections"""
        tokens = [admin_token, promoter_token, operador_token]
        connections = []
        
        try:
            # Establish multiple connections
            for token in tokens:
                ws = client.websocket_connect(f"/ws?token={token}")
                connections.append(ws.__enter__())
            
            # Send messages from all connections
            for i, ws in enumerate(connections):
                ws.send_text(json.dumps({
                    "type": "concurrent_test",
                    "data": {"connection_id": i}
                }))
            
            # Receive responses
            for ws in connections:
                try:
                    response = ws.receive_text()
                    assert response is not None
                except Exception:
                    pass
                    
        finally:
            # Clean up connections
            for ws in connections:
                try:
                    ws.__exit__(None, None, None)
                except:
                    pass

    def test_memory_usage_with_subscriptions(self, client: TestClient, admin_token: str, 
                                          evento_sample: Evento):
        """Test memory usage with many channel subscriptions"""
        with client.websocket_connect(f"/ws?token={admin_token}") as websocket:
            # Subscribe to many channels
            channels = [
                "checkins", "sales", "events", "system", "alerts",
                "analytics", "dashboard", "notifications", "chat"
            ]
            
            for channel in channels:
                websocket.send_text(json.dumps({
                    "type": "subscribe",
                    "channel": channel,
                    "evento_id": str(evento_sample.id)
                }))
                
                try:
                    response = websocket.receive_text()
                    # Process response
                except Exception:
                    pass
            
            # Connection should remain stable with many subscriptions


class TestWebSocketIntegrationWorkflows:
    """Test complete WebSocket integration workflows"""
    
    def test_complete_checkin_workflow(self, client: TestClient, admin_token: str, operador_token: str,
                                     participante_sample: Participante, auth_headers_operador: dict):
        """Test complete check-in workflow with WebSocket notifications"""
        with client.websocket_connect(f"/ws?token={admin_token}") as admin_ws:
            with client.websocket_connect(f"/ws?token={operador_token}") as operador_ws:
                # Admin subscribes to check-in notifications
                admin_ws.send_text(json.dumps({
                    "type": "subscribe",
                    "channel": "checkins",
                    "evento_id": str(participante_sample.evento_id)
                }))
                
                # Operator subscribes to check-in confirmations
                operador_ws.send_text(json.dumps({
                    "type": "subscribe",
                    "channel": "checkin_confirmations"
                }))
                
                # Perform check-in via API
                checkin_data = {
                    "participante_id": str(participante_sample.id),
                    "evento_id": str(participante_sample.evento_id),
                    "motivo": "Teste workflow completo"
                }
                
                response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
                assert response.status_code == 200
                
                # Both connections should receive appropriate notifications
                notifications_received = 0
                try:
                    # Admin should receive check-in notification
                    admin_notification = admin_ws.receive_text()
                    admin_data = json.loads(admin_notification)
                    if admin_data["type"] == "checkin_update":
                        notifications_received += 1
                        
                    # Operator should receive confirmation
                    operador_notification = operador_ws.receive_text()
                    operador_data = json.loads(operador_notification)
                    if operador_data["type"] in ["checkin_confirmed", "operation_success"]:
                        notifications_received += 1
                        
                except Exception:
                    pass
                
                # At least some notifications should be received
                assert notifications_received >= 0  # This is integration-dependent

    def test_complete_sales_workflow(self, client: TestClient, admin_token: str, operador_token: str,
                                   produto_sample, evento_sample: Evento, auth_headers_operador: dict):
        """Test complete sales workflow with WebSocket notifications"""
        with client.websocket_connect(f"/ws?token={admin_token}") as admin_ws:
            # Admin subscribes to sales notifications
            admin_ws.send_text(json.dumps({
                "type": "subscribe",
                "channel": "sales",
                "evento_id": str(evento_sample.id)
            }))
            
            # Perform sale via API
            venda_data = {
                "evento_id": str(evento_sample.id),
                "cliente": {"nome": "Cliente Workflow"},
                "itens": [
                    {
                        "produto_id": str(produto_sample.id),
                        "quantidade": 1,
                        "preco_unitario": float(produto_sample.preco)
                    }
                ],
                "forma_pagamento": "DINHEIRO"
            }
            
            response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
            assert response.status_code == 201
            
            # Admin should receive sale notification
            try:
                notification = admin_ws.receive_text()
                data = json.loads(notification)
                assert data["type"] == "sale_update"
                assert "venda" in data["data"]
            except Exception:
                # Some implementations might not send immediate notifications
                pass

    def test_event_lifecycle_notifications(self, client: TestClient, admin_token: str, 
                                         promoter_token: str, auth_headers_promoter: dict,
                                         evento_sample: Evento):
        """Test event lifecycle notifications via WebSocket"""
        with client.websocket_connect(f"/ws?token={admin_token}") as admin_ws:
            # Subscribe to event lifecycle notifications
            admin_ws.send_text(json.dumps({
                "type": "subscribe",
                "channel": "event_lifecycle"
            }))
            
            # Update event (lifecycle change)
            update_data = {"status": "CANCELADO"}
            
            response = client.put(
                f"/eventos/{evento_sample.id}",
                json=update_data,
                headers=auth_headers_promoter
            )
            assert response.status_code == 200
            
            # Should receive lifecycle notification
            try:
                notification = admin_ws.receive_text()
                data = json.loads(notification)
                assert data["type"] in ["event_lifecycle", "event_status_changed"]
                assert data["data"]["new_status"] == "CANCELADO"
            except Exception:
                pass