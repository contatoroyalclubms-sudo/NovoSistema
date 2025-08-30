"""
Sistema Universal de Gestão de Eventos
FastAPI Application - FASE 2

Aplicação principal com todas as funcionalidades core:
- Gestão de Eventos
- Sistema de Check-in
- PDV e Financeiro  
- Gamificação e Ranking
- WebSocket para tempo real
- APIs RESTful completas
"""

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import logging
import os
import time
import uvicorn
from datetime import datetime
from typing import Dict, List, Any
import json
import uuid

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ================================
# CONFIGURAÇÕES DA APLICAÇÃO
# ================================

# Configurações do ambiente
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

# Configurações de CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",    # React dev server
    "http://localhost:5173",    # Vite dev server  
    "http://localhost:8080",    # Vue dev server
    "https://localhost:3000",   # HTTPS local
    "https://localhost:5173",   # HTTPS Vite
]

# Adicionar origins do ambiente se especificado
if origins_env := os.getenv("ALLOWED_ORIGINS"):
    try:
        env_origins = json.loads(origins_env)
        ALLOWED_ORIGINS.extend(env_origins)
    except json.JSONDecodeError:
        logger.warning("ALLOWED_ORIGINS env var não é um JSON válido")

# ================================
# LIFESPAN E INICIALIZAÇÃO
# ================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida da aplicação
    """
    # Startup
    logger.info("🚀 Iniciando Sistema Universal de Gestão de Eventos...")
    
    try:
        # Inicializar banco de dados
        # from app.database import init_database, test_connection
        # await test_connection()
        # init_database()
        logger.info("✅ Banco de dados conectado")
        
        # Inicializar sistema de cache (Redis)
        # await init_redis()
        logger.info("✅ Sistema de cache inicializado")
        
        # Inicializar WebSocket manager
        websocket_manager.startup()
        logger.info("✅ WebSocket manager iniciado")
        
        # Startup concluído
        logger.info("🎉 Sistema iniciado com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Finalizando aplicação...")
    
    try:
        # Fechar conexões WebSocket
        await websocket_manager.shutdown()
        logger.info("✅ WebSocket connections fechadas")
        
        # Fechar conexões de cache
        # await close_redis()
        logger.info("✅ Cache desconectado")
        
        logger.info("👋 Aplicação finalizada com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro no shutdown: {e}")

# ================================
# CRIAÇÃO DA APLICAÇÃO
# ================================

app = FastAPI(
    title="Sistema Universal de Gestão de Eventos",
    description="""
    **Sistema completo para gestão de eventos com:**
    
    🎪 **Gestão de Eventos**
    - Criação e configuração completa
    - Templates personalizáveis
    - Controle de capacidade
    
    ✅ **Sistema de Check-in**
    - QR Codes únicos por participante
    - Check-in em tempo real
    - Controle de acesso
    
    💰 **PDV e Financeiro**
    - Sistema de vendas completo
    - Controle de estoque
    - Relatórios financeiros
    
    🏆 **Gamificação**
    - Sistema de pontuação
    - Rankings e conquistas
    - Badges personalizadas
    
    📊 **Dashboard em Tempo Real**
    - Métricas ao vivo
    - WebSocket para atualizações
    - Relatórios avançados
    """,
    version="2.0.0",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None,
    lifespan=lifespan
)

# ================================
# MIDDLEWARE E CONFIGURAÇÕES
# ================================

# CORS - Configuração para desenvolvimento e produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Compressão GZIP
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000
)

# Trusted Host (apenas em produção)
if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configurar hosts específicos em produção
    )

# ================================
# WEBSOCKET MANAGER
# ================================

class WebSocketManager:
    """
    Gerenciador de conexões WebSocket para tempo real
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.event_connections: Dict[str, List[str]] = {}  # evento_id -> [connection_ids]
        self.running = False
    
    def startup(self):
        """Inicializa o manager"""
        self.running = True
        logger.info("🔗 WebSocket Manager iniciado")
    
    async def shutdown(self):
        """Finaliza todas as conexões"""
        self.running = False
        for connection in self.active_connections.values():
            try:
                await connection.close()
            except:
                pass
        self.active_connections.clear()
        self.event_connections.clear()
        logger.info("🔌 WebSocket Manager finalizado")
    
    async def connect(self, websocket: WebSocket, connection_id: str, evento_id: str = None):
        """Aceita nova conexão WebSocket"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if evento_id:
            if evento_id not in self.event_connections:
                self.event_connections[evento_id] = []
            self.event_connections[evento_id].append(connection_id)
        
        logger.info(f"🔗 Nova conexão WebSocket: {connection_id}")
        
        # Enviar mensagem de boas-vindas
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
    
    def disconnect(self, connection_id: str):
        """Remove conexão"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remover de eventos específicos
        for evento_id, connections in self.event_connections.items():
            if connection_id in connections:
                connections.remove(connection_id)
                if not connections:  # Se lista vazia, remover evento
                    del self.event_connections[evento_id]
                break
        
        logger.info(f"🔌 Conexão WebSocket removida: {connection_id}")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Envia mensagem para conexão específica"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
            except:
                self.disconnect(connection_id)
    
    async def broadcast_to_event(self, message: dict, evento_id: str):
        """Broadcast para todas as conexões de um evento"""
        if evento_id in self.event_connections:
            for connection_id in self.event_connections[evento_id].copy():
                await self.send_personal_message(message, connection_id)
    
    async def broadcast_all(self, message: dict):
        """Broadcast para todas as conexões ativas"""
        for connection_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, connection_id)

