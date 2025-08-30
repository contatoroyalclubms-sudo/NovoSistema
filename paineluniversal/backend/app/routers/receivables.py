"""
Router para Sistema de Antecipação de Recebíveis
Sistema Universal de Gestão de Eventos - Sprint 2

Funcionalidades:
- Antecipação automática de recebíveis
- Cálculo inteligente de taxas
- Simulação de cenários
- Aprovação automática baseada em IA
- Controle de risco integrado
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid

# Imports do sistema
from app.core.security import get_current_user
from app.core.database import get_db
from app.services.receivables_service import ReceivablesService
from app.services.ai_risk_assessment import AIRiskAssessmentService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/receivables", tags=["Receivables Anticipation"])

# Enums
class ReceivableStatus(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    ANTICIPATED = "anticipated"
    SETTLED = "settled"
    CANCELLED = "cancelled"

class AnticipationStatus(str, Enum):
    REQUESTED = "requested"
    ANALYZING = "analyzing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"
    SETTLED = "settled"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

# Schemas
class ReceivableItem(BaseModel):
    receivable_id: str
    transaction_id: str
    amount: Decimal
    due_date: datetime
    payer_info: Dict[str, Any]
    status: ReceivableStatus
    created_at: datetime

class AnticipationRequest(BaseModel):
    receivable_ids: List[str] = Field(..., min_items=1, max_items=50)
    requested_amount: Optional[Decimal] = None  # Se None, antecipa valor total
    urgency_level: int = Field(default=1, ge=1, le=5)  # 1=normal, 5=urgente
    metadata: Optional[Dict[str, Any]] = None

class AnticipationSimulation(BaseModel):
    receivable_ids: List[str]
    total_receivable_amount: Decimal
    requested_amount: Decimal
    net_amount: Decimal
    total_fee: Decimal
    fee_percentage: Decimal
    processing_time_hours: int
    risk_level: RiskLevel
    estimated_approval_probability: float
    conditions: List[str]

class AnticipationResponse(BaseModel):
    anticipation_id: str
    status: AnticipationStatus
    requested_amount: Decimal
    approved_amount: Optional[Decimal]
    net_amount: Optional[Decimal]
    total_fee: Optional[Decimal]
    fee_breakdown: Optional[Dict[str, Decimal]]
    risk_assessment: Optional[Dict[str, Any]]
    estimated_settlement: Optional[datetime]
    created_at: datetime
    processed_at: Optional[datetime]

# Serviços
def get_receivables_service(db = Depends(get_db)) -> ReceivablesService:
    return ReceivablesService(db)

def get_ai_risk_service() -> AIRiskAssessmentService:
    return AIRiskAssessmentService()

def get_notification_service() -> NotificationService:
    return NotificationService()

# ================================
# CONSULTA DE RECEBÍVEIS
# ================================

@router.get("/available", response_model=List[ReceivableItem])
async def get_available_receivables(
    user_id: Optional[int] = Query(None),
    min_amount: Optional[Decimal] = Query(None),
    max_days_ahead: int = Query(default=365, ge=1, le=365),
    current_user = Depends(get_current_user),
    service: ReceivablesService = Depends(get_receivables_service)
):
    """
    Listar recebíveis disponíveis para antecipação
    """
    try:
        receivables = await service.get_available_receivables(
            account_user_id=user_id or current_user.id,
            min_amount=min_amount,
            max_days_ahead=max_days_ahead
        )
        return receivables
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao consultar recebíveis")

@router.get("/summary")
async def get_receivables_summary(
    current_user = Depends(get_current_user),
    service: ReceivablesService = Depends(get_receivables_service)
):
    """
    Resumo dos recebíveis do usuário
    """
    try:
        summary = await service.get_receivables_summary(current_user.id)
        return {
            "total_available": summary["total_available"],
            "total_amount": summary["total_amount"],
            "avg_days_to_settlement": summary["avg_days"],
            "anticipation_potential": summary["anticipation_potential"],
            "risk_profile": summary["risk_profile"],
            "recommended_amount": summary["recommended_amount"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao gerar resumo")

# ================================
# SIMULAÇÃO DE ANTECIPAÇÃO
# ================================

@router.post("/simulate", response_model=AnticipationSimulation)
async def simulate_anticipation(
    receivable_ids: List[str] = Field(..., min_items=1),
    requested_amount: Optional[Decimal] = None,
    urgency_level: int = Field(default=1, ge=1, le=5),
    current_user = Depends(get_current_user),
    service: ReceivablesService = Depends(get_receivables_service),
    ai_risk: AIRiskAssessmentService = Depends(get_ai_risk_service)
):
    """
    Simular antecipação de recebíveis com cálculo de taxas e riscos
    """
    try:
        # Validar recebíveis
        receivables = await service.validate_receivables_for_anticipation(
            receivable_ids=receivable_ids,
            user_id=current_user.id
        )
        
        if not receivables["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Recebíveis inválidos: {receivables['errors']}"
            )
        
        total_amount = sum(r["amount"] for r in receivables["items"])
        final_amount = requested_amount or total_amount
        
        if final_amount > total_amount:
            raise HTTPException(
                status_code=400,
                detail="Valor solicitado excede total dos recebíveis"
            )
        
        # Análise de risco com IA
        risk_analysis = await ai_risk.analyze_anticipation_risk(
            receivables=receivables["items"],
            requested_amount=final_amount,
            user_profile=await service.get_user_risk_profile(current_user.id),
            urgency_level=urgency_level
        )
        
        # Cálculo de taxas
        fee_calculation = await service.calculate_anticipation_fees(
            amount=final_amount,
            risk_level=risk_analysis["risk_level"],
            urgency_level=urgency_level,
            avg_days_to_settlement=risk_analysis["avg_settlement_days"]
        )
        
        return AnticipationSimulation(
            receivable_ids=receivable_ids,
            total_receivable_amount=total_amount,
            requested_amount=final_amount,
            net_amount=fee_calculation["net_amount"],
            total_fee=fee_calculation["total_fee"],
            fee_percentage=fee_calculation["fee_percentage"],
            processing_time_hours=risk_analysis["estimated_processing_hours"],
            risk_level=risk_analysis["risk_level"],
            estimated_approval_probability=risk_analysis["approval_probability"],
            conditions=fee_calculation["conditions"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro na simulação")

# ================================
# SOLICITAÇÃO DE ANTECIPAÇÃO
# ================================

@router.post("/request", response_model=AnticipationResponse)
async def request_anticipation(
    request_data: AnticipationRequest,
    current_user = Depends(get_current_user),
    service: ReceivablesService = Depends(get_receivables_service),
    ai_risk: AIRiskAssessmentService = Depends(get_ai_risk_service),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Solicitar antecipação de recebíveis
    """
    try:
        # Primeiro fazer simulação para validar
        simulation = await simulate_anticipation(
            receivable_ids=request_data.receivable_ids,
            requested_amount=request_data.requested_amount,
            urgency_level=request_data.urgency_level,
            current_user=current_user,
            service=service,
            ai_risk=ai_risk
        )
        
        # Criar solicitação
        anticipation_id = str(uuid.uuid4())
        anticipation = await service.create_anticipation_request(
            anticipation_id=anticipation_id,
            user_id=current_user.id,
            receivable_ids=request_data.receivable_ids,
            requested_amount=simulation.requested_amount,
            simulation_data=simulation.dict(),
            urgency_level=request_data.urgency_level,
            metadata=request_data.metadata
        )
        
        # Processar aprovação em background
        background_tasks.add_task(
            process_anticipation_approval,
            anticipation_id=anticipation_id,
            simulation=simulation,
            service=service,
            ai_risk=ai_risk
        )
        
        return AnticipationResponse(
            anticipation_id=anticipation_id,
            status=AnticipationStatus.ANALYZING,
            requested_amount=simulation.requested_amount,
            approved_amount=None,
            net_amount=None,
            total_fee=None,
            fee_breakdown=None,
            risk_assessment=None,
            estimated_settlement=None,
            created_at=anticipation["created_at"],
            processed_at=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao processar solicitação")

# ================================
# CONSULTA DE ANTECIPAÇÕES
# ================================

@router.get("/status/{anticipation_id}", response_model=AnticipationResponse)
async def get_anticipation_status(
    anticipation_id: str,
    current_user = Depends(get_current_user),
    service: ReceivablesService = Depends(get_receivables_service)
):
    """
    Consultar status de uma antecipação
    """
    try:
        anticipation = await service.get_anticipation_by_id(
            anticipation_id=anticipation_id,
            user_id=current_user.id
        )
        
        if not anticipation:
            raise HTTPException(status_code=404, detail="Antecipação não encontrada")
        
        return AnticipationResponse(**anticipation)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao consultar status")

@router.get("/history")
async def get_anticipation_history(
    status: Optional[AnticipationStatus] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    service: ReceivablesService = Depends(get_receivables_service)
):
    """
    Histórico de antecipações do usuário
    """
    try:
        history = await service.get_anticipation_history(
            user_id=current_user.id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        return {
            "anticipations": history["items"],
            "summary": history["summary"],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": history["total_count"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao consultar histórico")

# ================================
# ANÁLISES E RELATÓRIOS
# ================================

@router.get("/analytics")
async def get_anticipation_analytics(
    period_days: int = Query(default=30, ge=7, le=365),
    current_user = Depends(get_current_user),
    service: ReceivablesService = Depends(get_receivables_service)
):
    """
    Analytics de antecipações - insights e tendências
    """
    try:
        analytics = await service.get_anticipation_analytics(
            user_id=current_user.id,
            period_days=period_days
        )
        
        return {
            "period_summary": analytics["period_summary"],
            "trends": analytics["trends"],
            "efficiency_metrics": analytics["efficiency"],
            "recommendations": analytics["recommendations"],
            "risk_analysis": analytics["risk_analysis"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao gerar analytics")

# ================================
# CONFIGURAÇÕES
# ================================

@router.get("/settings")
async def get_anticipation_settings(
    current_user = Depends(get_current_user),
    service: ReceivablesService = Depends(get_receivables_service)
):
    """
    Configurações de antecipação do usuário
    """
    try:
        settings = await service.get_user_anticipation_settings(current_user.id)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao consultar configurações")

@router.put("/settings")
async def update_anticipation_settings(
    auto_anticipation_enabled: Optional[bool] = None,
    max_auto_amount: Optional[Decimal] = None,
    min_profit_margin: Optional[float] = None,
    notification_preferences: Optional[Dict[str, bool]] = None,
    current_user = Depends(get_current_user),
    service: ReceivablesService = Depends(get_receivables_service)
):
    """
    Atualizar configurações de antecipação
    """
    try:
        updated_settings = await service.update_anticipation_settings(
            user_id=current_user.id,
            auto_anticipation_enabled=auto_anticipation_enabled,
            max_auto_amount=max_auto_amount,
            min_profit_margin=min_profit_margin,
            notification_preferences=notification_preferences
        )
        return {"message": "Configurações atualizadas", "settings": updated_settings}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao atualizar configurações")

# ================================
# FUNÇÕES AUXILIARES
# ================================

async def process_anticipation_approval(
    anticipation_id: str,
    simulation: AnticipationSimulation,
    service: ReceivablesService,
    ai_risk: AIRiskAssessmentService
):
    """
    Processar aprovação de antecipação em background
    """
    try:
        # Análise final de aprovação
        approval_decision = await ai_risk.make_approval_decision(
            anticipation_id=anticipation_id,
            simulation=simulation
        )
        
        if approval_decision["approved"]:
            # Aprovar e processar
            await service.approve_and_process_anticipation(
                anticipation_id=anticipation_id,
                approved_amount=approval_decision["approved_amount"],
                net_amount=approval_decision["net_amount"],
                fee_breakdown=approval_decision["fee_breakdown"]
            )
        else:
            # Rejeitar com motivo
            await service.reject_anticipation(
                anticipation_id=anticipation_id,
                rejection_reason=approval_decision["rejection_reason"]
            )
            
    except Exception as e:
        # Log erro e marcar como falhado
        await service.mark_anticipation_failed(
            anticipation_id=anticipation_id,
            error_message=str(e)
        )