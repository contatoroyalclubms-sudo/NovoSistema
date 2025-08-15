from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
from datetime import datetime
import json
import asyncio
from sqlalchemy.orm import sessionmaker
from .database import engine
from datetime import datetime

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, evento_id: int):
        await websocket.accept()
        if evento_id not in self.active_connections:
            self.active_connections[evento_id] = []
        self.active_connections[evento_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, evento_id: int):
        if evento_id in self.active_connections:
            if websocket in self.active_connections[evento_id]:
                self.active_connections[evento_id].remove(websocket)
    
    async def broadcast_to_event(self, evento_id: int, message: dict):
        if evento_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[evento_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.active_connections[evento_id].remove(conn)

manager = ConnectionManager()

async def notify_stock_update(produto_id: int, evento_id: int, estoque_atual: int, produto_nome: str):
    await manager.broadcast_to_event(evento_id, {
        "type": "stock_update",
        "produto_id": produto_id,
        "estoque_atual": estoque_atual,
        "produto_nome": produto_nome,
        "timestamp": datetime.now().isoformat()
    })

async def notify_new_sale(evento_id: int, venda_data: dict):
    await manager.broadcast_to_event(evento_id, {
        "type": "new_sale",
        "venda": venda_data,
        "timestamp": datetime.now().isoformat()
    })

async def notify_cash_register_update(evento_id: int, caixa_data: dict):
    await manager.broadcast_to_event(evento_id, {
        "type": "cash_register_update",
        "caixa": caixa_data,
        "timestamp": datetime.now().isoformat()
    })

async def notify_checkin_update(evento_id: int, checkin_data: dict):
    await manager.broadcast_to_event(evento_id, {
        "type": "checkin_update",
        "data": checkin_data,
        "timestamp": datetime.now().isoformat()
    })

async def notify_dashboard_update(evento_id: int, dashboard_data: dict):
    await manager.broadcast_to_event(evento_id, {
        "type": "dashboard_update",
        "data": dashboard_data,
        "timestamp": datetime.now().isoformat()
    })
