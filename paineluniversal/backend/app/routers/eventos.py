from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from ..database import get_db
from ..models import Evento, Usuario, PromoterEvento, Transacao, Checkin, Lista, TipoUsuario
from ..schemas import (
    Evento as EventoSchema, 
    EventoCreate, 
    EventoDetalhado, 
    EventoFiltros,
    PromoterEventoCreate,
    PromoterEventoResponse
)
from ..auth import obter_usuario_atual, verificar_permissao_admin

router = APIRouter()

@router.post("/", response_model=EventoSchema)
async def criar_evento(
    evento: EventoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Criar novo evento"""
    
    if usuario_atual.tipo.value not in ["admin", "promoter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas admins e promoters podem criar eventos"
        )
    
    if usuario_atual.tipo.value == "promoter" and usuario_atual.empresa_id != evento.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: você só pode criar eventos para sua empresa"
        )
    
    if evento.data_evento <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data do evento deve ser futura"
        )
    
    evento_data = evento.dict()
    evento_data['criador_id'] = usuario_atual.id
    
    db_evento = Evento(**evento_data)
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    
    return db_evento

@router.get("/", response_model=List[EventoSchema])
async def listar_eventos(
    skip: int = 0,
    limit: int = 100,
    empresa_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar eventos"""
    
    query = db.query(Evento)
    
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Evento.empresa_id == usuario_atual.empresa_id)
    elif empresa_id:
        query = query.filter(Evento.empresa_id == empresa_id)
    
    if status:
        query = query.filter(Evento.status == status)
    
    eventos = query.offset(skip).limit(limit).all()
    return eventos

