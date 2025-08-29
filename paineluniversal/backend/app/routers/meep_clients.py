from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
import uuid

from ..database import get_db
from ..models import MeepClient, ClientCategory, ClientBlockHistory, Usuario
from ..schemas import (
    MeepClientCreate, MeepClientUpdate, MeepClientResponse,
    ClientCategoryCreate, ClientCategoryResponse,
    ClientBlockHistoryResponse
)
from ..auth import obter_usuario_atual

router = APIRouter()

@router.get("/meep-clients", response_model=List[MeepClientResponse])
async def listar_clientes(
    nome: Optional[str] = Query(None),
    cpf: Optional[str] = Query(None),
    identificador: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    nome_na_lista: Optional[bool] = Query(None),
    somente_bloqueados: Optional[bool] = Query(None),
    somente_com_alertas: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    query = db.query(MeepClient).filter(MeepClient.empresa_id == usuario_atual.empresa_id)
    
    if nome:
        query = query.filter(MeepClient.nome.ilike(f"%{nome}%"))
    if cpf:
        query = query.filter(MeepClient.cpf.ilike(f"%{cpf}%"))
    if identificador:
        query = query.filter(MeepClient.identificador.ilike(f"%{identificador}%"))
    if categoria:
        query = query.filter(MeepClient.categoria_id == categoria)
    if nome_na_lista is not None:
        query = query.filter(MeepClient.nome_na_lista == nome_na_lista)
    if somente_bloqueados:
        query = query.filter(MeepClient.status == "bloqueado")
    if somente_com_alertas:
        query = query.filter(MeepClient.has_alert == True)
    
    clientes = query.order_by(MeepClient.nome).all()
    return clientes

@router.post("/meep-clients", response_model=MeepClientResponse)
async def criar_cliente(
    cliente_data: MeepClientCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    if cliente_data.cpf:
        existing_client = db.query(MeepClient).filter(
            and_(
                MeepClient.cpf == cliente_data.cpf,
                MeepClient.empresa_id == usuario_atual.empresa_id
            )
        ).first()
        if existing_client:
            raise HTTPException(status_code=400, detail="Cliente com este CPF já existe")
    
    cliente = MeepClient(
        id=str(uuid.uuid4()),
        **cliente_data.model_dump(),
        empresa_id=usuario_atual.empresa_id
    )
    
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    
    return cliente

@router.get("/meep-clients/{cliente_id}", response_model=MeepClientResponse)
async def obter_cliente(
    cliente_id: str,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    cliente = db.query(MeepClient).filter(
        and_(
            MeepClient.id == cliente_id,
            MeepClient.empresa_id == usuario_atual.empresa_id
        )
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return cliente

@router.put("/meep-clients/{cliente_id}", response_model=MeepClientResponse)
async def atualizar_cliente(
    cliente_id: str,
    cliente_data: MeepClientUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    cliente = db.query(MeepClient).filter(
        and_(
            MeepClient.id == cliente_id,
            MeepClient.empresa_id == usuario_atual.empresa_id
        )
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    for field, value in cliente_data.model_dump(exclude_unset=True).items():
        setattr(cliente, field, value)
    
    db.commit()
    db.refresh(cliente)
    
    return cliente

@router.delete("/meep-clients/{cliente_id}")
async def deletar_cliente(
    cliente_id: str,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    cliente = db.query(MeepClient).filter(
        and_(
            MeepClient.id == cliente_id,
            MeepClient.empresa_id == usuario_atual.empresa_id
        )
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    db.delete(cliente)
    db.commit()
    
    return {"message": "Cliente deletado com sucesso"}

@router.patch("/meep-clients/{cliente_id}/toggle-block")
async def alternar_bloqueio_cliente(
    cliente_id: str,
    reason: str = "",
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    cliente = db.query(MeepClient).filter(
        and_(
            MeepClient.id == cliente_id,
            MeepClient.empresa_id == usuario_atual.empresa_id
        )
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if cliente.status == "bloqueado":
        cliente.status = "ativo"
        
        history_entry = ClientBlockHistory(
            id=str(uuid.uuid4()),
            cliente_id=cliente_id,
            desbloqueado_por=usuario_atual.nome,
            data_desbloqueio=datetime.now(),
            razao_desbloqueio=reason or "Desbloqueio manual"
        )
    else:
        cliente.status = "bloqueado"
        
        history_entry = ClientBlockHistory(
            id=str(uuid.uuid4()),
            cliente_id=cliente_id,
            bloqueado_por=usuario_atual.nome,
            data_bloqueio=datetime.now(),
            razao_bloqueio=reason or "Bloqueio manual"
        )
    
    db.add(history_entry)
    db.commit()
    db.refresh(cliente)
    
    return {"message": f"Cliente {'desbloqueado' if cliente.status == 'ativo' else 'bloqueado'} com sucesso"}

@router.get("/meep-clients/{cliente_id}/block-history", response_model=List[ClientBlockHistoryResponse])
async def obter_historico_bloqueios(
    cliente_id: str,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    cliente = db.query(MeepClient).filter(
        and_(
            MeepClient.id == cliente_id,
            MeepClient.empresa_id == usuario_atual.empresa_id
        )
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    historico = db.query(ClientBlockHistory).filter(
        ClientBlockHistory.cliente_id == cliente_id
    ).order_by(ClientBlockHistory.criado_em.desc()).all()
    
    return historico

@router.get("/client-categories", response_model=List[ClientCategoryResponse])
async def listar_categorias(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    categorias = db.query(ClientCategory).filter(
        ClientCategory.empresa_id == usuario_atual.empresa_id
    ).order_by(ClientCategory.descricao).all()
    
    return categorias

@router.post("/client-categories", response_model=ClientCategoryResponse)
async def criar_categoria(
    categoria_data: ClientCategoryCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    categoria = ClientCategory(
        id=str(uuid.uuid4()),
        **categoria_data.model_dump(),
        empresa_id=usuario_atual.empresa_id
    )
    
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    
    return categoria

@router.delete("/client-categories/{categoria_id}")
async def deletar_categoria(
    categoria_id: str,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    categoria = db.query(ClientCategory).filter(
        and_(
            ClientCategory.id == categoria_id,
            ClientCategory.empresa_id == usuario_atual.empresa_id
        )
    ).first()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    clientes_com_categoria = db.query(MeepClient).filter(
        MeepClient.categoria_id == categoria_id
    ).count()
    
    if clientes_com_categoria > 0:
        raise HTTPException(
            status_code=400, 
            detail="Não é possível deletar categoria que possui clientes vinculados"
        )
    
    db.delete(categoria)
    db.commit()
    
    return {"message": "Categoria deletada com sucesso"}
