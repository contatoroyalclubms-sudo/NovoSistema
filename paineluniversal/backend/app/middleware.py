from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import LogAuditoria
import json
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        method = request.method
        url = str(request.url)
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        if url.startswith("/api/"):
            db = SessionLocal()
            try:
                cpf_usuario = "anonimo"
                if hasattr(request.state, "usuario_atual"):
                    cpf_usuario = request.state.usuario_atual.cpf
                
                log = LogAuditoria(
                    cpf_usuario=cpf_usuario,
                    acao=f"{method} {url}",
                    ip_origem=client_ip,
                    user_agent=user_agent,
                    status="sucesso" if response.status_code < 400 else "erro",
                    detalhes=json.dumps({
                        "status_code": response.status_code,
                        "tempo_processamento": round(process_time, 3),
                        "metodo": method,
                        "url": url
                    })
                )
                
                db.add(log)
                db.commit()
            except Exception as e:
                print(f"Erro ao criar log de auditoria: {e}")
            finally:
                db.close()
        
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
