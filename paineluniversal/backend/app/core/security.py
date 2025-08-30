"""
Módulo de segurança e autenticação
Sistema Universal de Gestão de Eventos - FASE 2

JWT, hashing de senhas, autenticação e autorização
"""

import secrets
from typing import Optional, List, Union, Dict, Any
from datetime import datetime, timedelta

# Imports condicionais para lidar com dependências não instaladas
try:
    from fastapi import Depends, HTTPException, status
    from fastapi.security import OAuth2PasswordBearer
    from sqlalchemy.orm import Session
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

from .config import settings

# ================================
# CONFIGURAÇÃO DE CRIPTOGRAFIA
# ================================

# Context para hash de senhas (fallback se passlib não estiver disponível)
if CRYPTO_AVAILABLE:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    # Implementação básica de fallback
    pwd_context = None

# OAuth2 scheme para tokens
if FASTAPI_AVAILABLE:
    oauth2_scheme = OAuth2PasswordBearer(
        tokenUrl="auth/login",
        scopes={
            "admin": "Acesso administrativo completo",
            "organizador": "Criação e gestão de eventos",
            "operador": "Operação de eventos específicos", 
            "participante": "Participação em eventos"
        }
    )
else:
    oauth2_scheme = None

# ================================
# FUNÇÕES DE HASH E VERIFICAÇÃO
# ================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha em texto plano corresponde ao hash
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash da senha armazenado
        
    Returns:
        True se a senha está correta, False caso contrário
    """
    if not CRYPTO_AVAILABLE or not pwd_context:
        # Fallback básico (não usar em produção)
        return plain_password == hashed_password
    
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Gera hash de uma senha
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha
    """
    if not CRYPTO_AVAILABLE or not pwd_context:
        # Fallback básico (não usar em produção)
        return f"plain_{password}"
    
    return pwd_context.hash(password)

def generate_password() -> str:
    """
    Gera uma senha aleatória segura
    
    Returns:
        Senha aleatória de 12 caracteres
    """
    return secrets.token_urlsafe(12)

# ================================
# FUNÇÕES JWT
# ================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT de acesso
    
    Args:
        data: Dados para incluir no payload do token
        expires_delta: Tempo de expiração personalizado
        
    Returns:
        Token JWT codificado
    """
    if not CRYPTO_AVAILABLE:
        # Fallback simples (não usar em produção)
        return f"token_{data.get('sub', 'unknown')}_{datetime.utcnow().timestamp()}"
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica e decodifica um token JWT
    
    Args:
        token: Token JWT para verificar
        
    Returns:
        Payload do token se válido, None caso contrário
    """
    if not CRYPTO_AVAILABLE:
        # Fallback simples (não usar em produção)
        if token.startswith("token_"):
            parts = token.split("_")
            if len(parts) >= 2:
                return {"sub": parts[1]}
        return None
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

def get_current_user_from_token(token: str):
    """
    Obtém usuário atual a partir do token
    
    Args:
        token: Token JWT
        
    Returns:
        Dados do usuário ou None
    """
    if not FASTAPI_AVAILABLE:
        return None
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
            
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        return {"id": user_id, "payload": payload}
        
    except Exception:
        raise credentials_exception

# ================================
# DEPENDÊNCIAS FASTAPI
# ================================

if FASTAPI_AVAILABLE:
    async def get_current_user(token: str = Depends(oauth2_scheme)):
        """
        Dependência FastAPI para obter usuário atual
        
        Args:
            token: Token JWT fornecido automaticamente pelo OAuth2PasswordBearer
            
        Returns:
            Usuário atual
        """
        # Esta função será sobrescrita quando os modelos estiverem disponíveis
        return get_current_user_from_token(token)

    def require_roles(allowed_roles: List[str]):
        """
        Decorator para exigir roles específicos
        
        Args:
            allowed_roles: Lista de roles permitidos
            
        Returns:
            Dependency function
        """
        def role_checker(current_user = Depends(get_current_user)):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuário não autenticado"
                )
            
            # Verificar se o usuário tem algum dos roles permitidos
            user_role = getattr(current_user, 'tipo_usuario', None)
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acesso negado. Roles necessários: {', '.join(allowed_roles)}"
                )
            
            return current_user
        
        return role_checker

    def require_permissions(permissions: List[str]):
        """
        Decorator para exigir permissões específicas
        
        Args:
            permissions: Lista de permissões necessárias
            
        Returns:
            Dependency function
        """
        def permission_checker(current_user = Depends(get_current_user)):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuário não autenticado"
                )
            
            # Implementar verificação de permissões quando o sistema estiver completo
            user_permissions = getattr(current_user, 'permissions', [])
            
            missing_permissions = [p for p in permissions if p not in user_permissions]
            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissões insuficientes. Necessário: {', '.join(missing_permissions)}"
                )
            
            return current_user
        
        return permission_checker

else:
    # Fallbacks quando FastAPI não está disponível
    def get_current_user():
        return None
    
    def require_roles(allowed_roles: List[str]):
        def role_checker():
            return None
        return role_checker
    
    def require_permissions(permissions: List[str]):
        def permission_checker():
            return None
        return permission_checker

# ================================
# UTILIDADES DE SEGURANÇA
# ================================

def generate_verification_code(length: int = 6) -> str:
    """
    Gera código de verificação numérico
    
    Args:
        length: Tamanho do código
        
    Returns:
        Código numérico como string
    """
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def generate_api_key() -> str:
    """
    Gera chave de API segura
    
    Returns:
        Chave de API única
    """
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    """
    Gera hash de uma chave de API
    
    Args:
        api_key: Chave de API em texto plano
        
    Returns:
        Hash da chave de API
    """
    return get_password_hash(api_key)

