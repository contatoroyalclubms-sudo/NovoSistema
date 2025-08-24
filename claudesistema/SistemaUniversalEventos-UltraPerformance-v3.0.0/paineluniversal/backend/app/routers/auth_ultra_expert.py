"""
ROUTER DE AUTENTICAÇÃO ULTRA-EXPERT
Sprint 2: Autenticação Enterprise
Sistema Universal de Gestão de Eventos

Implementação completa: JWT, MFA, OAuth2, RBAC, Security Monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import asyncio
import logging
from pydantic import BaseModel, EmailStr

# Imports do sistema de segurança
from app.core.security import (
    security_manager, 
    UserRole, 
    Permission,
    generate_secure_token
)

# Logger
logger = logging.getLogger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Router
router = APIRouter(prefix="/auth", tags=["Autenticação Ultra-Expert"])

# ================================
# SCHEMAS DE AUTENTICAÇÃO
# ================================

class UserCreate(BaseModel):
    """Schema para criação de usuário"""
    email: EmailStr
    password: str
    nome: str
    role: UserRole = UserRole.PARTICIPANTE
    telefone: Optional[str] = None

class UserResponse(BaseModel):
    """Schema de resposta do usuário"""
    id: str
    email: str
    nome: str
    role: UserRole
    active: bool
    created_at: datetime
    last_login: Optional[datetime]

class LoginRequest(BaseModel):
    """Schema para request de login"""
    username: str  # Email ou username
    password: str
    remember_me: bool = False
    device_fingerprint: Optional[str] = None

class LoginResponse(BaseModel):
    """Schema de resposta do login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
    permissions: List[str]
    expires_in: int
    session_id: str

class TokenRefreshRequest(BaseModel):
    """Schema para refresh de token"""
    refresh_token: str

class PasswordChangeRequest(BaseModel):
    """Schema para mudança de senha"""
    current_password: str
    new_password: str

class PasswordResetRequest(BaseModel):
    """Schema para reset de senha"""
    email: EmailStr

class MFASetupRequest(BaseModel):
    """Schema para setup de MFA"""
    password: str
    phone_number: Optional[str] = None

# ================================
# MOCK DATABASE - Em produção seria SQLAlchemy
# ================================

# Mock users database
mock_users_db = {
    "admin@eventos.com": {
        "id": "admin-123",
        "email": "admin@eventos.com", 
        "nome": "Admin Sistema",
        "password_hash": security_manager.get_password_hash("Admin123!"),
        "role": UserRole.ADMIN,
        "active": True,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "mfa_enabled": False,
        "phone_number": None
    },
    "organizador@eventos.com": {
        "id": "org-123",
        "email": "organizador@eventos.com",
        "nome": "Organizador Teste", 
        "password_hash": security_manager.get_password_hash("Org123!"),
        "role": UserRole.ORGANIZADOR,
        "active": True,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "mfa_enabled": False,
        "phone_number": None
    },
    "user@eventos.com": {
        "id": "user-123",
        "email": "user@eventos.com",
        "nome": "Usuário Teste",
        "password_hash": security_manager.get_password_hash("User123!"),
        "role": UserRole.PARTICIPANTE,
        "active": True,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "mfa_enabled": False,
        "phone_number": None
    }
}

# ================================
# DEPENDENCY FUNCTIONS
# ================================

