"""
Router para Sistema de Split de Pagamentos
Sistema Universal de Gestão de Eventos - Sprint 2

Funcionalidades:
- Split automático de pagamentos
- Múltiplos destinatários por transação
- Regras personalizáveis de divisão
- Comissões automáticas
- Liquidação inteligente
- Controle de taxas por participante
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum
import uuid

# Imports do sistema
from app.core.security import get_current_user
from app.core.database import get_db
from app.services.split_payments_service import SplitPaymentsService
from app.services.digital_account_service import DigitalAccountService

router = APIRouter(prefix="/split-payments", tags=["Split Payments"])

# Enums
class SplitType(str, Enum):
    PERCENTAGE = "percentage"  # Divisão por percentual
    FIXED_AMOUNT = "fixed_amount"  # Valor fixo
    RATIO = "ratio"  # Proporção/ratio
    RULE_BASED = "rule_based"  # Baseado em regras

class SplitStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RecipientType(str, Enum):
    MAIN_ACCOUNT = "main_account"  # Conta principal
    COMMISSION = "commission"  # Comissão
    FEE = "fee"  # Taxa
    SUPPLIER = "supplier"  # Fornecedor
    PARTNER = "partner"  # Parceiro

# Schemas
class SplitRecipient(BaseModel):
    recipient_id: str
    recipient_type: RecipientType
    account_id: str
    amount: Optional[Decimal] = None
    percentage: Optional[float] = None
    ratio: Optional[int] = None
    description: Optional[str] = None
    is_liable_for_fees: bool = Field(default=False)
    metadata: Optional[Dict[str, Any]] = None

    @root_validator
    def validate_amount_or_percentage(cls, values):
        amount = values.get('amount')
        percentage = values.get('percentage')
        ratio = values.get('ratio')
        
        provided_fields = sum([
            amount is not None,
            percentage is not None,
            ratio is not None
        ])
        
        if provided_fields != 1:
            raise ValueError("Deve ser fornecido exatamente um: amount, percentage ou ratio")
        
        if percentage is not None and not (0 < percentage <= 100):
            raise ValueError("Percentual deve estar entre 0.01 e 100")
            
        if ratio is not None and ratio <= 0:
            raise ValueError("Ratio deve ser maior que zero")
            
        return values

class SplitRule(BaseModel):
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]  # Condições para aplicar a regra
    recipients: List[SplitRecipient]
    is_active: bool = True
    priority: int = Field(default=1, ge=1, le=10)

class SplitPaymentRequest(BaseModel):
    transaction_amount: Decimal = Field(..., gt=0)
    transaction_reference: str
    split_type: SplitType = SplitType.PERCENTAGE
    recipients: List[SplitRecipient] = Field(..., min_items=1, max_items=20)
    rule_id: Optional[str] = None  # Se usar regra pré-definida
    description: Optional[str] = None
    webhook_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('recipients')
    def validate_recipients_sum(cls, recipients, values):
        transaction_amount = values.get('transaction_amount', 0)
        split_type = values.get('split_type')
        
        if split_type == SplitType.PERCENTAGE:
            total_percentage = sum(r.percentage or 0 for r in recipients)
            if abs(total_percentage - 100.0) > 0.01:
                raise ValueError("Soma dos percentuais deve ser 100%")
        
        elif split_type == SplitType.FIXED_AMOUNT:
            total_amount = sum(r.amount or 0 for r in recipients)
            if total_amount > transaction_amount:
                raise ValueError("Soma dos valores excede o valor total da transação")
        
        return recipients

class SplitPaymentResponse(BaseModel):
    split_id: str
    status: SplitStatus
    transaction_amount: Decimal
    total_split_amount: Decimal
    total_fees: Decimal
    net_amount: Decimal
    recipients_count: int
    created_at: datetime
    processed_at: Optional[datetime]
    completed_at: Optional[datetime]
    webhook_url: Optional[str]

class SplitRecipientStatus(BaseModel):
    recipient_id: str
    account_id: str
    amount: Decimal
    net_amount: Decimal  # Após taxas
    fees: Decimal
    status: str  # "completed", "failed", "pending"
    processed_at: Optional[datetime]
    error_message: Optional[str]

class SplitDetailsResponse(BaseModel):
    split_id: str
    status: SplitStatus
    transaction_reference: str
    transaction_amount: Decimal
    split_type: SplitType
    description: Optional[str]
    recipients: List[SplitRecipientStatus]
    summary: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime]

# Serviços
def get_split_service(db = Depends(get_db)) -> SplitPaymentsService:
    return SplitPaymentsService(db)

# ================================
# PROCESSAMENTO DE SPLIT
# ================================

@router.post("/process", response_model=SplitPaymentResponse)
async def process_split_payment(
    split_request: SplitPaymentRequest,
    current_user = Depends(get_current_user),
    service: SplitPaymentsService = Depends(get_split_service),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Processar split de pagamento com múltiplos destinatários
    """
    try:
        # Validar contas destinatárias
        await service.validate_recipient_accounts(split_request.recipients)
        
        # Calcular distribuição exata
        distribution = await service.calculate_split_distribution(
            amount=split_request.transaction_amount,
            recipients=split_request.recipients,
            split_type=split_request.split_type
        )
        
        # Criar registro do split
        split_id = str(uuid.uuid4())
        split_record = await service.create_split_record(
            split_id=split_id,
            user_id=current_user.id,
            split_request=split_request,
            distribution=distribution
        )
        
        # Processar split em background
        background_tasks.add_task(
            process_split_transfers,
            split_id=split_id,
            distribution=distribution,
            service=service
        )
        
        return SplitPaymentResponse(
            split_id=split_id,
            status=SplitStatus.PROCESSING,
            transaction_amount=split_request.transaction_amount,
            total_split_amount=distribution["total_split_amount"],
            total_fees=distribution["total_fees"],
            net_amount=distribution["net_amount"],
            recipients_count=len(split_request.recipients),
            created_at=split_record["created_at"],
            processed_at=None,
            completed_at=None,
            webhook_url=split_request.webhook_url
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao processar split de pagamento")

@router.get("/status/{split_id}", response_model=SplitDetailsResponse)
async def get_split_status(
    split_id: str,
    current_user = Depends(get_current_user),
    service: SplitPaymentsService = Depends(get_split_service)
):
    """
    Consultar status detalhado de um split
    """
    try:
        split_details = await service.get_split_details(
            split_id=split_id,
            user_id=current_user.id
        )
        
        if not split_details:
            raise HTTPException(status_code=404, detail="Split não encontrado")
        
        return SplitDetailsResponse(**split_details)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao consultar status")

# ================================
# REGRAS DE SPLIT
# ================================

@router.post("/rules", response_model=Dict[str, str])
async def create_split_rule(
    rule: SplitRule,
    current_user = Depends(get_current_user),
    service: SplitPaymentsService = Depends(get_split_service)
):
    """
    Criar regra personalizada de split
    """
    try:
        # Validar regra
        await service.validate_split_rule(rule, current_user.id)
        
        # Criar regra
        rule_id = await service.create_split_rule(
            rule=rule,
            user_id=current_user.id
        )
        
        return {"rule_id": rule_id, "message": "Regra criada com sucesso"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao criar regra")

@router.get("/rules", response_model=List[SplitRule])
async def get_split_rules(
    active_only: bool = Query(default=True),
    current_user = Depends(get_current_user),
    service: SplitPaymentsService = Depends(get_split_service)
):
    """
    Listar regras de split do usuário
    """
    try:
        rules = await service.get_user_split_rules(
            user_id=current_user.id,
            active_only=active_only
        )
        return rules
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao consultar regras")

@router.put("/rules/{rule_id}")
async def update_split_rule(
    rule_id: str,
    rule_updates: Dict[str, Any],
    current_user = Depends(get_current_user),
    service: SplitPaymentsService = Depends(get_split_service)
):
    """
    Atualizar regra de split existente
    """
    try:
        updated_rule = await service.update_split_rule(
            rule_id=rule_id,
            user_id=current_user.id,
            updates=rule_updates
        )
        return {"message": "Regra atualizada com sucesso", "rule": updated_rule}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao atualizar regra")

# ================================
# SIMULAÇÃO DE SPLIT
# ================================

@router.post("/simulate")
async def simulate_split(
    transaction_amount: Decimal = Field(..., gt=0),
    recipients: List[SplitRecipient] = Field(..., min_items=1),
    split_type: SplitType = SplitType.PERCENTAGE,
    current_user = Depends(get_current_user),
    service: SplitPaymentsService = Depends(get_split_service)
):
    """
    Simular split de pagamento sem processar
    """
    try:
        simulation = await service.simulate_split(
            amount=transaction_amount,
            recipients=recipients,
            split_type=split_type,
            user_id=current_user.id
        )
        
        return {
            "transaction_amount": transaction_amount,
            "total_split_amount": simulation["total_split_amount"],
            "total_fees": simulation["total_fees"],
            "net_amount": simulation["net_amount"],
            "recipients_breakdown": simulation["recipients"],
            "fee_breakdown": simulation["fees"],
            "warnings": simulation.get("warnings", [])
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro na simulação")

# ================================
# HISTÓRICO E RELATÓRIOS
# ================================

@router.get("/history")
async def get_split_history(
    status: Optional[SplitStatus] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_amount: Optional[Decimal] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    service: SplitPaymentsService = Depends(get_split_service)
):
    """
    Histórico de splits do usuário
    """
    try:
        history = await service.get_split_history(
            user_id=current_user.id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            limit=limit,
            offset=offset
        )
        
        return {
            "splits": history["items"],
            "summary": history["summary"],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": history["total_count"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao consultar histórico")

@router.get("/analytics")
async def get_split_analytics(
    period_days: int = Query(default=30, ge=7, le=365),
    current_user = Depends(get_current_user),
    service: SplitPaymentsService = Depends(get_split_service)
):
    """
    Analytics de splits - volumes, eficiência, etc.
    """
    try:
        analytics = await service.get_split_analytics(
            user_id=current_user.id,
            period_days=period_days
        )
        
        return {
            "period_summary": analytics["period_summary"],
            "volume_trends": analytics["volume_trends"],
            "recipient_analysis": analytics["recipient_analysis"],
            "efficiency_metrics": analytics["efficiency_metrics"],
            "cost_analysis": analytics["cost_analysis"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao gerar analytics")

# ================================
# GERENCIAMENTO
# ================================

@router.post("/cancel/{split_id}")
async def cancel_split(
    split_id: str,
    reason: str = Field(..., max_length=255),
    current_user = Depends(get_current_user),
    service: SplitPaymentsService = Depends(get_split_service)
):
    """
    Cancelar split pendente
    """
    try:
        result = await service.cancel_split(
            split_id=split_id,
            user_id=current_user.id,
            reason=reason
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {"message": "Split cancelado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao cancelar split")

@router.post("/retry/{split_id}")
async def retry_failed_split(
    split_id: str,
    current_user = Depends(get_current_user),
    service: SplitPaymentsService = Depends(get_split_service),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Tentar novamente split que falhou
    """
    try:
        split_details = await service.get_split_details(split_id, current_user.id)
        
        if not split_details or split_details["status"] != SplitStatus.FAILED:
            raise HTTPException(
                status_code=400, 
                detail="Split não encontrado ou não está em status de falha"
            )
        
        # Reprocessar em background
        background_tasks.add_task(
            retry_split_processing,
            split_id=split_id,
            service=service
        )
        
        return {"message": "Split sendo reprocessado"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao reprocessar split")

# ================================
# FUNÇÕES AUXILIARES
# ================================

async def process_split_transfers(
    split_id: str,
    distribution: Dict[str, Any],
    service: SplitPaymentsService
):
    """
    Processar transferências do split em background
    """
    try:
        await service.execute_split_transfers(split_id, distribution)
    except Exception as e:
        await service.mark_split_failed(split_id, str(e))

async def retry_split_processing(
    split_id: str,
    service: SplitPaymentsService
):
    """
    Reprocessar split que falhou
    """
    try:
        await service.retry_split_processing(split_id)
    except Exception as e:
        await service.mark_split_failed(split_id, str(e))