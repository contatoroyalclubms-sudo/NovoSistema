"""
Router de Autenticação - Login, Logout, Refresh Token
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models import Usuario, StatusUsuario, TipoUsuario
from app.schemas import (
    LoginRequest, Token, RefreshTokenRequest, 
    Usuario as UsuarioSchema, UsuarioCreate, UsuarioUpdate,
    UsuarioChangePassword, ResponseSuccess
)
from app.auth import (
    authenticate_user, create_token_pair, verify_refresh_token,
    get_current_user, get_current_active_user, get_current_admin_user,
    get_password_hash, verify_password, log_user_action
)
from app.middleware.rate_limit import login_rate_limit
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# =============================================================================
# ENDPOINTS DE AUTENTICAÇÃO
# =============================================================================

@router.post("/login", response_model=Token, summary="Login de usuário")
@login_rate_limit
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Realiza login do usuário com email e senha
    
    - **email**: Email do usuário
    - **senha**: Senha do usuário
    
    Retorna token JWT de acesso e refresh token.
    """
    try:
        # Autenticar usuário
        user = authenticate_user(db, login_data.email, login_data.senha)
        
        if not user:
            # Log da tentativa de login inválida
            logger.warning(f"Tentativa de login inválida: {login_data.email} de {request.client.host}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # Verificar se usuário está ativo
        if user.status != StatusUsuario.ATIVO:
            logger.warning(f"Tentativa de login com usuário inativo: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo. Entre em contato com o administrador."
            )
        
        # Criar tokens
        token_data = create_token_pair(user)
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=user,
            action="LOGIN",
            request=request,
            details=f"Login bem-sucedido de {request.client.host}"
        )
        
        # Atualizar último login
        user.ultimo_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"Login bem-sucedido: {user.email}")
        
        return {
            **token_data,
            "user": UsuarioSchema.from_orm(user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.post("/refresh", response_model=Token, summary="Renovar token de acesso")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Renova o token de acesso usando refresh token
    
    - **refresh_token**: Token de renovação válido
    
    Retorna novo par de tokens.
    """
    try:
        # Verificar refresh token através de um mock do verify_refresh_token
        from app.auth import verify_token, get_user_by_id
        
        # Verificar e decodificar refresh token
        token_data = verify_token(refresh_data.refresh_token, "refresh_token")
        
        # Buscar usuário
        user = get_user_by_id(db, token_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )
        
        # Verificar se usuário está ativo
        if user.status != StatusUsuario.ATIVO:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo"
            )
        
        # Criar novos tokens
        token_data = create_token_pair(user)
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=user,
            action="REFRESH_TOKEN",
            request=request,
            details="Token renovado"
        )
        
        logger.info(f"Token renovado para usuário: {user.email}")
        
        return {
            **token_data,
            "user": UsuarioSchema.from_orm(user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao renovar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de renovação inválido"
        )

@router.post("/logout", response_model=ResponseSuccess, summary="Logout de usuário")
async def logout(
    request: Request,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Realiza logout do usuário
    
    Invalida os tokens do usuário (implementação futura com blacklist).
    """
    try:
        # Log de auditoria
        log_user_action(
            db=db,
            user=current_user,
            action="LOGOUT",
            request=request,
            details=f"Logout de {request.client.host}"
        )
        
        # TODO: Implementar blacklist de tokens com Redis
        # Por enquanto, os tokens vão expirar naturalmente
        
        logger.info(f"Logout realizado: {current_user.email}")
        
        return ResponseSuccess(
            message="Logout realizado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro no logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

# =============================================================================
# ENDPOINTS DE PERFIL DO USUÁRIO
# =============================================================================

@router.get("/me", response_model=UsuarioSchema, summary="Obter dados do usuário atual")
async def get_current_user_profile(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Retorna dados do usuário autenticado
    """
    return UsuarioSchema.from_orm(current_user)

@router.put("/me", response_model=UsuarioSchema, summary="Atualizar perfil do usuário")
async def update_current_user_profile(
    user_update: UsuarioUpdate,
    request: Request,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza dados do perfil do usuário autenticado
    
    Não permite alterar tipo, status ou empresa.
    """
    try:
        # Dados anteriores para auditoria
        old_data = {
            "nome": current_user.nome,
            "email": current_user.email,
            "cpf": current_user.cpf,
            "telefone": current_user.telefone
        }
        
        # Atualizar apenas campos permitidos
        update_data = user_update.dict(exclude_unset=True)
        
        # Remover campos que não podem ser alterados pelo próprio usuário
        forbidden_fields = ["tipo", "status", "empresa_id"]
        for field in forbidden_fields:
            update_data.pop(field, None)
        
        # Verificar se email já existe (se estiver sendo alterado)
        if "email" in update_data and update_data["email"] != current_user.email:
            existing_user = db.query(Usuario).filter(
                Usuario.email == update_data["email"],
                Usuario.id != current_user.id
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já está em uso por outro usuário"
                )
        
        # Verificar se CPF já existe (se estiver sendo alterado)
        if "cpf" in update_data and update_data["cpf"] != current_user.cpf:
            existing_user = db.query(Usuario).filter(
                Usuario.cpf == update_data["cpf"],
                Usuario.id != current_user.id
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CPF já está em uso por outro usuário"
                )
        
        # Aplicar atualizações
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=current_user,
            action="UPDATE_PROFILE",
            table_name="usuarios",
            record_id=current_user.id,
            old_data=old_data,
            new_data=update_data,
            request=request,
            details="Atualização de perfil próprio"
        )
        
        logger.info(f"Perfil atualizado: {current_user.email}")
        
        return UsuarioSchema.from_orm(current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.put("/change-password", response_model=ResponseSuccess, summary="Alterar senha")
async def change_password(
    password_data: UsuarioChangePassword,
    request: Request,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Altera a senha do usuário autenticado
    
    - **senha_atual**: Senha atual do usuário
    - **senha_nova**: Nova senha (mínimo 6 caracteres)
    """
    try:
        # Verificar senha atual
        if not verify_password(password_data.senha_atual, current_user.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
        
        # Verificar se nova senha é diferente da atual
        if verify_password(password_data.senha_nova, current_user.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nova senha deve ser diferente da senha atual"
            )
        
        # Atualizar senha
        current_user.senha_hash = get_password_hash(password_data.senha_nova)
        db.commit()
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=current_user,
            action="CHANGE_PASSWORD",
            table_name="usuarios",
            record_id=current_user.id,
            request=request,
            details="Alteração de senha"
        )
        
        logger.info(f"Senha alterada: {current_user.email}")
        
        return ResponseSuccess(
            message="Senha alterada com sucesso"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

# =============================================================================
# ENDPOINTS ADMINISTRATIVOS
# =============================================================================

@router.post("/create-user", response_model=UsuarioSchema, summary="Criar novo usuário (Admin)")
async def create_user(
    user_data: UsuarioCreate,
    request: Request,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Cria novo usuário no sistema (apenas administradores)
    """
    try:
        # Verificar se email já existe
        existing_user = db.query(Usuario).filter(Usuario.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        
        # Verificar se CPF já existe (se fornecido)
        if user_data.cpf:
            existing_cpf = db.query(Usuario).filter(Usuario.cpf == user_data.cpf).first()
            if existing_cpf:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CPF já está em uso"
                )
        
        # Criar usuário
        db_user = Usuario(
            nome=user_data.nome,
            email=user_data.email,
            cpf=user_data.cpf,
            telefone=user_data.telefone,
            senha_hash=get_password_hash(user_data.senha),
            tipo=user_data.tipo,
            empresa_id=user_data.empresa_id,
            status=StatusUsuario.ATIVO,
            configuracoes=user_data.configuracoes
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=current_user,
            action="CREATE_USER",
            table_name="usuarios",
            record_id=db_user.id,
            new_data=user_data.dict(exclude={"senha"}),
            request=request,
            details=f"Criação de usuário {db_user.email}"
        )
        
        logger.info(f"Usuário criado por {current_user.email}: {db_user.email}")
        
        return UsuarioSchema.from_orm(db_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.get("/validate", response_model=ResponseSuccess, summary="Validar token")
async def validate_token(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Valida se o token de acesso ainda é válido
    """
    return ResponseSuccess(
        message="Token válido",
        data={
            "user_id": current_user.id,
            "email": current_user.email,
            "tipo": current_user.tipo.value,
            "empresa_id": current_user.empresa_id
        }
    )

# =============================================================================
# ENDPOINTS DE RECUPERAÇÃO DE SENHA (FUTURO)
# =============================================================================

@router.post("/forgot-password", response_model=ResponseSuccess, summary="Solicitar recuperação de senha")
async def forgot_password(
    request: Request,
    email: str,
    db: Session = Depends(get_db)
):
    """
    Solicita recuperação de senha por email
    
    TODO: Implementar envio de email com token de recuperação
    """
    try:
        # Verificar se usuário existe
        user = db.query(Usuario).filter(Usuario.email == email).first()
        
        # Por segurança, sempre retornar sucesso (não revelar se email existe)
        logger.info(f"Solicitação de recuperação de senha para: {email}")
        
        # TODO: Gerar token de recuperação e enviar por email
        # if user:
        #     # Gerar token de recuperação
        #     # Enviar email
        #     pass
        
        return ResponseSuccess(
            message="Se o email estiver cadastrado, você receberá instruções para recuperação da senha"
        )
        
    except Exception as e:
        logger.error(f"Erro na recuperação de senha: {e}")
        # Sempre retornar sucesso por segurança
        return ResponseSuccess(
            message="Se o email estiver cadastrado, você receberá instruções para recuperação da senha"
        )
