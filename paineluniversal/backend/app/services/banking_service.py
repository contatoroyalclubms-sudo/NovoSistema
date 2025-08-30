"""
Banking Service - Comprehensive Banking Integration System
Sistema Universal de Gestão de Eventos

Core banking service that orchestrates all banking operations including:
- Multi-gateway payment processing
- PIX integration
- Account management
- Treasury operations
- Compliance and security
- Transaction monitoring
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import asyncio
import uuid
import json
import hashlib
import hmac
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
import httpx
import redis
from loguru import logger

from app.core.config import get_settings
from app.core.database import get_db
from app.services.digital_account_service import DigitalAccountService
from app.services.payment_links_service import PaymentLinksService
from app.services.validation_service import ValidationService
from app.services.webhook_service import WebhookService
from app.services.notification_service import NotificationService


class BankingGateway(str, Enum):
    """Supported banking gateways"""
    PICPAY = "picpay"
    PAGSEGURO = "pagseguro"
    ASAAS = "asaas"
    MERCADOPAGO = "mercadopago"
    STRIPE = "stripe"
    INTER = "inter"
    NUBANK = "nubank"
    C6BANK = "c6bank"


class TransactionStatus(str, Enum):
    """Transaction status definitions"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    CHARGEBACK = "chargeback"


class PaymentMethod(str, Enum):
    """Supported payment methods"""
    PIX = "pix"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    BOLETO = "boleto"
    WALLET = "wallet"
    CASH = "cash"


class PIXKeyType(str, Enum):
    """PIX key types"""
    CPF = "cpf"
    CNPJ = "cnpj"
    EMAIL = "email"
    PHONE = "phone"
    RANDOM = "random"


class BankingServiceError(Exception):
    """Base exception for banking service errors"""
    def __init__(self, message: str, code: str = None, gateway: str = None):
        self.message = message
        self.code = code
        self.gateway = gateway
        super().__init__(self.message)


class GatewayUnavailableError(BankingServiceError):
    """Gateway is unavailable"""
    pass


class InsufficientFundsError(BankingServiceError):
    """Insufficient funds for transaction"""
    pass


