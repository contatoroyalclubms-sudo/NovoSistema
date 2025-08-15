from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import json
import aiohttp
from ..database import get_db
from ..models import Evento, Transacao, Usuario, LogAuditoria
from ..auth import verificar_permissao_admin

router = APIRouter(prefix="/n8n", tags=["N8N Automações"])

@router.post("/webhook/meta-ads", summary="Webhook Meta Ads")
async def webhook_meta_ads(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook para receber dados do Meta Ads via N8N.
    
    **Uso:** Configure este endpoint no N8N para receber dados do Meta Ads.
    """
    
    try:
        data = await request.json()
        
        log = LogAuditoria(
            cpf_usuario="sistema",
            acao="webhook_meta_ads",
            dados_novos=json.dumps(data),
            ip_origem=request.client.host,
            status="sucesso"
        )
        db.add(log)
        db.commit()
        
        if data.get("event_type") == "lead":
            await processar_lead_meta_ads(data, db)
        elif data.get("event_type") == "purchase":
            await processar_compra_meta_ads(data, db)
        
        return {"status": "success", "message": "Webhook Meta Ads processado"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/webhook/crm", summary="Webhook CRM")
async def webhook_crm(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook para integração com CRM via N8N.
    
    **Uso:** Configure este endpoint no N8N para receber dados do CRM.
    """
    
    try:
        data = await request.json()
        
        log = LogAuditoria(
            cpf_usuario="sistema",
            acao="webhook_crm",
            dados_novos=json.dumps(data),
            ip_origem=request.client.host,
            status="sucesso"
        )
        db.add(log)
        db.commit()
        
        if data.get("action") == "new_contact":
            await processar_novo_contato_crm(data, db)
        elif data.get("action") == "update_contact":
            await processar_atualizacao_contato_crm(data, db)
        
        return {"status": "success", "message": "Webhook CRM processado"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/trigger/evento-criado", summary="Disparar automação evento criado")
async def trigger_evento_criado(
    evento_id: int,
    n8n_webhook_url: str,
    db: Session = Depends(get_db),
    usuario_atual = Depends(verificar_permissao_admin)
):
    """
    Disparar automação N8N quando evento é criado.
    
    **Permissões necessárias:** Admin
    """
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    payload = {
        "event": "evento_criado",
        "evento_id": evento.id,
        "evento_nome": evento.nome,
        "data_evento": evento.data_evento.isoformat(),
        "local": evento.local,
        "empresa_id": evento.empresa_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(n8n_webhook_url, json=payload) as response:
                if response.status == 200:
                    return {"status": "success", "message": "Automação N8N disparada"}
                else:
                    return {"status": "error", "message": f"Erro HTTP {response.status}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/trigger/venda-realizada", summary="Disparar automação venda realizada")
async def trigger_venda_realizada(
    transacao_id: int,
    n8n_webhook_url: str,
    db: Session = Depends(get_db),
    usuario_atual = Depends(verificar_permissao_admin)
):
    """
    Disparar automação N8N quando venda é realizada.
    
    **Permissões necessárias:** Admin
    """
    
    transacao = db.query(Transacao).filter(Transacao.id == transacao_id).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    payload = {
        "event": "venda_realizada",
        "transacao_id": transacao.id,
        "evento_id": transacao.evento_id,
        "cpf_comprador": transacao.cpf_comprador,
        "nome_comprador": transacao.nome_comprador,
        "valor": float(transacao.valor),
        "lista_id": transacao.lista_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(n8n_webhook_url, json=payload) as response:
                if response.status == 200:
                    return {"status": "success", "message": "Automação N8N disparada"}
                else:
                    return {"status": "error", "message": f"Erro HTTP {response.status}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def processar_lead_meta_ads(data: Dict[str, Any], db: Session):
    """Processar lead do Meta Ads"""
    pass

async def processar_compra_meta_ads(data: Dict[str, Any], db: Session):
    """Processar compra do Meta Ads"""
    pass

async def processar_novo_contato_crm(data: Dict[str, Any], db: Session):
    """Processar novo contato do CRM"""
    pass

async def processar_atualizacao_contato_crm(data: Dict[str, Any], db: Session):
    """Processar atualização de contato do CRM"""
    pass