@router.get("/buscar", response_model=List[EventoSchema])
async def buscar_eventos(
    nome: Optional[str] = None,
    status: Optional[str] = None,
    empresa_id: Optional[int] = None,
    local: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Busca avançada de eventos com filtros"""
    
    query = db.query(Evento)
    
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Evento.empresa_id == usuario_atual.empresa_id)
    elif empresa_id:
        query = query.filter(Evento.empresa_id == empresa_id)
    
    if nome:
        query = query.filter(Evento.nome.ilike(f"%{nome}%"))
    
    if status:
        status_lower = status.lower()
        query = query.filter(Evento.status == status_lower)
    
    if local:
        query = query.filter(Evento.local.ilike(f"%{local}%"))
    
    eventos = query.offset(skip).limit(limit).all()
    return eventos

@router.get("/{evento_id}", response_model=EventoSchema)
async def obter_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter dados de um evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    return evento

@router.put("/{evento_id}", response_model=EventoSchema)
async def atualizar_evento(
    evento_id: int,
    evento_update: EventoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar dados do evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    if evento_update.data_evento <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data do evento deve ser futura"
        )
    
    for field, value in evento_update.dict(exclude={'empresa_id'}).items():
        setattr(evento, field, value)
    
    db.commit()
    db.refresh(evento)
    
    return evento

@router.delete("/{evento_id}")
async def cancelar_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_admin)
):
    """Cancelar evento (apenas admins)"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    evento.status = "cancelado"
    db.commit()
    
    return {"mensagem": "Evento cancelado com sucesso"}

@router.get("/detalhado/{evento_id}", response_model=EventoDetalhado)
async def obter_evento_detalhado(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter evento com dados financeiros e promoters"""
    
    evento = db.query(Evento).options(
        joinedload(Evento.promoters).joinedload(PromoterEvento.promoter)
    ).filter(Evento.id == evento_id).first()
    
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    total_vendas = db.query(func.count(Transacao.id)).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == "aprovada"
    ).scalar() or 0
    
    receita_total = db.query(func.sum(Transacao.valor)).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == "aprovada"
    ).scalar() or Decimal('0.00')
    
    total_checkins = db.query(func.count(Checkin.id)).filter(
        Checkin.evento_id == evento_id
    ).scalar() or 0
    
    promoters_vinculados = []
    for promoter_evento in evento.promoters:
        if promoter_evento.ativo:
            promoters_vinculados.append({
                "id": promoter_evento.id,
                "promoter_id": promoter_evento.promoter_id,
                "nome": promoter_evento.promoter.nome,
                "meta_vendas": promoter_evento.meta_vendas,
                "vendas_realizadas": promoter_evento.vendas_realizadas,
                "comissao_percentual": float(promoter_evento.comissao_percentual or 0)
            })
    
    if receita_total == 0:
        status_financeiro = "sem_vendas"
    elif receita_total < 1000:
        status_financeiro = "baixo"
    elif receita_total < 5000:
        status_financeiro = "medio"
    else:
        status_financeiro = "alto"
    
    evento_dict = {
        "id": evento.id,
        "nome": evento.nome,
        "descricao": evento.descricao,
        "data_evento": evento.data_evento,
        "local": evento.local,
        "endereco": evento.endereco,
        "limite_idade": evento.limite_idade,
        "capacidade_maxima": evento.capacidade_maxima,
        "status": evento.status,
        "empresa_id": evento.empresa_id,
        "criador_id": evento.criador_id,
        "criado_em": evento.criado_em,
        "atualizado_em": evento.atualizado_em,
        "total_vendas": total_vendas,
        "receita_total": receita_total,
        "total_checkins": total_checkins,
        "promoters_vinculados": promoters_vinculados,
        "status_financeiro": status_financeiro
    }
    
    return EventoDetalhado(**evento_dict)


@router.post("/{evento_id}/promoters", response_model=PromoterEventoResponse)
async def vincular_promoter(
    evento_id: int,
    promoter_data: PromoterEventoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Vincular promoter ao evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    promoter = db.query(Usuario).filter(
        Usuario.id == promoter_data.promoter_id,
        Usuario.tipo == TipoUsuario.PROMOTER
    ).first()
    if not promoter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promoter não encontrado"
        )
    
    existing = db.query(PromoterEvento).filter(
        PromoterEvento.evento_id == evento_id,
        PromoterEvento.promoter_id == promoter_data.promoter_id,
        PromoterEvento.ativo == True
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Promoter já vinculado ao evento"
        )
    
    promoter_evento = PromoterEvento(
        evento_id=evento_id,
        promoter_id=promoter_data.promoter_id,
        meta_vendas=promoter_data.meta_vendas,
        comissao_percentual=promoter_data.comissao_percentual,
        ativo=True
    )
    
    db.add(promoter_evento)
    db.commit()
    db.refresh(promoter_evento)
    
    return PromoterEventoResponse(
        id=promoter_evento.id,
        promoter_id=promoter_evento.promoter_id,
        evento_id=promoter_evento.evento_id,
        meta_vendas=promoter_evento.meta_vendas,
        vendas_realizadas=promoter_evento.vendas_realizadas,
        comissao_percentual=promoter_evento.comissao_percentual,
        ativo=promoter_evento.ativo,
        promoter_nome=promoter.nome
    )

@router.delete("/{evento_id}/promoters/{promoter_id}")
async def desvincular_promoter(
    evento_id: int,
    promoter_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Desvincular promoter do evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    promoter_evento = db.query(PromoterEvento).filter(
        PromoterEvento.evento_id == evento_id,
        PromoterEvento.promoter_id == promoter_id,
        PromoterEvento.ativo == True
    ).first()
    
    if not promoter_evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vinculação não encontrada"
        )
    
    promoter_evento.ativo = False
    db.commit()
    
    return {"mensagem": "Promoter desvinculado com sucesso"}

@router.get("/{evento_id}/financeiro")
async def obter_status_financeiro(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter status financeiro detalhado do evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    vendas_por_lista = db.query(
        Lista.nome,
        Lista.tipo,
        Lista.preco,
        func.count(Transacao.id).label('vendas'),
        func.sum(Transacao.valor).label('receita')
    ).join(
        Transacao, Transacao.lista_id == Lista.id
    ).filter(
        Lista.evento_id == evento_id,
        Transacao.status == "aprovada"
    ).group_by(Lista.id, Lista.nome, Lista.tipo, Lista.preco).all()
    
    vendas_por_promoter = db.query(
        Usuario.nome,
        func.count(Transacao.id).label('vendas'),
        func.sum(Transacao.valor).label('receita')
    ).join(
        Lista, Lista.promoter_id == Usuario.id
    ).join(
        Transacao, Transacao.lista_id == Lista.id
    ).filter(
        Lista.evento_id == evento_id,
        Transacao.status == "aprovada"
    ).group_by(Usuario.id, Usuario.nome).all()
    
    total_receita = sum(row.receita or 0 for row in vendas_por_lista)
    total_vendas = sum(row.vendas for row in vendas_por_lista)
    
    return {
        "evento_id": evento_id,
        "total_receita": float(total_receita),
        "total_vendas": total_vendas,
        "vendas_por_lista": [
            {
                "nome": row.nome,
                "tipo": row.tipo.value,
                "preco": float(row.preco),
                "vendas": row.vendas,
                "receita": float(row.receita or 0)
            }
            for row in vendas_por_lista
        ],
        "vendas_por_promoter": [
            {
                "nome": row.nome,
                "vendas": row.vendas,
                "receita": float(row.receita or 0)
            }
            for row in vendas_por_promoter
        ]
    }

@router.get("/{evento_id}/export/csv")
async def exportar_evento_csv(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Exportar dados do evento em CSV"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    transacoes = db.query(Transacao).join(Lista).filter(
        Lista.evento_id == evento_id
    ).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'ID Transação', 'CPF Comprador', 'Nome Comprador', 'Email', 'Telefone',
        'Lista', 'Valor', 'Status', 'Data Compra', 'Promoter'
    ])
    
    for transacao in transacoes:
        lista = transacao.lista
        promoter_nome = lista.promoter.nome if lista.promoter else "N/A"
        
        writer.writerow([
            transacao.id,
            transacao.cpf_comprador,
            transacao.nome_comprador,
            transacao.email_comprador,
            transacao.telefone_comprador,
            lista.nome,
            float(transacao.valor),
            transacao.status.value,
            transacao.criado_em.strftime('%d/%m/%Y %H:%M'),
            promoter_nome
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=evento_{evento_id}_vendas.csv"}
    )

@router.get("/{evento_id}/export/pdf")
async def exportar_evento_pdf(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Exportar dados do evento em PDF"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Relatório do Evento: {evento.nome}")
    
    p.setFont("Helvetica", 12)
    y_position = height - 100
    
    info_evento = [
        f"Data: {evento.data_evento.strftime('%d/%m/%Y %H:%M')}",
        f"Local: {evento.local}",
        f"Endereço: {evento.endereco or 'N/A'}",
        f"Limite de Idade: {evento.limite_idade}+",
        f"Capacidade: {evento.capacidade_maxima}",
        f"Status: {evento.status.value}"
    ]
    
    for info in info_evento:
        p.drawString(50, y_position, info)
        y_position -= 20
    
    total_vendas = db.query(func.count(Transacao.id)).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == "aprovada"
    ).scalar() or 0
    
    receita_total = db.query(func.sum(Transacao.valor)).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == "aprovada"
    ).scalar() or Decimal('0.00')
    
    y_position -= 30
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "Resumo Financeiro")
    
    y_position -= 30
    p.setFont("Helvetica", 12)
    p.drawString(50, y_position, f"Total de Vendas: {total_vendas}")
    y_position -= 20
    p.drawString(50, y_position, f"Receita Total: R$ {float(receita_total):.2f}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=evento_{evento_id}_relatorio.pdf"}
    )
