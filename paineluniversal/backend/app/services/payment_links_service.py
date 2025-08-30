"""
PaymentLinksService - Serviço completo para Links de Pagamento Dinâmicos
Sistema Universal de Gestão de Eventos

Funcionalidades:
- Criação e gestão de links de pagamento
- Processamento de pagamentos via links públicos
- Analytics e métricas em tempo real
- Sistema de notificações e webhooks
- Integração com split de pagamentos
- Validações de segurança
"""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
import uuid
import hashlib
import secrets
import asyncio
import json
import logging
from enum import Enum

# Imports do sistema
from app.models import PaymentLink, PaymentAttempt, User, Event
from app.core.config import settings
from app.services.notification_service import NotificationService
from app.services.payment_processor import PaymentProcessor


logger = logging.getLogger(__name__)


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class LinkStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    COMPLETED = "completed"


class PaymentLinksService:
    """
    Serviço principal para gerenciamento de links de pagamento dinâmicos
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_service = NotificationService()
        self.payment_processor = PaymentProcessor()
        
    async def create_payment_link(
        self, 
        link_id: str, 
        user_id: int, 
        link_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Criar novo link de pagamento com todas as configurações
        """
        try:
            # Validações de segurança
            await self._validate_link_data(link_data, user_id)
            
            # Gerar hash único para URL
            url_hash = self._generate_url_hash(link_id)
            
            # Criar registro do link
            payment_link = PaymentLink(
                id=link_id,
                user_id=user_id,
                url_hash=url_hash,
                title=link_data["title"],
                description=link_data.get("description"),
                amount=link_data.get("amount"),
                min_amount=link_data.get("min_amount"),
                max_amount=link_data.get("max_amount"),
                currency=link_data.get("currency", "BRL"),
                payment_type=link_data["payment_type"],
                expires_at=link_data.get("expires_at"),
                max_uses=link_data.get("max_uses"),
                
                # Personalização
                theme=link_data.get("theme", "default"),
                custom_css=link_data.get("custom_css"),
                logo_url=str(link_data["logo_url"]) if link_data.get("logo_url") else None,
                success_url=str(link_data["success_url"]) if link_data.get("success_url") else None,
                cancel_url=str(link_data["cancel_url"]) if link_data.get("cancel_url") else None,
                
                # Split de pagamentos
                enable_split=link_data.get("enable_split", False),
                split_recipients=json.dumps(link_data.get("split_recipients", [])) if link_data.get("split_recipients") else None,
                
                # Configurações
                collect_customer_info=link_data.get("collect_customer_info", True),
                send_receipt=link_data.get("send_receipt", True),
                allow_installments=link_data.get("allow_installments", False),
                webhook_url=str(link_data["webhook_url"]) if link_data.get("webhook_url") else None,
                
                # Metadata
                metadata=json.dumps(link_data.get("metadata", {})),
                
                # Status
                status=LinkStatus.ACTIVE,
                uses_count=0,
                total_collected=Decimal('0.00'),
                views_count=0,
                
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(payment_link)
            await self.db.commit()
            await self.db.refresh(payment_link)
            
            # Log de auditoria
            logger.info(f"Payment link created: {link_id} by user {user_id}")
            
            # Enviar notificação de criação
            await self.notification_service.send_link_created_notification(
                user_id, link_id, link_data["title"]
            )
            
            return {
                "link_id": link_id,
                "url_hash": url_hash,
                "created_at": payment_link.created_at,
                "updated_at": payment_link.updated_at
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating payment link: {str(e)}")
            raise Exception(f"Erro ao criar link de pagamento: {str(e)}")
    
    async def get_user_payment_links(
        self,
        user_id: int,
        status: Optional[str] = None,
        payment_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Listar links de pagamento do usuário com filtros
        """
        try:
            # Query base
            query = select(PaymentLink).where(PaymentLink.user_id == user_id)
            
            # Aplicar filtros
            if status:
                query = query.where(PaymentLink.status == status)
            if payment_type:
                query = query.where(PaymentLink.payment_type == payment_type)
            
            # Ordenação e paginação
            query = query.order_by(PaymentLink.created_at.desc())
            
            # Contar total
            count_query = select(func.count()).select_from(query.subquery())
            total_count = await self.db.scalar(count_query)
            
            # Aplicar paginação
            query = query.offset(offset).limit(limit)
            result = await self.db.execute(query)
            links = result.scalars().all()
            
            # Preparar resposta
            items = []
            for link in links:
                items.append({
                    "link_id": link.id,
                    "title": link.title,
                    "amount": link.amount,
                    "status": link.status,
                    "payment_type": link.payment_type,
                    "uses_count": link.uses_count,
                    "max_uses": link.max_uses,
                    "total_collected": link.total_collected,
                    "views_count": link.views_count,
                    "expires_at": link.expires_at,
                    "created_at": link.created_at,
                    "updated_at": link.updated_at
                })
            
            # Estatísticas resumidas
            summary_query = select(
                func.count(PaymentLink.id).label('total_links'),
                func.sum(PaymentLink.total_collected).label('total_revenue'),
                func.avg(PaymentLink.uses_count).label('avg_uses')
            ).where(PaymentLink.user_id == user_id)
            
            summary_result = await self.db.execute(summary_query)
            summary = summary_result.first()
            
            return {
                "items": items,
                "total_count": total_count,
                "summary": {
                    "total_links": summary.total_links or 0,
                    "total_revenue": summary.total_revenue or Decimal('0.00'),
                    "avg_uses": float(summary.avg_uses or 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing payment links: {str(e)}")
            raise Exception(f"Erro ao listar links: {str(e)}")
    
    async def get_payment_link_by_id(
        self, 
        link_id: str, 
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Obter detalhes de um link específico
        """
        try:
            query = select(PaymentLink).where(
                and_(
                    PaymentLink.id == link_id,
                    PaymentLink.user_id == user_id
                )
            )
            result = await self.db.execute(query)
            link = result.scalar_one_or_none()
            
            if not link:
                return None
            
            return {
                "link_id": link.id,
                "url_hash": link.url_hash,
                "title": link.title,
                "description": link.description,
                "amount": link.amount,
                "min_amount": link.min_amount,
                "max_amount": link.max_amount,
                "currency": link.currency,
                "payment_type": link.payment_type,
                "status": link.status,
                "expires_at": link.expires_at,
                "max_uses": link.max_uses,
                "uses_count": link.uses_count,
                "total_collected": link.total_collected,
                "views_count": link.views_count,
                
                # Personalização
                "theme": link.theme,
                "custom_css": link.custom_css,
                "logo_url": link.logo_url,
                "success_url": link.success_url,
                "cancel_url": link.cancel_url,
                
                # Split
                "enable_split": link.enable_split,
                "split_recipients": json.loads(link.split_recipients) if link.split_recipients else [],
                
                # Configurações
                "collect_customer_info": link.collect_customer_info,
                "send_receipt": link.send_receipt,
                "allow_installments": link.allow_installments,
                "webhook_url": link.webhook_url,
                
                "metadata": json.loads(link.metadata) if link.metadata else {},
                "created_at": link.created_at,
                "updated_at": link.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting payment link: {str(e)}")
            raise Exception(f"Erro ao consultar link: {str(e)}")
    
    async def get_public_payment_link(self, link_id: str) -> Optional[Dict[str, Any]]:
        """
        Obter link público para processamento de pagamento (sem autenticação)
        """
        try:
            query = select(PaymentLink).where(PaymentLink.id == link_id)
            result = await self.db.execute(query)
            link = result.scalar_one_or_none()
            
            if not link:
                return None
                
            # Verificar se está ativo
            if link.status != LinkStatus.ACTIVE:
                return None
                
            # Verificar expiração
            if link.expires_at and datetime.utcnow() > link.expires_at:
                # Marcar como expirado
                await self.update_link_status(link_id, LinkStatus.EXPIRED)
                return None
                
            # Verificar limite de usos
            if link.max_uses and link.uses_count >= link.max_uses:
                await self.update_link_status(link_id, LinkStatus.COMPLETED)
                return None
            
            return {
                "link_id": link.id,
                "title": link.title,
                "description": link.description,
                "amount": link.amount,
                "min_amount": link.min_amount,
                "max_amount": link.max_amount,
                "currency": link.currency,
                "payment_type": link.payment_type,
                "theme": link.theme,
                "custom_css": link.custom_css,
                "logo_url": link.logo_url,
                "collect_customer_info": link.collect_customer_info,
                "allow_installments": link.allow_installments,
                "expires_at": link.expires_at,
                "max_uses": link.max_uses,
                "uses_count": link.uses_count
            }
            
        except Exception as e:
            logger.error(f"Error getting public payment link: {str(e)}")
            return None
    
    async def process_link_payment(
        self,
        link_id: str,
        payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processar pagamento via link público
        """
        try:
            # Obter link e validar
            link = await self.get_public_payment_link(link_id)
            if not link:
                raise ValueError("Link de pagamento inválido ou expirado")
            
            # Validar dados de pagamento
            await self._validate_payment_data(link, payment_data)
            
            # Gerar ID único para tentativa
            attempt_id = str(uuid.uuid4())
            
            # Determinar valor final
            final_amount = self._determine_payment_amount(link, payment_data)
            
            # Criar registro de tentativa
            payment_attempt = PaymentAttempt(
                id=attempt_id,
                link_id=link_id,
                amount=final_amount,
                customer_name=payment_data.get("customer_name"),
                customer_email=payment_data.get("customer_email"),
                payment_method=payment_data.get("payment_method"),
                status=PaymentStatus.PENDING,
                ip_address=payment_data.get("ip_address"),
                user_agent=payment_data.get("user_agent"),
                created_at=datetime.utcnow()
            )
            
            self.db.add(payment_attempt)
            await self.db.commit()
            
            # Processar pagamento com gateway
            payment_result = await self.payment_processor.process_payment({
                "amount": final_amount,
                "currency": link["currency"],
                "payment_method": payment_data["payment_method"],
                "customer_name": payment_data.get("customer_name"),
                "customer_email": payment_data.get("customer_email"),
                "description": f"Pagamento via link: {link['title']}",
                "metadata": {
                    "link_id": link_id,
                    "attempt_id": attempt_id
                }
            })
            
            # Atualizar status da tentativa
            await self._update_payment_attempt_status(
                attempt_id, 
                PaymentStatus.PROCESSING,
                payment_result.get("transaction_id")
            )
            
            # Se pagamento foi aprovado imediatamente
            if payment_result.get("status") == "approved":
                await self._complete_payment(link_id, attempt_id, payment_result)
            
            # Enviar webhook se configurado
            if link.get("webhook_url"):
                await self.notification_service.send_webhook(
                    link["webhook_url"],
                    {
                        "event": "payment_initiated",
                        "link_id": link_id,
                        "attempt_id": attempt_id,
                        "amount": float(final_amount),
                        "customer": {
                            "name": payment_data.get("customer_name"),
                            "email": payment_data.get("customer_email")
                        }
                    }
                )
            
            return {
                "payment_id": payment_result["payment_id"],
                "status": payment_result["status"],
                "redirect_url": payment_result.get("redirect_url"),
                "qr_code": payment_result.get("qr_code"),
                "attempt_id": attempt_id
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error processing link payment: {str(e)}")
            raise Exception(f"Erro ao processar pagamento: {str(e)}")
    
    async def get_link_analytics(
        self,
        link_id: str,
        user_id: int,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Gerar analytics detalhado de um link
        """
        try:
            # Verificar propriedade do link
            link = await self.get_payment_link_by_id(link_id, user_id)
            if not link:
                raise ValueError("Link não encontrado")
            
            start_date = datetime.utcnow() - timedelta(days=period_days)
            
            # Estatísticas gerais
            stats_query = select(
                func.count(PaymentAttempt.id).label('total_attempts'),
                func.count().filter(PaymentAttempt.status == PaymentStatus.COMPLETED).label('successful_payments'),
                func.sum(PaymentAttempt.amount).filter(PaymentAttempt.status == PaymentStatus.COMPLETED).label('total_collected'),
                func.avg(PaymentAttempt.amount).filter(PaymentAttempt.status == PaymentStatus.COMPLETED).label('avg_amount')
            ).where(
                and_(
                    PaymentAttempt.link_id == link_id,
                    PaymentAttempt.created_at >= start_date
                )
            )
            
            stats_result = await self.db.execute(stats_query)
            stats = stats_result.first()
            
            # Breakdown por método de pagamento
            payment_methods_query = select(
                PaymentAttempt.payment_method,
                func.count(PaymentAttempt.id).label('count')
            ).where(
                and_(
                    PaymentAttempt.link_id == link_id,
                    PaymentAttempt.status == PaymentStatus.COMPLETED,
                    PaymentAttempt.created_at >= start_date
                )
            ).group_by(PaymentAttempt.payment_method)
            
            payment_methods_result = await self.db.execute(payment_methods_query)
            payment_methods = {row.payment_method: row.count for row in payment_methods_result}
            
            # Estatísticas diárias
            daily_stats = await self._get_daily_stats(link_id, start_date)
            
            # Calcular taxa de conversão
            conversion_rate = 0.0
            if link["views_count"] > 0 and stats.successful_payments:
                conversion_rate = (stats.successful_payments / link["views_count"]) * 100
            
            return {
                "link_id": link_id,
                "period_days": period_days,
                "total_views": link["views_count"],
                "total_attempts": stats.total_attempts or 0,
                "successful_payments": stats.successful_payments or 0,
                "total_collected": stats.total_collected or Decimal('0.00'),
                "avg_amount": stats.avg_amount or Decimal('0.00'),
                "conversion_rate": round(conversion_rate, 2),
                "payment_methods_breakdown": payment_methods,
                "daily_stats": daily_stats
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            raise Exception(f"Erro ao gerar analytics: {str(e)}")
    
    async def get_link_payments(
        self,
        link_id: str,
        user_id: int,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Listar pagamentos de um link específico
        """
        try:
            # Verificar propriedade do link
            link = await self.get_payment_link_by_id(link_id, user_id)
            if not link:
                raise ValueError("Link não encontrado")
            
            # Query base
            query = select(PaymentAttempt).where(PaymentAttempt.link_id == link_id)
            
            # Aplicar filtros
            if status:
                query = query.where(PaymentAttempt.status == status)
            if start_date:
                query = query.where(PaymentAttempt.created_at >= start_date)
            if end_date:
                query = query.where(PaymentAttempt.created_at <= end_date)
            
            # Contar total
            count_query = select(func.count()).select_from(query.subquery())
            total_count = await self.db.scalar(count_query)
            
            # Ordenação e paginação
            query = query.order_by(PaymentAttempt.created_at.desc()).offset(offset).limit(limit)
            result = await self.db.execute(query)
            payments = result.scalars().all()
            
            # Preparar itens
            items = []
            for payment in payments:
                items.append({
                    "attempt_id": payment.id,
                    "amount": payment.amount,
                    "status": payment.status,
                    "payment_method": payment.payment_method,
                    "customer_name": payment.customer_name,
                    "customer_email": payment.customer_email,
                    "transaction_id": payment.transaction_id,
                    "created_at": payment.created_at,
                    "completed_at": payment.completed_at
                })
            
            # Resumo
            summary_query = select(
                func.count(PaymentAttempt.id).filter(PaymentAttempt.status == PaymentStatus.COMPLETED).label('completed_count'),
                func.sum(PaymentAttempt.amount).filter(PaymentAttempt.status == PaymentStatus.COMPLETED).label('total_amount')
            ).where(PaymentAttempt.link_id == link_id)
            
            if start_date:
                summary_query = summary_query.where(PaymentAttempt.created_at >= start_date)
            if end_date:
                summary_query = summary_query.where(PaymentAttempt.created_at <= end_date)
            
            summary_result = await self.db.execute(summary_query)
            summary = summary_result.first()
            
            return {
                "items": items,
                "total_count": total_count,
                "summary": {
                    "completed_payments": summary.completed_count or 0,
                    "total_amount": summary.total_amount or Decimal('0.00')
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing link payments: {str(e)}")
            raise Exception(f"Erro ao listar pagamentos: {str(e)}")
    
    async def increment_link_views(self, link_id: str) -> None:
        """
        Incrementar contador de visualizações do link
        """
        try:
            query = update(PaymentLink).where(
                PaymentLink.id == link_id
            ).values(
                views_count=PaymentLink.views_count + 1,
                updated_at=datetime.utcnow()
            )
            
            await self.db.execute(query)
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Error incrementing link views: {str(e)}")
    
    async def update_payment_link(
        self,
        link_id: str,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Atualizar link de pagamento existente
        """
        try:
            # Verificar propriedade
            existing_link = await self.get_payment_link_by_id(link_id, user_id)
            if not existing_link:
                raise ValueError("Link não encontrado")
            
            # Filtrar campos permitidos para atualização
            allowed_fields = {
                'title', 'description', 'expires_at', 'max_uses',
                'theme', 'custom_css', 'logo_url', 'success_url', 'cancel_url',
                'webhook_url', 'metadata'
            }
            
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            filtered_updates['updated_at'] = datetime.utcnow()
            
            # Atualizar registro
            query = update(PaymentLink).where(
                and_(
                    PaymentLink.id == link_id,
                    PaymentLink.user_id == user_id
                )
            ).values(**filtered_updates)
            
            await self.db.execute(query)
            await self.db.commit()
            
            # Retornar link atualizado
            return await self.get_payment_link_by_id(link_id, user_id)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating payment link: {str(e)}")
            raise Exception(f"Erro ao atualizar link: {str(e)}")
    
    async def deactivate_payment_link(self, link_id: str, user_id: int) -> None:
        """
        Desativar link de pagamento
        """
        try:
            query = update(PaymentLink).where(
                and_(
                    PaymentLink.id == link_id,
                    PaymentLink.user_id == user_id
                )
            ).values(
                status=LinkStatus.INACTIVE,
                updated_at=datetime.utcnow()
            )
            
            result = await self.db.execute(query)
            if result.rowcount == 0:
                raise ValueError("Link não encontrado")
            
            await self.db.commit()
            
            logger.info(f"Payment link deactivated: {link_id}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deactivating payment link: {str(e)}")
            raise Exception(f"Erro ao desativar link: {str(e)}")
    
    # Métodos auxiliares privados
    
    def _generate_url_hash(self, link_id: str) -> str:
        """Gerar hash único para URL do link"""
        salt = secrets.token_hex(16)
        return hashlib.sha256(f"{link_id}{salt}".encode()).hexdigest()[:12]
    
    async def _validate_link_data(self, link_data: Dict[str, Any], user_id: int) -> None:
        """Validar dados do link antes da criação"""
        # Validar limites do usuário
        user_links_count = await self.db.scalar(
            select(func.count(PaymentLink.id)).where(PaymentLink.user_id == user_id)
        )
        
        # Limite baseado no plano do usuário (implementar lógica de planos)
        max_links = 100  # Valor padrão
        if user_links_count >= max_links:
            raise ValueError(f"Limite de {max_links} links atingido")
        
        # Validações de valor
        if link_data["payment_type"] == "single" and not link_data.get("amount"):
            raise ValueError("Pagamento único deve ter valor definido")
        
        if link_data.get("min_amount") and link_data.get("max_amount"):
            if link_data["min_amount"] >= link_data["max_amount"]:
                raise ValueError("Valor mínimo deve ser menor que o máximo")
    
    def _determine_payment_amount(self, link: Dict[str, Any], payment_data: Dict[str, Any]) -> Decimal:
        """Determinar valor final do pagamento"""
        if link["payment_type"] == "flexible":
            amount = Decimal(str(payment_data.get("amount", 0)))
            
            if link.get("min_amount") and amount < link["min_amount"]:
                raise ValueError(f"Valor mínimo: {link['min_amount']}")
            if link.get("max_amount") and amount > link["max_amount"]:
                raise ValueError(f"Valor máximo: {link['max_amount']}")
            
            return amount
        else:
            return link["amount"]
    
    async def _validate_payment_data(self, link: Dict[str, Any], payment_data: Dict[str, Any]) -> None:
        """Validar dados de pagamento"""
        required_fields = []
        
        if link.get("collect_customer_info"):
            required_fields.extend(["customer_name", "customer_email"])
        
        for field in required_fields:
            if not payment_data.get(field):
                raise ValueError(f"Campo obrigatório: {field}")
        
        if not payment_data.get("payment_method"):
            raise ValueError("Método de pagamento é obrigatório")
    
    async def _update_payment_attempt_status(
        self,
        attempt_id: str,
        status: PaymentStatus,
        transaction_id: Optional[str] = None
    ) -> None:
        """Atualizar status de tentativa de pagamento"""
        updates = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if transaction_id:
            updates["transaction_id"] = transaction_id
        
        if status == PaymentStatus.COMPLETED:
            updates["completed_at"] = datetime.utcnow()
        
        query = update(PaymentAttempt).where(
            PaymentAttempt.id == attempt_id
        ).values(**updates)
        
        await self.db.execute(query)
        await self.db.commit()
    
    async def _complete_payment(
        self,
        link_id: str,
        attempt_id: str,
        payment_result: Dict[str, Any]
    ) -> None:
        """Completar pagamento e atualizar estatísticas"""
        # Atualizar tentativa
        await self._update_payment_attempt_status(
            attempt_id, 
            PaymentStatus.COMPLETED,
            payment_result.get("transaction_id")
        )
        
        # Atualizar estatísticas do link
        attempt = await self.db.scalar(
            select(PaymentAttempt).where(PaymentAttempt.id == attempt_id)
        )
        
        query = update(PaymentLink).where(
            PaymentLink.id == link_id
        ).values(
            uses_count=PaymentLink.uses_count + 1,
            total_collected=PaymentLink.total_collected + attempt.amount,
            updated_at=datetime.utcnow()
        )
        
        await self.db.execute(query)
        await self.db.commit()
    
    async def _get_daily_stats(self, link_id: str, start_date: datetime) -> List[Dict[str, Any]]:
        """Obter estatísticas diárias para analytics"""
        query = select(
            func.date(PaymentAttempt.created_at).label('date'),
            func.count(PaymentAttempt.id).label('attempts'),
            func.count(PaymentAttempt.id).filter(PaymentAttempt.status == PaymentStatus.COMPLETED).label('completed'),
            func.sum(PaymentAttempt.amount).filter(PaymentAttempt.status == PaymentStatus.COMPLETED).label('revenue')
        ).where(
            and_(
                PaymentAttempt.link_id == link_id,
                PaymentAttempt.created_at >= start_date
            )
        ).group_by(func.date(PaymentAttempt.created_at)).order_by(func.date(PaymentAttempt.created_at))
        
        result = await self.db.execute(query)
        
        daily_stats = []
        for row in result:
            daily_stats.append({
                "date": row.date.isoformat(),
                "attempts": row.attempts,
                "completed_payments": row.completed,
                "revenue": float(row.revenue or 0)
            })
        
        return daily_stats
    
    async def update_link_status(self, link_id: str, status: LinkStatus) -> None:
        """Atualizar status do link"""
        query = update(PaymentLink).where(
            PaymentLink.id == link_id
        ).values(
            status=status,
            updated_at=datetime.utcnow()
        )
        
        await self.db.execute(query)
        await self.db.commit()