"""
Banking Webhook Service - Advanced Webhook Processing and Reconciliation
Sistema Universal de Gestão de Eventos

Comprehensive webhook handling for:
- Multi-gateway banking callbacks
- Payment status updates
- PIX transaction notifications
- Card payment confirmations
- Automated reconciliation
- Fraud alerts and security notifications
- Real-time balance updates
- Transaction dispute handling
"""

from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import asyncio
import uuid
import json
import hmac
import hashlib
import base64
from urllib.parse import parse_qs

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, desc, select
import httpx
import redis
from loguru import logger
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from app.core.config import get_settings
from app.core.database import get_db
from app.services.banking_service import BankingService, BankingGateway, PaymentMethod, TransactionStatus
from app.services.digital_account_service import EnhancedDigitalAccountService
from app.services.pix_service import PIXService, PIXStatus
from app.services.payment_processor_service import PaymentProcessorService
from app.services.notification_service import NotificationService
from app.services.validation_service import ValidationService


class WebhookEventType(str, Enum):
    """Webhook event types"""
    PAYMENT_CREATED = "payment.created"
    PAYMENT_AUTHORIZED = "payment.authorized"
    PAYMENT_CAPTURED = "payment.captured"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_CANCELLED = "payment.cancelled"
    PAYMENT_REFUNDED = "payment.refunded"
    PAYMENT_DISPUTED = "payment.disputed"
    
    PIX_CREATED = "pix.created"
    PIX_PAID = "pix.paid"
    PIX_EXPIRED = "pix.expired"
    PIX_CANCELLED = "pix.cancelled"
    PIX_REFUNDED = "pix.refunded"
    
    TRANSFER_INITIATED = "transfer.initiated"
    TRANSFER_COMPLETED = "transfer.completed"
    TRANSFER_FAILED = "transfer.failed"
    
    ACCOUNT_BLOCKED = "account.blocked"
    ACCOUNT_UNBLOCKED = "account.unblocked"
    
    FRAUD_DETECTED = "fraud.detected"
    CHARGEBACK_INITIATED = "chargeback.initiated"
    
    RECONCILIATION_COMPLETED = "reconciliation.completed"
    BALANCE_UPDATED = "balance.updated"


class WebhookStatus(str, Enum):
    """Webhook processing status"""
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    RETRY = "retry"
    IGNORED = "ignored"


class WebhookProcessingError(Exception):
    """Webhook processing error"""
    def __init__(self, message: str, event_type: str = None, gateway: str = None):
        self.message = message
        self.event_type = event_type
        self.gateway = gateway
        super().__init__(self.message)


