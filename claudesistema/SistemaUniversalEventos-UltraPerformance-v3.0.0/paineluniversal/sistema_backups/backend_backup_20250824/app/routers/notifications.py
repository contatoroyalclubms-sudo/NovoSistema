"""
API Router - Sistema de Notificações
Endpoints para gerenciar notificações, templates e destinatários
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import logging

from ..notification_manager import (
    notification_manager,
    NotificationType,
    NotificationPriority,
    NotificationStatus,
    NotificationTemplate,
    NotificationRecipient,
    Notification
)

router = APIRouter(prefix="/notifications", tags=["notifications"])
logger = logging.getLogger(__name__)

# Modelos Pydantic

class TemplateCreate(BaseModel):
    name: str
    type: NotificationType
    subject: str
    content: str
    html_content: Optional[str] = None
    variables: Optional[List[str]] = None

class RecipientCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    push_token: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class NotificationCreate(BaseModel):
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    recipient_id: str
    template_id: Optional[str] = None
    subject: str
    content: str
    html_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None

class BulkNotificationCreate(BaseModel):
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    recipient_ids: List[str]
    template_id: Optional[str] = None
    subject: str
    content: str
    html_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None

class EmailConfig(BaseModel):
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True

# Endpoints

@router.get("/health")
async def health_check():
    """Health check do sistema de notificações"""
    try:
        stats = await notification_manager.get_stats()
        
        return {
            "status": "healthy",
            "service": "notification_system",
            "version": "1.0.0",
            "queue_size": stats.get("queue_size", 0),
            "is_processing": stats.get("is_processing", False),
            "total_notifications": stats.get("total_notifications", 0),
            "success_rate": stats.get("success_rate", 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[NOTIFICATION_API] Health check error: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/stats")
async def get_statistics():
    """Estatísticas do sistema de notificações"""
    try:
        stats = await notification_manager.get_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"[NOTIFICATION_API] Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

# Templates

@router.post("/templates")
async def create_template(template_data: TemplateCreate):
    """Criar template de notificação"""
    try:
        template = NotificationTemplate(
            id=str(uuid.uuid4()),
            name=template_data.name,
            type=template_data.type,
            subject=template_data.subject,
            content=template_data.content,
            html_content=template_data.html_content,
            variables=template_data.variables or [],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        success = await notification_manager.create_template(template)
        
        if success:
            logger.info(f"[NOTIFICATION_API] Template criado: {template.name}")
            return {
                "success": True,
                "message": "Template criado com sucesso",
                "template_id": template.id
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao criar template")
            
    except Exception as e:
        logger.error(f"[NOTIFICATION_API] Error creating template: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

# Destinatários

@router.post("/recipients")
async def create_recipient(recipient_data: RecipientCreate):
    """Criar destinatário"""
    try:
        recipient = NotificationRecipient(
            id=str(uuid.uuid4()),
            name=recipient_data.name,
            email=recipient_data.email,
            phone=recipient_data.phone,
            push_token=recipient_data.push_token,
            preferences=recipient_data.preferences or {}
        )
        
        success = await notification_manager.create_recipient(recipient)
        
        if success:
            logger.info(f"[NOTIFICATION_API] Destinatário criado: {recipient.name}")
            return {
                "success": True,
                "message": "Destinatário criado com sucesso",
                "recipient_id": recipient.id
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao criar destinatário")
            
    except Exception as e:
        logger.error(f"[NOTIFICATION_API] Error creating recipient: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating recipient: {str(e)}")

# Notificações

@router.post("/send")
async def send_notification(notification_data: NotificationCreate, background_tasks: BackgroundTasks):
    """Enviar notificação individual"""
    try:
        notification = Notification(
            id=str(uuid.uuid4()),
            type=notification_data.type,
            priority=notification_data.priority,
            status=NotificationStatus.PENDING,
            recipient_id=notification_data.recipient_id,
            template_id=notification_data.template_id,
            subject=notification_data.subject,
            content=notification_data.content,
            html_content=notification_data.html_content,
            metadata=notification_data.metadata or {},
            scheduled_at=notification_data.scheduled_at,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        success = await notification_manager.send_notification(notification)
        
        if success:
            logger.info(f"[NOTIFICATION_API] Notificação enviada: {notification.id}")
            return {
                "success": True,
                "message": "Notificação enviada com sucesso",
                "notification_id": notification.id
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao enviar notificação")
            
    except Exception as e:
        logger.error(f"[NOTIFICATION_API] Error sending notification: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending notification: {str(e)}")

@router.post("/send-bulk")
async def send_bulk_notifications(bulk_data: BulkNotificationCreate, background_tasks: BackgroundTasks):
    """Enviar notificações em massa"""
    try:
        notifications_sent = []
        
        for recipient_id in bulk_data.recipient_ids:
            notification = Notification(
                id=str(uuid.uuid4()),
                type=bulk_data.type,
                priority=bulk_data.priority,
                status=NotificationStatus.PENDING,
                recipient_id=recipient_id,
                template_id=bulk_data.template_id,
                subject=bulk_data.subject,
                content=bulk_data.content,
                html_content=bulk_data.html_content,
                metadata=bulk_data.metadata or {},
                scheduled_at=bulk_data.scheduled_at,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            success = await notification_manager.send_notification(notification)
            if success:
                notifications_sent.append(notification.id)
        
        logger.info(f"[NOTIFICATION_API] Notificações em massa enviadas: {len(notifications_sent)}")
        return {
            "success": True,
            "message": f"{len(notifications_sent)} notificações enviadas com sucesso",
            "notification_ids": notifications_sent,
            "total_sent": len(notifications_sent),
            "total_requested": len(bulk_data.recipient_ids)
        }
        
    except Exception as e:
        logger.error(f"[NOTIFICATION_API] Error sending bulk notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending bulk notifications: {str(e)}")

@router.get("/list")
async def list_notifications(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None
):
    """Listar notificações"""
    try:
        status_filter = None
        if status:
            try:
                status_filter = NotificationStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Status inválido: {status}")
        
        notifications = await notification_manager.get_notifications(
            limit=limit,
            offset=offset,
            status_filter=status_filter
        )
        
        return {
            "success": True,
            "data": notifications,
            "count": len(notifications),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"[NOTIFICATION_API] Error listing notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing notifications: {str(e)}")

# Configuração

@router.post("/config/email")
async def configure_email(email_config: EmailConfig):
    """Configurar provedor de email"""
    try:
        notification_manager.configure_email(
            smtp_server=email_config.smtp_server,
            smtp_port=email_config.smtp_port,
            username=email_config.username,
            password=email_config.password,
            use_tls=email_config.use_tls
        )
        
        logger.info("[NOTIFICATION_API] Configuração de email atualizada")
        return {
            "success": True,
            "message": "Configuração de email atualizada com sucesso"
        }
        
    except Exception as e:
        logger.error(f"[NOTIFICATION_API] Error configuring email: {e}")
        raise HTTPException(status_code=500, detail=f"Error configuring email: {str(e)}")

# Modelos para testes
class EmailTestRequest(BaseModel):
    email: EmailStr
    subject: str = "Teste de Email"
    content: str = "Este é um email de teste"

class SMSTestRequest(BaseModel):
    phone: str
    message: str = "Esta é uma mensagem de teste"

class PushTestRequest(BaseModel):
    token: str
    title: str = "Teste de Push"
    body: str = "Esta é uma notificação push de teste"

# Testes

@router.post("/test/email")
async def test_email(request: EmailTestRequest):
    """Testar envio de email"""
    try:
        # Criar destinatário temporário
        recipient_id = str(uuid.uuid4())
        recipient = NotificationRecipient(
            id=recipient_id,
            name="Teste",
            email=request.email
        )
        
        await notification_manager.create_recipient(recipient)
        
        # Enviar notificação de teste
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.EMAIL,
            priority=NotificationPriority.NORMAL,
            status=NotificationStatus.PENDING,
            recipient_id=recipient_id,
            template_id=None,
            subject=request.subject,
            content=request.content,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        success = await notification_manager.send_notification(notification)
        
        if success:
            logger.info(f"[NOTIFICATION_API] Email de teste enviado para: {request.email}")
            return {
                "success": True,
                "message": f"Email de teste enviado para {request.email}",
                "notification_id": notification.id
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao enviar email de teste")
            
    except Exception as e:
        logger.error(f"[NOTIFICATION_API] Error testing email: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing email: {str(e)}")

@router.post("/test/sms")
async def test_sms(request: SMSTestRequest):
    """Testar envio de SMS"""
    try:
        # Criar destinatário temporário
        recipient_id = str(uuid.uuid4())
        recipient = NotificationRecipient(
            id=recipient_id,
            name="Teste SMS",
            phone=request.phone
        )
        
        await notification_manager.create_recipient(recipient)
        
        # Enviar notificação de teste
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.SMS,
            priority=NotificationPriority.NORMAL,
            status=NotificationStatus.PENDING,
            recipient_id=recipient_id,
            template_id=None,
            subject="Teste SMS",
            content=request.message,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        success = await notification_manager.send_notification(notification)
        
        if success:
            logger.info(f"[NOTIFICATION_API] SMS de teste enviado para: {request.phone}")
            return {
                "success": True,
                "message": f"SMS de teste enviado para {request.phone}",
                "notification_id": notification.id
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao enviar SMS de teste")
            
    except Exception as e:
        logger.error(f"[NOTIFICATION_API] Error testing SMS: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing SMS: {str(e)}")

@router.post("/test/push")
async def test_push(request: PushTestRequest):
    """Testar envio de push notification"""
    try:
        # Criar destinatário temporário
        recipient_id = str(uuid.uuid4())
        recipient = NotificationRecipient(
            id=recipient_id,
            name="Teste Push",
            push_token=request.token
        )
        
        await notification_manager.create_recipient(recipient)
        
        # Enviar notificação de teste
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.PUSH,
            priority=NotificationPriority.NORMAL,
            status=NotificationStatus.PENDING,
            recipient_id=recipient_id,
            template_id=None,
            subject=request.title,
            content=request.body,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        success = await notification_manager.send_notification(notification)
        
        if success:
            logger.info(f"[NOTIFICATION_API] Push notification de teste enviada")
            return {
                "success": True,
                "message": "Push notification de teste enviada",
                "notification_id": notification.id
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao enviar push notification de teste")
            
    except Exception as e:
        logger.error(f"[NOTIFICATION_API] Error testing push: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing push: {str(e)}")

# Utilitários

@router.get("/types")
async def get_notification_types():
    """Obter tipos de notificação disponíveis"""
    return {
        "success": True,
        "data": {
            "types": [t.value for t in NotificationType],
            "priorities": [p.value for p in NotificationPriority],
            "statuses": [s.value for s in NotificationStatus]
        }
    }

@router.get("/dashboard")
async def get_dashboard_data():
    """Dados para dashboard de notificações"""
    try:
        stats = await notification_manager.get_stats()
        
        return {
            "success": True,
            "data": {
                "summary": {
                    "total_notifications": stats.get("total_notifications", 0),
                    "success_rate": stats.get("success_rate", 0),
                    "last_24h": stats.get("last_24h", 0),
                    "queue_size": stats.get("queue_size", 0)
                },
                "by_status": stats.get("by_status", {}),
                "by_type": stats.get("by_type", {}),
                "by_priority": stats.get("by_priority", {}),
                "system": {
                    "is_processing": stats.get("is_processing", False),
                    "service_status": "active" if stats.get("is_processing", False) else "inactive"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"[NOTIFICATION_API] Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting dashboard data: {str(e)}")

# Inicialização do processamento de notificações
@router.on_event("startup")
async def start_notification_processing():
    """Iniciar processamento de notificações"""
    import asyncio
    asyncio.create_task(notification_manager.process_notifications())
    logger.info("[NOTIFICATION_API] Processamento de notificações iniciado")

@router.on_event("shutdown")
async def stop_notification_processing():
    """Parar processamento de notificações"""
    await notification_manager.stop_processing()
    logger.info("[NOTIFICATION_API] Processamento de notificações parado")
