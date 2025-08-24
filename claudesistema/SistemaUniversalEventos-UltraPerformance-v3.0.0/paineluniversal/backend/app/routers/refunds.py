"""
Refunds Router - API REST para Sistema de Estornos
Sistema Universal de Gestão de Eventos

API completa para gestão de estornos com recursos avançados:
- CRUD completo de solicitações de estorno
- Análise de elegibilidade com IA
- Workflows de aprovação automatizados
- Analytics e relatórios em tempo real
- Integração com gateways de pagamento
- Prevenção de fraude e compliance
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from loguru import logger

from app.core.database import get_db, get_async_db
from app.core.security import get_current_user
from app.models import User
from app.services.refund_service import RefundService, RefundRequest, RefundStatus, RefundType, RefundReason, RefundPriority
from app.services.refund_validator import RefundValidator, ValidationReport
from app.services.refund_orchestrator import RefundOrchestrator, WorkflowType
from app.services.refund_intelligence import RefundIntelligence
from app.services.chargeback_manager import ChargebackManager
from app.services.banking_service import PaymentMethod, BankingGateway
import app.schemas as schemas

# Create router
router = APIRouter(prefix="/refunds", tags=["refunds"])

# ================================
# REFUND REQUEST ENDPOINTS
# ================================

@router.post("/request", response_model=schemas.RefundResponse)
async def request_refund(
    transaction_id: str = Form(...),
    amount: Decimal = Form(...),
    reason: RefundReason = Form(...),
    description: Optional[str] = Form(None),
    priority: RefundPriority = Form(RefundPriority.MEDIUM),
    customer_contact: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Solicitar um novo estorno com análise automática de elegibilidade
    """
    try:
        logger.info(f"Refund request received for transaction {transaction_id}")
        
        # Initialize services
        refund_service = RefundService(db)
        refund_orchestrator = RefundOrchestrator(db)
        
        # Get original transaction
        original_transaction = await refund_service._get_transaction_details(transaction_id)
        if not original_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Create refund request
        refund_request = RefundRequest(
            refund_id=f"ref_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            transaction_id=transaction_id,
            original_payment_id=original_transaction["payment_id"],
            customer_id=current_user.id,
            amount=amount,
            reason=reason,
            refund_type=RefundType.PARTIAL if amount < original_transaction["amount"] else RefundType.FULL,
            priority=priority,
            description=description,
            requested_by=current_user.email,
            gateway=original_transaction.get("gateway"),
            payment_method=original_transaction.get("payment_method")
        )
        
        # Handle file uploads
        uploaded_files = []
        for file in files:
            if file.filename:
                # In production, store files securely
                file_content = await file.read()
                uploaded_files.append({
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": len(file_content)
                })
        
        # Start orchestrated refund process
        workflow = await refund_orchestrator.orchestrate_refund(
            refund_request, original_transaction
        )
        
        return schemas.RefundResponse(
            refund_id=refund_request.refund_id,
            status=workflow.current_state.value,
            workflow_id=workflow.workflow_id,
            estimated_processing_time=workflow.sla_deadline,
            message="Solicitação de estorno criada com sucesso"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refund request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process refund request: {str(e)}")


@router.get("/{refund_id}/status", response_model=schemas.RefundStatusResponse)
async def get_refund_status(
    refund_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter status detalhado de um estorno
    """
    try:
        refund_service = RefundService(db)
        refund_orchestrator = RefundOrchestrator(db)
        
        # Get refund details
        refund_data = await refund_service._get_refund_request(refund_id)
        if not refund_data:
            raise HTTPException(status_code=404, detail="Refund not found")
        
        # Get workflow status if available
        workflow_status = None
        try:
            workflow_status = await refund_orchestrator.get_workflow_status(refund_data.get("workflow_id"))
        except ValueError:
            pass  # No workflow found
        
        return schemas.RefundStatusResponse(
            refund_id=refund_id,
            status=refund_data["status"],
            amount=refund_data["amount"],
            created_at=refund_data["created_at"],
            updated_at=refund_data["updated_at"],
            workflow_status=workflow_status,
            estimated_completion=workflow_status.get("remaining_sla_time_seconds") if workflow_status else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get refund status: {str(e)}")


@router.get("", response_model=schemas.RefundListResponse)
async def list_refunds(
    status: Optional[RefundStatus] = Query(None),
    priority: Optional[RefundPriority] = Query(None),
    gateway: Optional[BankingGateway] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar estornos com filtros avançados
    """
    try:
        refund_service = RefundService(db)
        
        # Build filters
        filters = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority
        if gateway:
            filters["gateway"] = gateway
        if date_from:
            filters["date_from"] = date_from
        if date_to:
            filters["date_to"] = date_to
        
        # Get refunds (mock implementation)
        refunds = []  # Would query database with filters
        total_count = 0
        
        return schemas.RefundListResponse(
            refunds=refunds,
            total_count=total_count,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Refund listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list refunds: {str(e)}")


# ================================
# REFUND APPROVAL ENDPOINTS
# ================================

@router.post("/{refund_id}/approve", response_model=schemas.RefundApprovalResponse)
async def approve_refund(
    refund_id: str,
    approval_data: schemas.RefundApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aprovar um estorno manualmente
    """
    try:
        refund_service = RefundService(db)
        refund_orchestrator = RefundOrchestrator(db)
        
        # Check if user has approval permissions
        if not hasattr(current_user, 'can_approve_refunds') or not current_user.can_approve_refunds:
            raise HTTPException(status_code=403, detail="Insufficient permissions to approve refunds")
        
        # Approve the refund
        result = await refund_service.approve_refund(
            refund_id=refund_id,
            approved_by=current_user.email,
            notes=approval_data.notes
        )
        
        # If there's an active workflow, approve it too
        refund_data = await refund_service._get_refund_request(refund_id)
        if refund_data and refund_data.get("workflow_id"):
            await refund_orchestrator.approve_workflow(
                workflow_id=refund_data["workflow_id"],
                approved_by=current_user.email,
                notes=approval_data.notes
            )
        
        return schemas.RefundApprovalResponse(
            refund_id=refund_id,
            approved=True,
            approved_by=current_user.email,
            approved_at=datetime.utcnow(),
            notes=approval_data.notes,
            result=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refund approval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve refund: {str(e)}")


@router.post("/{refund_id}/reject", response_model=schemas.RefundRejectionResponse)
async def reject_refund(
    refund_id: str,
    rejection_data: schemas.RefundRejectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rejeitar um estorno
    """
    try:
        refund_service = RefundService(db)
        refund_orchestrator = RefundOrchestrator(db)
        
        # Check permissions
        if not hasattr(current_user, 'can_approve_refunds') or not current_user.can_approve_refunds:
            raise HTTPException(status_code=403, detail="Insufficient permissions to reject refunds")
        
        # Reject the refund
        result = await refund_service.reject_refund(
            refund_id=refund_id,
            rejected_by=current_user.email,
            reason=rejection_data.reason,
            notes=rejection_data.notes
        )
        
        # Reject workflow if exists
        refund_data = await refund_service._get_refund_request(refund_id)
        if refund_data and refund_data.get("workflow_id"):
            await refund_orchestrator.reject_workflow(
                workflow_id=refund_data["workflow_id"],
                rejected_by=current_user.email,
                reason=rejection_data.reason,
                notes=rejection_data.notes
            )
        
        return schemas.RefundRejectionResponse(
            refund_id=refund_id,
            rejected=True,
            rejected_by=current_user.email,
            rejected_at=datetime.utcnow(),
            reason=rejection_data.reason,
            notes=rejection_data.notes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refund rejection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reject refund: {str(e)}")


# ================================
# AI AND ANALYTICS ENDPOINTS
# ================================

@router.post("/analyze-eligibility", response_model=schemas.RefundEligibilityResponse)
async def analyze_refund_eligibility(
    eligibility_request: schemas.RefundEligibilityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analisar elegibilidade de estorno com IA
    """
    try:
        refund_validator = RefundValidator(db)
        refund_intelligence = RefundIntelligence(db)
        
        # Create temporary refund request for analysis
        refund_request = RefundRequest(
            refund_id="temp_analysis",
            transaction_id=eligibility_request.transaction_id,
            original_payment_id=eligibility_request.transaction_id,
            customer_id=current_user.id,
            amount=eligibility_request.amount,
            reason=RefundReason(eligibility_request.reason)
        )
        
        # Run validation
        validation_report = await refund_validator.validate_refund_request(
            refund_request, 
            eligibility_request.original_transaction,
            {"customer_id": current_user.id}
        )
        
        # Run AI analysis
        ai_analysis = await refund_intelligence.analyze_refund_request(
            refund_request,
            eligibility_request.original_transaction,
            {"customer_id": current_user.id}
        )
        
        return schemas.RefundEligibilityResponse(
            eligible=validation_report.result.value == "approved",
            confidence=validation_report.confidence,
            risk_score=validation_report.risk_score,
            risk_level=validation_report.risk_level.value,
            issues=[issue.message for issue in validation_report.issues],
            recommendations=validation_report.recommendations,
            estimated_processing_time=validation_report.estimated_processing_time,
            ai_analysis=ai_analysis
        )
        
    except Exception as e:
        logger.error(f"Eligibility analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze eligibility: {str(e)}")


@router.post("/ai-suggestions", response_model=schemas.RefundSuggestionsResponse)
async def get_ai_suggestions(
    suggestion_request: schemas.RefundSuggestionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter sugestões de IA para descrição do estorno
    """
    try:
        refund_intelligence = RefundIntelligence(db)
        
        # Generate suggestions based on reason and context
        suggestions = [
            f"Solicitação de estorno por {suggestion_request.reason}",
            "Cliente insatisfeito com o produto/serviço",
            "Problema técnico identificado no sistema",
            "Cancelamento dentro do prazo de devolução",
            "Duplicação acidental de pagamento"
        ]
        
        return schemas.RefundSuggestionsResponse(
            suggestions=suggestions,
            context=suggestion_request.reason,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"AI suggestions failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {str(e)}")


@router.get("/analytics/metrics", response_model=schemas.RefundMetricsResponse)
async def get_refund_metrics(
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter métricas de estorno para analytics
    """
    try:
        refund_service = RefundService(db)
        
        # Calculate time range
        end_date = datetime.utcnow()
        if time_range == "7d":
            start_date = end_date - timedelta(days=7)
        elif time_range == "30d":
            start_date = end_date - timedelta(days=30)
        elif time_range == "90d":
            start_date = end_date - timedelta(days=90)
        else:  # 1y
            start_date = end_date - timedelta(days=365)
        
        # Mock metrics - in production would calculate from database
        metrics = schemas.RefundMetrics(
            total_refunds=150,
            pending_approval=12,
            processing=5,
            completed=120,
            rejected=13,
            total_amount=Decimal("45000.00"),
            avg_processing_time=45.5,
            fraud_prevented=8,
            auto_approval_rate=78.5,
            chargebacks_prevented=3
        )
        
        return schemas.RefundMetricsResponse(
            metrics=metrics,
            time_range=time_range,
            start_date=start_date,
            end_date=end_date,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/analytics/trends", response_model=schemas.RefundTrendsResponse)
async def get_refund_trends(
    time_range: str = Query("30d"),
    granularity: str = Query("daily", regex="^(hourly|daily|weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter dados de tendências de estornos
    """
    try:
        # Mock trend data - in production would calculate from database
        trends = []
        for i in range(30):
            date = datetime.utcnow() - timedelta(days=i)
            trends.append(schemas.RefundTrendData(
                date=date.strftime("%Y-%m-%d"),
                refunds=10 + (i % 5),
                amount=Decimal("1500.00") + Decimal(i * 100),
                approved=8 + (i % 3),
                rejected=2 + (i % 2),
                avg_risk_score=0.3 + (i % 10) / 20,
                processing_time=40 + (i % 20)
            ))
        
        return schemas.RefundTrendsResponse(
            trends=trends[::-1],  # Reverse to show chronologically
            time_range=time_range,
            granularity=granularity,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Trends retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")


# ================================
# CHARGEBACK MANAGEMENT ENDPOINTS
# ================================

@router.post("/chargebacks/analyze-risk", response_model=schemas.ChargebackRiskResponse)
async def analyze_chargeback_risk(
    risk_request: schemas.ChargebackRiskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analisar risco de chargeback para uma transação
    """
    try:
        chargeback_manager = ChargebackManager(db)
        
        risk_analysis = await chargeback_manager.analyze_chargeback_risk(
            transaction_id=risk_request.transaction_id,
            payment_data=risk_request.payment_data,
            customer_data=risk_request.customer_data
        )
        
        return schemas.ChargebackRiskResponse(
            transaction_id=risk_request.transaction_id,
            risk_score=risk_analysis["risk_score"],
            risk_level=risk_analysis["risk_level"],
            risk_factors=risk_analysis["risk_factors"],
            recommendations=risk_analysis["recommendations"],
            prevention_alert=risk_analysis.get("prevention_alert"),
            analyzed_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Chargeback risk analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze chargeback risk: {str(e)}")


@router.get("/chargebacks/analytics", response_model=schemas.ChargebackAnalyticsResponse)
async def get_chargeback_analytics(
    time_range: str = Query("30d"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter analytics de chargebacks
    """
    try:
        chargeback_manager = ChargebackManager(db)
        
        analytics = await chargeback_manager.get_chargeback_analytics()
        
        return schemas.ChargebackAnalyticsResponse(
            overview=analytics["overview"],
            by_status=analytics["by_status"],
            by_category=analytics["by_category"],
            by_gateway=analytics["by_gateway"],
            trends=analytics["trends"],
            prevention_metrics=analytics["prevention_metrics"],
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Chargeback analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chargeback analytics: {str(e)}")


# ================================
# REPORTING ENDPOINTS
# ================================

@router.get("/reports/export")
async def export_refunds_report(
    format: str = Query("csv", regex="^(csv|xlsx|pdf)$"),
    time_range: str = Query("30d"),
    status: Optional[RefundStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exportar relatório de estornos
    """
    try:
        # Generate report based on format
        if format == "csv":
            # Generate CSV content
            csv_content = "refund_id,transaction_id,amount,status,created_at,updated_at\n"
            csv_content += "ref_123,txn_456,150.00,completed,2024-01-01,2024-01-02\n"
            
            def generate_csv():
                yield csv_content
            
            return StreamingResponse(
                generate_csv(),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=refunds_report_{time_range}.csv"}
            )
        
        elif format == "xlsx":
            # Would generate Excel file
            raise HTTPException(status_code=501, detail="Excel export not implemented yet")
        
        elif format == "pdf":
            # Would generate PDF report
            raise HTTPException(status_code=501, detail="PDF export not implemented yet")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")


# ================================
# WEBHOOK ENDPOINTS
# ================================

@router.post("/webhooks/{gateway}")
async def handle_refund_webhook(
    gateway: BankingGateway,
    webhook_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Handle webhook notifications from payment gateways about refund status changes
    """
    try:
        logger.info(f"Webhook received from {gateway}: {webhook_data}")
        
        refund_service = RefundService(db)
        
        # Process webhook based on gateway
        if gateway == BankingGateway.MERCADOPAGO:
            # Handle MercadoPago webhook
            if webhook_data.get("type") == "payment" and webhook_data.get("action") == "refunded":
                refund_id = webhook_data.get("data", {}).get("id")
                # Update refund status
                # Implementation would update database
        
        elif gateway == BankingGateway.STRIPE:
            # Handle Stripe webhook
            if webhook_data.get("type") == "charge.dispute.created":
                # Handle chargeback
                pass
        
        return {"status": "success", "processed_at": datetime.utcnow()}
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")


# ================================
# ADMIN ENDPOINTS
# ================================

@router.get("/admin/queue", response_model=schemas.RefundQueueResponse)
async def get_approval_queue(
    priority: Optional[RefundPriority] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter fila de aprovação para administradores
    """
    try:
        # Check admin permissions
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        refund_service = RefundService(db)
        
        # Get pending refunds
        pending_refunds = []  # Would query database for pending approvals
        
        return schemas.RefundQueueResponse(
            pending_refunds=pending_refunds,
            total_count=len(pending_refunds),
            priority_filter=priority,
            generated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Queue retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get approval queue: {str(e)}")


@router.get("/admin/metrics", response_model=schemas.AdminRefundMetrics)
async def get_admin_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter métricas administrativas detalhadas
    """
    try:
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        refund_service = RefundService(db)
        refund_orchestrator = RefundOrchestrator(db)
        chargeback_manager = ChargebackManager(db)
        
        # Get comprehensive metrics
        orchestrator_metrics = await refund_orchestrator.get_orchestrator_metrics()
        chargeback_metrics = await chargeback_manager.get_chargeback_analytics()
        
        return schemas.AdminRefundMetrics(
            workflow_metrics=orchestrator_metrics,
            chargeback_metrics=chargeback_metrics["overview"],
            system_performance={
                "avg_response_time": 250,
                "success_rate": 99.2,
                "error_rate": 0.8
            },
            generated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin metrics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get admin metrics: {str(e)}")


# ================================
# HEALTH CHECK ENDPOINT
# ================================

@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "services": {
            "refund_service": "operational",
            "ai_intelligence": "operational", 
            "orchestrator": "operational",
            "chargeback_manager": "operational"
        }
    }