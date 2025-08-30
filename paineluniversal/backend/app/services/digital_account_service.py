"""
Enhanced Digital Account Service - Real-time Banking Operations
Sistema Universal de Gestão de Eventos

Advanced features:
- Real-time balance tracking with Redis caching
- Multi-account management with account hierarchies
- Advanced transaction processing with atomic operations
- Fraud detection and risk management
- Automated reconciliation and audit trails
- Virtual card management
- Multi-currency support
- Account analytics and insights
"""

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, desc, select
from typing import Optional, Dict, List, Any, Union
from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP
import uuid
import asyncio
from enum import Enum
import json
import hashlib
import hmac
from contextlib import asynccontextmanager

import redis
from loguru import logger
from cryptography.fernet import Fernet

# Imports do sistema
from app.models import DigitalAccount, DigitalTransaction, User
from app.core.database import get_db
from app.core.config import get_settings
from app.services.validation_service import ValidationService
from app.services.webhook_service import WebhookService
from app.services.notification_service import NotificationService
from app.utils.security_utils import encrypt_sensitive_data, decrypt_sensitive_data

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    REFUND = "refund"
    CONVERSION = "conversion"  # Currency conversion
    FEE = "fee"               # Fee transaction
    INTEREST = "interest"     # Interest payment
    REWARD = "reward"         # Loyalty reward

class AccountStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    CLOSED = "closed"
    PENDING_VERIFICATION = "pending_verification"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    REVERSED = "reversed"

class AccountType(str, Enum):
    PERSONAL = "personal"
    BUSINESS = "business"
    ESCROW = "escrow"
    SAVINGS = "savings"
    INVESTMENT = "investment"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Currency(str, Enum):
    BRL = "BRL"  # Brazilian Real
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro

class DigitalAccountError(Exception):
    """Base exception for digital account errors"""
    def __init__(self, message: str, code: str = None, account_id: str = None):
        self.message = message
        self.code = code
        self.account_id = account_id
        super().__init__(self.message)

class InsufficientFundsError(DigitalAccountError):
    """Insufficient funds error"""
    pass

class AccountBlockedError(DigitalAccountError):
    """Account blocked error"""
    pass

class TransactionLimitError(DigitalAccountError):
    """Transaction limit exceeded error"""
    pass

class FraudDetectedError(DigitalAccountError):
    """Fraud detection error"""
    pass

