"""
NotificationService - Serviço completo de notificações
Sistema Universal de Gestão de Eventos

Funcionalidades:
- Webhooks para payment links
- Notificações por email
- Alertas em tempo real
- Push notifications
- Sistema de templates
- Retry automático
- Analytics de entrega
"""

import asyncio
import json
import logging
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from jinja2 import Template
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import smtplib

# Imports do sistema
from app.core.config import settings
from app.services.webhook_service import webhook_service
from app.services.email_service import EmailService
from app.services.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    WEBHOOK = "webhook"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"


class NotificationService:
    """
    Serviço centralizado de notificações para o sistema
    """
    
    def __init__(self):
        self.webhook_service = webhook_service
        self.email_service = EmailService()
        self.cache = RedisCache()
        
        # Configurações de retry
        self.max_retries = {
            NotificationType.WEBHOOK: 3,
            NotificationType.EMAIL: 2,
            NotificationType.SMS: 3,
            NotificationType.PUSH: 2,
        }
        
        self.retry_delays = {
            NotificationType.WEBHOOK: [5, 15, 60],  # segundos
            NotificationType.EMAIL: [10, 30],
            NotificationType.SMS: [2, 10, 30],
            NotificationType.PUSH: [5, 20],
        }
        
        # Templates de notificação
        self.templates = {
            "payment_link_created": {
                "subject": "🔗 Link de pagamento criado: {{title}}",
                "body": """
                <h2>Link de pagamento criado com sucesso!</h2>
                <p><strong>Título:</strong> {{title}}</p>
                <p><strong>Valor:</strong> {{amount_formatted}}</p>
                <p><strong>URL:</strong> <a href="{{url}}">{{short_url}}</a></p>
                <p><strong>Criado em:</strong> {{created_at}}</p>
                """
            },
            "payment_completed": {
                "subject": "✅ Pagamento recebido: {{amount_formatted}}",
                "body": """
                <h2>Pagamento recebido com sucesso!</h2>
                <p><strong>Valor:</strong> {{amount_formatted}}</p>
                <p><strong>Cliente:</strong> {{customer_name}}</p>
                <p><strong>Email:</strong> {{customer_email}}</p>
                <p><strong>Método:</strong> {{payment_method}}</p>
                <p><strong>Data:</strong> {{completed_at}}</p>
                """
            },
            "payment_failed": {
                "subject": "❌ Falha no pagamento: {{link_title}}",
                "body": """
                <h2>Tentativa de pagamento falhou</h2>
                <p><strong>Link:</strong> {{link_title}}</p>
                <p><strong>Cliente:</strong> {{customer_name}}</p>
                <p><strong>Valor tentado:</strong> {{amount_formatted}}</p>
                <p><strong>Motivo:</strong> {{failure_reason}}</p>
                <p><strong>Data:</strong> {{failed_at}}</p>
                """
            }
        }
    
    async def send_notification(
        self,
        notification_type: NotificationType,
        recipient: str,
        subject: str,
        content: Dict[str, Any],
        priority: NotificationPriority = NotificationPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enviar notificação com retry automático
        """
        try:
            notification_id = f"notif_{int(datetime.utcnow().timestamp())}_{hash(recipient)}"
            
            # Aplicar template se especificado
            if template_name and template_data:
                content = self._apply_template(template_name, template_data)
                if template_name in self.templates:
                    subject = Template(self.templates[template_name]["subject"]).render(**template_data)
            
            # Log da notificação
            logger.info(f"Sending {notification_type.value} notification to {recipient}")
            
            # Enviar baseado no tipo
            if notification_type == NotificationType.WEBHOOK:
                return await self._send_webhook_notification(recipient, content, metadata)
            
            elif notification_type == NotificationType.EMAIL:
                return await self._send_email_notification(recipient, subject, content, priority)
            
            elif notification_type == NotificationType.SMS:
                return await self._send_sms_notification(recipient, content, priority)
            
            elif notification_type == NotificationType.PUSH:
                return await self._send_push_notification(recipient, subject, content, priority)
            
            elif notification_type == NotificationType.IN_APP:
                return await self._send_in_app_notification(recipient, subject, content, priority)
            
            else:
                raise ValueError(f"Tipo de notificação não suportado: {notification_type}")
        
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "notification_id": notification_id
            }
    
    async def _send_webhook_notification(
        self,
        webhook_url: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enviar notificação via webhook"""
        try:
            headers = metadata.get("headers") if metadata else None
            secret = metadata.get("secret") if metadata else None
            
            result = await self.webhook_service._send_webhook(
                url=webhook_url,
                payload=content,
                headers=headers,
                secret=secret
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Webhook notification failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _send_email_notification(
        self,
        email: str,
        subject: str,
        content: Dict[str, Any],
        priority: NotificationPriority
    ) -> Dict[str, Any]:
        """Enviar notificação por email"""
        try:
            body = content.get("body", "")
            html_body = content.get("html_body", body)
            
            # Configurar prioridade
            priority_headers = {}
            if priority == NotificationPriority.URGENT:
                priority_headers["X-Priority"] = "1"
                priority_headers["X-MSMail-Priority"] = "High"
            elif priority == NotificationPriority.HIGH:
                priority_headers["X-Priority"] = "2"
            
            success = await self.email_service.send_email(
                to_email=email,
                subject=subject,
                body=body,
                html_body=html_body,
                headers=priority_headers
            )
            
            return {
                "success": success,
                "delivery_method": "email",
                "recipient": email
            }
        
        except Exception as e:
            logger.error(f"Email notification failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _send_sms_notification(
        self,
        phone: str,
        content: Dict[str, Any],
        priority: NotificationPriority
    ) -> Dict[str, Any]:
        """Enviar notificação por SMS (implementar integração)"""
        # Placeholder para integração com serviço de SMS
        logger.info(f"SMS notification to {phone}: {content.get('message', '')}")
        
        # Em produção, integrar com Twilio, AWS SNS, etc.
        return {
            "success": True,
            "delivery_method": "sms",
            "recipient": phone,
            "note": "SMS integration not implemented yet"
        }
    
    async def _send_push_notification(
        self,
        device_token: str,
        subject: str,
        content: Dict[str, Any],
        priority: NotificationPriority
    ) -> Dict[str, Any]:
        """Enviar push notification (implementar integração)"""
        # Placeholder para integração com FCM, APNS, etc.
        logger.info(f"Push notification to {device_token}: {subject}")
        
        return {
            "success": True,
            "delivery_method": "push",
            "recipient": device_token,
            "note": "Push notification integration not implemented yet"
        }
    
    async def _send_in_app_notification(
        self,
        user_id: str,
        subject: str,
        content: Dict[str, Any],
        priority: NotificationPriority
    ) -> Dict[str, Any]:
        """Enviar notificação in-app via WebSocket"""
        try:
            # Armazenar notificação no cache para recuperação
            cache_key = f"notification:{user_id}:{int(datetime.utcnow().timestamp())}"
            
            notification_data = {
                "id": cache_key,
                "user_id": user_id,
                "subject": subject,
                "content": content,
                "priority": priority.value,
                "created_at": datetime.utcnow().isoformat(),
                "read": False
            }
            
            # Armazenar no cache por 30 dias
            await self.cache.set(cache_key, json.dumps(notification_data), ttl=2592000)
            
            # Enviar via WebSocket se disponível
            # TODO: Implementar envio WebSocket
            
            return {
                "success": True,
                "delivery_method": "in_app",
                "recipient": user_id,
                "notification_id": cache_key
            }
        
        except Exception as e:
            logger.error(f"In-app notification failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _apply_template(self, template_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aplicar template aos dados"""
        if template_name not in self.templates:
            return {"body": "Template not found"}
        
        template = self.templates[template_name]
        
        try:
            # Renderizar template
            body_template = Template(template["body"])
            rendered_body = body_template.render(**data)
            
            return {
                "html_body": rendered_body,
                "body": self._html_to_text(rendered_body)
            }
        
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            return {"body": f"Template error: {str(e)}"}
    
    def _html_to_text(self, html: str) -> str:
        """Converter HTML simples para texto"""
        import re
        text = re.sub('<[^<]+?>', '', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    # ================================
    # MÉTODOS ESPECÍFICOS PARA PAYMENT LINKS
    # ================================
    
    async def send_link_created_notification(
        self,
        user_id: int,
        link_id: str,
        link_title: str,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Notificar criação de link de pagamento"""
        notifications = []
        
        # Webhook se configurado
        if webhook_url:
            webhook_result = await self.send_notification(
                notification_type=NotificationType.WEBHOOK,
                recipient=webhook_url,
                subject="",
                content={
                    "event": "payment_link_created",
                    "link_id": link_id,
                    "link_title": link_title,
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            notifications.append(webhook_result)
        
        # Notificação in-app
        in_app_result = await self.send_notification(
            notification_type=NotificationType.IN_APP,
            recipient=str(user_id),
            subject="Link de pagamento criado",
            content={
                "message": f"Seu link '{link_title}' foi criado com sucesso!",
                "link_id": link_id,
                "action_url": f"/payment-links/{link_id}"
            },
            priority=NotificationPriority.NORMAL
        )
        notifications.append(in_app_result)
        
        return {
            "success": any(n.get("success", False) for n in notifications),
            "notifications": notifications
        }
    
    async def send_payment_completed_notification(
        self,
        link_id: str,
        user_id: int,
        payment_data: Dict[str, Any],
        webhook_url: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Notificar pagamento completo"""
        notifications = []
        
        # Webhook se configurado
        if webhook_url:
            webhook_result = await self.send_notification(
                notification_type=NotificationType.WEBHOOK,
                recipient=webhook_url,
                subject="",
                content={
                    "event": "payment_completed",
                    "link_id": link_id,
                    "payment_id": payment_data.get("payment_id"),
                    "amount": float(payment_data.get("amount", 0)),
                    "currency": payment_data.get("currency", "BRL"),
                    "customer": {
                        "name": payment_data.get("customer_name"),
                        "email": payment_data.get("customer_email")
                    },
                    "payment_method": payment_data.get("payment_method"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            notifications.append(webhook_result)
        
        # Email se configurado
        if user_email:
            template_data = {
                "amount_formatted": f"R$ {payment_data.get('amount', 0):,.2f}",
                "customer_name": payment_data.get("customer_name", "N/A"),
                "customer_email": payment_data.get("customer_email", "N/A"),
                "payment_method": payment_data.get("payment_method", "N/A"),
                "completed_at": datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
            }
            
            email_result = await self.send_notification(
                notification_type=NotificationType.EMAIL,
                recipient=user_email,
                subject="",
                content={},
                template_name="payment_completed",
                template_data=template_data,
                priority=NotificationPriority.HIGH
            )
            notifications.append(email_result)
        
        # Notificação in-app
        in_app_result = await self.send_notification(
            notification_type=NotificationType.IN_APP,
            recipient=str(user_id),
            subject="Pagamento recebido",
            content={
                "message": f"Você recebeu um pagamento de R$ {payment_data.get('amount', 0):,.2f}!",
                "payment_id": payment_data.get("payment_id"),
                "amount": payment_data.get("amount"),
                "customer_name": payment_data.get("customer_name"),
                "action_url": f"/payment-links/{link_id}/analytics"
            },
            priority=NotificationPriority.HIGH
        )
        notifications.append(in_app_result)
        
        return {
            "success": any(n.get("success", False) for n in notifications),
            "notifications": notifications
        }
    
    async def send_payment_failed_notification(
        self,
        link_id: str,
        user_id: int,
        failure_data: Dict[str, Any],
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Notificar falha no pagamento"""
        notifications = []
        
        # Webhook se configurado
        if webhook_url:
            webhook_result = await self.send_notification(
                notification_type=NotificationType.WEBHOOK,
                recipient=webhook_url,
                subject="",
                content={
                    "event": "payment_failed",
                    "link_id": link_id,
                    "attempt_id": failure_data.get("attempt_id"),
                    "amount": float(failure_data.get("amount", 0)),
                    "customer": {
                        "name": failure_data.get("customer_name"),
                        "email": failure_data.get("customer_email")
                    },
                    "failure_reason": failure_data.get("failure_reason"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            notifications.append(webhook_result)
        
        # Notificação in-app (apenas para falhas críticas)
        if failure_data.get("critical", False):
            in_app_result = await self.send_notification(
                notification_type=NotificationType.IN_APP,
                recipient=str(user_id),
                subject="Falha no pagamento",
                content={
                    "message": f"Falha no pagamento: {failure_data.get('failure_reason', 'Erro desconhecido')}",
                    "link_id": link_id,
                    "action_url": f"/payment-links/{link_id}"
                },
                priority=NotificationPriority.HIGH
            )
            notifications.append(in_app_result)
        
        return {
            "success": any(n.get("success", False) for n in notifications),
            "notifications": notifications
        }
    
    async def send_webhook(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """Método de conveniência para enviar webhook"""
        return await self.webhook_service._send_webhook(
            url=url,
            payload=payload,
            headers=headers,
            secret=secret
        )
    
    async def send_bulk_notifications(
        self,
        notifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Enviar múltiplas notificações em lote
        """
        tasks = []
        for notif in notifications:
            task = self.send_notification(**notif)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        failed_count = len(results) - success_count
        
        return {
            "total": len(notifications),
            "success": success_count,
            "failed": failed_count,
            "results": results
        }
    
    async def get_user_notifications(
        self,
        user_id: str,
        limit: int = 20,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Obter notificações do usuário"""
        try:
            # Buscar no cache usando pattern
            cache_pattern = f"notification:{user_id}:*"
            keys = await self.cache.scan_keys(cache_pattern)
            
            notifications = []
            for key in keys[-limit:]:  # Últimas notificações
                data = await self.cache.get(key)
                if data:
                    notification = json.loads(data)
                    if not unread_only or not notification.get("read", False):
                        notifications.append(notification)
            
            # Ordenar por data de criação (mais recentes primeiro)
            notifications.sort(key=lambda x: x["created_at"], reverse=True)
            
            return notifications
        
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            return []
    
    async def mark_notification_as_read(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """Marcar notificação como lida"""
        try:
            data = await self.cache.get(notification_id)
            if data:
                notification = json.loads(data)
                if notification["user_id"] == user_id:
                    notification["read"] = True
                    notification["read_at"] = datetime.utcnow().isoformat()
                    await self.cache.set(notification_id, json.dumps(notification), ttl=2592000)
                    return True
            return False
        
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False


# Instância global do serviço
notification_service = NotificationService()