"""
SISTEMA DE NOTIFICAÇÕES - PRIORITY #8
Sistema completo de notificações push, email e SMS
"""

import asyncio
import smtplib
import ssl
import json
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import aiofiles
import os
from pathlib import Path

# Configurar logging
logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Tipos de notificação"""
    EMAIL = "email"
    SMS = "sms" 
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"

class NotificationPriority(Enum):
    """Prioridades de notificação"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(Enum):
    """Status da notificação"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class NotificationTemplate:
    """Template de notificação"""
    id: str
    name: str
    type: NotificationType
    subject: str
    content: str
    html_content: Optional[str] = None
    variables: List[str] = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class NotificationRecipient:
    """Destinatário da notificação"""
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    push_token: Optional[str] = None
    preferences: Dict[str, Any] = None
    is_active: bool = True

@dataclass
class Notification:
    """Notificação"""
    id: str
    type: NotificationType
    priority: NotificationPriority
    status: NotificationStatus
    recipient_id: str
    template_id: Optional[str]
    subject: str
    content: str
    html_content: Optional[str] = None
    metadata: Dict[str, Any] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    updated_at: datetime = None

class EmailProvider:
    """Provedor de email"""
    
    def __init__(self, 
                 smtp_server: str = "smtp.gmail.com",
                 smtp_port: int = 587,
                 username: str = "",
                 password: str = "",
                 use_tls: bool = True):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        
    async def send_email(self, 
                        to_email: str,
                        subject: str,
                        content: str,
                        html_content: Optional[str] = None,
                        attachments: Optional[List[str]] = None) -> bool:
        """Envia email"""
        try:
            # Criar mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.username
            message["To"] = to_email
            
            # Adicionar conteúdo texto
            text_part = MIMEText(content, "plain", "utf-8")
            message.attach(text_part)
            
            # Adicionar conteúdo HTML se fornecido
            if html_content:
                html_part = MIMEText(html_content, "html", "utf-8")
                message.attach(html_part)
            
            # Adicionar anexos se fornecidos
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        message.attach(part)
            
            # Criar contexto SSL
            context = ssl.create_default_context()
            
            # Conectar e enviar
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.username, self.password)
                server.sendmail(self.username, to_email, message.as_string())
            
            logger.info(f"[NOTIFICATION] Email enviado para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"[NOTIFICATION] Erro ao enviar email para {to_email}: {e}")
            return False

class SMSProvider:
    """Provedor de SMS (simulado - integração com Twilio/AWS SNS)"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
        
    async def send_sms(self, to_phone: str, message: str) -> bool:
        """Envia SMS (simulado)"""
        try:
            # Simular envio de SMS
            # Em produção: integrar com Twilio, AWS SNS, etc.
            logger.info(f"[SMS] Simulando envio para {to_phone}: {message[:50]}...")
            
            # Simular delay de rede
            await asyncio.sleep(0.5)
            
            # Simular sucesso (95% das vezes)
            import random
            success = random.random() > 0.05
            
            if success:
                logger.info(f"[SMS] SMS enviado com sucesso para {to_phone}")
            else:
                logger.error(f"[SMS] Falha ao enviar SMS para {to_phone}")
                
            return success
            
        except Exception as e:
            logger.error(f"[SMS] Erro ao enviar SMS para {to_phone}: {e}")
            return False

class PushProvider:
    """Provedor de notificações push"""
    
    def __init__(self, fcm_key: str = ""):
        self.fcm_key = fcm_key
        
    async def send_push(self, 
                       token: str, 
                       title: str, 
                       body: str,
                       data: Optional[Dict] = None) -> bool:
        """Envia notificação push (simulado)"""
        try:
            # Simular envio de push notification
            # Em produção: integrar com Firebase FCM, Apple APNS, etc.
            logger.info(f"[PUSH] Simulando push: {title}")
            
            # Simular delay de rede
            await asyncio.sleep(0.3)
            
            # Simular sucesso (90% das vezes)
            import random
            success = random.random() > 0.1
            
            if success:
                logger.info(f"[PUSH] Push enviado com sucesso")
            else:
                logger.error(f"[PUSH] Falha ao enviar push notification")
                
            return success
            
        except Exception as e:
            logger.error(f"[PUSH] Erro ao enviar push: {e}")
            return False

