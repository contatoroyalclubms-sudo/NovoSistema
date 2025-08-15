from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Usuario, Empresa
from ..schemas import Usuario as UsuarioSchema, UsuarioCreate
from ..auth import obter_usuario_atual, verificar_permissao_admin, gerar_hash_senha, validar_cpf_basico

router = APIRouter()

@router.post("/", response_model=UsuarioSchema)
async def criar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Criar novo usuário (apenas admins)"""
    
    if not validar_cpf_basico(usuario.cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF inválido"
        )
    
    usuario_existente = db.query(Usuario).filter(Usuario.cpf == usuario.cpf).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )
    
    email_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if email_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    empresa = db.query(Empresa).filter(Empresa.id == usuario.empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    senha_hash = gerar_hash_senha(usuario.senha)
    usuario_data = usuario.dict()
    del usuario_data['senha']
    usuario_data['senha_hash'] = senha_hash
    
    db_usuario = Usuario(**usuario_data)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario

@router.get("/", response_model=List[UsuarioSchema])
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar usuários"""
    
    query = db.query(Usuario)
    
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Usuario.empresa_id == usuario_atual.empresa_id)
    elif empresa_id:
        query = query.filter(Usuario.empresa_id == empresa_id)
    
    usuarios = query.offset(skip).limit(limit).all()
    return usuarios

@router.get("/{usuario_id}", response_model=UsuarioSchema)
async def obter_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter dados de um usuário"""
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != usuario.empresa_id and 
        usuario_atual.id != usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioSchema)
async def atualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Atualizar dados do usuário (apenas admins)"""
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    if usuario_update.cpf != usuario.cpf:
        if not validar_cpf_basico(usuario_update.cpf):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF inválido"
            )
        
        usuario_existente = db.query(Usuario).filter(Usuario.cpf == usuario_update.cpf).first()
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
    
    if usuario_update.email != usuario.email:
        email_existente = db.query(Usuario).filter(Usuario.email == usuario_update.email).first()
        if email_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
    
    for field, value in usuario_update.dict(exclude={'senha'}).items():
        setattr(usuario, field, value)
    
    if usuario_update.senha:
        usuario.senha_hash = gerar_hash_senha(usuario_update.senha)
    
    db.commit()
    db.refresh(usuario)
    
    return usuario

@router.delete("/{usuario_id}")
async def desativar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Desativar usuário (soft delete)"""
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    usuario.ativo = False
    db.commit()
    
    return {"mensagem": "Usuário desativado com sucesso"}
