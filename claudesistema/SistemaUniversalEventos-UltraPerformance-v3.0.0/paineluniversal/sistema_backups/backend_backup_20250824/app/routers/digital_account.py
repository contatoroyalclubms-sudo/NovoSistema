"""
Router para Sistema de Conta Digital
Sistema Universal de Gestão de Eventos - Sprint 2

Funcionalidades:
- Conta digital completa com saldo em tempo real
- Transferências instantâneas
- Histórico de transações
- Carteira digital integrada
- Controle de limites e bloqueios
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import BaseModel, Field
import uuid
from enum import Enum

# Imports do sistema
from app.core.security import get_current_user
from app.core.database import get_db
from app.schemas import ResponseModel
from app.services.digital_account_service import DigitalAccountService
from app.services.validation_service import ValidationService

router = APIRouter(prefix="/digital-account", tags=["Digital Account"])

# Enums
class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    REFUND = "refund"

class AccountStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended" 
    BLOCKED = "blocked"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Schemas
class DigitalAccountCreate(BaseModel):
    user_id: int
    initial_balance: Decimal = Field(default=0.00, ge=0)
    daily_limit: Decimal = Field(default=5000.00, ge=0)
    monthly_limit: Decimal = Field(default=50000.00, ge=0)

class DigitalAccountResponse(BaseModel):
    account_id: str
    user_id: int
    balance: Decimal
    available_balance: Decimal
    blocked_balance: Decimal
    daily_limit: Decimal
    monthly_limit: Decimal
    status: AccountStatus
    created_at: datetime
    updated_at: datetime

class TransactionCreate(BaseModel):
    transaction_type: TransactionType
    amount: Decimal = Field(gt=0)
    description: str = Field(max_length=255)
    destination_account_id: Optional[str] = None
    reference_id: Optional[str] = None
    metadata: Optional[dict] = None

class TransactionResponse(BaseModel):
    transaction_id: str
    account_id: str
    transaction_type: TransactionType
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    description: str
    status: TransactionStatus
    reference_id: Optional[str]
    destination_account_id: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

class BalanceResponse(BaseModel):
    account_id: str
    balance: Decimal
    available_balance: Decimal
    blocked_balance: Decimal
    last_transaction: Optional[datetime]

class TransferRequest(BaseModel):
    destination_account_id: str
    amount: Decimal = Field(gt=0)
    description: str = Field(max_length=255)
    transfer_key: Optional[str] = None  # Chave PIX ou similar

# Serviços (injetados via DI)
def get_digital_account_service(db = Depends(get_db)) -> DigitalAccountService:
    return DigitalAccountService(db)

def get_validation_service() -> ValidationService:
    return ValidationService()

# ================================
# ENDPOINTS DA CONTA DIGITAL
# ================================

@router.post("/create", response_model=DigitalAccountResponse)
async def create_digital_account(
    account_data: DigitalAccountCreate,
    current_user = Depends(get_current_user),
    service: DigitalAccountService = Depends(get_digital_account_service)
):
    """
    Criar nova conta digital
    """
    try:
        account = await service.create_account(
            user_id=account_data.user_id,
            initial_balance=account_data.initial_balance,
            daily_limit=account_data.daily_limit,
            monthly_limit=account_data.monthly_limit,
            created_by=current_user.id
        )
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/balance/{account_id}", response_model=BalanceResponse)
async def get_account_balance(
    account_id: str,
    current_user = Depends(get_current_user),
    service: DigitalAccountService = Depends(get_digital_account_service)
):
    """
    Consultar saldo da conta em tempo real
    """
    try:
        balance = await service.get_balance(account_id, user_id=current_user.id)
        return balance
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/statement/{account_id}")
async def get_account_statement(
    account_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    transaction_type: Optional[TransactionType] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    service: DigitalAccountService = Depends(get_digital_account_service)
):
    """
    Extrato detalhado da conta com filtros
    """
    try:
        # Default para últimos 30 dias se não especificado
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        statement = await service.get_statement(
            account_id=account_id,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
            limit=limit,
            offset=offset
        )
        
        return {
            "account_id": account_id,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": statement["summary"],
            "transactions": statement["transactions"],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": statement["total_count"]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ================================
# TRANSAÇÕES
# ================================

@router.post("/transaction", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    account_id: str,
    current_user = Depends(get_current_user),
    service: DigitalAccountService = Depends(get_digital_account_service),
    validation: ValidationService = Depends(get_validation_service)
):
    """
    Criar nova transação (depósito, saque, pagamento)
    """
    try:
        # Validações de negócio
        await validation.validate_transaction_limits(
            account_id=account_id,
            amount=transaction.amount,
            transaction_type=transaction.transaction_type
        )

        result = await service.process_transaction(
            account_id=account_id,
            transaction_type=transaction.transaction_type,
            amount=transaction.amount,
            description=transaction.description,
            destination_account_id=transaction.destination_account_id,
            reference_id=transaction.reference_id,
            metadata=transaction.metadata,
            user_id=current_user.id
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/transfer")
async def transfer_funds(
    transfer: TransferRequest,
    account_id: str,
    current_user = Depends(get_current_user),
    service: DigitalAccountService = Depends(get_digital_account_service)
):
    """
    Transferir fundos entre contas digitais
    """
    try:
        result = await service.transfer_funds(
            source_account_id=account_id,
            destination_account_id=transfer.destination_account_id,
            amount=transfer.amount,
            description=transfer.description,
            transfer_key=transfer.transfer_key,
            user_id=current_user.id
        )
        
        return {
            "transfer_id": result["transfer_id"],
            "status": result["status"],
            "processed_at": result["processed_at"],
            "amount": result["amount"],
            "fee": result.get("fee", 0),
            "net_amount": result["net_amount"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ================================
# GESTÃO DA CONTA
# ================================

@router.put("/limits/{account_id}")
async def update_account_limits(
    account_id: str,
    daily_limit: Optional[Decimal] = None,
    monthly_limit: Optional[Decimal] = None,
    current_user = Depends(get_current_user),
    service: DigitalAccountService = Depends(get_digital_account_service)
):
    """
    Atualizar limites da conta digital
    """
    try:
        result = await service.update_limits(
            account_id=account_id,
            daily_limit=daily_limit,
            monthly_limit=monthly_limit,
            user_id=current_user.id
        )
        return {"message": "Limites atualizados com sucesso", "account": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/block/{account_id}")
async def block_account(
    account_id: str,
    reason: str = Query(..., max_length=255),
    current_user = Depends(get_current_user),
    service: DigitalAccountService = Depends(get_digital_account_service)
):
    """
    Bloquear conta digital
    """
    try:
        await service.block_account(
            account_id=account_id,
            reason=reason,
            blocked_by=current_user.id
        )
        return {"message": "Conta bloqueada com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/unblock/{account_id}")
async def unblock_account(
    account_id: str,
    current_user = Depends(get_current_user),
    service: DigitalAccountService = Depends(get_digital_account_service)
):
    """
    Desbloquear conta digital
    """
    try:
        await service.unblock_account(
            account_id=account_id,
            unblocked_by=current_user.id
        )
        return {"message": "Conta desbloqueada com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ================================
# RELATÓRIOS E ANALYTICS
# ================================

@router.get("/analytics/{account_id}")
async def get_account_analytics(
    account_id: str,
    period_days: int = Query(30, ge=1, le=365),
    current_user = Depends(get_current_user),
    service: DigitalAccountService = Depends(get_digital_account_service)
):
    """
    Analytics da conta digital - gráficos e insights
    """
    try:
        analytics = await service.get_account_analytics(
            account_id=account_id,
            period_days=period_days,
            user_id=current_user.id
        )
        
        return {
            "account_id": account_id,
            "period_days": period_days,
            "balance_trend": analytics["balance_trend"],
            "transaction_summary": analytics["transaction_summary"],
            "monthly_flow": analytics["monthly_flow"],
            "category_breakdown": analytics["category_breakdown"],
            "insights": analytics["insights"]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ================================
# WEBHOOKS E NOTIFICAÇÕES
# ================================

@router.post("/webhook/transaction")
async def transaction_webhook(
    webhook_data: dict,
    service: DigitalAccountService = Depends(get_digital_account_service)
):
    """
    Webhook para notificações de transações externas
    """
    try:
        result = await service.process_webhook(webhook_data)
        return {"status": "processed", "transaction_id": result["transaction_id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro processando webhook")

# ================================
# UTILITÁRIOS
# ================================

@router.get("/validate-account/{account_id}")
async def validate_account(
    account_id: str,
    service: DigitalAccountService = Depends(get_digital_account_service)
):
    """
    Validar se conta existe e está ativa (para transferências)
    """
    try:
        is_valid = await service.validate_account(account_id)
        return {
            "account_id": account_id,
            "is_valid": is_valid["exists"],
            "is_active": is_valid["active"],
            "can_receive": is_valid["can_receive"]
        }
    except Exception as e:
        return {"is_valid": False, "error": "Erro na validação"}