class NotificationManager:
    """Gerenciador central de notificações"""
    
    def __init__(self, db_path: str = "notifications.db"):
        self.db_path = db_path
        self.email_provider = EmailProvider()
        self.sms_provider = SMSProvider()
        self.push_provider = PushProvider()
        self.notification_queue = asyncio.Queue()
        self.is_processing = False
        
        # Criar tabelas
        self._create_tables()
        
        logger.info("[NOTIFICATION] NotificationManager inicializado")
    
    def _create_tables(self):
        """Criar tabelas do banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de templates
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notification_templates (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        content TEXT NOT NULL,
                        html_content TEXT,
                        variables TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de destinatários
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notification_recipients (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT,
                        phone TEXT,
                        push_token TEXT,
                        preferences TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de notificações
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notifications (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        status TEXT NOT NULL,
                        recipient_id TEXT NOT NULL,
                        template_id TEXT,
                        subject TEXT NOT NULL,
                        content TEXT NOT NULL,
                        html_content TEXT,
                        metadata TEXT,
                        scheduled_at TIMESTAMP,
                        sent_at TIMESTAMP,
                        delivered_at TIMESTAMP,
                        failed_at TIMESTAMP,
                        error_message TEXT,
                        retry_count INTEGER DEFAULT 0,
                        max_retries INTEGER DEFAULT 3,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (recipient_id) REFERENCES notification_recipients (id),
                        FOREIGN KEY (template_id) REFERENCES notification_templates (id)
                    )
                """)
                
                conn.commit()
                logger.info("[NOTIFICATION] Tabelas criadas com sucesso")
                
        except Exception as e:
            logger.error(f"[NOTIFICATION] Erro ao criar tabelas: {e}")
    
    def configure_email(self, smtp_server: str, smtp_port: int, 
                       username: str, password: str, use_tls: bool = True):
        """Configurar provedor de email"""
        self.email_provider = EmailProvider(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            username=username,
            password=password,
            use_tls=use_tls
        )
        logger.info("[NOTIFICATION] Provedor de email configurado")
    
    def configure_sms(self, api_key: str, api_secret: str):
        """Configurar provedor de SMS"""
        self.sms_provider = SMSProvider(api_key=api_key, api_secret=api_secret)
        logger.info("[NOTIFICATION] Provedor de SMS configurado")
    
    def configure_push(self, fcm_key: str):
        """Configurar provedor de push"""
        self.push_provider = PushProvider(fcm_key=fcm_key)
        logger.info("[NOTIFICATION] Provedor de push configurado")
    
    async def create_template(self, template: NotificationTemplate) -> bool:
        """Criar template de notificação"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO notification_templates 
                    (id, name, type, subject, content, html_content, variables, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template.id,
                    template.name,
                    template.type.value,
                    template.subject,
                    template.content,
                    template.html_content,
                    json.dumps(template.variables) if template.variables else None,
                    template.is_active
                ))
                
                conn.commit()
                logger.info(f"[NOTIFICATION] Template criado: {template.name}")
                return True
                
        except Exception as e:
            logger.error(f"[NOTIFICATION] Erro ao criar template: {e}")
            return False
    
    async def create_recipient(self, recipient: NotificationRecipient) -> bool:
        """Criar destinatário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO notification_recipients 
                    (id, name, email, phone, push_token, preferences, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    recipient.id,
                    recipient.name,
                    recipient.email,
                    recipient.phone,
                    recipient.push_token,
                    json.dumps(recipient.preferences) if recipient.preferences else None,
                    recipient.is_active
                ))
                
                conn.commit()
                logger.info(f"[NOTIFICATION] Destinatário criado: {recipient.name}")
                return True
                
        except Exception as e:
            logger.error(f"[NOTIFICATION] Erro ao criar destinatário: {e}")
            return False
    
    async def send_notification(self, notification: Notification) -> bool:
        """Enviar notificação"""
        try:
            # Salvar no banco
            notification.created_at = datetime.now()
            notification.updated_at = datetime.now()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO notifications 
                    (id, type, priority, status, recipient_id, template_id, 
                     subject, content, html_content, metadata, scheduled_at, 
                     retry_count, max_retries)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    notification.id,
                    notification.type.value,
                    notification.priority.value,
                    notification.status.value,
                    notification.recipient_id,
                    notification.template_id,
                    notification.subject,
                    notification.content,
                    notification.html_content,
                    json.dumps(notification.metadata) if notification.metadata else None,
                    notification.scheduled_at,
                    notification.retry_count,
                    notification.max_retries
                ))
                
                conn.commit()
            
            # Adicionar à fila se não agendada
            if not notification.scheduled_at or notification.scheduled_at <= datetime.now():
                await self.notification_queue.put(notification)
                logger.info(f"[NOTIFICATION] Notificação adicionada à fila: {notification.id}")
            else:
                logger.info(f"[NOTIFICATION] Notificação agendada: {notification.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"[NOTIFICATION] Erro ao enviar notificação: {e}")
            return False
    
    async def process_notifications(self):
        """Processar fila de notificações"""
        self.is_processing = True
        logger.info("[NOTIFICATION] Iniciando processamento de notificações")
        
        while self.is_processing:
            try:
                # Buscar notificação da fila (timeout de 1 segundo)
                notification = await asyncio.wait_for(
                    self.notification_queue.get(), timeout=1.0
                )
                
                await self._process_single_notification(notification)
                
            except asyncio.TimeoutError:
                # Verificar notificações agendadas
                await self._process_scheduled_notifications()
                continue
                
            except Exception as e:
                logger.error(f"[NOTIFICATION] Erro no processamento: {e}")
                await asyncio.sleep(1)
    
    async def _process_single_notification(self, notification: Notification):
        """Processar uma notificação individual"""
        try:
            # Buscar dados do destinatário
            recipient = await self._get_recipient(notification.recipient_id)
            if not recipient:
                logger.error(f"[NOTIFICATION] Destinatário não encontrado: {notification.recipient_id}")
                return
            
            # Atualizar status para enviando
            await self._update_notification_status(notification.id, NotificationStatus.PENDING)
            
            success = False
            
            # Enviar baseado no tipo
            if notification.type == NotificationType.EMAIL and recipient.email:
                success = await self.email_provider.send_email(
                    to_email=recipient.email,
                    subject=notification.subject,
                    content=notification.content,
                    html_content=notification.html_content
                )
                
            elif notification.type == NotificationType.SMS and recipient.phone:
                success = await self.sms_provider.send_sms(
                    to_phone=recipient.phone,
                    message=notification.content
                )
                
            elif notification.type == NotificationType.PUSH and recipient.push_token:
                success = await self.push_provider.send_push(
                    token=recipient.push_token,
                    title=notification.subject,
                    body=notification.content,
                    data=notification.metadata
                )
            
            # Atualizar status baseado no resultado
            if success:
                await self._update_notification_status(
                    notification.id, 
                    NotificationStatus.SENT,
                    sent_at=datetime.now()
                )
                logger.info(f"[NOTIFICATION] Enviada com sucesso: {notification.id}")
            else:
                # Tentar novamente se não excedeu o limite
                if notification.retry_count < notification.max_retries:
                    notification.retry_count += 1
                    await self._update_notification_retry(notification.id, notification.retry_count)
                    
                    # Reagendar para reenvio em 5 minutos
                    notification.scheduled_at = datetime.now() + timedelta(minutes=5)
                    await self.notification_queue.put(notification)
                    
                    logger.info(f"[NOTIFICATION] Reagendada para reenvio: {notification.id}")
                else:
                    await self._update_notification_status(
                        notification.id,
                        NotificationStatus.FAILED,
                        failed_at=datetime.now(),
                        error_message="Máximo de tentativas excedido"
                    )
                    logger.error(f"[NOTIFICATION] Falha definitiva: {notification.id}")
                    
        except Exception as e:
            logger.error(f"[NOTIFICATION] Erro ao processar notificação {notification.id}: {e}")
    
    async def _process_scheduled_notifications(self):
        """Processar notificações agendadas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Buscar notificações agendadas para agora
                cursor.execute("""
                    SELECT * FROM notifications 
                    WHERE status = 'pending' 
                    AND scheduled_at <= ? 
                    AND scheduled_at IS NOT NULL
                    ORDER BY priority DESC, scheduled_at ASC
                    LIMIT 10
                """, (datetime.now(),))
                
                rows = cursor.fetchall()
                
                for row in rows:
                    notification = self._row_to_notification(row)
                    await self.notification_queue.put(notification)
                    
                    # Remover agendamento
                    cursor.execute("""
                        UPDATE notifications 
                        SET scheduled_at = NULL 
                        WHERE id = ?
                    """, (notification.id,))
                
                if rows:
                    conn.commit()
                    logger.info(f"[NOTIFICATION] {len(rows)} notificações agendadas adicionadas à fila")
                    
        except Exception as e:
            logger.error(f"[NOTIFICATION] Erro ao processar notificações agendadas: {e}")
    
    async def _get_recipient(self, recipient_id: str) -> Optional[NotificationRecipient]:
        """Buscar destinatário por ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM notification_recipients 
                    WHERE id = ? AND is_active = 1
                """, (recipient_id,))
                
                row = cursor.fetchone()
                if row:
                    return NotificationRecipient(
                        id=row[0],
                        name=row[1],
                        email=row[2],
                        phone=row[3],
                        push_token=row[4],
                        preferences=json.loads(row[5]) if row[5] else None,
                        is_active=bool(row[6])
                    )
                    
        except Exception as e:
            logger.error(f"[NOTIFICATION] Erro ao buscar destinatário: {e}")
        
        return None
    
    async def _update_notification_status(self, 
                                        notification_id: str,
                                        status: NotificationStatus,
                                        sent_at: Optional[datetime] = None,
                                        delivered_at: Optional[datetime] = None,
                                        failed_at: Optional[datetime] = None,
                                        error_message: Optional[str] = None):
        """Atualizar status da notificação"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE notifications 
                    SET status = ?, sent_at = ?, delivered_at = ?, 
                        failed_at = ?, error_message = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    status.value,
                    sent_at,
                    delivered_at,
                    failed_at,
                    error_message,
                    datetime.now(),
                    notification_id
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"[NOTIFICATION] Erro ao atualizar status: {e}")
    
    async def _update_notification_retry(self, notification_id: str, retry_count: int):
        """Atualizar contador de tentativas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE notifications 
                    SET retry_count = ?, updated_at = ?
                    WHERE id = ?
                """, (retry_count, datetime.now(), notification_id))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"[NOTIFICATION] Erro ao atualizar retry: {e}")
    
    def _row_to_notification(self, row) -> Notification:
        """Converter linha do banco em Notification"""
        return Notification(
            id=row[0],
            type=NotificationType(row[1]),
            priority=NotificationPriority(row[2]),
            status=NotificationStatus(row[3]),
            recipient_id=row[4],
            template_id=row[5],
            subject=row[6],
            content=row[7],
            html_content=row[8],
            metadata=json.loads(row[9]) if row[9] else None,
            scheduled_at=datetime.fromisoformat(row[10]) if row[10] else None,
            sent_at=datetime.fromisoformat(row[11]) if row[11] else None,
            delivered_at=datetime.fromisoformat(row[12]) if row[12] else None,
            failed_at=datetime.fromisoformat(row[13]) if row[13] else None,
            error_message=row[14],
            retry_count=row[15],
            max_retries=row[16]
        )
    
    async def get_notifications(self, 
                              limit: int = 50,
                              offset: int = 0,
                              status_filter: Optional[NotificationStatus] = None) -> List[Dict]:
        """Buscar notificações"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT n.*, r.name as recipient_name, r.email, r.phone
                    FROM notifications n
                    LEFT JOIN notification_recipients r ON n.recipient_id = r.id
                """
                params = []
                
                if status_filter:
                    query += " WHERE n.status = ?"
                    params.append(status_filter.value)
                
                query += " ORDER BY n.created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                notifications = []
                for row in rows:
                    notifications.append({
                        'id': row[0],
                        'type': row[1],
                        'priority': row[2],
                        'status': row[3],
                        'recipient_id': row[4],
                        'template_id': row[5],
                        'subject': row[6],
                        'content': row[7][:100] + '...' if len(row[7]) > 100 else row[7],
                        'scheduled_at': row[10],
                        'sent_at': row[11],
                        'delivered_at': row[12],
                        'failed_at': row[13],
                        'error_message': row[14],
                        'retry_count': row[15],
                        'created_at': row[17],
                        'recipient_name': row[19],
                        'recipient_email': row[20],
                        'recipient_phone': row[21]
                    })
                
                return notifications
                
        except Exception as e:
            logger.error(f"[NOTIFICATION] Erro ao buscar notificações: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Estatísticas de notificações"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de notificações
                cursor.execute("SELECT COUNT(*) FROM notifications")
                total = cursor.fetchone()[0]
                
                # Por status
                cursor.execute("""
                    SELECT status, COUNT(*) 
                    FROM notifications 
                    GROUP BY status
                """)
                by_status = dict(cursor.fetchall())
                
                # Por tipo
                cursor.execute("""
                    SELECT type, COUNT(*) 
                    FROM notifications 
                    GROUP BY type
                """)
                by_type = dict(cursor.fetchall())
                
                # Por prioridade
                cursor.execute("""
                    SELECT priority, COUNT(*) 
                    FROM notifications 
                    GROUP BY priority
                """)
                by_priority = dict(cursor.fetchall())
                
                # Taxa de sucesso
                sent = by_status.get('sent', 0)
                failed = by_status.get('failed', 0)
                success_rate = (sent / (sent + failed) * 100) if (sent + failed) > 0 else 0
                
                # Últimas 24h
                cursor.execute("""
                    SELECT COUNT(*) FROM notifications 
                    WHERE created_at > datetime('now', '-1 day')
                """)
                last_24h = cursor.fetchone()[0]
                
                return {
                    'total_notifications': total,
                    'by_status': by_status,
                    'by_type': by_type,
                    'by_priority': by_priority,
                    'success_rate': round(success_rate, 2),
                    'last_24h': last_24h,
                    'queue_size': self.notification_queue.qsize(),
                    'is_processing': self.is_processing
                }
                
        except Exception as e:
            logger.error(f"[NOTIFICATION] Erro ao buscar estatísticas: {e}")
            return {}
    
    async def stop_processing(self):
        """Parar processamento de notificações"""
        self.is_processing = False
        logger.info("[NOTIFICATION] Processamento de notificações parado")

# Instância global
notification_manager = NotificationManager(
    db_path=os.path.join(os.path.dirname(__file__), "data", "notifications.db")
)

# Criar diretório data se não existir
os.makedirs(os.path.dirname(notification_manager.db_path), exist_ok=True)
