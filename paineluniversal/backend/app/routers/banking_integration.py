"""
Banking Integration Router - Complete Banking System API
Sistema Universal de Gestão de Eventos

Comprehensive banking integration providing:
- Unified banking operations API
- PIX payment processing
- Multi-gateway payment processing  
- Account management with real-time tracking
- Treasury operations and automation
- Webhook processing and reconciliation
- Compliance and security enforcement
- Integration with existing payment systems
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid

from app.core.security import get_current_user
from app.core.database import get_db
from app.services.banking_service import BankingService, BankingGateway, PaymentMethod
from app.services.pix_service import PIXService, PIXKeyType, PIXStatus
from app.services.payment_processor_service import PaymentProcessorService, CardType
from app.services.digital_account_service import (
    EnhancedDigitalAccountService, 
    AccountType, 
    Currency, 
    TransactionType,
    RiskLevel
)
from app.services.treasury_service import TreasuryService, TreasuryOperationType
from app.services.banking_webhook_service import BankingWebhookService, WebhookEventType
from app.services.compliance_security_service import ComplianceSecurityService
from app.services.payment_links_service import PaymentLinksService
from app.services.split_payments_service import SplitPaymentsService

router = APIRouter(prefix="/api/v1/banking", tags=["Banking Integration"])

# ================================
# ACCOUNT MANAGEMENT
# ================================

class AccountCreateRequest(BaseModel):
    account_type: AccountType = AccountType.PERSONAL
    currency: Currency = Currency.BRL
    initial_balance: Decimal = Field(default=Decimal('0.00'), ge=0)
    daily_limit: Decimal = Field(default=Decimal('5000.00'), ge=0)
    monthly_limit: Decimal = Field(default=Decimal('50000.00'), ge=0)
    parent_account_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AccountResponse(BaseModel):
    account_id: str
    account_number: str
    account_type: AccountType
    currency: Currency
    balance: Decimal
    available_balance: Decimal
    blocked_balance: Decimal
    pending_balance: Decimal
    status: str
    risk_level: RiskLevel
    daily_limit: Decimal
    monthly_limit: Decimal
    parent_account_id: Optional[str]
    created_at: datetime
    updated_at: datetime


@router.post("/accounts", response_model=AccountResponse)
async def create_account(
    account_data: AccountCreateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create new banking account with enhanced features"""
    try:
        account_service = EnhancedDigitalAccountService(db)
        
        account = await account_service.create_account(
            user_id=current_user.id,
            account_type=account_data.account_type,
            currency=account_data.currency,
            initial_balance=account_data.initial_balance,
            daily_limit=account_data.daily_limit,
            monthly_limit=account_data.monthly_limit,
            parent_account_id=account_data.parent_account_id,
            metadata=account_data.metadata,
            created_by=current_user.id
        )
        
        return AccountResponse(**account)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Account creation failed: {str(e)}")


