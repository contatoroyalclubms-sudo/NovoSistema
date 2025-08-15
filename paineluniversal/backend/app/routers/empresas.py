from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Empresa, Usuario
from ..schemas import Empresa as EmpresaSchema, EmpresaCreate
from ..auth import obter_usuario_atual, verificar_permissao_admin

router = APIRouter()

@router.post("/", response_model=EmpresaSchema)
async def criar_empresa(
    empresa: EmpresaCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Criar nova empresa (apenas admins)"""
    
    empresa_existente = db.query(Empresa).filter(Empresa.cnpj == empresa.cnpj).first()
    if empresa_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já cadastrado"
        )
    
    db_empresa = Empresa(**empresa.dict())
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    
    return db_empresa

@router.get("/", response_model=List[EmpresaSchema])
async def listar_empresas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Listar todas as empresas (apenas admins)"""
    empresas = db.query(Empresa).offset(skip).limit(limit).all()
    return empresas

@router.get("/{empresa_id}", response_model=EmpresaSchema)
async def obter_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter dados de uma empresa"""
    
    if usuario_atual.tipo.value != "admin" and usuario_atual.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    return empresa

@router.put("/{empresa_id}", response_model=EmpresaSchema)
async def atualizar_empresa(
    empresa_id: int,
    empresa_update: EmpresaCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Atualizar dados da empresa (apenas admins)"""
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    if empresa_update.cnpj != empresa.cnpj:
        empresa_existente = db.query(Empresa).filter(Empresa.cnpj == empresa_update.cnpj).first()
        if empresa_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ já cadastrado"
            )
    
    for field, value in empresa_update.dict().items():
        setattr(empresa, field, value)
    
    db.commit()
    db.refresh(empresa)
    
    return empresa

@router.delete("/{empresa_id}")
async def desativar_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Desativar empresa (soft delete)"""
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    empresa.ativa = False
    db.commit()
    
    return {"mensagem": "Empresa desativada com sucesso"}
