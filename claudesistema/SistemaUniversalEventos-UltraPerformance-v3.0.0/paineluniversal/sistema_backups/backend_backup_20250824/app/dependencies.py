"""
Dependências do FastAPI - Gerenciamento de autenticação e serviços
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import jwt
from datetime import datetime, timezone

from app.database import get_db
from app.models import Usuario
from app.core.config import settings
from app.services.openai_service import OpenAIService

# Security
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Obtém o usuário atual baseado no token JWT
    """
    try:
        # Decodificar o token
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Verificar se o token não expirou
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        if datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        
        # Obter dados do usuário
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Buscar usuário no banco
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )
        
        if not user.ativo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo"
            )
        
        return user
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

def get_admin_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Verifica se o usuário atual é administrador
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissões de administrador necessárias"
        )
    return current_user

# Cache para o serviço OpenAI (singleton)
_openai_service: Optional[OpenAIService] = None

def get_openai_service() -> OpenAIService:
    """
    Obtém instância singleton do serviço OpenAI
    """
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service

async def verificar_acesso_evento(
    evento_id: str,
    current_user: Usuario,
    db: Session,
    require_admin: bool = False
) -> bool:
    """
    Verifica se o usuário tem acesso ao evento
    """
    from app.models import Evento
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    # Admin sempre tem acesso
    if current_user.is_admin:
        return True
    
    # Se requer admin e não é admin
    if require_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissões de administrador necessárias"
        )
    
    # Verificar se é o criador do evento
    if evento.criado_por == current_user.id:
        return True
    
    # Verificar se é da mesma empresa (se aplicável)
    if hasattr(evento, 'empresa_id') and evento.empresa_id == current_user.empresa_id:
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Sem permissão para acessar este evento"
    )

async def log_user_action(
    user_id: str,
    action: str,
    resource_type: str,
    record_id: Optional[str] = None,
    old_data: Optional[dict] = None,
    new_data: Optional[dict] = None,
    db: Session = None
):
    """
    Registra ação do usuário para auditoria
    """
    try:
        # Implementar logging de auditoria
        # Por enquanto, apenas log básico
        import logging
        logger = logging.getLogger(__name__)
        
        log_data = {
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "record_id": record_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "old_data": old_data,
            "new_data": new_data
        }
        
        logger.info(f"User action logged: {log_data}")
        
    except Exception as e:
        # Não deve falhar a operação principal
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao registrar ação do usuário: {e}")