@router.get("/accounts", response_model=List[AccountResponse])
async def list_accounts(
    account_type: Optional[AccountType] = Query(None),
    currency: Optional[Currency] = Query(None),
    status: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """List user's banking accounts with filtering"""
    try:
        account_service = EnhancedDigitalAccountService(db)
        
        # Get all user accounts (implementation would include filtering)
        accounts = await account_service.get_user_accounts(
            user_id=current_user.id,
            account_type=account_type,
            currency=currency,
            status=status
        )
        
        return {"accounts": accounts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch accounts: {str(e)}")


@router.get("/accounts/{account_id}/balance")
async def get_real_time_balance(
    account_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get real-time account balance with caching"""
    try:
        account_service = EnhancedDigitalAccountService(db)
        
        balance_data = await account_service.get_real_time_balance(account_id)
        
        return balance_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Balance retrieval failed: {str(e)}")


@router.get("/accounts/{account_id}/analytics")
async def get_account_analytics(
    account_id: str,
    period_days: int = Query(30, ge=1, le=365),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get comprehensive account analytics"""
    try:
        account_service = EnhancedDigitalAccountService(db)
        
        analytics = await account_service.get_account_analytics(
            account_id=account_id,
            period_days=period_days,
            user_id=current_user.id
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")


# ================================
# PIX OPERATIONS
# ================================

class PIXCreateRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    recipient_key: str
    recipient_name: str
    description: Optional[str] = None
    expires_in_minutes: int = Field(default=30, ge=1, le=1440)
    merchant_city: str = Field(default="Sao Paulo")


class PIXKeyRegisterRequest(BaseModel):
    key_value: str
    key_type: PIXKeyType
    account_id: str
    owner_name: str
    owner_document: str


@router.post("/pix/create-qr")
async def create_pix_qr_code(
    pix_data: PIXCreateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create dynamic PIX QR code for payments"""
    try:
        pix_service = PIXService(db)
        
        pix_qr = await pix_service.create_dynamic_pix_qr(
            amount=pix_data.amount,
            recipient_key=pix_data.recipient_key,
            recipient_name=pix_data.recipient_name,
            description=pix_data.description,
            expires_in_minutes=pix_data.expires_in_minutes,
            merchant_city=pix_data.merchant_city
        )
        
        return pix_qr
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PIX QR creation failed: {str(e)}")


@router.post("/pix/register-key")
async def register_pix_key(
    key_data: PIXKeyRegisterRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Register PIX key for receiving payments"""
    try:
        pix_service = PIXService(db)
        
        result = await pix_service.register_pix_key(
            key_value=key_data.key_value,
            key_type=key_data.key_type,
            account_id=key_data.account_id,
            owner_name=key_data.owner_name,
            owner_document=key_data.owner_document
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PIX key registration failed: {str(e)}")


@router.get("/pix/{pix_id}/status")
async def check_pix_status(
    pix_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Check PIX payment status"""
    try:
        pix_service = PIXService(db)
        
        status = await pix_service.check_pix_status(pix_id)
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PIX status check failed: {str(e)}")


# ================================
# PAYMENT PROCESSING
# ================================

class CardPaymentRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    card_data: Dict[str, Any]
    customer_data: Dict[str, Any]
    installments: int = Field(default=1, ge=1, le=12)
    capture: bool = True
    gateway: Optional[BankingGateway] = None
    metadata: Optional[Dict[str, Any]] = None


class RecurringPaymentRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    card_token: str
    customer_data: Dict[str, Any]
    frequency: str  # "monthly", "weekly", "yearly"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_cycles: Optional[int] = None
    description: Optional[str] = None


@router.post("/payments/card")
async def process_card_payment(
    payment_data: CardPaymentRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Process credit/debit card payment with fraud detection"""
    try:
        payment_processor = PaymentProcessorService(db)
        compliance_service = ComplianceSecurityService(db)
        
        # PCI compliance validation
        pci_validation = await compliance_service.validate_pci_operation(
            operation_type="card_payment",
            context={
                "amount": payment_data.amount,
                "card_data": payment_data.card_data,
                "user_id": current_user.id
            }
        )
        
        if not pci_validation["compliant"]:
            raise HTTPException(status_code=400, detail="PCI compliance violation")
        
        # Process payment
        result = await payment_processor.process_card_payment(
            amount=payment_data.amount,
            card_data=payment_data.card_data,
            customer_data=payment_data.customer_data,
            installments=payment_data.installments,
            capture=payment_data.capture,
            gateway=payment_data.gateway,
            metadata=payment_data.metadata
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Card payment failed: {str(e)}")


@router.post("/payments/recurring")
async def create_recurring_payment(
    recurring_data: RecurringPaymentRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create recurring payment subscription"""
    try:
        payment_processor = PaymentProcessorService(db)
        
        result = await payment_processor.create_recurring_payment(
            amount=recurring_data.amount,
            card_token=recurring_data.card_token,
            customer_data=recurring_data.customer_data,
            frequency=recurring_data.frequency,
            start_date=recurring_data.start_date,
            end_date=recurring_data.end_date,
            total_cycles=recurring_data.total_cycles,
            description=recurring_data.description
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recurring payment creation failed: {str(e)}")


@router.post("/payments/boleto")
async def generate_boleto(
    amount: Decimal = Field(gt=0),
    customer_data: Dict[str, Any] = None,
    due_date: Optional[date] = None,
    description: Optional[str] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Generate boleto bancário for payment"""
    try:
        payment_processor = PaymentProcessorService(db)
        
        boleto = await payment_processor.generate_boleto(
            amount=amount,
            customer_data=customer_data or {},
            due_date=due_date,
            description=description
        )
        
        return boleto
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Boleto generation failed: {str(e)}")


# ================================
# TREASURY MANAGEMENT
# ================================

@router.post("/treasury/sweep")
async def run_cash_sweep(
    account_ids: Optional[List[str]] = None,
    target_account_id: Optional[str] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Execute automated cash sweep operation"""
    try:
        treasury_service = TreasuryService(db)
        
        result = await treasury_service.run_automated_cash_sweep(
            account_ids=account_ids,
            target_account_id=target_account_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cash sweep failed: {str(e)}")


@router.get("/treasury/liquidity")
async def monitor_liquidity(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Monitor liquidity levels across accounts"""
    try:
        treasury_service = TreasuryService(db)
        
        liquidity_status = await treasury_service.monitor_liquidity_levels()
        
        return liquidity_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Liquidity monitoring failed: {str(e)}")


@router.post("/treasury/invest")
async def automated_investment(
    account_id: str,
    investment_amount: Optional[Decimal] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Execute automated investment placement"""
    try:
        treasury_service = TreasuryService(db)
        
        result = await treasury_service.run_automated_investment(
            account_id=account_id,
            investment_amount=investment_amount
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Automated investment failed: {str(e)}")


# ================================
# WEBHOOK PROCESSING
# ================================

@router.post("/webhooks/{gateway}")
async def process_banking_webhook(
    gateway: BankingGateway,
    request: Request,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Process banking webhooks from payment gateways"""
    try:
        webhook_service = BankingWebhookService(db)
        
        # Get request data
        headers = dict(request.headers)
        raw_body = await request.body()
        
        try:
            payload = await request.json()
        except:
            payload = {}
        
        # Process webhook in background for better response time
        background_tasks.add_task(
            webhook_service.process_webhook,
            gateway=gateway,
            headers=headers,
            payload=payload,
            raw_body=raw_body.decode() if raw_body else None
        )
        
        return {"status": "received", "message": "Webhook processing initiated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


@router.post("/reconciliation/run")
async def run_reconciliation(
    gateway: Optional[BankingGateway] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Run automated reconciliation process"""
    try:
        webhook_service = BankingWebhookService(db)
        
        result = await webhook_service.run_automated_reconciliation(
            gateway=gateway,
            start_date=start_date,
            end_date=end_date
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reconciliation failed: {str(e)}")


# ================================
# INTEGRATION WITH EXISTING SYSTEMS
# ================================

@router.post("/integration/payment-link")
async def create_integrated_payment_link(
    amount: Decimal = Field(gt=0),
    title: str = Field(max_length=100),
    description: Optional[str] = None,
    payment_methods: List[PaymentMethod] = Field(default=[PaymentMethod.PIX, PaymentMethod.CREDIT_CARD]),
    enable_split: bool = False,
    split_recipients: Optional[List[Dict[str, Any]]] = None,
    expires_at: Optional[datetime] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create payment link with integrated banking services"""
    try:
        # Use existing payment links service with banking integration
        payment_links_service = PaymentLinksService(db)
        banking_service = BankingService(db)
        
        # Create payment link with enhanced features
        link_data = {
            "title": title,
            "description": description,
            "amount": amount,
            "payment_methods": payment_methods,
            "enable_split": enable_split,
            "split_recipients": split_recipients,
            "expires_at": expires_at,
            "banking_integration": True,  # Enable banking features
            "fraud_protection": True,
            "compliance_checks": True
        }
        
        result = await payment_links_service.create_enhanced_payment_link(
            user_id=current_user.id,
            link_data=link_data
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integrated payment link creation failed: {str(e)}")


@router.post("/integration/split-payment")
async def create_integrated_split_payment(
    transaction_amount: Decimal = Field(gt=0),
    transaction_reference: str,
    recipients: List[Dict[str, Any]] = Field(min_items=1),
    payment_method: PaymentMethod = PaymentMethod.PIX,
    gateway: Optional[BankingGateway] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create split payment with banking integration"""
    try:
        split_service = SplitPaymentsService(db)
        banking_service = BankingService(db)
        
        # Enhanced split payment with banking features
        split_data = {
            "transaction_amount": transaction_amount,
            "transaction_reference": transaction_reference,
            "recipients": recipients,
            "payment_method": payment_method,
            "gateway": gateway,
            "banking_integration": True,
            "real_time_processing": True,
            "fraud_protection": True
        }
        
        result = await split_service.create_integrated_split_payment(
            user_id=current_user.id,
            split_data=split_data
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integrated split payment creation failed: {str(e)}")


# ================================
# SECURITY AND COMPLIANCE
# ================================

@router.get("/compliance/status")
async def get_compliance_status(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get compliance status across all frameworks"""
    try:
        compliance_service = ComplianceSecurityService(db)
        
        status = await compliance_service.get_overall_compliance_status(
            user_id=current_user.id
        )
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance status check failed: {str(e)}")


@router.get("/security/alerts")
async def get_security_alerts(
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get active security alerts and fraud notifications"""
    try:
        compliance_service = ComplianceSecurityService(db)
        
        alerts = await compliance_service.get_security_alerts(
            user_id=current_user.id,
            severity=severity,
            limit=limit
        )
        
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security alerts retrieval failed: {str(e)}")


@router.post("/security/analyze-risk")
async def analyze_transaction_risk(
    transaction_data: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Analyze transaction risk using fraud detection engine"""
    try:
        compliance_service = ComplianceSecurityService(db)
        
        # Add user context
        context = user_context or {}
        context["user_id"] = current_user.id
        
        risk_analysis = await compliance_service.analyze_transaction_risk(
            transaction_data=transaction_data,
            user_context=context
        )
        
        return risk_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


# ================================
# DASHBOARD AND METRICS
# ================================

@router.get("/metrics/overview")
async def get_banking_metrics(
    timeframe: str = Query("7d", regex="^(1d|7d|30d|90d)$"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get comprehensive banking metrics for dashboard"""
    try:
        account_service = EnhancedDigitalAccountService(db)
        banking_service = BankingService(db)
        
        # Calculate timeframe
        days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
        days = days_map[timeframe]
        
        metrics = await banking_service.get_dashboard_metrics(
            user_id=current_user.id,
            days=days
        )
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")


@router.get("/transactions")
async def get_transaction_history(
    account_id: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get transaction history with filtering and pagination"""
    try:
        account_service = EnhancedDigitalAccountService(db)
        
        transactions = await account_service.get_transaction_history(
            user_id=current_user.id,
            account_id=account_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        return transactions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transaction history retrieval failed: {str(e)}")


@router.get("/fraud-alerts")
async def get_fraud_alerts(
    status: Optional[str] = Query("active"),
    severity: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get fraud alerts for user accounts"""
    try:
        compliance_service = ComplianceSecurityService(db)
        
        alerts = await compliance_service.get_fraud_alerts(
            user_id=current_user.id,
            status=status,
            severity=severity,
            limit=limit
        )
        
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fraud alerts retrieval failed: {str(e)}")


# ================================
# UTILITY ENDPOINTS
# ================================

@router.get("/health")
async def banking_health_check():
    """Health check for banking services"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "banking_service": "operational",
            "pix_service": "operational", 
            "payment_processor": "operational",
            "account_management": "operational",
            "treasury_management": "operational",
            "webhook_processing": "operational",
            "compliance_security": "operational"
        }
    }


@router.get("/supported-gateways")
async def get_supported_gateways():
    """Get list of supported payment gateways"""
    return {
        "gateways": [
            {
                "name": "PicPay",
                "code": "picpay",
                "methods": ["pix", "credit_card", "wallet"],
                "active": True
            },
            {
                "name": "PagSeguro",
                "code": "pagseguro", 
                "methods": ["pix", "credit_card", "boleto"],
                "active": True
            },
            {
                "name": "Asaas",
                "code": "asaas",
                "methods": ["pix", "credit_card", "boleto", "bank_transfer"],
                "active": True
            },
            {
                "name": "MercadoPago",
                "code": "mercadopago",
                "methods": ["pix", "credit_card", "debit_card", "bank_transfer"],
                "active": True
            }
        ]
    }