def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verifica uma chave de API contra seu hash
    
    Args:
        plain_key: Chave em texto plano
        hashed_key: Hash armazenado
        
    Returns:
        True se a chave está correta
    """
    return verify_password(plain_key, hashed_key)

def is_strong_password(password: str) -> tuple[bool, List[str]]:
    """
    Verifica se uma senha é forte
    
    Args:
        password: Senha para verificar
        
    Returns:
        Tupla (is_strong, errors)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Senha deve ter pelo menos 8 caracteres")
    
    if not any(c.isupper() for c in password):
        errors.append("Senha deve conter pelo menos uma letra maiúscula")
    
    if not any(c.islower() for c in password):
        errors.append("Senha deve conter pelo menos uma letra minúscula")
    
    if not any(c.isdigit() for c in password):
        errors.append("Senha deve conter pelo menos um número")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Senha deve conter pelo menos um caractere especial")
    
    return len(errors) == 0, errors

def sanitize_input(input_string: str) -> str:
    """
    Sanitiza entrada do usuário removendo caracteres perigosos
    
    Args:
        input_string: String de entrada
        
    Returns:
        String sanitizada
    """
    if not input_string:
        return ""
    
    # Remover caracteres potencialmente perigosos
    dangerous_chars = ["<", ">", "\"", "'", "&", "script", "javascript"]
    sanitized = input_string
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    
    return sanitized.strip()

# ================================
# PERMISSÕES E ROLES
# ================================

class Permissions:
    """Constantes para permissões do sistema"""
    
    # Eventos
    CREATE_EVENT = "create_event"
    EDIT_EVENT = "edit_event" 
    DELETE_EVENT = "delete_event"
    VIEW_EVENT = "view_event"
    MANAGE_EVENT_TEAM = "manage_event_team"
    
    # Usuários
    CREATE_USER = "create_user"
    EDIT_USER = "edit_user"
    DELETE_USER = "delete_user"
    VIEW_USER = "view_user"
    MANAGE_USER_ROLES = "manage_user_roles"
    
    # Check-in
    CHECKIN_PARTICIPANTS = "checkin_participants"
    VIEW_CHECKIN_DATA = "view_checkin_data"
    
    # PDV
    OPERATE_PDV = "operate_pdv"
    MANAGE_PRODUCTS = "manage_products"
    VIEW_SALES_DATA = "view_sales_data"
    
    # Relatórios
    VIEW_REPORTS = "view_reports"
    EXPORT_DATA = "export_data"
    
    # Sistema
    ADMIN_SYSTEM = "admin_system"
    MANAGE_SETTINGS = "manage_settings"

class Roles:
    """Definições de roles e suas permissões"""
    
    ADMIN = {
        "name": "admin",
        "description": "Administrador do sistema",
        "permissions": [
            Permissions.CREATE_EVENT,
            Permissions.EDIT_EVENT,
            Permissions.DELETE_EVENT,
            Permissions.VIEW_EVENT,
            Permissions.MANAGE_EVENT_TEAM,
            Permissions.CREATE_USER,
            Permissions.EDIT_USER,
            Permissions.DELETE_USER,
            Permissions.VIEW_USER,
            Permissions.MANAGE_USER_ROLES,
            Permissions.CHECKIN_PARTICIPANTS,
            Permissions.VIEW_CHECKIN_DATA,
            Permissions.OPERATE_PDV,
            Permissions.MANAGE_PRODUCTS,
            Permissions.VIEW_SALES_DATA,
            Permissions.VIEW_REPORTS,
            Permissions.EXPORT_DATA,
            Permissions.ADMIN_SYSTEM,
            Permissions.MANAGE_SETTINGS,
        ]
    }
    
    ORGANIZADOR = {
        "name": "organizador",
        "description": "Organizador de eventos",
        "permissions": [
            Permissions.CREATE_EVENT,
            Permissions.EDIT_EVENT,
            Permissions.VIEW_EVENT,
            Permissions.MANAGE_EVENT_TEAM,
            Permissions.VIEW_USER,
            Permissions.CHECKIN_PARTICIPANTS,
            Permissions.VIEW_CHECKIN_DATA,
            Permissions.OPERATE_PDV,
            Permissions.MANAGE_PRODUCTS,
            Permissions.VIEW_SALES_DATA,
            Permissions.VIEW_REPORTS,
            Permissions.EXPORT_DATA,
        ]
    }
    
    OPERADOR = {
        "name": "operador",
        "description": "Operador de eventos",
        "permissions": [
            Permissions.VIEW_EVENT,
            Permissions.CHECKIN_PARTICIPANTS,
            Permissions.VIEW_CHECKIN_DATA,
            Permissions.OPERATE_PDV,
            Permissions.VIEW_SALES_DATA,
        ]
    }
    
    PARTICIPANTE = {
        "name": "participante",
        "description": "Participante de eventos",
        "permissions": [
            Permissions.VIEW_EVENT,
        ]
    }

def get_role_permissions(role_name: str) -> List[str]:
    """
    Obtém permissões de um role
    
    Args:
        role_name: Nome do role
        
    Returns:
        Lista de permissões
    """
    role_mapping = {
        "admin": Roles.ADMIN,
        "organizador": Roles.ORGANIZADOR,
        "operador": Roles.OPERADOR,
        "participante": Roles.PARTICIPANTE,
    }
    
    role = role_mapping.get(role_name, Roles.PARTICIPANTE)
    return role["permissions"]

def user_has_permission(user_role: str, required_permission: str) -> bool:
    """
    Verifica se um usuário tem uma permissão específica
    
    Args:
        user_role: Role do usuário
        required_permission: Permissão necessária
        
    Returns:
        True se o usuário tem a permissão
    """
    user_permissions = get_role_permissions(user_role)
    return required_permission in user_permissions
