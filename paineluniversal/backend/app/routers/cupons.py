from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import Lista, Evento
from ..schemas import CupomCreate, CupomResponse
from ..auth import verificar_permissao_promoter

router = APIRouter(prefix="/cupons", tags=["Cupons"])

@router.post("/", response_model=CupomResponse, summary="Criar cupom de desconto")
async def criar_cupom(
    cupom_data: CupomCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(verificar_permissao_promoter)
):
    """
    Criar cupom de desconto para lista específica.
    
    **Permissões necessárias:** Promoter ou Admin
    """
    
    lista = db.query(Lista).filter(Lista.id == cupom_data.lista_id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    evento = db.query(Evento).filter(Evento.id == lista.evento_id).first()
    if evento.empresa_id != usuario_atual.empresa_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    cupom_existente = db.query(Lista).filter(Lista.codigo_cupom == cupom_data.codigo).first()
    if cupom_existente:
        raise HTTPException(status_code=400, detail="Código de cupom já existe")
    
    lista.codigo_cupom = cupom_data.codigo
    lista.desconto_percentual = cupom_data.desconto_percentual
    lista.desconto_valor = cupom_data.desconto_valor
    lista.data_inicio_desconto = cupom_data.data_inicio
    lista.data_fim_desconto = cupom_data.data_fim
    lista.limite_uso_cupom = cupom_data.limite_uso
    
    db.commit()
    db.refresh(lista)
    
    return CupomResponse(
        id=lista.id,
        codigo=lista.codigo_cupom,
        desconto_percentual=lista.desconto_percentual,
        desconto_valor=lista.desconto_valor,
        lista_nome=lista.nome,
        evento_nome=evento.nome
    )

@router.post("/validar/{codigo}", summary="Validar cupom de desconto")
async def validar_cupom(
    codigo: str,
    db: Session = Depends(get_db)
):
    """
    Validar cupom de desconto e retornar informações de desconto.
    
    **Uso público:** Endpoint pode ser usado sem autenticação para validação de cupons.
    """
    
    lista = db.query(Lista).filter(Lista.codigo_cupom == codigo).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")
    
    agora = datetime.now()
    if lista.data_inicio_desconto and agora < lista.data_inicio_desconto:
        raise HTTPException(status_code=400, detail="Cupom ainda não está ativo")
    
    if lista.data_fim_desconto and agora > lista.data_fim_desconto:
        raise HTTPException(status_code=400, detail="Cupom expirado")
    
    if lista.limite_uso_cupom and lista.usos_cupom >= lista.limite_uso_cupom:
        raise HTTPException(status_code=400, detail="Limite de uso do cupom atingido")
    
    return {
        "valido": True,
        "desconto_percentual": float(lista.desconto_percentual or 0),
        "desconto_valor": float(lista.desconto_valor or 0),
        "lista_nome": lista.nome,
        "preco_original": float(lista.preco)
    }

@router.post("/usar/{codigo}", summary="Usar cupom de desconto")
async def usar_cupom(
    codigo: str,
    db: Session = Depends(get_db)
):
    """
    Marcar cupom como usado (incrementar contador de uso).
    
    **Uso:** Chamar após confirmação de compra com cupom.
    """
    
    lista = db.query(Lista).filter(Lista.codigo_cupom == codigo).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")
    
    if lista.limite_uso_cupom and lista.usos_cupom >= lista.limite_uso_cupom:
        raise HTTPException(status_code=400, detail="Limite de uso do cupom atingido")
    
    lista.usos_cupom = (lista.usos_cupom or 0) + 1
    db.commit()
    
    return {
        "message": "Cupom usado com sucesso",
        "usos_restantes": (lista.limite_uso_cupom - lista.usos_cupom) if lista.limite_uso_cupom else None
    }

@router.get("/evento/{evento_id}", response_model=List[CupomResponse], summary="Listar cupons do evento")
async def listar_cupons_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(verificar_permissao_promoter)
):
    """
    Listar todos os cupons de um evento específico.
    
    **Permissões necessárias:** Promoter ou Admin
    """
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if evento.empresa_id != usuario_atual.empresa_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    listas_com_cupom = db.query(Lista).filter(
        Lista.evento_id == evento_id,
        Lista.codigo_cupom.isnot(None)
    ).all()
    
    cupons = []
    for lista in listas_com_cupom:
        cupons.append(CupomResponse(
            id=lista.id,
            codigo=lista.codigo_cupom,
            desconto_percentual=lista.desconto_percentual,
            desconto_valor=lista.desconto_valor,
            lista_nome=lista.nome,
            evento_nome=evento.nome
        ))
    
    return cupons