class BankingService:
    """
    Main banking service orchestrating all banking operations
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.redis_client = self._init_redis()
        
        # Initialize dependent services
        self.digital_account_service = DigitalAccountService(db)
        self.payment_links_service = PaymentLinksService(db)
        self.validation_service = ValidationService()
        self.webhook_service = WebhookService(db)
        self.notification_service = NotificationService(db)
        
        # Gateway configurations
        self.gateways = self._init_gateways()
        
        # Circuit breaker state for each gateway
        self.circuit_breakers = {gateway: {"failures": 0, "last_failure": None, "open": False} 
                               for gateway in BankingGateway}
    
    def _init_redis(self) -> redis.Redis:
        """Initialize Redis connection for caching and rate limiting"""
        try:
            return redis.Redis(
                host=self.settings.REDIS_HOST,
                port=self.settings.REDIS_PORT,
                password=self.settings.REDIS_PASSWORD,
                db=0,
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            return None
    
    def _init_gateways(self) -> Dict[str, Dict[str, Any]]:
        """Initialize gateway configurations"""
        return {
            BankingGateway.PICPAY: {
                "base_url": "https://appws.picpay.com/ecommerce/public",
                "api_key": self.settings.PICPAY_API_KEY,
                "secret": self.settings.PICPAY_SECRET,
                "active": True,
                "priority": 1,
                "supported_methods": [PaymentMethod.PIX, PaymentMethod.CREDIT_CARD, PaymentMethod.WALLET]
            },
            BankingGateway.PAGSEGURO: {
                "base_url": "https://ws.riodoce.pagseguro.uol.com.br",
                "api_key": self.settings.PAGSEGURO_API_KEY,
                "secret": self.settings.PAGSEGURO_SECRET,
                "active": True,
                "priority": 2,
                "supported_methods": [PaymentMethod.PIX, PaymentMethod.CREDIT_CARD, PaymentMethod.BOLETO]
            },
            BankingGateway.ASAAS: {
                "base_url": "https://www.asaas.com/api/v3",
                "api_key": self.settings.ASAAS_API_KEY,
                "secret": self.settings.ASAAS_SECRET,
                "active": True,
                "priority": 3,
                "supported_methods": [PaymentMethod.PIX, PaymentMethod.CREDIT_CARD, PaymentMethod.BOLETO, PaymentMethod.BANK_TRANSFER]
            },
            BankingGateway.MERCADOPAGO: {
                "base_url": "https://api.mercadopago.com/v1",
                "api_key": self.settings.MERCADOPAGO_API_KEY,
                "secret": self.settings.MERCADOPAGO_SECRET,
                "active": True,
                "priority": 4,
                "supported_methods": [PaymentMethod.PIX, PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD, PaymentMethod.BANK_TRANSFER]
            }
        }
    
    # ================================
    # PAYMENT PROCESSING
    # ================================
    
    async def process_payment(
        self,
        amount: Decimal,
        payment_method: PaymentMethod,
        customer_data: Dict[str, Any],
        metadata: Dict[str, Any] = None,
        preferred_gateway: BankingGateway = None
    ) -> Dict[str, Any]:
        """
        Process payment with intelligent gateway selection and fallback
        """
        transaction_id = str(uuid.uuid4())
        
        try:
            # Log payment initiation
            await self._log_transaction(
                transaction_id=transaction_id,
                action="payment_initiated",
                amount=amount,
                payment_method=payment_method,
                customer_data=customer_data,
                metadata=metadata
            )
            
            # Validate payment data
            await self._validate_payment_request(amount, payment_method, customer_data)
            
            # Select gateway with failover support
            gateway = await self._select_gateway(payment_method, amount, preferred_gateway)
            
            # Process payment
            result = await self._process_payment_with_gateway(
                gateway=gateway,
                transaction_id=transaction_id,
                amount=amount,
                payment_method=payment_method,
                customer_data=customer_data,
                metadata=metadata or {}
            )
            
            # Update account balance if successful
            if result["status"] in [TransactionStatus.COMPLETED, TransactionStatus.PROCESSING]:
                await self._update_account_balance(
                    customer_data.get("account_id"),
                    amount,
                    "credit",
                    transaction_id
                )
            
            # Send notifications
            await self._send_payment_notification(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            await self._log_transaction(
                transaction_id=transaction_id,
                action="payment_failed",
                amount=amount,
                error=str(e)
            )
            raise BankingServiceError(f"Payment processing failed: {str(e)}")
    
    async def _select_gateway(
        self,
        payment_method: PaymentMethod,
        amount: Decimal,
        preferred_gateway: BankingGateway = None
    ) -> BankingGateway:
        """
        Intelligent gateway selection based on availability, method support, and preferences
        """
        # Filter available gateways
        available_gateways = []
        for gateway_name, config in self.gateways.items():
            if (config.get("active") and 
                payment_method in config.get("supported_methods", []) and
                not self.circuit_breakers[gateway_name]["open"]):
                available_gateways.append((gateway_name, config))
        
        if not available_gateways:
            raise GatewayUnavailableError("No available gateways for payment method")
        
        # Use preferred gateway if available
        if preferred_gateway:
            for gateway_name, config in available_gateways:
                if gateway_name == preferred_gateway:
                    return gateway_name
        
        # Sort by priority and select best option
        available_gateways.sort(key=lambda x: x[1]["priority"])
        
        # Consider amount-based routing (e.g., high value transactions to specific gateways)
        if amount > Decimal("10000.00"):
            # For high value transactions, prefer more reliable gateways
            priority_gateways = [g for g in available_gateways if g[0] in [BankingGateway.ASAAS, BankingGateway.MERCADOPAGO]]
            if priority_gateways:
                return priority_gateways[0][0]
        
        return available_gateways[0][0]
    
    async def _process_payment_with_gateway(
        self,
        gateway: BankingGateway,
        transaction_id: str,
        amount: Decimal,
        payment_method: PaymentMethod,
        customer_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process payment with specific gateway with retry logic
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if gateway == BankingGateway.PICPAY:
                    result = await self._process_picpay_payment(
                        transaction_id, amount, payment_method, customer_data, metadata
                    )
                elif gateway == BankingGateway.PAGSEGURO:
                    result = await self._process_pagseguro_payment(
                        transaction_id, amount, payment_method, customer_data, metadata
                    )
                elif gateway == BankingGateway.ASAAS:
                    result = await self._process_asaas_payment(
                        transaction_id, amount, payment_method, customer_data, metadata
                    )
                elif gateway == BankingGateway.MERCADOPAGO:
                    result = await self._process_mercadopago_payment(
                        transaction_id, amount, payment_method, customer_data, metadata
                    )
                else:
                    raise BankingServiceError(f"Unsupported gateway: {gateway}")
                
                # Reset circuit breaker on success
                self.circuit_breakers[gateway]["failures"] = 0
                self.circuit_breakers[gateway]["open"] = False
                
                return result
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Gateway {gateway} attempt {retry_count} failed: {e}")
                
                # Update circuit breaker
                self._update_circuit_breaker(gateway, failed=True)
                
                if retry_count >= max_retries:
                    # Try fallback gateway
                    fallback_gateway = await self._get_fallback_gateway(gateway, payment_method)
                    if fallback_gateway:
                        logger.info(f"Failing over from {gateway} to {fallback_gateway}")
                        return await self._process_payment_with_gateway(
                            fallback_gateway, transaction_id, amount, 
                            payment_method, customer_data, metadata
                        )
                    else:
                        raise BankingServiceError(f"All gateways failed for transaction {transaction_id}")
                
                # Exponential backoff
                await asyncio.sleep(2 ** retry_count)
    
    # ================================
    # PIX INTEGRATION
    # ================================
    
    async def create_pix_payment(
        self,
        amount: Decimal,
        customer_data: Dict[str, Any],
        description: str = None,
        expires_in_minutes: int = 30,
        pix_key: str = None,
        gateway: BankingGateway = None
    ) -> Dict[str, Any]:
        """
        Create PIX payment with dynamic QR code
        """
        try:
            pix_id = str(uuid.uuid4())
            
            # Select gateway for PIX
            selected_gateway = gateway or await self._select_gateway(PaymentMethod.PIX, amount)
            
            # Generate PIX payment
            pix_data = await self._create_pix_with_gateway(
                gateway=selected_gateway,
                pix_id=pix_id,
                amount=amount,
                customer_data=customer_data,
                description=description,
                expires_in_minutes=expires_in_minutes,
                pix_key=pix_key
            )
            
            # Cache PIX data for quick access
            if self.redis_client:
                await self._cache_pix_data(pix_id, pix_data, expires_in_minutes)
            
            # Log PIX creation
            await self._log_transaction(
                transaction_id=pix_id,
                action="pix_created",
                amount=amount,
                gateway=selected_gateway,
                customer_data=customer_data
            )
            
            return {
                "pix_id": pix_id,
                "qr_code": pix_data["qr_code"],
                "qr_code_image": pix_data.get("qr_code_image"),
                "pix_copy_paste": pix_data["pix_copy_paste"],
                "amount": amount,
                "expires_at": pix_data["expires_at"],
                "status": TransactionStatus.PENDING,
                "gateway": selected_gateway
            }
            
        except Exception as e:
            logger.error(f"PIX creation failed: {e}")
            raise BankingServiceError(f"PIX creation failed: {str(e)}")
    
    async def check_pix_status(self, pix_id: str) -> Dict[str, Any]:
        """
        Check PIX payment status across gateways
        """
        try:
            # Check cache first
            if self.redis_client:
                cached_status = await self._get_cached_pix_status(pix_id)
                if cached_status:
                    return cached_status
            
            # Query all gateways for status
            for gateway_name in self.gateways.keys():
                try:
                    status = await self._check_pix_status_with_gateway(gateway_name, pix_id)
                    if status and status.get("found"):
                        # Cache the result
                        if self.redis_client:
                            await self._cache_pix_status(pix_id, status)
                        return status
                except Exception as e:
                    logger.warning(f"Gateway {gateway_name} PIX status check failed: {e}")
                    continue
            
            return {
                "pix_id": pix_id,
                "status": TransactionStatus.PENDING,
                "found": False,
                "message": "PIX not found in any gateway"
            }
            
        except Exception as e:
            logger.error(f"PIX status check failed: {e}")
            raise BankingServiceError(f"PIX status check failed: {str(e)}")
    
    async def process_pix_webhook(self, gateway: BankingGateway, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process PIX webhook from gateways
        """
        try:
            # Validate webhook signature
            await self._validate_webhook_signature(gateway, webhook_data)
            
            # Extract PIX data
            pix_data = await self._extract_pix_data_from_webhook(gateway, webhook_data)
            
            # Update transaction status
            await self._update_pix_transaction(pix_data)
            
            # Update account balance if paid
            if pix_data.get("status") == TransactionStatus.COMPLETED:
                await self._update_account_balance(
                    pix_data.get("account_id"),
                    pix_data.get("amount"),
                    "credit",
                    pix_data.get("pix_id")
                )
            
            # Send notifications
            await self._send_pix_notification(pix_data)
            
            # Cache updated status
            if self.redis_client:
                await self._cache_pix_status(pix_data["pix_id"], pix_data)
            
            return {"status": "processed", "pix_id": pix_data["pix_id"]}
            
        except Exception as e:
            logger.error(f"PIX webhook processing failed: {e}")
            raise BankingServiceError(f"PIX webhook processing failed: {str(e)}")
    
    # ================================
    # ACCOUNT MANAGEMENT
    # ================================
    
    async def create_virtual_account(
        self,
        user_id: int,
        account_type: str = "default",
        initial_balance: Decimal = Decimal("0.00"),
        daily_limit: Decimal = Decimal("5000.00"),
        monthly_limit: Decimal = Decimal("50000.00")
    ) -> Dict[str, Any]:
        """
        Create virtual account with real-time balance tracking
        """
        try:
            account_id = str(uuid.uuid4())
            
            # Create account in database
            account = await self.digital_account_service.create_account(
                user_id=user_id,
                initial_balance=initial_balance,
                daily_limit=daily_limit,
                monthly_limit=monthly_limit
            )
            
            # Initialize balance cache
            if self.redis_client:
                await self._init_balance_cache(account_id, initial_balance)
            
            # Log account creation
            await self._log_transaction(
                transaction_id=account_id,
                action="account_created",
                user_id=user_id,
                account_type=account_type,
                initial_balance=initial_balance
            )
            
            return {
                "account_id": account_id,
                "user_id": user_id,
                "balance": initial_balance,
                "available_balance": initial_balance,
                "daily_limit": daily_limit,
                "monthly_limit": monthly_limit,
                "status": "active",
                "created_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Virtual account creation failed: {e}")
            raise BankingServiceError(f"Virtual account creation failed: {str(e)}")
    
    async def get_real_time_balance(self, account_id: str) -> Dict[str, Any]:
        """
        Get real-time balance with caching
        """
        try:
            # Check cache first
            if self.redis_client:
                cached_balance = await self._get_cached_balance(account_id)
                if cached_balance:
                    return cached_balance
            
            # Query database
            balance_data = await self.digital_account_service.get_balance(account_id)
            
            # Cache the result
            if self.redis_client:
                await self._cache_balance(account_id, balance_data)
            
            return balance_data
            
        except Exception as e:
            logger.error(f"Balance retrieval failed: {e}")
            raise BankingServiceError(f"Balance retrieval failed: {str(e)}")
    
    async def transfer_funds(
        self,
        source_account_id: str,
        destination_account_id: str,
        amount: Decimal,
        description: str = None,
        transfer_type: str = "internal"
    ) -> Dict[str, Any]:
        """
        Transfer funds between accounts with real-time processing
        """
        transfer_id = str(uuid.uuid4())
        
        try:
            # Validate accounts
            await self._validate_transfer_accounts(source_account_id, destination_account_id)
            
            # Check balance
            source_balance = await self.get_real_time_balance(source_account_id)
            if source_balance["available_balance"] < amount:
                raise InsufficientFundsError(f"Insufficient funds for transfer")
            
            # Process transfer atomically
            async with self._get_db_transaction() as transaction:
                # Debit source account
                await self._update_account_balance(
                    source_account_id,
                    amount,
                    "debit",
                    transfer_id,
                    description=f"Transfer to {destination_account_id}"
                )
                
                # Credit destination account
                await self._update_account_balance(
                    destination_account_id,
                    amount,
                    "credit",
                    transfer_id,
                    description=f"Transfer from {source_account_id}"
                )
                
                # Log transfer
                await self._log_transfer(
                    transfer_id=transfer_id,
                    source_account_id=source_account_id,
                    destination_account_id=destination_account_id,
                    amount=amount,
                    description=description,
                    transfer_type=transfer_type
                )
            
            # Update cache
            if self.redis_client:
                await self._invalidate_balance_cache([source_account_id, destination_account_id])
            
            # Send notifications
            await self._send_transfer_notifications(
                transfer_id=transfer_id,
                source_account_id=source_account_id,
                destination_account_id=destination_account_id,
                amount=amount
            )
            
            return {
                "transfer_id": transfer_id,
                "status": TransactionStatus.COMPLETED,
                "amount": amount,
                "processed_at": datetime.utcnow(),
                "fee": Decimal("0.00"),
                "net_amount": amount
            }
            
        except Exception as e:
            logger.error(f"Fund transfer failed: {e}")
            await self._log_transfer(
                transfer_id=transfer_id,
                source_account_id=source_account_id,
                destination_account_id=destination_account_id,
                amount=amount,
                error=str(e),
                status="failed"
            )
            raise BankingServiceError(f"Fund transfer failed: {str(e)}")
    
    # ================================
    # UTILITY METHODS
    # ================================
    
    @asynccontextmanager
    async def _get_db_transaction(self):
        """Get database transaction context"""
        async with self.db.begin() as transaction:
            try:
                yield transaction
                await transaction.commit()
            except Exception:
                await transaction.rollback()
                raise
    
    def _update_circuit_breaker(self, gateway: BankingGateway, failed: bool = False):
        """Update circuit breaker state for gateway"""
        if failed:
            self.circuit_breakers[gateway]["failures"] += 1
            self.circuit_breakers[gateway]["last_failure"] = datetime.utcnow()
            
            # Open circuit if too many failures
            if self.circuit_breakers[gateway]["failures"] >= 5:
                self.circuit_breakers[gateway]["open"] = True
                logger.warning(f"Circuit breaker opened for gateway {gateway}")
        else:
            self.circuit_breakers[gateway]["failures"] = 0
            self.circuit_breakers[gateway]["open"] = False
    
    async def _get_fallback_gateway(
        self,
        failed_gateway: BankingGateway,
        payment_method: PaymentMethod
    ) -> Optional[BankingGateway]:
        """Get fallback gateway for failed gateway"""
        for gateway_name, config in self.gateways.items():
            if (gateway_name != failed_gateway and
                config.get("active") and
                payment_method in config.get("supported_methods", []) and
                not self.circuit_breakers[gateway_name]["open"]):
                return gateway_name
        return None
    
    async def _validate_payment_request(
        self,
        amount: Decimal,
        payment_method: PaymentMethod,
        customer_data: Dict[str, Any]
    ):
        """Validate payment request data"""
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        
        if amount > Decimal("100000.00"):  # Max transaction limit
            raise ValueError("Amount exceeds maximum transaction limit")
        
        # Validate customer data
        await self.validation_service.validate_customer_data(customer_data)
    
    async def _log_transaction(self, **kwargs):
        """Log transaction for audit and monitoring"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": "banking_service",
            **kwargs
        }
        logger.info(f"Banking transaction: {json.dumps(log_data)}")
    
    # Gateway-specific implementations would be added here
    # These are placeholder methods for the actual gateway integrations
    
    async def _process_picpay_payment(self, transaction_id: str, amount: Decimal, 
                                    payment_method: PaymentMethod, customer_data: Dict[str, Any], 
                                    metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment with PicPay gateway"""
        # Implementation for PicPay API integration
        pass
    
    async def _process_pagseguro_payment(self, transaction_id: str, amount: Decimal,
                                       payment_method: PaymentMethod, customer_data: Dict[str, Any],
                                       metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment with PagSeguro gateway"""
        # Implementation for PagSeguro API integration
        pass
    
    async def _process_asaas_payment(self, transaction_id: str, amount: Decimal,
                                   payment_method: PaymentMethod, customer_data: Dict[str, Any],
                                   metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment with Asaas gateway"""
        # Implementation for Asaas API integration
        pass
    
    async def _process_mercadopago_payment(self, transaction_id: str, amount: Decimal,
                                         payment_method: PaymentMethod, customer_data: Dict[str, Any],
                                         metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment with MercadoPago gateway"""
        # Implementation for MercadoPago API integration
        pass
    
    # Additional helper methods for caching, notifications, etc. would be implemented here
    async def _cache_pix_data(self, pix_id: str, pix_data: Dict[str, Any], expires_in_minutes: int):
        """Cache PIX data in Redis"""
        if self.redis_client:
            cache_key = f"pix:{pix_id}"
            await self.redis_client.setex(
                cache_key, 
                expires_in_minutes * 60, 
                json.dumps(pix_data, default=str)
            )
    
    async def _update_account_balance(self, account_id: str, amount: Decimal, 
                                    operation: str, reference_id: str, description: str = None):
        """Update account balance atomically"""
        # Implementation for balance updates with proper locking
        pass
    
    async def _send_payment_notification(self, payment_result: Dict[str, Any]):
        """Send payment notifications to customers"""
        await self.notification_service.send_payment_notification(payment_result)
    
    async def _validate_webhook_signature(self, gateway: BankingGateway, webhook_data: Dict[str, Any]):
        """Validate webhook signature for security"""
        # Implementation for webhook signature validation
        pass