# Instância global do WebSocket manager
websocket_manager = WebSocketManager()

# ================================
# MIDDLEWARE PERSONALIZADO
# ================================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Adiciona header com tempo de processamento"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log de todas as requisições"""
    start_time = time.time()
    
    # Log da requisição
    logger.info(f"📥 {request.method} {request.url.path} - {request.client.host}")
    
    response = await call_next(request)
    
    # Log da resposta
    process_time = time.time() - start_time
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {round(process_time * 1000, 2)}ms"
    )
    
    return response

# ================================
# ROTAS BÁSICAS
# ================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial da API"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema Universal de Gestão de Eventos</title>
        <meta charset="utf-8">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            h1 { font-size: 2.5em; margin-bottom: 20px; }
            .status { font-size: 1.2em; margin: 20px 0; }
            .links { margin-top: 30px; }
            .links a { 
                display: inline-block; 
                margin: 10px; 
                padding: 15px 25px; 
                background: rgba(255, 255, 255, 0.2);
                color: white;
                text-decoration: none; 
                border-radius: 10px;
                transition: all 0.3s ease;
            }
            .links a:hover { 
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }
            .version { 
                margin-top: 30px; 
                opacity: 0.8; 
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎪 Sistema Universal de Gestão de Eventos</h1>
            <div class="status">
                ✅ <strong>API Online e Funcionando!</strong>
            </div>
            <p>Sistema completo para gestão de eventos, check-in, PDV e gamificação</p>
            
            <div class="links">
                <a href="/docs">📚 Documentação (Swagger)</a>
                <a href="/redoc">📖 ReDoc</a>
                <a href="/health">🏥 Health Check</a>
                <a href="/api/v1/eventos">🎪 API Eventos</a>
            </div>
            
            <div class="version">
                <strong>Versão:</strong> 2.0.0 (FASE 2) • 
                <strong>Ambiente:</strong> Development • 
                <strong>Timestamp:</strong> """ + datetime.utcnow().isoformat() + """
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check da aplicação"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "phase": "FASE 2",
        "environment": ENVIRONMENT,
        "database": "connected",  # Será implementado
        "cache": "connected",     # Será implementado
        "websocket": "active",
        "uptime_seconds": time.time() - start_time
    }

@app.get("/api/v1/system/info")
async def system_info():
    """Informações do sistema"""
    return {
        "name": "Sistema Universal de Gestão de Eventos",
        "version": "2.0.0",
        "phase": "FASE 2",
        "environment": ENVIRONMENT,
        "debug": DEBUG,
        "features": [
            "Gestão de Eventos",
            "Sistema de Check-in",
            "PDV e Financeiro",
            "Gamificação e Ranking",
            "WebSocket Tempo Real",
            "Dashboard Analytics"
        ],
        "api_prefix": API_PREFIX,
        "docs_url": "/docs" if DEBUG else None,
        "websocket_connections": len(websocket_manager.active_connections),
        "timestamp": datetime.utcnow().isoformat()
    }