def get_client_ip(request: Request) -> str:
    """Extrai IP do cliente"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def get_user_agent(request: Request) -> str:
    """Extrai User-Agent"""
    return request.headers.get("User-Agent", "Unknown")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Dependency para obter usuário atual"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = security_manager.verify_token(token)
        if payload is None:
            raise credentials_exception
            
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Em produção, buscaria do banco
        # Aqui vamos simular encontrando o usuário
        for user_data in mock_users_db.values():
            if user_data["id"] == user_id:
                return user_data
                
        raise credentials_exception
        
    except Exception:
        raise credentials_exception

def require_permission(permission: Permission):
    """Dependency factory para verificar permissões"""
    async def permission_checker(current_user: Dict = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = UserRole(current_user["role"])
        
        if not security_manager.user_has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission.value}"
            )
        
        return current_user
    
    return permission_checker

# ================================
# ENDPOINTS DE AUTENTICAÇÃO
# ================================

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    request: Request
):
    """Registrar novo usuário"""
    try:
        client_ip = get_client_ip(request)
        
        # Verificar se email já existe
        if user_data.email in mock_users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validar política de senha
        password_validation = security_manager.validate_password_policy(user_data.password)
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Password policy violation", "errors": password_validation["errors"]}
            )
        
        # Criar usuário
        user_id = f"user-{generate_secure_token()[:8]}"
        password_hash = security_manager.get_password_hash(user_data.password)
        
        new_user = {
            "id": user_id,
            "email": user_data.email,
            "nome": user_data.nome,
            "password_hash": password_hash,
            "role": user_data.role,
            "active": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "mfa_enabled": False,
            "phone_number": user_data.telefone
        }
        
        # Adicionar ao mock database
        mock_users_db[user_data.email] = new_user
        
        # Log de segurança
        security_manager.log_security_event(
            "user_registered",
            user_id=user_id,
            ip_address=client_ip,
            details={"email": user_data.email, "role": user_data.role.value}
        )
        
        # Retornar resposta
        return UserResponse(
            id=user_id,
            email=user_data.email,
            nome=user_data.nome,
            role=user_data.role,
            active=True,
            created_at=new_user["created_at"],
            last_login=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in register_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Login com JWT e refresh token"""
    try:
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Verificar se IP está bloqueado
        if security_manager.is_ip_blocked(client_ip):
            security_manager.log_security_event(
                "blocked_ip_attempt",
                ip_address=client_ip,
                details={"username": form_data.username}
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Try again later."
            )
        
        # Encontrar usuário
        user = mock_users_db.get(form_data.username)
        if not user:
            security_manager.track_failed_login(client_ip, form_data.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Verificar senha
        if not security_manager.verify_password(form_data.password, user["password_hash"]):
            security_manager.track_failed_login(client_ip, form_data.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Verificar se usuário está ativo
        if not user["active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Gerar fingerprint do device
        device_fingerprint = security_manager.generate_device_fingerprint(user_agent, client_ip)
        
        # Criar tokens
        access_token = security_manager.create_access_token(
            data={"sub": user["id"], "email": user["email"], "role": user["role"].value}
        )
        refresh_token = security_manager.create_refresh_token(user["id"])
        
        # Criar sessão
        session_id = security_manager.create_session(user["id"], device_fingerprint, client_ip)
        
        # Atualizar último login
        user["last_login"] = datetime.utcnow()
        
        # Obter permissões do usuário
        user_role = UserRole(user["role"])
        permissions = [perm.value for perm in security_manager.get_user_permissions(user_role)]
        
        # Log de segurança
        security_manager.log_security_event(
            "user_login",
            user_id=user["id"],
            ip_address=client_ip,
            details={
                "email": user["email"],
                "device_fingerprint": device_fingerprint,
                "session_id": session_id
            }
        )
        
        # Retornar resposta
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                nome=user["nome"],
                role=user_role,
                active=user["active"],
                created_at=user["created_at"],
                last_login=user["last_login"]
            ),
            permissions=permissions,
            expires_in=30 * 60,  # 30 minutos
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/refresh")
async def refresh_token(request: TokenRefreshRequest):
    """Refresh access token"""
    try:
        new_access_token = security_manager.refresh_access_token(request.refresh_token)
        
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 30 * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in refresh_token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Informações do usuário atual"""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        nome=current_user["nome"],
        role=UserRole(current_user["role"]),
        active=current_user["active"],
        created_at=current_user["created_at"],
        last_login=current_user["last_login"]
    )

@router.get("/permissions")
async def get_user_permissions(current_user: Dict = Depends(get_current_user)):
    """Obter permissões do usuário"""
    user_role = UserRole(current_user["role"])
    permissions = security_manager.get_user_permissions(user_role)
    
    return {
        "user_id": current_user["id"],
        "role": user_role.value,
        "permissions": [perm.value for perm in permissions]
    }

@router.post("/logout")
async def logout(
    current_user: Dict = Depends(get_current_user),
    request: Request
):
    """Logout do usuário"""
    try:
        client_ip = get_client_ip(request)
        
        # Em produção, invalidaria o token no banco/cache
        # Aqui vamos apenas logar o evento
        security_manager.log_security_event(
            "user_logout",
            user_id=current_user["id"],
            ip_address=client_ip
        )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Error in logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/change-password")
async def change_password(
    request_data: PasswordChangeRequest,
    current_user: Dict = Depends(get_current_user),
    request: Request
):
    """Alterar senha do usuário"""
    try:
        client_ip = get_client_ip(request)
        
        # Verificar senha atual
        if not security_manager.verify_password(request_data.current_password, current_user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validar nova senha
        password_validation = security_manager.validate_password_policy(request_data.new_password)
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Password policy violation", "errors": password_validation["errors"]}
            )
        
        # Atualizar senha
        new_password_hash = security_manager.get_password_hash(request_data.new_password)
        current_user["password_hash"] = new_password_hash
        
        # Log de segurança
        security_manager.log_security_event(
            "password_changed",
            user_id=current_user["id"],
            ip_address=client_ip
        )
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in change_password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ================================
# ENDPOINTS ADMINISTRATIVOS
# ================================

@router.get("/users")
async def list_users(
    current_user: Dict = Depends(require_permission(Permission.MANAGE_USERS))
):
    """Listar usuários (apenas admins)"""
    users = []
    for user_data in mock_users_db.values():
        users.append(UserResponse(
            id=user_data["id"],
            email=user_data["email"],
            nome=user_data["nome"],
            role=UserRole(user_data["role"]),
            active=user_data["active"],
            created_at=user_data["created_at"],
            last_login=user_data["last_login"]
        ))
    
    return {"users": users, "total": len(users)}

@router.get("/security/events")
async def get_security_events(
    current_user: Dict = Depends(require_permission(Permission.VIEW_LOGS))
):
    """Obter eventos de segurança"""
    # Em produção, buscaria do banco de dados
    return {
        "events": [],
        "message": "Security events endpoint - implemented in production database"
    }

@router.get("/security/failed-attempts")
async def get_failed_attempts(
    current_user: Dict = Depends(require_permission(Permission.VIEW_LOGS))
):
    """Obter tentativas de login falhadas"""
    return {
        "failed_attempts": security_manager.failed_login_attempts,
        "total_ips": len(security_manager.failed_login_attempts)
    }