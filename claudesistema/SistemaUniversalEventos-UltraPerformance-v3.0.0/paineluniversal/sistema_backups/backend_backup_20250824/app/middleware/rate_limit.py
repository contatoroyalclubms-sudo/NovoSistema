"""
Middleware para rate limiting e controle de requisições
"""

from functools import wraps
from typing import Dict
from fastapi import HTTPException, status, Request
from datetime import datetime, timedelta

# Cache em memória para rate limiting (em produção usar Redis)
rate_limit_cache: Dict[str, Dict] = {}

def get_client_ip(request: Request) -> str:
    """Obtém o IP real do cliente considerando proxies"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return str(request.client.host) if request.client else "unknown"

def check_rate_limit(
    identifier: str,
    max_requests: int = 5,
    time_window: int = 300,  # 5 minutos
    block_duration: int = 900  # 15 minutos
) -> Dict:
    """Verifica se o identificador excedeu o limite de requisições"""
    current_time = datetime.utcnow()
    
    if identifier not in rate_limit_cache:
        rate_limit_cache[identifier] = {
            "attempts": 1,
            "first_attempt": current_time,
            "reset_time": current_time + timedelta(seconds=time_window),
            "blocked_until": None
        }
        return {"allowed": True, "attempts": 1}
    
    data = rate_limit_cache[identifier]
    
    # Verificar se ainda está bloqueado
    if data.get("blocked_until") and current_time < data["blocked_until"]:
        return {
            "allowed": False,
            "reason": "IP bloqueado temporariamente",
            "blocked_until": data["blocked_until"]
        }
    
    # Verificar se a janela de tempo resetou
    if current_time >= data["reset_time"]:
        rate_limit_cache[identifier] = {
            "attempts": 1,
            "first_attempt": current_time,
            "reset_time": current_time + timedelta(seconds=time_window),
            "blocked_until": None
        }
        return {"allowed": True, "attempts": 1}
    
    # Incrementar tentativas
    data["attempts"] += 1
    
    # Verificar se excedeu o limite
    if data["attempts"] > max_requests:
        data["blocked_until"] = current_time + timedelta(seconds=block_duration)
        return {
            "allowed": False,
            "reason": f"Muitas tentativas. Bloqueado por {block_duration // 60} minutos",
            "blocked_until": data["blocked_until"]
        }
    
    return {"allowed": True, "attempts": data["attempts"]}

def login_rate_limit(func):
    """Decorator para rate limiting em login"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Encontrar o objeto Request nos argumentos
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            for value in kwargs.values():
                if isinstance(value, Request):
                    request = value
                    break
        
        if request:
            client_ip = get_client_ip(request)
            limit_info = check_rate_limit(
                identifier=f"login:{client_ip}",
                max_requests=5,
                time_window=300,
                block_duration=900
            )
            
            if not limit_info["allowed"]:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "message": limit_info.get("reason", "Muitas tentativas de login"),
                        "blocked_until": limit_info.get("blocked_until").isoformat() if limit_info.get("blocked_until") else None
                    }
                )
        
        return await func(*args, **kwargs)
    
    return wrapper
