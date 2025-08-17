"""
Módulo de autenticação e autorização
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models import Usuario, LogAuditoria, StatusUsuario, TipoUsuario
from app.core.config import settings

# Configuração de segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Cria token JWT de acesso"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access_token"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar token: {str(e)}"
        )

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Cria token JWT de refresh"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh_token"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar refresh token: {str(e)}"
        )

def verify_token(token: str, expected_type: str = "access_token") -> Dict[str, Any]:
    """Verifica e decodifica token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        token_type = payload.get("type")
        if token_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Tipo de token inválido. Esperado: {expected_type}"
            )
        
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )

def create_token_pair(user: Usuario) -> Dict[str, str]:
    """Cria par de tokens (access + refresh) para usuário"""
    token_data = {
        "sub": str(user.id),
        "user_id": str(user.id),
        "email": user.email,
        "tipo": user.tipo.value,
        "empresa_id": str(user.empresa_id) if user.empresa_id else None
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id), "user_id": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def authenticate_user(db: Session, email: str, password: str) -> Optional[Usuario]:
    """Autentica usuário com email e senha"""
    try:
        user = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.senha_hash):
            return None
        
        return user
        
    except Exception:
        return None

def get_user_by_id(db: Session, user_id: str) -> Optional[Usuario]:
    """Busca usuário por ID"""
    try:
        return db.query(Usuario).filter(Usuario.id == uuid.UUID(user_id)).first()
    except Exception:
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """Obtém usuário atual através do token"""
    token = credentials.credentials
    
    try:
        payload = verify_token(token, "access_token")
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido - usuário não encontrado"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )
    
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    
    return user

async def get_current_active_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Obtém usuário atual verificando se está ativo"""
    if current_user.status != StatusUsuario.ATIVO:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )
    
    return current_user

async def get_current_admin_user(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
    """Obtém usuário atual verificando se é administrador"""
    if current_user.tipo != TipoUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissões de administrador necessárias"
        )
    
    return current_user

def log_user_action(
    db: Session,
    user: Usuario,
    action: str,
    request: Request = None,
    table_name: Optional[str] = None,
    record_id: Optional[uuid.UUID] = None,
    old_data: Optional[Dict] = None,
    new_data: Optional[Dict] = None,
    details: Optional[str] = None
):
    """Registra ação do usuário para auditoria"""
    try:
        # Obter IP do cliente
        client_ip = "unknown"
        user_agent = "unknown"
        
        if request:
            client_ip = request.headers.get("X-Forwarded-For", 
                       request.headers.get("X-Real-IP", 
                       str(request.client.host) if request.client else "unknown"))
            user_agent = request.headers.get("User-Agent", "unknown")
        
        # Criar log de auditoria
        log_entry = LogAuditoria(
            usuario_id=user.id,
            acao=action,
            tabela=table_name,
            registro_id=record_id,
            dados_anteriores=old_data,
            dados_novos=new_data,
            ip_origem=client_ip,
            user_agent=user_agent,
            detalhes=details
        )
        
        db.add(log_entry)
        db.commit()
        
    except Exception as e:
        print(f"Erro ao registrar log de auditoria: {e}")
        db.rollback()

def verify_refresh_token(token: str, db: Session) -> Dict[str, Any]:
    """Verifica refresh token específico"""
    try:
        payload = verify_token(token, "refresh_token")
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )
        
        user = get_user_by_id(db, user_id)
        if not user or user.status != StatusUsuario.ATIVO:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inválido ou inativo"
            )
        
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Refresh token inválido: {str(e)}"
        )

