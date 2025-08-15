from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from ..database import get_db
from ..auth import obter_usuario_atual, verificar_permissao_promoter
from ..models import Usuario, Evento, Lista
from ..services.whatsapp_service import whatsapp_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

class WhatsAppInitRequest(BaseModel):
    webhook_url: str = None

class SendInviteRequest(BaseModel):
    phone: str
    evento_id: int
    lista_id: int

class BulkInviteRequest(BaseModel):
    phones: List[str]
    evento_id: int
    lista_id: int

class WebhookMessage(BaseModel):
    phone: str
    message: str
    timestamp: str = None

@router.post("/init", summary="Inicializar sessão WhatsApp")
async def inicializar_whatsapp(
    request: WhatsAppInitRequest,
    usuario_atual: Usuario = Depends(verificar_permissao_promoter)
):
    """
    Inicializa sessão do WhatsApp e retorna QR Code para escaneamento.
    
    **Permissões necessárias:** Promoter ou Admin
    """
    try:
        result = await whatsapp_service.initialize_session()
        
        if request.webhook_url:
            whatsapp_service.webhook_url = request.webhook_url
        
        return {
            "message": "Sessão WhatsApp inicializada",
            "data": result
        }
    except Exception as e:
        logger.error(f"Erro ao inicializar WhatsApp: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", summary="Status da sessão WhatsApp")
async def status_whatsapp(
    usuario_atual: Usuario = Depends(verificar_permissao_promoter)
):
    """
    Retorna o status atual da sessão WhatsApp.
    
    **Permissões necessárias:** Promoter ou Admin
    """
    try:
        status = await whatsapp_service.get_session_status()
        return {
            "message": "Status da sessão WhatsApp",
            "data": status
        }
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-invite", summary="Enviar convite individual")
async def enviar_convite(
    request: SendInviteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_promoter)
):
    """
    Envia convite individual via WhatsApp.
    
    **Permissões necessárias:** Promoter ou Admin
    
    **Campos obrigatórios:**
    - phone: Número do telefone (formato: +5511999999999)
    - evento_id: ID do evento
    - lista_id: ID da lista
    """
    try:
        evento = db.query(Evento).filter(
            Evento.id == request.evento_id,
            Evento.empresa_id == usuario_atual.empresa_id
        ).first()
        
        if not evento:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        
        lista = db.query(Lista).filter(
            Lista.id == request.lista_id,
            Lista.evento_id == request.evento_id
        ).first()
        
        if not lista:
            raise HTTPException(status_code=404, detail="Lista não encontrada")
        
        background_tasks.add_task(
            whatsapp_service.send_invite,
            request.phone,
            request.evento_id,
            request.lista_id,
            db
        )
        
        return {
            "message": "Convite sendo enviado",
            "phone": request.phone,
            "evento": evento.nome,
            "lista": lista.nome
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao enviar convite: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-bulk", summary="Enviar convites em massa")
async def enviar_convites_massa(
    request: BulkInviteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_promoter)
):
    """
    Envia convites em massa via WhatsApp.
    
    **Permissões necessárias:** Promoter ou Admin
    
    **Campos obrigatórios:**
    - phones: Lista de números de telefone
    - evento_id: ID do evento
    - lista_id: ID da lista
    """
    try:
        evento = db.query(Evento).filter(
            Evento.id == request.evento_id,
            Evento.empresa_id == usuario_atual.empresa_id
        ).first()
        
        if not evento:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        
        lista = db.query(Lista).filter(
            Lista.id == request.lista_id,
            Lista.evento_id == request.evento_id
        ).first()
        
        if not lista:
            raise HTTPException(status_code=404, detail="Lista não encontrada")
        
        if len(request.phones) > 100:
            raise HTTPException(status_code=400, detail="Máximo de 100 números por vez")
        
        background_tasks.add_task(
            whatsapp_service.send_bulk_invites,
            request.evento_id,
            request.lista_id,
            request.phones,
            db
        )
        
        return {
            "message": "Convites sendo enviados em massa",
            "total_phones": len(request.phones),
            "evento": evento.nome,
            "lista": lista.nome
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao enviar convites em massa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook", summary="Webhook para mensagens recebidas")
async def webhook_mensagens(
    message: WebhookMessage,
    db: Session = Depends(get_db)
):
    """
    Webhook para processar mensagens recebidas via WhatsApp.
    
    **Uso:** Este endpoint deve ser configurado no sistema de WhatsApp
    para receber mensagens automaticamente.
    """
    try:
        result = await whatsapp_service.process_incoming_message(
            message.phone,
            message.message,
            db
        )
        
        return {
            "message": "Mensagem processada",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/eventos/{evento_id}/invites", summary="Listar convites enviados")
async def listar_convites_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_permissao_promoter)
):
    """
    Lista todos os convites enviados para um evento específico.
    
    **Permissões necessárias:** Promoter ou Admin
    """
    try:
        evento = db.query(Evento).filter(
            Evento.id == evento_id,
            Evento.empresa_id == usuario_atual.empresa_id
        ).first()
        
        if not evento:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        
        convites_mock = [
            {
                "id": 1,
                "phone": "+5511999999999",
                "status": "enviado",
                "enviado_em": "2025-08-07T10:30:00",
                "confirmado": True,
                "checkin_realizado": False
            },
            {
                "id": 2,
                "phone": "+5511888888888",
                "status": "enviado",
                "enviado_em": "2025-08-07T10:31:00",
                "confirmado": False,
                "checkin_realizado": False
            }
        ]
        
        return {
            "message": "Convites do evento",
            "evento": evento.nome,
            "total": len(convites_mock),
            "convites": convites_mock
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar convites: {e}")
        raise HTTPException(status_code=500, detail=str(e))