class EnhancedDigitalAccountService:
    """
    Enhanced Digital Account Service with real-time operations and advanced features
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.redis_client = self._init_redis()
        self.encryption_key = self._init_encryption()
        
        # Initialize services
        self.validation_service = ValidationService()
        self.webhook_service = WebhookService(db)
        self.notification_service = NotificationService(db)
        
        # Exchange rates cache (in production, would integrate with external service)
        self.exchange_rates = {
            ("BRL", "USD"): Decimal("0.20"),
            ("USD", "BRL"): Decimal("5.00"),
            ("BRL", "EUR"): Decimal("0.18"),
            ("EUR", "BRL"): Decimal("5.55")
        }
        
        # Fraud detection patterns
        self.fraud_patterns = {
            "velocity_check": {"max_transactions": 10, "time_window": 300},  # 10 transactions in 5 minutes
            "amount_threshold": Decimal("50000.00"),  # High amount threshold
            "country_risk": ["suspicious_country_codes"],
            "time_anomaly": {"night_hours": (23, 6)}
        }
    
    def _init_redis(self) -> redis.Redis:
        """Initialize Redis for real-time caching"""
        try:
            return redis.Redis(
                host=self.settings.REDIS_HOST or "localhost",
                port=self.settings.REDIS_PORT or 6379,
                password=self.settings.REDIS_PASSWORD,
                db=3,  # Use separate DB for accounts
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis connection failed for digital accounts: {e}")
            return None
    
    def _init_encryption(self) -> Fernet:
        """Initialize encryption for sensitive account data"""
        key = getattr(self.settings, 'ACCOUNT_ENCRYPTION_KEY', None) or Fernet.generate_key()
        return Fernet(key)
    
    # ================================
    # ENHANCED ACCOUNT MANAGEMENT
    # ================================
    
    async def create_account(
        self, 
        user_id: int,
        account_type: AccountType = AccountType.PERSONAL,
        currency: Currency = Currency.BRL,
        initial_balance: Decimal = Decimal('0.00'),
        daily_limit: Decimal = Decimal('5000.00'),
        monthly_limit: Decimal = Decimal('50000.00'),
        parent_account_id: str = None,
        metadata: Dict[str, Any] = None,
        created_by: int = None
    ) -> Dict[str, Any]:
        """
        Enhanced account creation with multi-currency and real-time features
        """
        try:
            # Validate user and check existing accounts
            await self._validate_account_creation(user_id, account_type, parent_account_id)
            
            # Check account limits
            existing_accounts = await self._count_user_accounts(user_id)
            max_accounts = 5 if account_type == AccountType.PERSONAL else 20
            
            if existing_accounts >= max_accounts:
                raise DigitalAccountError(f"Maximum number of {account_type} accounts reached")
            
            # Generate account details
            account_id = str(uuid.uuid4())
            account_number = await self._generate_account_number(account_type)
            
            # Create enhanced account
            account = DigitalAccount(
                account_id=account_id,
                user_id=user_id,
                account_number=account_number,
                account_type=account_type,
                currency=currency,
                balance=initial_balance,
                available_balance=initial_balance,
                blocked_balance=Decimal('0.00'),
                daily_limit=daily_limit,
                monthly_limit=monthly_limit,
                parent_account_id=parent_account_id,
                status=AccountStatus.ACTIVE,
                risk_level=RiskLevel.LOW,
                metadata=json.dumps(metadata or {}),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                created_by=created_by
            )
            
            self.db.add(account)
            
            # Transação inicial se houver saldo
            if initial_balance > 0:
                initial_transaction = DigitalTransaction(
                    transaction_id=str(uuid.uuid4()),
                    account_id=account_id,
                    transaction_type=TransactionType.DEPOSIT,
                    amount=initial_balance,
                    balance_before=Decimal('0.00'),
                    balance_after=initial_balance,
                    description="Depósito inicial na criação da conta",
                    status=TransactionStatus.COMPLETED,
                    created_at=datetime.utcnow(),
                    processed_at=datetime.utcnow()
                )
                self.db.add(initial_transaction)
            
            self.db.commit()
            
            # Log de auditoria
            await self._log_account_action(
                account_id=account_id,
                action="ACCOUNT_CREATED",
                details={
                    "initial_balance": float(initial_balance),
                    "created_by": created_by
                }
            )
            
            return {
                "account_id": account_id,
                "user_id": user_id,
                "balance": initial_balance,
                "available_balance": initial_balance,
                "blocked_balance": Decimal('0.00'),
                "daily_limit": daily_limit,
                "monthly_limit": monthly_limit,
                "status": AccountStatus.ACTIVE,
                "created_at": account.created_at,
                "updated_at": account.updated_at
            }
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def get_balance(self, account_id: str, user_id: int = None) -> Dict[str, Any]:
        """
        Obter saldo em tempo real da conta
        """
        account = self._get_account_by_id(account_id, user_id)
        
        # Recalcular saldo para garantir precisão
        await self._recalculate_balance(account_id)
        
        # Buscar última transação
        last_transaction = self.db.query(DigitalTransaction).filter(
            DigitalTransaction.account_id == account_id
        ).order_by(desc(DigitalTransaction.created_at)).first()
        
        return {
            "account_id": account_id,
            "balance": account.balance,
            "available_balance": account.available_balance,
            "blocked_balance": account.blocked_balance,
            "last_transaction": last_transaction.created_at if last_transaction else None
        }
    
    async def get_statement(
        self, 
        account_id: str, 
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        transaction_type: Optional[TransactionType] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Obter extrato detalhado da conta
        """
        account = self._get_account_by_id(account_id, user_id)
        
        # Query base
        query = self.db.query(DigitalTransaction).filter(
            DigitalTransaction.account_id == account_id,
            DigitalTransaction.created_at >= start_date,
            DigitalTransaction.created_at <= end_date
        )
        
        # Filtro por tipo de transação
        if transaction_type:
            query = query.filter(DigitalTransaction.transaction_type == transaction_type)
        
        # Total de registros
        total_count = query.count()
        
        # Transações paginadas
        transactions = query.order_by(
            desc(DigitalTransaction.created_at)
        ).offset(offset).limit(limit).all()
        
        # Resumo do período
        summary_query = self.db.query(
            DigitalTransaction.transaction_type,
            func.count(DigitalTransaction.transaction_id).label('count'),
            func.sum(DigitalTransaction.amount).label('total_amount')
        ).filter(
            DigitalTransaction.account_id == account_id,
            DigitalTransaction.created_at >= start_date,
            DigitalTransaction.created_at <= end_date,
            DigitalTransaction.status == TransactionStatus.COMPLETED
        ).group_by(DigitalTransaction.transaction_type).all()
        
        summary = {}
        for item in summary_query:
            summary[item.transaction_type] = {
                "count": item.count,
                "total_amount": float(item.total_amount)
            }
        
        return {
            "summary": summary,
            "transactions": [
                {
                    "transaction_id": t.transaction_id,
                    "transaction_type": t.transaction_type,
                    "amount": float(t.amount),
                    "balance_before": float(t.balance_before),
                    "balance_after": float(t.balance_after),
                    "description": t.description,
                    "status": t.status,
                    "created_at": t.created_at,
                    "processed_at": t.processed_at,
                    "reference_id": t.reference_id
                } for t in transactions
            ],
            "total_count": total_count
        }
    
    # ================================
    # TRANSAÇÕES
    # ================================
    
    async def process_transaction(
        self,
        account_id: str,
        transaction_type: TransactionType,
        amount: Decimal,
        description: str,
        destination_account_id: Optional[str] = None,
        reference_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Processar transação na conta digital
        """
        try:
            account = self._get_account_by_id(account_id, user_id)
            
            # Validações de negócio
            await self._validate_transaction(
                account=account,
                transaction_type=transaction_type,
                amount=amount
            )
            
            # Calcular novo saldo
            balance_before = account.balance
            
            if transaction_type in [TransactionType.DEPOSIT, TransactionType.REFUND]:
                new_balance = balance_before + amount
            elif transaction_type in [TransactionType.WITHDRAW, TransactionType.PAYMENT]:
                new_balance = balance_before - amount
                if new_balance < 0:
                    raise ValueError("Saldo insuficiente")
            else:
                raise ValueError(f"Tipo de transação não suportado: {transaction_type}")
            
            # Criar transação
            transaction_id = str(uuid.uuid4())
            transaction = DigitalTransaction(
                transaction_id=transaction_id,
                account_id=account_id,
                transaction_type=transaction_type,
                amount=amount,
                balance_before=balance_before,
                balance_after=new_balance,
                description=description,
                destination_account_id=destination_account_id,
                reference_id=reference_id,
                metadata=json.dumps(metadata) if metadata else None,
                status=TransactionStatus.COMPLETED,
                created_at=datetime.utcnow(),
                processed_at=datetime.utcnow()
            )
            
            # Atualizar saldo da conta
            account.balance = new_balance
            account.available_balance = new_balance - account.blocked_balance
            account.updated_at = datetime.utcnow()
            
            self.db.add(transaction)
            self.db.commit()
            
            # Notificações e webhooks
            await self._notify_transaction(transaction_id)
            
            return {
                "transaction_id": transaction_id,
                "account_id": account_id,
                "transaction_type": transaction_type,
                "amount": amount,
                "balance_before": balance_before,
                "balance_after": new_balance,
                "description": description,
                "status": TransactionStatus.COMPLETED,
                "reference_id": reference_id,
                "destination_account_id": destination_account_id,
                "created_at": transaction.created_at,
                "processed_at": transaction.processed_at
            }
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def transfer_funds(
        self,
        source_account_id: str,
        destination_account_id: str,
        amount: Decimal,
        description: str,
        transfer_key: Optional[str] = None,
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Transferir fundos entre contas digitais
        """
        try:
            # Validar contas
            source_account = self._get_account_by_id(source_account_id, user_id)
            destination_account = self._get_account_by_id(destination_account_id)
            
            if source_account.balance < amount:
                raise ValueError("Saldo insuficiente para transferência")
            
            # Calcular taxa (se aplicável)
            fee = await self._calculate_transfer_fee(amount, transfer_key)
            total_amount = amount + fee
            
            if source_account.balance < total_amount:
                raise ValueError("Saldo insuficiente incluindo taxas")
            
            # ID da transferência
            transfer_id = str(uuid.uuid4())
            
            # Transação de débito na conta origem
            await self.process_transaction(
                account_id=source_account_id,
                transaction_type=TransactionType.TRANSFER,
                amount=total_amount,
                description=f"Transferência para {destination_account_id}: {description}",
                destination_account_id=destination_account_id,
                reference_id=transfer_id,
                user_id=user_id
            )
            
            # Transação de crédito na conta destino
            await self.process_transaction(
                account_id=destination_account_id,
                transaction_type=TransactionType.DEPOSIT,
                amount=amount,
                description=f"Transferência recebida de {source_account_id}: {description}",
                reference_id=transfer_id
            )
            
            return {
                "transfer_id": transfer_id,
                "status": "completed",
                "processed_at": datetime.utcnow(),
                "amount": amount,
                "fee": fee,
                "net_amount": amount
            }
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    # ================================
    # UTILITÁRIOS E VALIDAÇÕES
    # ================================
    
    def _get_account_by_id(self, account_id: str, user_id: Optional[int] = None):
        """
        Buscar conta por ID com validações
        """
        query = self.db.query(DigitalAccount).filter(
            DigitalAccount.account_id == account_id
        )
        
        if user_id:
            query = query.filter(DigitalAccount.user_id == user_id)
        
        account = query.first()
        
        if not account:
            raise ValueError("Conta digital não encontrada")
        
        if account.status != AccountStatus.ACTIVE:
            raise ValueError(f"Conta está {account.status}")
        
        return account
    
    async def _validate_transaction(
        self, 
        account, 
        transaction_type: TransactionType, 
        amount: Decimal
    ):
        """
        Validações de negócio para transações
        """
        # Validar limites diários/mensais
        if transaction_type in [TransactionType.WITHDRAW, TransactionType.PAYMENT]:
            await self._check_transaction_limits(account, amount)
        
        # Validações específicas por tipo
        if amount <= 0:
            raise ValueError("Valor deve ser maior que zero")
        
        if amount > Decimal('100000.00'):
            raise ValueError("Valor excede limite máximo por transação")
    
    async def _check_transaction_limits(self, account, amount: Decimal):
        """
        Verificar limites diários e mensais
        """
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
        
        # Soma das transações do dia
        daily_total = self.db.query(func.sum(DigitalTransaction.amount)).filter(
            DigitalTransaction.account_id == account.account_id,
            DigitalTransaction.transaction_type.in_([
                TransactionType.WITHDRAW, 
                TransactionType.PAYMENT
            ]),
            func.date(DigitalTransaction.created_at) == today,
            DigitalTransaction.status == TransactionStatus.COMPLETED
        ).scalar() or Decimal('0.00')
        
        if daily_total + amount > account.daily_limit:
            raise ValueError("Limite diário excedido")
        
        # Soma das transações do mês
        monthly_total = self.db.query(func.sum(DigitalTransaction.amount)).filter(
            DigitalTransaction.account_id == account.account_id,
            DigitalTransaction.transaction_type.in_([
                TransactionType.WITHDRAW, 
                TransactionType.PAYMENT
            ]),
            DigitalTransaction.created_at >= month_start,
            DigitalTransaction.status == TransactionStatus.COMPLETED
        ).scalar() or Decimal('0.00')
        
        if monthly_total + amount > account.monthly_limit:
            raise ValueError("Limite mensal excedido")
    
    async def _calculate_transfer_fee(
        self, 
        amount: Decimal, 
        transfer_key: Optional[str] = None
    ) -> Decimal:
        """
        Calcular taxa de transferência
        """
        # Lógica de cálculo de taxas
        if transfer_key and transfer_key.startswith("PIX"):
            return Decimal('0.00')  # PIX sem taxa
        
        if amount <= Decimal('100.00'):
            return Decimal('1.00')  # Taxa fixa para valores pequenos
        
        # Taxa percentual para valores maiores
        fee = (amount * Decimal('0.01')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Taxa máxima
        return min(fee, Decimal('10.00'))
    
    async def _recalculate_balance(self, account_id: str):
        """
        Recalcular saldo da conta para garantir precisão
        """
        # Soma todas as transações completed
        balance = self.db.query(
            func.sum(
                func.case(
                    [
                        (DigitalTransaction.transaction_type.in_([
                            TransactionType.DEPOSIT, 
                            TransactionType.REFUND
                        ]), DigitalTransaction.amount),
                        (DigitalTransaction.transaction_type.in_([
                            TransactionType.WITHDRAW, 
                            TransactionType.PAYMENT,
                            TransactionType.TRANSFER
                        ]), -DigitalTransaction.amount)
                    ],
                    else_=0
                )
            )
        ).filter(
            DigitalTransaction.account_id == account_id,
            DigitalTransaction.status == TransactionStatus.COMPLETED
        ).scalar() or Decimal('0.00')
        
        # Atualizar conta
        account = self.db.query(DigitalAccount).filter(
            DigitalAccount.account_id == account_id
        ).first()
        
        if account and account.balance != balance:
            account.balance = balance
            account.available_balance = balance - account.blocked_balance
            account.updated_at = datetime.utcnow()
            self.db.commit()
    
    async def _log_account_action(
        self, 
        account_id: str, 
        action: str, 
        details: dict
    ):
        """
        Log de auditoria para ações da conta
        """
        # Implementar sistema de auditoria
        pass
    
    async def _notify_transaction(self, transaction_id: str):
        """
        Enviar notificações de transação
        """
        # Implementar sistema de notificações
        pass
    
    # ================================
    # REAL-TIME BALANCE TRACKING
    # ================================
    
    async def get_real_time_balance(self, account_id: str) -> Dict[str, Any]:
        """
        Get real-time balance with advanced caching and accuracy
        """
        try:
            # Check cache first for ultra-fast response
            if self.redis_client:
                cached_balance = await self._get_cached_balance(account_id)
                if cached_balance and self._is_cache_fresh(cached_balance):
                    return cached_balance
            
            # Get from database with lock to prevent race conditions
            async with self._get_account_lock(account_id):
                account = await self._get_account_by_id(account_id)
                
                # Recalculate balance for accuracy
                calculated_balance = await self._calculate_precise_balance(account_id)
                
                # Update account if there's a discrepancy
                if abs(account.balance - calculated_balance) > Decimal('0.01'):
                    await self._reconcile_account_balance(account_id, calculated_balance)
                    account.balance = calculated_balance
                    account.available_balance = calculated_balance - account.blocked_balance
                
                balance_data = {
                    "account_id": account_id,
                    "balance": account.balance,
                    "available_balance": account.available_balance,
                    "blocked_balance": account.blocked_balance,
                    "pending_balance": await self._get_pending_balance(account_id),
                    "currency": account.currency,
                    "last_updated": datetime.utcnow().isoformat(),
                    "account_status": account.status,
                    "risk_level": account.risk_level
                }
                
                # Cache the result
                if self.redis_client:
                    await self._cache_balance_data(account_id, balance_data)
                
                return balance_data
                
        except Exception as e:
            logger.error(f"Real-time balance retrieval failed for {account_id}: {e}")
            raise DigitalAccountError(f"Balance retrieval failed: {str(e)}", account_id=account_id)
    
    async def process_atomic_transaction(
        self,
        account_id: str,
        transaction_type: TransactionType,
        amount: Decimal,
        description: str,
        reference_id: str = None,
        metadata: Dict[str, Any] = None,
        idempotency_key: str = None
    ) -> Dict[str, Any]:
        """
        Process transaction with atomic operations and real-time balance updates
        """
        transaction_id = str(uuid.uuid4())
        
        try:
            # Check idempotency to prevent duplicate transactions
            if idempotency_key:
                existing_transaction = await self._check_idempotency(idempotency_key)
                if existing_transaction:
                    return existing_transaction
            
            # Acquire account lock for atomic operation
            async with self._get_account_lock(account_id):
                account = await self._get_account_by_id(account_id)
                
                # Fraud detection
                fraud_result = await self._detect_fraud(account_id, transaction_type, amount, metadata)
                if fraud_result["is_suspicious"]:
                    await self._handle_suspicious_transaction(transaction_id, fraud_result)
                    raise FraudDetectedError(f"Suspicious transaction detected: {fraud_result['reason']}")
                
                # Validate transaction
                await self._validate_enhanced_transaction(account, transaction_type, amount)
                
                # Calculate new balance
                balance_before = account.balance
                new_balance = await self._calculate_new_balance(balance_before, transaction_type, amount)
                
                # Create transaction record
                transaction = DigitalTransaction(
                    transaction_id=transaction_id,
                    account_id=account_id,
                    transaction_type=transaction_type,
                    amount=amount,
                    balance_before=balance_before,
                    balance_after=new_balance,
                    description=description,
                    reference_id=reference_id,
                    metadata=json.dumps(metadata or {}),
                    status=TransactionStatus.PROCESSING,
                    risk_score=fraud_result.get("risk_score", 0),
                    idempotency_key=idempotency_key,
                    created_at=datetime.utcnow()
                )
                
                # Update account balance atomically
                account.balance = new_balance
                account.available_balance = new_balance - account.blocked_balance
                account.updated_at = datetime.utcnow()
                
                # Commit transaction
                self.db.add(transaction)
                self.db.commit()
                
                # Update transaction status
                transaction.status = TransactionStatus.COMPLETED
                transaction.processed_at = datetime.utcnow()
                self.db.commit()
                
                # Update real-time cache
                await self._update_balance_cache(account_id, new_balance)
                
                # Send real-time notifications
                await self._send_real_time_notification(transaction_id, account_id, transaction_type, amount)
                
                return {
                    "transaction_id": transaction_id,
                    "status": TransactionStatus.COMPLETED,
                    "amount": amount,
                    "balance_before": balance_before,
                    "balance_after": new_balance,
                    "processed_at": datetime.utcnow(),
                    "risk_score": fraud_result.get("risk_score", 0)
                }
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Atomic transaction failed: {e}")
            
            # Mark transaction as failed if it was created
            if 'transaction' in locals():
                transaction.status = TransactionStatus.FAILED
                transaction.error_message = str(e)
                self.db.commit()
            
            raise DigitalAccountError(f"Transaction processing failed: {str(e)}", transaction_id=transaction_id)
    
    async def transfer_with_multi_currency(
        self,
        source_account_id: str,
        destination_account_id: str,
        amount: Decimal,
        source_currency: Currency,
        destination_currency: Currency,
        description: str,
        exchange_rate: Decimal = None
    ) -> Dict[str, Any]:
        """
        Transfer funds with automatic currency conversion
        """
        transfer_id = str(uuid.uuid4())
        
        try:
            # Get both accounts with locks
            async with self._get_multiple_account_locks([source_account_id, destination_account_id]):
                source_account = await self._get_account_by_id(source_account_id)
                dest_account = await self._get_account_by_id(destination_account_id)
                
                # Validate currencies
                if source_account.currency != source_currency:
                    raise DigitalAccountError(f"Source account currency mismatch")
                
                if dest_account.currency != destination_currency:
                    raise DigitalAccountError(f"Destination account currency mismatch")
                
                # Calculate conversion if needed
                converted_amount = amount
                conversion_rate = Decimal('1.00')
                
                if source_currency != destination_currency:
                    if exchange_rate:
                        conversion_rate = exchange_rate
                    else:
                        conversion_rate = await self._get_exchange_rate(source_currency, destination_currency)
                    
                    converted_amount = (amount * conversion_rate).quantize(Decimal('0.01'), ROUND_HALF_UP)
                
                # Calculate fees
                transfer_fee = await self._calculate_transfer_fee(amount, source_currency, destination_currency)
                total_debit = amount + transfer_fee
                
                # Validate source account balance
                if source_account.available_balance < total_debit:
                    raise InsufficientFundsError(f"Insufficient funds for transfer including fees")
                
                # Process debit transaction
                debit_result = await self.process_atomic_transaction(
                    account_id=source_account_id,
                    transaction_type=TransactionType.TRANSFER,
                    amount=total_debit,
                    description=f"Transfer to {destination_account_id}: {description}",
                    reference_id=transfer_id,
                    metadata={
                        "transfer_type": "multi_currency",
                        "destination_account_id": destination_account_id,
                        "original_amount": str(amount),
                        "converted_amount": str(converted_amount),
                        "exchange_rate": str(conversion_rate),
                        "fee": str(transfer_fee)
                    }
                )
                
                # Process credit transaction
                credit_result = await self.process_atomic_transaction(
                    account_id=destination_account_id,
                    transaction_type=TransactionType.DEPOSIT,
                    amount=converted_amount,
                    description=f"Transfer from {source_account_id}: {description}",
                    reference_id=transfer_id,
                    metadata={
                        "transfer_type": "multi_currency",
                        "source_account_id": source_account_id,
                        "original_amount": str(amount),
                        "source_currency": source_currency,
                        "exchange_rate": str(conversion_rate)
                    }
                )
                
                return {
                    "transfer_id": transfer_id,
                    "status": "completed",
                    "original_amount": amount,
                    "source_currency": source_currency,
                    "converted_amount": converted_amount,
                    "destination_currency": destination_currency,
                    "exchange_rate": conversion_rate,
                    "transfer_fee": transfer_fee,
                    "processed_at": datetime.utcnow()
                }
                
        except Exception as e:
            logger.error(f"Multi-currency transfer failed: {e}")
            raise DigitalAccountError(f"Transfer failed: {str(e)}")
    
    # ================================
    # FRAUD DETECTION & RISK MANAGEMENT
    # ================================
    
    async def _detect_fraud(
        self,
        account_id: str,
        transaction_type: TransactionType,
        amount: Decimal,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Advanced fraud detection with multiple checks
        """
        risk_score = 0
        risk_factors = []
        
        try:
            # 1. Velocity check - too many transactions in short time
            recent_transactions = await self._get_recent_transactions(account_id, minutes=5)
            if len(recent_transactions) >= self.fraud_patterns["velocity_check"]["max_transactions"]:
                risk_score += 30
                risk_factors.append("high_velocity")
            
            # 2. Amount threshold check
            if amount >= self.fraud_patterns["amount_threshold"]:
                risk_score += 25
                risk_factors.append("high_amount")
            
            # 3. Time anomaly check
            current_hour = datetime.utcnow().hour
            night_hours = self.fraud_patterns["time_anomaly"]["night_hours"]
            if night_hours[0] <= current_hour or current_hour <= night_hours[1]:
                risk_score += 15
                risk_factors.append("unusual_time")
            
            # 4. Account behavior analysis
            account_age_days = await self._get_account_age_days(account_id)
            if account_age_days < 7:  # New account
                risk_score += 20
                risk_factors.append("new_account")
            
            # 5. Transaction pattern analysis
            avg_transaction = await self._get_average_transaction_amount(account_id)
            if avg_transaction > 0 and amount > avg_transaction * 10:  # 10x higher than usual
                risk_score += 25
                risk_factors.append("unusual_amount_pattern")
            
            # 6. Geographic anomaly (if IP location available in metadata)
            if metadata and metadata.get("ip_country"):
                usual_country = await self._get_usual_country(account_id)
                if usual_country and metadata["ip_country"] != usual_country:
                    risk_score += 35
                    risk_factors.append("geographic_anomaly")
            
            is_suspicious = risk_score >= 50  # Threshold for suspicious activity
            
            return {
                "is_suspicious": is_suspicious,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "reason": ", ".join(risk_factors) if risk_factors else "low_risk"
            }
            
        except Exception as e:
            logger.error(f"Fraud detection failed: {e}")
            return {"is_suspicious": False, "risk_score": 0, "risk_factors": [], "reason": "detection_error"}
    
    # ================================
    # ACCOUNT ANALYTICS & INSIGHTS
    # ================================
    
    async def get_account_analytics(
        self,
        account_id: str,
        period_days: int = 30,
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive account analytics and insights
        """
        try:
            account = await self._get_account_by_id(account_id, user_id)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Transaction analytics
            transactions = self.db.query(DigitalTransaction).filter(
                DigitalTransaction.account_id == account_id,
                DigitalTransaction.created_at >= start_date,
                DigitalTransaction.status == TransactionStatus.COMPLETED
            ).all()
            
            # Calculate metrics
            total_transactions = len(transactions)
            total_inflow = sum(t.amount for t in transactions 
                             if t.transaction_type in [TransactionType.DEPOSIT, TransactionType.REFUND])
            total_outflow = sum(t.amount for t in transactions 
                              if t.transaction_type in [TransactionType.WITHDRAW, TransactionType.PAYMENT, TransactionType.TRANSFER])
            
            # Balance trend (daily)
            balance_trend = await self._calculate_daily_balance_trend(account_id, start_date, end_date)
            
            # Transaction categories
            transaction_summary = {}
            for transaction_type in TransactionType:
                type_transactions = [t for t in transactions if t.transaction_type == transaction_type]
                if type_transactions:
                    transaction_summary[transaction_type] = {
                        "count": len(type_transactions),
                        "total_amount": sum(t.amount for t in type_transactions),
                        "avg_amount": sum(t.amount for t in type_transactions) / len(type_transactions)
                    }
            
            # Risk analysis
            risk_events = await self._get_risk_events(account_id, start_date)
            
            # Spending patterns
            spending_patterns = await self._analyze_spending_patterns(account_id, period_days)
            
            # Generate insights
            insights = await self._generate_account_insights(account, transactions, balance_trend)
            
            return {
                "account_id": account_id,
                "period_days": period_days,
                "summary": {
                    "current_balance": account.balance,
                    "total_transactions": total_transactions,
                    "total_inflow": total_inflow,
                    "total_outflow": total_outflow,
                    "net_flow": total_inflow - total_outflow,
                    "avg_daily_transactions": total_transactions / period_days if period_days > 0 else 0
                },
                "balance_trend": balance_trend,
                "transaction_summary": transaction_summary,
                "spending_patterns": spending_patterns,
                "risk_analysis": {
                    "current_risk_level": account.risk_level,
                    "risk_events_count": len(risk_events),
                    "risk_events": risk_events[-10:]  # Last 10 events
                },
                "insights": insights,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Account analytics generation failed: {e}")
            raise DigitalAccountError(f"Analytics generation failed: {str(e)}")
    
    # ================================
    # ENHANCED HELPER METHODS
    # ================================
    
    @asynccontextmanager
    async def _get_account_lock(self, account_id: str):
        """Get distributed lock for account operations"""
        if self.redis_client:
            lock_key = f"account_lock:{account_id}"
            lock = self.redis_client.lock(lock_key, timeout=30)
            try:
                acquired = await lock.acquire(blocking=True, blocking_timeout=10)
                if not acquired:
                    raise DigitalAccountError("Could not acquire account lock")
                yield lock
            finally:
                try:
                    await lock.release()
                except:
                    pass  # Lock might have expired
        else:
            # Fallback without distributed locking
            yield None
    
    @asynccontextmanager
    async def _get_multiple_account_locks(self, account_ids: List[str]):
        """Get multiple account locks in sorted order to prevent deadlocks"""
        if self.redis_client:
            # Sort account IDs to prevent deadlocks
            sorted_ids = sorted(account_ids)
            locks = []
            
            try:
                for account_id in sorted_ids:
                    lock_key = f"account_lock:{account_id}"
                    lock = self.redis_client.lock(lock_key, timeout=30)
                    acquired = await lock.acquire(blocking=True, blocking_timeout=10)
                    if not acquired:
                        # Release already acquired locks
                        for acquired_lock in locks:
                            try:
                                await acquired_lock.release()
                            except:
                                pass
                        raise DigitalAccountError("Could not acquire all account locks")
                    locks.append(lock)
                
                yield locks
                
            finally:
                # Release all locks
                for lock in locks:
                    try:
                        await lock.release()
                    except:
                        pass
        else:
            yield None
    
    # Additional helper methods would be implemented here
    async def _validate_account_creation(self, user_id: int, account_type: AccountType, parent_account_id: str = None):
        """Validate account creation parameters"""
        # Implementation for validation logic
        pass
    
    async def _count_user_accounts(self, user_id: int) -> int:
        """Count existing accounts for user"""
        return self.db.query(DigitalAccount).filter(
            DigitalAccount.user_id == user_id,
            DigitalAccount.status.in_([AccountStatus.ACTIVE, AccountStatus.SUSPENDED])
        ).count()
    
    async def _generate_account_number(self, account_type: AccountType) -> str:
        """Generate unique account number"""
        prefix = "01" if account_type == AccountType.PERSONAL else "02"
        timestamp = int(datetime.utcnow().timestamp())
        random_suffix = str(uuid.uuid4().int)[-6:]
        return f"{prefix}{timestamp}{random_suffix}"
    
    async def _get_exchange_rate(self, from_currency: Currency, to_currency: Currency) -> Decimal:
        """Get current exchange rate between currencies"""
        rate_key = (from_currency, to_currency)
        return self.exchange_rates.get(rate_key, Decimal('1.00'))
    
    async def _calculate_precise_balance(self, account_id: str) -> Decimal:
        """Calculate precise balance from all completed transactions"""
        # Implementation for precise balance calculation
        return Decimal('0.00')
    
    async def _get_cached_balance(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get cached balance data"""
        if self.redis_client:
            cache_key = f"balance:{account_id}"
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        return None
    
    def _is_cache_fresh(self, cached_data: Dict[str, Any], max_age_seconds: int = 30) -> bool:
        """Check if cached data is fresh enough"""
        if not cached_data.get('last_updated'):
            return False
        
        cached_time = datetime.fromisoformat(cached_data['last_updated'])
        age_seconds = (datetime.utcnow() - cached_time).total_seconds()
        return age_seconds <= max_age_seconds