"""
Router para Sistema de Autenticação
Priority #7: Authentication & Authorization System - API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from ..auth_manager import auth_manager, UserRole, User

logger = logging.getLogger(__name__)

# Configuração de segurança
security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Models para requests
class RegisterRequest(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: Optional[str] = "user"

class LoginRequest(BaseModel):
    username: str
    password: str

class UpdateRoleRequest(BaseModel):
    user_id: int
    new_role: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# Dependency para obter usuário atual
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency para obter usuário autenticado"""
    token = credentials.credentials
    user = auth_manager.validate_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Dependency para verificar se é admin
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency que requer privilégios de admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilégios de administrador necessários"
        )
    return current_user

# Dependency para verificar se é admin ou manager
async def require_admin_or_manager(current_user: User = Depends(get_current_user)) -> User:
    """Dependency que requer privilégios de admin ou manager"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilégios de administrador ou gerente necessários"
        )
    return current_user

@router.get("/health")
async def health_check():
    """Health check do sistema de autenticação"""
    try:
        stats = auth_manager.get_auth_stats()
        return {
            "status": "healthy",
            "message": "Sistema de autenticação funcionando",
            "timestamp": datetime.now().isoformat(),
            "stats": stats
        }
    except Exception as e:
        logger.error(f"[AUTH_API] Erro no health check: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.post("/register")
async def register_user(request: RegisterRequest, req: Request):
    """Registra novo usuário"""
    try:
        # Validar role
        try:
            role_value = request.role.lower() if request.role else "user"
            role = UserRole(role_value)
        except ValueError:
            raise HTTPException(status_code=400, detail="Role inválida")
        
        # Obter informações da requisição
        ip_address = req.client.host if req.client else ""
        user_agent = req.headers.get("user-agent", "")
        
        success, message, user = auth_manager.register_user(
            username=request.username,
            email=request.email,
            full_name=request.full_name,
            password=request.password,
            role=role
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        logger.info(f"[AUTH_API] Usuário registrado: {request.username}")
        
        return {
            "success": True,
            "message": message,
            "user": user.to_dict() if user else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AUTH_API] Erro no registro: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.post("/login")
async def login_user(request: LoginRequest, req: Request):
    """Realiza login do usuário"""
    try:
        # Obter informações da requisição
        ip_address = req.client.host if req.client else ""
        user_agent = req.headers.get("user-agent", "")
        
        success, message, token, user = auth_manager.login(
            username=request.username,
            password=request.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not success:
            raise HTTPException(status_code=401, detail=message)
        
        logger.info(f"[AUTH_API] Login realizado: {request.username}")
        
        return {
            "success": True,
            "message": message,
            "access_token": token,
            "token_type": "bearer",
            "user": user.to_dict() if user else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AUTH_API] Erro no login: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.post("/logout")
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Realiza logout do usuário"""
    try:
        token = credentials.credentials
        success = auth_manager.logout(token)
        
        if not success:
            raise HTTPException(status_code=400, detail="Erro ao fazer logout")
        
        logger.info("[AUTH_API] Logout realizado")
        
        return {
            "success": True,
            "message": "Logout realizado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AUTH_API] Erro no logout: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Retorna informações do usuário atual"""
    try:
        return {
            "success": True,
            "user": current_user.to_dict()
        }
        
    except Exception as e:
        logger.error(f"[AUTH_API] Erro ao obter usuário atual: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/validate")
async def validate_token(current_user: User = Depends(get_current_user)):
    """Valida token atual"""
    try:
        return {
            "success": True,
            "valid": True,
            "user": current_user.to_dict(),
            "message": "Token válido"
        }
        
    except Exception as e:
        logger.error(f"[AUTH_API] Erro na validação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/users")
async def list_users(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_admin_or_manager)
):
    """Lista usuários (requer privilégios)"""
    try:
        users = auth_manager.list_users(limit=limit, offset=offset)
        
        return {
            "success": True,
            "users": [user.to_dict() for user in users],
            "total": len(users),
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AUTH_API] Erro ao listar usuários: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/dashboard")
async def get_auth_dashboard(current_user: User = Depends(require_admin_or_manager)):
    """Dashboard do sistema de autenticação"""
    try:
        stats = auth_manager.get_auth_stats()
        
        # Informações adicionais para o dashboard
        import sqlite3
        with sqlite3.connect(auth_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Usuários criados nas últimas 24h
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE created_at > datetime('now', '-1 day')
            """)
            new_users_24h = cursor.fetchone()[0]
            
            # Últimos logins
            cursor.execute("""
                SELECT u.username, u.last_login 
                FROM users u 
                WHERE u.last_login IS NOT NULL 
                ORDER BY u.last_login DESC 
                LIMIT 10
            """)
            recent_logins = [
                {"username": row[0], "last_login": row[1]} 
                for row in cursor.fetchall()
            ]
        
        dashboard_data = {
            **stats,
            "new_users_24h": new_users_24h,
            "recent_logins": recent_logins,
            "system_status": "operational",
            "security_level": "high" if stats.get("success_rate", 0) > 80 else "medium"
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AUTH_API] Erro no dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