class BankingWebhookService:
    """
    Comprehensive banking webhook service with advanced processing and reconciliation
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.redis_client = self._init_redis()
        
        # Initialize services
        self.banking_service = BankingService(db)
        self.account_service = EnhancedDigitalAccountService(db)
        self.pix_service = PIXService(db)
        self.payment_processor = PaymentProcessorService(db)
        self.notification_service = NotificationService(db)
        self.validation_service = ValidationService()
        
        # Gateway webhook configurations
        self.gateway_configs = self._init_gateway_configs()
        
        # Event handlers registry
        self.event_handlers = self._register_event_handlers()
        
        # Reconciliation settings
        self.reconciliation_config = {
            "batch_size": 100,
            "retry_attempts": 3,
            "reconciliation_window_hours": 24,
            "auto_reconcile_enabled": True
        }
    
    def _init_redis(self) -> redis.Redis:
        """Initialize Redis for webhook caching and deduplication"""
        try:
            return redis.Redis(
                host=self.settings.REDIS_HOST,
                port=self.settings.REDIS_PORT,
                password=self.settings.REDIS_PASSWORD,
                db=4,  # Separate DB for webhooks
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis connection failed for webhook service: {e}")
            return None
    
    def _init_gateway_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize webhook configurations for each gateway"""
        return {
            BankingGateway.PICPAY: {
                "signature_header": "x-picpay-signature",
                "signature_algorithm": "sha256",
                "webhook_secret": self.settings.PICPAY_WEBHOOK_SECRET,
                "verify_ssl": True,
                "timeout_seconds": 30
            },
            BankingGateway.PAGSEGURO: {
                "signature_header": "x-pagseguro-signature",
                "signature_algorithm": "sha256",
                "webhook_secret": self.settings.PAGSEGURO_WEBHOOK_SECRET,
                "verify_ssl": True,
                "timeout_seconds": 30
            },
            BankingGateway.ASAAS: {
                "signature_header": "asaas-access-token",
                "signature_algorithm": "sha256",
                "webhook_secret": self.settings.ASAAS_WEBHOOK_SECRET,
                "verify_ssl": True,
                "timeout_seconds": 30
            },
            BankingGateway.MERCADOPAGO: {
                "signature_header": "x-signature",
                "signature_algorithm": "sha256",
                "webhook_secret": self.settings.MERCADOPAGO_WEBHOOK_SECRET,
                "verify_ssl": True,
                "timeout_seconds": 30
            }
        }
    
    def _register_event_handlers(self) -> Dict[WebhookEventType, Callable]:
        """Register event handlers for different webhook types"""
        return {
            WebhookEventType.PAYMENT_COMPLETED: self._handle_payment_completed,
            WebhookEventType.PAYMENT_FAILED: self._handle_payment_failed,
            WebhookEventType.PAYMENT_REFUNDED: self._handle_payment_refunded,
            WebhookEventType.PAYMENT_DISPUTED: self._handle_payment_disputed,
            
            WebhookEventType.PIX_PAID: self._handle_pix_paid,
            WebhookEventType.PIX_EXPIRED: self._handle_pix_expired,
            WebhookEventType.PIX_REFUNDED: self._handle_pix_refunded,
            
            WebhookEventType.TRANSFER_COMPLETED: self._handle_transfer_completed,
            WebhookEventType.TRANSFER_FAILED: self._handle_transfer_failed,
            
            WebhookEventType.FRAUD_DETECTED: self._handle_fraud_detected,
            WebhookEventType.CHARGEBACK_INITIATED: self._handle_chargeback,
            
            WebhookEventType.BALANCE_UPDATED: self._handle_balance_updated
        }
    
    # ================================
    # MAIN WEBHOOK PROCESSING
    # ================================
    
    async def process_webhook(
        self,
        gateway: BankingGateway,
        headers: Dict[str, str],
        payload: Dict[str, Any],
        raw_body: str = None
    ) -> Dict[str, Any]:
        """
        Main webhook processing entry point with comprehensive handling
        """
        webhook_id = str(uuid.uuid4())
        
        try:
            # Log webhook reception
            await self._log_webhook_received(webhook_id, gateway, headers, payload)
            
            # Verify webhook signature for security
            await self._verify_webhook_signature(gateway, headers, raw_body or json.dumps(payload))
            
            # Check for duplicate webhooks (idempotency)
            if await self._is_duplicate_webhook(gateway, payload):
                logger.info(f"Duplicate webhook ignored: {webhook_id}")
                return {"status": WebhookStatus.IGNORED, "message": "Duplicate webhook"}
            
            # Extract and normalize webhook data
            normalized_data = await self._normalize_webhook_data(gateway, payload)
            
            # Determine event type
            event_type = await self._determine_event_type(gateway, normalized_data)
            
            # Store webhook for audit and retry purposes
            await self._store_webhook_record(webhook_id, gateway, event_type, normalized_data)
            
            # Process webhook based on event type
            processing_result = await self._process_webhook_event(webhook_id, event_type, normalized_data)
            
            # Update webhook status
            await self._update_webhook_status(webhook_id, WebhookStatus.PROCESSED)
            
            # Trigger reconciliation if needed
            if processing_result.get("trigger_reconciliation"):
                await self._trigger_reconciliation(gateway, normalized_data.get("account_id"))
            
            # Send success response
            return {
                "webhook_id": webhook_id,
                "status": WebhookStatus.PROCESSED,
                "event_type": event_type,
                "processed_at": datetime.utcnow().isoformat(),
                "result": processing_result
            }
            
        except Exception as e:
            logger.error(f"Webhook processing failed for {webhook_id}: {e}")
            
            # Update webhook status to failed
            await self._update_webhook_status(webhook_id, WebhookStatus.FAILED, str(e))
            
            # Schedule retry if appropriate
            if self._should_retry_webhook(e):
                await self._schedule_webhook_retry(webhook_id)
            
            raise WebhookProcessingError(f"Webhook processing failed: {str(e)}", gateway=gateway)
    
    async def _verify_webhook_signature(
        self,
        gateway: BankingGateway,
        headers: Dict[str, str],
        body: str
    ):
        """
        Verify webhook signature for security and authenticity
        """
        try:
            config = self.gateway_configs.get(gateway)
            if not config:
                raise WebhookProcessingError(f"No configuration found for gateway: {gateway}")
            
            signature_header = config["signature_header"]
            webhook_secret = config["webhook_secret"]
            algorithm = config["signature_algorithm"]
            
            # Get signature from headers
            signature = headers.get(signature_header) or headers.get(signature_header.upper())
            if not signature:
                raise WebhookProcessingError(f"Missing signature header: {signature_header}")
            
            # Calculate expected signature
            if gateway == BankingGateway.MERCADOPAGO:
                # MercadoPago uses different signature format
                expected_signature = await self._calculate_mercadopago_signature(body, webhook_secret)
            else:
                # Standard HMAC signature
                expected_signature = hmac.new(
                    webhook_secret.encode(),
                    body.encode(),
                    getattr(hashlib, algorithm)
                ).hexdigest()
            
            # Compare signatures (constant time comparison)
            if not hmac.compare_digest(signature, expected_signature):
                raise WebhookProcessingError("Invalid webhook signature")
            
            logger.debug(f"Webhook signature verified for gateway: {gateway}")
            
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise WebhookProcessingError(f"Signature verification failed: {str(e)}")
    
    async def _normalize_webhook_data(
        self,
        gateway: BankingGateway,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Normalize webhook data from different gateways into a standard format
        """
        if gateway == BankingGateway.PICPAY:
            return await self._normalize_picpay_webhook(payload)
        elif gateway == BankingGateway.PAGSEGURO:
            return await self._normalize_pagseguro_webhook(payload)
        elif gateway == BankingGateway.ASAAS:
            return await self._normalize_asaas_webhook(payload)
        elif gateway == BankingGateway.MERCADOPAGO:
            return await self._normalize_mercadopago_webhook(payload)
        else:
            # Generic normalization
            return {
                "transaction_id": payload.get("id") or payload.get("transaction_id"),
                "reference_id": payload.get("reference_id"),
                "amount": Decimal(str(payload.get("amount", "0.00"))),
                "currency": payload.get("currency", "BRL"),
                "status": payload.get("status"),
                "payment_method": payload.get("payment_method"),
                "customer_data": payload.get("customer", {}),
                "metadata": payload.get("metadata", {}),
                "created_at": payload.get("created_at"),
                "updated_at": payload.get("updated_at"),
                "raw_data": payload
            }
    
    async def _process_webhook_event(
        self,
        webhook_id: str,
        event_type: WebhookEventType,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process webhook event using registered handlers
        """
        try:
            handler = self.event_handlers.get(event_type)
            if not handler:
                logger.warning(f"No handler found for event type: {event_type}")
                return {"status": "no_handler", "message": f"No handler for {event_type}"}
            
            # Execute handler
            result = await handler(data)
            
            # Log successful processing
            await self._log_webhook_processed(webhook_id, event_type, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Event handler failed for {event_type}: {e}")
            raise WebhookProcessingError(f"Event handling failed: {str(e)}", event_type=event_type)
    
    # ================================
    # EVENT HANDLERS
    # ================================
    
    async def _handle_payment_completed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment completion webhook"""
        try:
            transaction_id = data.get("transaction_id")
            amount = data.get("amount")
            account_id = data.get("customer_data", {}).get("account_id")
            
            if not all([transaction_id, amount, account_id]):
                raise ValueError("Missing required payment completion data")
            
            # Update account balance
            await self.account_service.process_atomic_transaction(
                account_id=account_id,
                transaction_type="deposit",
                amount=amount,
                description=f"Payment completed - {transaction_id}",
                reference_id=transaction_id,
                metadata={"webhook_event": "payment_completed", "gateway_data": data}
            )
            
            # Send completion notification
            await self.notification_service.send_payment_completion_notification(
                account_id=account_id,
                transaction_id=transaction_id,
                amount=amount
            )
            
            return {
                "action": "payment_processed",
                "transaction_id": transaction_id,
                "amount": amount,
                "account_updated": True,
                "trigger_reconciliation": True
            }
            
        except Exception as e:
            logger.error(f"Payment completion handling failed: {e}")
            raise WebhookProcessingError(f"Payment completion failed: {str(e)}")
    
    async def _handle_pix_paid(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PIX payment confirmation"""
        try:
            pix_id = data.get("reference_id")
            amount = data.get("amount")
            payer_info = data.get("payer_info", {})
            
            # Process PIX payment
            result = await self.pix_service.process_pix_payment(
                pix_id=pix_id,
                payer_info=payer_info,
                amount=amount
            )
            
            # Update PIX status cache
            if self.redis_client:
                await self._update_pix_status_cache(pix_id, PIXStatus.COMPLETED)
            
            return {
                "action": "pix_processed",
                "pix_id": pix_id,
                "amount": amount,
                "payment_result": result,
                "trigger_reconciliation": True
            }
            
        except Exception as e:
            logger.error(f"PIX payment handling failed: {e}")
            raise WebhookProcessingError(f"PIX payment failed: {str(e)}")
    
    async def _handle_payment_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment failure"""
        try:
            transaction_id = data.get("transaction_id")
            failure_reason = data.get("failure_reason", "Unknown error")
            account_id = data.get("customer_data", {}).get("account_id")
            
            # Log payment failure
            await self._log_payment_failure(transaction_id, failure_reason, data)
            
            # Send failure notification
            if account_id:
                await self.notification_service.send_payment_failure_notification(
                    account_id=account_id,
                    transaction_id=transaction_id,
                    reason=failure_reason
                )
            
            return {
                "action": "payment_failed_processed",
                "transaction_id": transaction_id,
                "failure_reason": failure_reason,
                "notification_sent": bool(account_id)
            }
            
        except Exception as e:
            logger.error(f"Payment failure handling failed: {e}")
            raise WebhookProcessingError(f"Payment failure handling failed: {str(e)}")
    
    async def _handle_fraud_detected(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fraud detection alerts"""
        try:
            account_id = data.get("account_id")
            fraud_type = data.get("fraud_type", "unknown")
            risk_score = data.get("risk_score", 0)
            transaction_id = data.get("transaction_id")
            
            # Block account if high risk
            if risk_score >= 80:
                await self.account_service.block_account(
                    account_id=account_id,
                    reason=f"Fraud detected: {fraud_type}",
                    blocked_by=0  # System block
                )
            
            # Send fraud alert
            await self.notification_service.send_fraud_alert(
                account_id=account_id,
                fraud_type=fraud_type,
                risk_score=risk_score,
                transaction_id=transaction_id
            )
            
            # Log fraud event
            await self._log_fraud_event(account_id, fraud_type, risk_score, data)
            
            return {
                "action": "fraud_processed",
                "account_id": account_id,
                "fraud_type": fraud_type,
                "risk_score": risk_score,
                "account_blocked": risk_score >= 80
            }
            
        except Exception as e:
            logger.error(f"Fraud detection handling failed: {e}")
            raise WebhookProcessingError(f"Fraud handling failed: {str(e)}")
    
    # ================================
    # AUTOMATED RECONCILIATION
    # ================================
    
    async def run_automated_reconciliation(
        self,
        gateway: BankingGateway = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Run automated reconciliation process
        """
        try:
            # Set default date range (last 24 hours)
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(hours=self.reconciliation_config["reconciliation_window_hours"])
            
            reconciliation_id = str(uuid.uuid4())
            
            logger.info(f"Starting reconciliation {reconciliation_id} for {gateway or 'all gateways'}")
            
            # Get gateways to reconcile
            gateways_to_reconcile = [gateway] if gateway else list(self.gateway_configs.keys())
            
            reconciliation_results = []
            
            for gw in gateways_to_reconcile:
                gateway_result = await self._reconcile_gateway_transactions(
                    gw, start_date, end_date, reconciliation_id
                )
                reconciliation_results.append(gateway_result)
            
            # Aggregate results
            total_processed = sum(r["transactions_processed"] for r in reconciliation_results)
            total_discrepancies = sum(r["discrepancies_found"] for r in reconciliation_results)
            total_resolved = sum(r["discrepancies_resolved"] for r in reconciliation_results)
            
            # Store reconciliation summary
            reconciliation_summary = {
                "reconciliation_id": reconciliation_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "gateways_processed": len(gateways_to_reconcile),
                "total_transactions_processed": total_processed,
                "total_discrepancies_found": total_discrepancies,
                "total_discrepancies_resolved": total_resolved,
                "success_rate": (total_resolved / total_discrepancies) if total_discrepancies > 0 else 1.0,
                "gateway_results": reconciliation_results,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            await self._store_reconciliation_report(reconciliation_summary)
            
            logger.info(f"Reconciliation {reconciliation_id} completed: {total_processed} transactions, {total_discrepancies} discrepancies found, {total_resolved} resolved")
            
            return reconciliation_summary
            
        except Exception as e:
            logger.error(f"Automated reconciliation failed: {e}")
            raise WebhookProcessingError(f"Reconciliation failed: {str(e)}")
    
    async def _reconcile_gateway_transactions(
        self,
        gateway: BankingGateway,
        start_date: datetime,
        end_date: datetime,
        reconciliation_id: str
    ) -> Dict[str, Any]:
        """
        Reconcile transactions for a specific gateway
        """
        try:
            # Get local transactions
            local_transactions = await self._get_local_transactions(gateway, start_date, end_date)
            
            # Get gateway transactions
            gateway_transactions = await self._fetch_gateway_transactions(gateway, start_date, end_date)
            
            # Compare and find discrepancies
            discrepancies = await self._compare_transactions(local_transactions, gateway_transactions)
            
            # Resolve discrepancies
            resolved_count = 0
            for discrepancy in discrepancies:
                try:
                    await self._resolve_discrepancy(discrepancy, gateway)
                    resolved_count += 1
                except Exception as e:
                    logger.error(f"Failed to resolve discrepancy {discrepancy['id']}: {e}")
            
            return {
                "gateway": gateway,
                "transactions_processed": len(local_transactions) + len(gateway_transactions),
                "discrepancies_found": len(discrepancies),
                "discrepancies_resolved": resolved_count,
                "local_transactions_count": len(local_transactions),
                "gateway_transactions_count": len(gateway_transactions)
            }
            
        except Exception as e:
            logger.error(f"Gateway reconciliation failed for {gateway}: {e}")
            return {
                "gateway": gateway,
                "transactions_processed": 0,
                "discrepancies_found": 0,
                "discrepancies_resolved": 0,
                "error": str(e)
            }
    
    # ================================
    # HELPER METHODS
    # ================================
    
    async def _is_duplicate_webhook(
        self,
        gateway: BankingGateway,
        payload: Dict[str, Any]
    ) -> bool:
        """Check if webhook is a duplicate using Redis"""
        if not self.redis_client:
            return False
        
        # Create unique identifier for webhook
        webhook_hash = hashlib.sha256(
            f"{gateway}:{json.dumps(payload, sort_keys=True)}".encode()
        ).hexdigest()
        
        cache_key = f"webhook_processed:{webhook_hash}"
        
        # Check if already processed
        if await self.redis_client.get(cache_key):
            return True
        
        # Mark as processed (expire after 24 hours)
        await self.redis_client.setex(cache_key, 86400, "processed")
        return False
    
    async def _determine_event_type(
        self,
        gateway: BankingGateway,
        data: Dict[str, Any]
    ) -> WebhookEventType:
        """Determine webhook event type based on gateway and data"""
        status = data.get("status", "").lower()
        payment_method = data.get("payment_method", "").lower()
        
        # PIX events
        if "pix" in payment_method:
            if status in ["paid", "completed"]:
                return WebhookEventType.PIX_PAID
            elif status in ["expired", "cancelled"]:
                return WebhookEventType.PIX_EXPIRED
            elif status == "refunded":
                return WebhookEventType.PIX_REFUNDED
        
        # Payment events
        if status in ["completed", "paid", "approved"]:
            return WebhookEventType.PAYMENT_COMPLETED
        elif status in ["failed", "declined", "rejected"]:
            return WebhookEventType.PAYMENT_FAILED
        elif status == "refunded":
            return WebhookEventType.PAYMENT_REFUNDED
        elif status in ["disputed", "chargeback"]:
            return WebhookEventType.PAYMENT_DISPUTED
        
        # Default to generic payment event
        return WebhookEventType.PAYMENT_COMPLETED
    
    # Gateway-specific normalization methods (simplified for brevity)
    async def _normalize_picpay_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize PicPay webhook data"""
        return {
            "transaction_id": payload.get("referenceId"),
            "amount": Decimal(str(payload.get("value", "0.00"))),
            "status": payload.get("status"),
            "payment_method": "pix" if payload.get("paymentMethod") == "PIX" else "card",
            "raw_data": payload
        }
    
    async def _normalize_pagseguro_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize PagSeguro webhook data"""
        return {
            "transaction_id": payload.get("code"),
            "amount": Decimal(str(payload.get("grossAmount", "0.00"))),
            "status": payload.get("status"),
            "payment_method": payload.get("paymentMethod", {}).get("type", "unknown"),
            "raw_data": payload
        }
    
    async def _normalize_asaas_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Asaas webhook data"""
        return {
            "transaction_id": payload.get("id"),
            "amount": Decimal(str(payload.get("value", "0.00"))),
            "status": payload.get("status"),
            "payment_method": payload.get("billingType", "unknown"),
            "raw_data": payload
        }
    
    async def _normalize_mercadopago_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize MercadoPago webhook data"""
        return {
            "transaction_id": payload.get("data", {}).get("id"),
            "amount": Decimal(str(payload.get("transaction_amount", "0.00"))),
            "status": payload.get("status"),
            "payment_method": payload.get("payment_method_id", "unknown"),
            "raw_data": payload
        }
    
    # Additional helper methods for logging, storage, and processing
    async def _log_webhook_received(self, webhook_id: str, gateway: BankingGateway, headers: Dict[str, str], payload: Dict[str, Any]):
        """Log webhook reception"""
        logger.info(f"Webhook received: {webhook_id} from {gateway}")
    
    async def _store_webhook_record(self, webhook_id: str, gateway: BankingGateway, event_type: WebhookEventType, data: Dict[str, Any]):
        """Store webhook record for audit"""
        # Implementation would store in database
        pass
    
    async def _update_webhook_status(self, webhook_id: str, status: WebhookStatus, error_message: str = None):
        """Update webhook processing status"""
        # Implementation would update database
        pass
    
    async def _should_retry_webhook(self, error: Exception) -> bool:
        """Determine if webhook should be retried"""
        # Retry on temporary errors, not on validation errors
        return not isinstance(error, (ValueError, WebhookProcessingError))
    
    async def _calculate_mercadopago_signature(self, body: str, secret: str) -> str:
        """Calculate MercadoPago specific signature"""
        # MercadoPago specific signature calculation
        return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    
    # Additional implementation methods would be added here
    async def _fetch_gateway_transactions(self, gateway: BankingGateway, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Fetch transactions from gateway API for reconciliation"""
        # Implementation would call gateway APIs
        return []
    
    async def _compare_transactions(self, local_transactions: List[Dict[str, Any]], gateway_transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compare local and gateway transactions to find discrepancies"""
        # Implementation would compare transactions
        return []
    
    async def _resolve_discrepancy(self, discrepancy: Dict[str, Any], gateway: BankingGateway):
        """Resolve a transaction discrepancy"""
        # Implementation would resolve discrepancies
        pass