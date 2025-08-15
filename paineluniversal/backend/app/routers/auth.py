from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db, settings
from ..models import Usuario
from ..schemas import Token, LoginRequest, Usuario as UsuarioSchema
from ..auth import autenticar_usuario, criar_access_token, gerar_codigo_verificacao, obter_usuario_atual

router = APIRouter()
security = HTTPBearer()

codigos_verificacao = {}

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Autenticação multi-fator:
    1. Primeira etapa: CPF + senha
    2. Segunda etapa: código de verificação (simulado)
    """
    
    usuario = autenticar_usuario(login_data.cpf, login_data.senha, db)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CPF ou senha incorretos"
        )
    
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )
    
    if not login_data.codigo_verificacao:
        codigo = gerar_codigo_verificacao()
        codigos_verificacao[login_data.cpf] = codigo
        
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail=f"Código de verificação enviado. Use: {codigo}"
        )
    
    codigo_armazenado = codigos_verificacao.get(login_data.cpf)
    if not codigo_armazenado or codigo_armazenado != login_data.codigo_verificacao:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de verificação inválido"
        )
    
    del codigos_verificacao[login_data.cpf]
    
    usuario.ultimo_login = db.query(Usuario).filter(Usuario.id == usuario.id).first().criado_em
    db.commit()
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = criar_access_token(
        data={"sub": usuario.cpf}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": UsuarioSchema.from_orm(usuario)
    }

@router.get("/me", response_model=UsuarioSchema)
async def obter_perfil(usuario_atual: Usuario = Depends(obter_usuario_atual)):
    """Obter dados do usuário logado"""
    return usuario_atual

@router.post("/logout")
async def logout(usuario_atual: Usuario = Depends(obter_usuario_atual)):
    """Logout do usuário (invalidar token)"""
    return {"mensagem": "Logout realizado com sucesso"}

@router.post("/solicitar-codigo")
async def solicitar_codigo_verificacao(cpf: str, db: Session = Depends(get_db)):
    """Solicitar novo código de verificação"""
    usuario = db.query(Usuario).filter(Usuario.cpf == cpf).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    codigo = gerar_codigo_verificacao()
    codigos_verificacao[cpf] = codigo
    
    return {
        "mensagem": "Código de verificação enviado",
        "codigo_desenvolvimento": codigo  # Remover em produção
    }