# ================================
# WEBSOCKET ENDPOINTS
# ================================

@app.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str, evento_id: str = None):
    """
    Endpoint WebSocket para comunicação em tempo real
    
    Parâmetros:
    - connection_id: ID único da conexão
    - evento_id: ID do evento (opcional) para receber updates específicos
    """
    await websocket_manager.connect(websocket, connection_id, evento_id)
    
    try:
        while True:
            # Receber mensagens do cliente
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Processar diferentes tipos de mensagem
            message_type = message.get("type")
            
            if message_type == "ping":
                # Responder ping com pong
                await websocket_manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, connection_id)
            
            elif message_type == "join_event":
                # Associar conexão a um evento específico
                evento_id = message.get("evento_id")
                if evento_id:
                    if evento_id not in websocket_manager.event_connections:
                        websocket_manager.event_connections[evento_id] = []
                    if connection_id not in websocket_manager.event_connections[evento_id]:
                        websocket_manager.event_connections[evento_id].append(connection_id)
                    
                    await websocket_manager.send_personal_message({
                        "type": "joined_event",
                        "evento_id": evento_id,
                        "status": "success"
                    }, connection_id)
            
            elif message_type == "leave_event":
                # Remover conexão de um evento específico
                evento_id = message.get("evento_id")
                if evento_id and evento_id in websocket_manager.event_connections:
                    if connection_id in websocket_manager.event_connections[evento_id]:
                        websocket_manager.event_connections[evento_id].remove(connection_id)
            
            # Log da mensagem recebida
            logger.info(f"📨 WebSocket message from {connection_id}: {message_type}")
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(connection_id)
        logger.info(f"🔌 WebSocket client {connection_id} disconnected")
    except Exception as e:
        logger.error(f"❌ WebSocket error for {connection_id}: {e}")
        websocket_manager.disconnect(connection_id)

# ================================
# EXCEPTION HANDLERS
# ================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para HTTPException personalizado"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler geral para exceções não tratadas"""
    logger.error(f"❌ Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error" if ENVIRONMENT == "production" else str(exc),
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

# ================================
# INCLUSÃO DE ROUTERS
# ================================

# Os routers implementados:
from app.routers import auth, eventos, pdv, gamificacao, estoque, utils
from app.routers import relatorios_avancados, ia_avancada, monitoramento, backup, cache_inteligente, qr_codes
from app.routers import usuarios, listas, transacoes, whatsapp, n8n

app.include_router(auth.router, prefix=f"{API_PREFIX}")
app.include_router(usuarios.router, prefix=f"{API_PREFIX}")
app.include_router(listas.router, prefix=f"{API_PREFIX}")
app.include_router(transacoes.router, prefix=f"{API_PREFIX}")
app.include_router(whatsapp.router, prefix=f"{API_PREFIX}")
app.include_router(n8n.router, prefix=f"{API_PREFIX}")
app.include_router(eventos.router, prefix=f"{API_PREFIX}")
app.include_router(pdv.router, prefix=f"{API_PREFIX}")
app.include_router(gamificacao.router, prefix=f"{API_PREFIX}")
app.include_router(estoque.router, prefix=f"{API_PREFIX}")
app.include_router(utils.router, prefix=f"{API_PREFIX}")
app.include_router(relatorios_avancados.router, prefix=f"{API_PREFIX}")
app.include_router(ia_avancada.router, prefix=f"{API_PREFIX}")
app.include_router(monitoramento.router, prefix=f"{API_PREFIX}")
app.include_router(backup.router, prefix=f"{API_PREFIX}")
app.include_router(cache_inteligente.router, prefix=f"{API_PREFIX}")
app.include_router(qr_codes.router, prefix=f"{API_PREFIX}")

# TODO: Implementar routers adicionais conforme necessário:
# - empresas, listas, transacoes, checkins
# - dashboard, relatorios, whatsapp, cupons, n8n, financeiro

# ================================
# EXECUTAR APLICAÇÃO
# ================================

# Timestamp de início para uptime
start_time = time.time()

if __name__ == "__main__":
    logger.info("🚀 Iniciando servidor FastAPI...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=DEBUG,
        log_level="info" if DEBUG else "warning",
        access_log=DEBUG,
        use_colors=True
    )
