from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..models import Checkin, Transacao, Evento, Usuario, Comanda
from ..schemas import Checkin as CheckinSchema, CheckinCreate
from ..auth import obter_usuario_atual, validar_cpf_basico
from ..websocket import manager
from ..services.whatsapp_service import whatsapp_service

router = APIRouter()

@router.post("/", response_model=CheckinSchema)
async def realizar_checkin(
    checkin: CheckinCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Realizar check-in no evento"""
    
    if not validar_cpf_basico(checkin.cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF inválido"
        )
    
    evento = db.query(Evento).filter(Evento.id == checkin.evento_id).first()
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
    
    checkin_existente = db.query(Checkin).filter(
        Checkin.cpf == checkin.cpf,
        Checkin.evento_id == checkin.evento_id
    ).first()
    
    if checkin_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in já realizado para este CPF neste evento"
        )
    
    transacao = db.query(Transacao).filter(
        Transacao.cpf_comprador == checkin.cpf,
        Transacao.evento_id == checkin.evento_id,
        Transacao.status == "aprovada"
    ).first()
    
    if not transacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma transação aprovada encontrada para este CPF neste evento"
        )
    
    cpf_limpo = checkin.cpf.replace(".", "").replace("-", "")
    if checkin.validacao_cpf != cpf_limpo[:3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validação de CPF incorreta"
        )
    
    checkin_data = checkin.dict()
    checkin_data['nome'] = transacao.nome_comprador
    checkin_data['usuario_id'] = usuario_atual.id
    checkin_data['transacao_id'] = transacao.id
    
    db_checkin = Checkin(**checkin_data)
    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)
    
    return db_checkin

@router.get("/evento/{evento_id}", response_model=List[CheckinSchema])
async def listar_checkins_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar check-ins de um evento"""
    
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
    
    checkins = db.query(Checkin).filter(Checkin.evento_id == evento_id).all()
    return checkins

@router.get("/cpf/{cpf}")
async def verificar_checkin_cpf(
    cpf: str,
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Verificar se CPF já fez check-in no evento"""
    
    if not validar_cpf_basico(cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF inválido"
        )
    
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
    
    checkin = db.query(Checkin).filter(
        Checkin.cpf == cpf,
        Checkin.evento_id == evento_id
    ).first()
    
    transacao = db.query(Transacao).filter(
        Transacao.cpf_comprador == cpf,
        Transacao.evento_id == evento_id,
        Transacao.status == "aprovada"
    ).first()
    
    return {
        "cpf": cpf,
        "evento_id": evento_id,
        "tem_transacao": transacao is not None,
        "ja_fez_checkin": checkin is not None,
        "nome": transacao.nome_comprador if transacao else None,
        "checkin_em": checkin.checkin_em if checkin else None
    }

@router.post("/qr", response_model=CheckinSchema)
async def checkin_por_qr(
    qr_code: str,
    validacao_cpf: str,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Check-in por QR Code único"""
    
    transacao = db.query(Transacao).filter(
        Transacao.qr_code_ticket == qr_code,
        Transacao.status == "aprovada"
    ).first()
    
    if not transacao:
        comanda = db.query(Comanda).filter(Comanda.qr_code == qr_code).first()
        if not comanda:
            raise HTTPException(status_code=404, detail="QR Code não encontrado ou inválido")
        
        cpf_formatado = comanda.cpf_cliente
        nome_cliente = comanda.nome_cliente
        evento_id = comanda.evento_id
    else:
        cpf_formatado = transacao.cpf_comprador
        nome_cliente = transacao.nome_comprador
        evento_id = transacao.evento_id
    
    if not cpf_formatado:
        raise HTTPException(status_code=400, detail="CPF não encontrado no QR Code")
    
    cpf_limpo = cpf_formatado.replace(".", "").replace("-", "")
    if validacao_cpf != cpf_limpo[:3]:
        raise HTTPException(status_code=400, detail="Validação de CPF incorreta")
    
    checkin_existente = db.query(Checkin).filter(
        Checkin.cpf == cpf_formatado,
        Checkin.evento_id == evento_id
    ).first()
    
    if checkin_existente:
        raise HTTPException(status_code=400, detail="Check-in já realizado para este CPF neste evento")
    
    db_checkin = Checkin(
        cpf=cpf_formatado,
        nome=nome_cliente,
        evento_id=evento_id,
        usuario_id=usuario_atual.id,
        transacao_id=transacao.id if transacao else None,
        metodo_checkin="qr_code",
        validacao_cpf=validacao_cpf
    )
    
    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)
    
    await manager.broadcast_to_event(evento_id, {
        "type": "checkin_update",
        "data": {
            "tipo": "novo_checkin",
            "checkin": {
                "nome": nome_cliente,
                "cpf": cpf_formatado,
                "metodo": "qr_code",
                "horario": db_checkin.checkin_em.isoformat()
            }
        },
        "timestamp": datetime.now().isoformat()
    })
    
    if transacao and transacao.telefone_comprador:
        await whatsapp_service.notify_n8n("checkin_realizado", {
            "cpf": cpf_formatado,
            "nome": nome_cliente,
            "evento_id": evento_id,
            "telefone": transacao.telefone_comprador
        })
    
    return db_checkin

@router.get("/dashboard/{evento_id}")
async def dashboard_checkin_tempo_real(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Dashboard de check-in em tempo real"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    total_checkins = db.query(Checkin).filter(Checkin.evento_id == evento_id).count()
    
    uma_hora_atras = datetime.now() - timedelta(hours=1)
    checkins_ultima_hora = db.query(Checkin).filter(
        Checkin.evento_id == evento_id,
        Checkin.checkin_em >= uma_hora_atras
    ).count()
    
    total_vendas = db.query(Transacao).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == "aprovada"
    ).count()
    
    checkins_por_metodo = db.query(
        Checkin.metodo_checkin,
        db.func.count(Checkin.id).label('total')
    ).filter(Checkin.evento_id == evento_id).group_by(Checkin.metodo_checkin).all()
    
    vendas_sem_checkin = db.query(Transacao).outerjoin(
        Checkin, Transacao.cpf_comprador == Checkin.cpf
    ).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == "aprovada",
        Checkin.id.is_(None)
    ).count()
    
    return {
        "evento_id": evento_id,
        "nome_evento": evento.nome,
        "total_checkins": total_checkins,
        "checkins_ultima_hora": checkins_ultima_hora,
        "total_vendas": total_vendas,
        "taxa_presenca": round((total_checkins / total_vendas * 100) if total_vendas > 0 else 0, 1),
        "fila_espera": vendas_sem_checkin,
        "checkins_por_metodo": [{"metodo": m[0], "total": m[1]} for m in checkins_por_metodo],
        "status_evento": evento.status.value,
        "timestamp": datetime.now().isoformat()
    }
