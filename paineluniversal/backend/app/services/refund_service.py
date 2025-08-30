"""
Refund Service - Comprehensive Refund Management System
Sistema Universal de Gestão de Eventos

Advanced refund management with AI-powered decision making, multi-gateway support,
chargeback management, and intelligent workflow automation.

Features:
- AI-powered refund eligibility detection
- Multi-gateway refund processing (PIX, Cards, Boleto)
- Fraud prevention and risk scoring
- Automated approval workflows
- Chargeback prevention and management
- Real-time analytics and reporting
- Compliance and audit trail
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from contextlib import asynccontextmanager
import hashlib
import hmac
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
import httpx
import redis
from loguru import logger

from app.core.config import get_settings
from app.core.database import get_db
from app.services.banking_service import BankingService, BankingGateway, TransactionStatus, PaymentMethod
from app.services.payment_processor import PaymentProcessor, PaymentStatus
from app.services.validation_service import ValidationService
from app.services.notification_service import NotificationService
from app.services.openai_service import OpenAIService


class RefundStatus(str, Enum):
    """Refund status definitions"""
    REQUESTED = "requested"
    PENDING_APPROVAL = "pending_approval" 
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    FAILED = "failed"
    PARTIAL = "partial"
    REVERSED = "reversed"


class RefundType(str, Enum):
    """Types of refunds"""
    FULL = "full"
    PARTIAL = "partial"
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    CHARGEBACK = "chargeback"
    DISPUTE = "dispute"
    GOODWILL = "goodwill"
    CANCELLATION = "cancellation"


class RefundReason(str, Enum):
    """Refund reason codes"""
    CUSTOMER_REQUEST = "customer_request"
    EVENT_CANCELLED = "event_cancelled"
    DUPLICATE_PAYMENT = "duplicate_payment"
    FRAUD_PREVENTION = "fraud_prevention"
    TECHNICAL_ERROR = "technical_error"
    CHARGEBACK = "chargeback"
    DISPUTE = "dispute"
    POLICY_VIOLATION = "policy_violation"
    QUALITY_ISSUE = "quality_issue"
    LATE_DELIVERY = "late_delivery"
    GOODWILL = "goodwill"


class RefundPriority(str, Enum):
    """Refund priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class RefundRequest:
    """Refund request data structure"""
    refund_id: str
    transaction_id: str
    original_payment_id: str
    customer_id: int
    amount: Decimal
    currency: str = "BRL"
    reason: RefundReason = RefundReason.CUSTOMER_REQUEST
    refund_type: RefundType = RefundType.FULL
    priority: RefundPriority = RefundPriority.MEDIUM
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    requested_by: Optional[str] = None
    gateway: Optional[BankingGateway] = None
    payment_method: Optional[PaymentMethod] = None


@dataclass
class RefundAnalysis:
    """AI-powered refund analysis result"""
    eligible: bool
    risk_score: float  # 0.0 to 1.0
    risk_level: RiskLevel
    confidence: float  # 0.0 to 1.0
    fraud_indicators: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    auto_approve: bool = False
    estimated_processing_time: int = 0  # minutes
    analysis_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RefundResult:
    """Refund processing result"""
    refund_id: str
    status: RefundStatus
    amount: Decimal
    gateway_refund_id: Optional[str] = None
    gateway_response: Dict[str, Any] = field(default_factory=dict)
    processing_fee: Decimal = Decimal("0.00")
    net_refund_amount: Decimal = Decimal("0.00")
    processed_at: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class RefundServiceError(Exception):
    """Base exception for refund service errors"""
    def __init__(self, message: str, code: str = None, refund_id: str = None):
        self.message = message
        self.code = code
        self.refund_id = refund_id
        super().__init__(self.message)


class IneligibleRefundError(RefundServiceError):
    """Refund is not eligible for processing"""
    pass


class RefundService:
    """
    Main refund service orchestrating all refund operations
    Provides comprehensive refund management with AI-powered intelligence
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.redis_client = self._init_redis()
        
        # Initialize dependent services
        self.banking_service = BankingService(db)
        self.payment_processor = PaymentProcessor()
        self.validation_service = ValidationService()
        self.notification_service = NotificationService(db)
        self.openai_service = OpenAIService()
        
        # Initialize refund processors for each gateway
        self.refund_processors = self._init_refund_processors()
        
        # Refund configuration
        self.config = self._init_refund_config()
        
        # Analytics and metrics
        self.metrics = {
            "total_refunds": 0,
            "auto_approved": 0,
            "manual_reviewed": 0,
            "fraud_prevented": 0,
            "processing_time_avg": 0,
            "success_rate": 0.0
        }
    
    def _init_redis(self) -> redis.Redis:
        """Initialize Redis connection for caching and rate limiting"""
        try:
            return redis.Redis(
                host=self.settings.REDIS_HOST,
                port=self.settings.REDIS_PORT,
                password=self.settings.REDIS_PASSWORD,
                db=1,  # Different DB for refunds
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            return None
    
    def _init_refund_processors(self) -> Dict[BankingGateway, Any]:
        """Initialize refund processors for each gateway"""
        from app.services.refund_processor import (
            PIXRefundProcessor, CardRefundProcessor, BoletoRefundProcessor
        )
        
        return {
            BankingGateway.PICPAY: PIXRefundProcessor(),
            BankingGateway.PAGSEGURO: CardRefundProcessor(),
            BankingGateway.ASAAS: PIXRefundProcessor(),
            BankingGateway.MERCADOPAGO: CardRefundProcessor(),
            BankingGateway.STRIPE: CardRefundProcessor(),
        }
    
    def _init_refund_config(self) -> Dict[str, Any]:
        """Initialize refund configuration settings"""
        return {
            "auto_approval_threshold": Decimal("500.00"),  # Auto-approve refunds under R$500
            "max_refund_age_days": 90,  # No refunds after 90 days
            "fraud_score_threshold": 0.7,  # Block refunds with fraud score > 0.7
            "daily_refund_limit": Decimal("50000.00"),  # Daily refund limit
            "processing_timeout_minutes": 30,  # Timeout for gateway processing
            "retry_max_attempts": 3,  # Max retry attempts
            "priority_sla": {  # SLA in minutes by priority
                RefundPriority.CRITICAL: 15,
                RefundPriority.URGENT: 60,
                RefundPriority.HIGH: 240,
                RefundPriority.MEDIUM: 1440,  # 24 hours
                RefundPriority.LOW: 2880     # 48 hours
            }
        }
    
    # ================================
    # MAIN REFUND OPERATIONS
    # ================================
    
    async def request_refund(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None,
        reason: RefundReason = RefundReason.CUSTOMER_REQUEST,
        description: str = None,
        requested_by: str = None,
        priority: RefundPriority = RefundPriority.MEDIUM,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Request a refund with AI-powered eligibility analysis
        """
        refund_id = f"ref_{uuid.uuid4().hex[:16]}"
        
        try:
            # Get original transaction details
            original_transaction = await self._get_transaction_details(transaction_id)
            if not original_transaction:
                raise RefundServiceError(f"Transaction not found: {transaction_id}")
            
            # Determine refund amount
            refund_amount = amount or original_transaction.get("amount")
            refund_type = RefundType.PARTIAL if amount and amount < original_transaction.get("amount") else RefundType.FULL
            
            # Create refund request
            refund_request = RefundRequest(
                refund_id=refund_id,
                transaction_id=transaction_id,
                original_payment_id=original_transaction.get("payment_id"),
                customer_id=original_transaction.get("customer_id"),
                amount=refund_amount,
                reason=reason,
                refund_type=refund_type,
                priority=priority,
                description=description,
                requested_by=requested_by,
                metadata=metadata or {},
                gateway=original_transaction.get("gateway"),
                payment_method=original_transaction.get("payment_method")
            )
            
            # AI-powered eligibility analysis
            analysis = await self._analyze_refund_eligibility(refund_request, original_transaction)
            
            # Log refund request
            await self._log_refund_event(
                refund_id=refund_id,
                action="refund_requested",
                refund_request=refund_request,
                analysis=analysis
            )
            
            # Check if eligible
            if not analysis.eligible:
                await self._update_refund_status(refund_id, RefundStatus.REJECTED)
                return {
                    "refund_id": refund_id,
                    "status": RefundStatus.REJECTED,
                    "message": "Refund request not eligible",
                    "analysis": analysis
                }
            
            # Store refund request
            await self._store_refund_request(refund_request, analysis)
            
            # Auto-approve if criteria met
            if analysis.auto_approve:
                logger.info(f"Auto-approving refund {refund_id}")
                await self._update_refund_status(refund_id, RefundStatus.APPROVED)
                
                # Process immediately
                processing_result = await self._process_approved_refund(refund_request)
                
                return {
                    "refund_id": refund_id,
                    "status": processing_result.status,
                    "amount": refund_amount,
                    "auto_approved": True,
                    "estimated_arrival": processing_result.estimated_arrival,
                    "analysis": analysis,
                    "processing_result": processing_result
                }
            else:
                # Queue for manual review
                await self._queue_for_manual_review(refund_request, analysis)
                await self._update_refund_status(refund_id, RefundStatus.PENDING_APPROVAL)
                
                return {
                    "refund_id": refund_id,
                    "status": RefundStatus.PENDING_APPROVAL,
                    "amount": refund_amount,
                    "estimated_review_time": self._calculate_review_time(priority),
                    "analysis": analysis
                }
            
        except Exception as e:
            logger.error(f"Refund request failed: {e}")
            await self._log_refund_event(
                refund_id=refund_id,
                action="refund_request_failed",
                error=str(e)
            )
            raise RefundServiceError(f"Refund request failed: {str(e)}", refund_id=refund_id)
    
    async def approve_refund(
        self,
        refund_id: str,
        approved_by: str,
        notes: str = None
    ) -> Dict[str, Any]:
        """
        Manually approve a refund request
        """
        try:
            # Get refund request
            refund_request = await self._get_refund_request(refund_id)
            if not refund_request:
                raise RefundServiceError(f"Refund request not found: {refund_id}")
            
            if refund_request["status"] != RefundStatus.PENDING_APPROVAL:
                raise RefundServiceError(f"Refund not pending approval: {refund_id}")
            
            # Update status
            await self._update_refund_status(refund_id, RefundStatus.APPROVED)
            
            # Log approval
            await self._log_refund_event(
                refund_id=refund_id,
                action="refund_approved",
                approved_by=approved_by,
                notes=notes
            )
            
            # Process the refund
            processing_result = await self._process_approved_refund(refund_request)
            
            # Send notifications
            await self._send_refund_notification("approved", refund_request, processing_result)
            
            return {
                "refund_id": refund_id,
                "status": processing_result.status,
                "approved_by": approved_by,
                "processing_result": processing_result
            }
            
        except Exception as e:
            logger.error(f"Refund approval failed: {e}")
            raise RefundServiceError(f"Refund approval failed: {str(e)}", refund_id=refund_id)
    
    async def reject_refund(
        self,
        refund_id: str,
        rejected_by: str,
        reason: str,
        notes: str = None
    ) -> Dict[str, Any]:
        """
        Reject a refund request
        """
        try:
            # Get refund request
            refund_request = await self._get_refund_request(refund_id)
            if not refund_request:
                raise RefundServiceError(f"Refund request not found: {refund_id}")
            
            # Update status
            await self._update_refund_status(refund_id, RefundStatus.REJECTED)
            
            # Log rejection
            await self._log_refund_event(
                refund_id=refund_id,
                action="refund_rejected",
                rejected_by=rejected_by,
                reason=reason,
                notes=notes
            )
            
            # Send notifications
            await self._send_refund_notification("rejected", refund_request, reason=reason)
            
            return {
                "refund_id": refund_id,
                "status": RefundStatus.REJECTED,
                "rejected_by": rejected_by,
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"Refund rejection failed: {e}")
            raise RefundServiceError(f"Refund rejection failed: {str(e)}", refund_id=refund_id)
    
    async def process_refund(
        self,
        refund_id: str,
        force: bool = False
    ) -> RefundResult:
        """
        Process an approved refund through the appropriate gateway
        """
        try:
            # Get refund request
            refund_request = await self._get_refund_request(refund_id)
            if not refund_request:
                raise RefundServiceError(f"Refund request not found: {refund_id}")
            
            # Check status
            if not force and refund_request["status"] != RefundStatus.APPROVED:
                raise RefundServiceError(f"Refund not approved for processing: {refund_id}")
            
            # Update status to processing
            await self._update_refund_status(refund_id, RefundStatus.PROCESSING)
            
            # Process through appropriate gateway
            result = await self._process_refund_with_gateway(refund_request)
            
            # Update final status
            final_status = RefundStatus.COMPLETED if result.status == RefundStatus.COMPLETED else RefundStatus.FAILED
            await self._update_refund_status(refund_id, final_status)
            
            # Log processing result
            await self._log_refund_event(
                refund_id=refund_id,
                action="refund_processed",
                result=result
            )
            
            # Send notifications
            await self._send_refund_notification("processed", refund_request, result)
            
            # Update metrics
            await self._update_refund_metrics(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Refund processing failed: {e}")
            await self._update_refund_status(refund_id, RefundStatus.FAILED)
            raise RefundServiceError(f"Refund processing failed: {str(e)}", refund_id=refund_id)
    
    # ================================
    # AI-POWERED ANALYSIS
    # ================================
    
    async def _analyze_refund_eligibility(
        self,
        refund_request: RefundRequest,
        original_transaction: Dict[str, Any]
    ) -> RefundAnalysis:
        """
        AI-powered refund eligibility analysis with fraud detection
        """
        try:
            # Basic eligibility checks
            eligibility_checks = await self._run_basic_eligibility_checks(refund_request, original_transaction)
            
            # Fraud detection and risk scoring
            risk_analysis = await self._run_fraud_detection(refund_request, original_transaction)
            
            # Pattern recognition and ML analysis
            ml_analysis = await self._run_ml_analysis(refund_request, original_transaction)
            
            # AI-powered decision making
            ai_decision = await self._get_ai_decision(refund_request, original_transaction, risk_analysis)
            
            # Combine all analyses
            analysis = RefundAnalysis(
                eligible=eligibility_checks["eligible"] and risk_analysis["acceptable_risk"],
                risk_score=risk_analysis["risk_score"],
                risk_level=self._calculate_risk_level(risk_analysis["risk_score"]),
                confidence=ml_analysis["confidence"],
                fraud_indicators=risk_analysis["fraud_indicators"],
                recommendations=ai_decision["recommendations"],
                auto_approve=self._should_auto_approve(refund_request, risk_analysis, ml_analysis),
                estimated_processing_time=self._estimate_processing_time(refund_request),
                analysis_details={
                    "eligibility_checks": eligibility_checks,
                    "risk_analysis": risk_analysis,
                    "ml_analysis": ml_analysis,
                    "ai_decision": ai_decision
                }
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Refund analysis failed: {e}")
            # Return conservative analysis on error
            return RefundAnalysis(
                eligible=False,
                risk_score=1.0,
                risk_level=RiskLevel.VERY_HIGH,
                confidence=0.0,
                fraud_indicators=["analysis_error"],
                recommendations=["Manual review required due to analysis error"]
            )
    
    async def _run_basic_eligibility_checks(
        self,
        refund_request: RefundRequest,
        original_transaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run basic eligibility checks for refund
        """
        checks = {
            "transaction_exists": original_transaction is not None,
            "within_refund_window": self._check_refund_window(original_transaction),
            "amount_valid": refund_request.amount <= original_transaction.get("amount", 0),
            "no_previous_refund": await self._check_no_previous_refund(refund_request.original_payment_id),
            "payment_completed": original_transaction.get("status") == "completed",
            "account_active": await self._check_account_status(refund_request.customer_id),
        }
        
        checks["eligible"] = all(checks.values())
        
        return checks
    
    async def _run_fraud_detection(
        self,
        refund_request: RefundRequest,
        original_transaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Advanced fraud detection for refund requests
        """
        fraud_indicators = []
        risk_score = 0.0
        
        # Check for unusual patterns
        customer_refund_history = await self._get_customer_refund_history(refund_request.customer_id)
        
        # Frequency analysis
        recent_refunds = len([r for r in customer_refund_history if 
                            (datetime.utcnow() - r["created_at"]).days <= 30])
        if recent_refunds > 3:
            fraud_indicators.append("high_refund_frequency")
            risk_score += 0.3
        
        # Amount analysis
        avg_transaction = await self._get_customer_avg_transaction(refund_request.customer_id)
        if refund_request.amount > avg_transaction * 3:
            fraud_indicators.append("unusually_high_amount")
            risk_score += 0.2
        
        # Time analysis
        transaction_age_hours = (datetime.utcnow() - original_transaction.get("created_at")).total_seconds() / 3600
        if transaction_age_hours < 1:  # Refund requested too quickly
            fraud_indicators.append("immediate_refund_request")
            risk_score += 0.4
        
        # Location analysis
        if await self._check_location_mismatch(refund_request.customer_id, original_transaction):
            fraud_indicators.append("location_mismatch")
            risk_score += 0.3
        
        # Device fingerprint analysis
        if await self._check_device_anomaly(refund_request.customer_id, original_transaction):
            fraud_indicators.append("device_anomaly")
            risk_score += 0.2
        
        # Behavioral analysis
        behavioral_score = await self._analyze_customer_behavior(refund_request.customer_id)
        risk_score += behavioral_score * 0.3
        
        return {
            "risk_score": min(risk_score, 1.0),
            "fraud_indicators": fraud_indicators,
            "acceptable_risk": risk_score < self.config["fraud_score_threshold"]
        }
    
    async def _run_ml_analysis(
        self,
        refund_request: RefundRequest,
        original_transaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Machine learning analysis for refund pattern recognition
        """
        try:
            # Prepare features for ML model
            features = await self._extract_ml_features(refund_request, original_transaction)
            
            # Run ML prediction (simulated - would use actual ML model)
            prediction_score = await self._predict_refund_legitimacy(features)
            
            # Pattern matching against historical data
            similar_cases = await self._find_similar_refund_cases(features)
            
            return {
                "prediction_score": prediction_score,
                "confidence": 0.85,  # Simulated confidence
                "similar_cases": len(similar_cases),
                "pattern_match": "legitimate_refund" if prediction_score > 0.7 else "suspicious_refund",
                "features": features
            }
            
        except Exception as e:
            logger.warning(f"ML analysis failed: {e}")
            return {
                "prediction_score": 0.5,
                "confidence": 0.1,
                "error": str(e)
            }
    
    async def _get_ai_decision(
        self,
        refund_request: RefundRequest,
        original_transaction: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get AI-powered decision recommendation
        """
        try:
            # Prepare context for AI
            context = {
                "refund_amount": float(refund_request.amount),
                "original_amount": float(original_transaction.get("amount", 0)),
                "refund_reason": refund_request.reason.value,
                "customer_history": await self._get_customer_summary(refund_request.customer_id),
                "risk_indicators": risk_analysis["fraud_indicators"],
                "transaction_age_days": (datetime.utcnow() - original_transaction.get("created_at")).days
            }
            
            # Get AI recommendation
            ai_response = await self.openai_service.get_refund_recommendation(context)
            
            return {
                "recommendation": ai_response.get("recommendation", "manual_review"),
                "confidence": ai_response.get("confidence", 0.5),
                "reasoning": ai_response.get("reasoning", "AI analysis completed"),
                "recommendations": ai_response.get("recommendations", [])
            }
            
        except Exception as e:
            logger.warning(f"AI decision failed: {e}")
            return {
                "recommendation": "manual_review",
                "confidence": 0.0,
                "reasoning": "AI decision unavailable",
                "recommendations": ["Manual review recommended due to AI service unavailability"]
            }
    
    # ================================
    # REFUND PROCESSING
    # ================================
    
    async def _process_approved_refund(
        self,
        refund_request: Union[RefundRequest, Dict[str, Any]]
    ) -> RefundResult:
        """
        Process an approved refund through the orchestration system
        """
        if isinstance(refund_request, dict):
            # Convert dict to RefundRequest object
            refund_request = RefundRequest(**refund_request)
        
        try:
            # Initialize processing
            await self._log_refund_event(
                refund_id=refund_request.refund_id,
                action="processing_started",
                gateway=refund_request.gateway,
                amount=refund_request.amount
            )
            
            # Select optimal processing strategy
            strategy = await self._select_processing_strategy(refund_request)
            
            # Execute refund processing
            if strategy == "instant_pix":
                result = await self._process_instant_pix_refund(refund_request)
            elif strategy == "card_refund":
                result = await self._process_card_refund(refund_request)
            elif strategy == "boleto_credit":
                result = await self._process_boleto_refund(refund_request)
            else:
                result = await self._process_generic_refund(refund_request)
            
            # Post-processing
            await self._handle_refund_completion(refund_request, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Refund processing failed: {e}")
            return RefundResult(
                refund_id=refund_request.refund_id,
                status=RefundStatus.FAILED,
                amount=refund_request.amount,
                error_message=str(e)
            )
    
    async def _process_refund_with_gateway(
        self,
        refund_request: Union[RefundRequest, Dict[str, Any]]
    ) -> RefundResult:
        """
        Process refund through specific gateway with retry logic
        """
        if isinstance(refund_request, dict):
            refund_request = RefundRequest(**refund_request)
        
        gateway = refund_request.gateway
        max_retries = self.config["retry_max_attempts"]
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Get appropriate processor
                processor = self.refund_processors.get(gateway)
                if not processor:
                    raise RefundServiceError(f"No processor available for gateway: {gateway}")
                
                # Process refund
                result = await processor.process_refund(refund_request)
                
                # Calculate fees and net amount
                result.processing_fee = await self._calculate_refund_fee(refund_request, result)
                result.net_refund_amount = result.amount - result.processing_fee
                
                # Set estimated arrival time
                result.estimated_arrival = await self._calculate_arrival_time(refund_request, result)
                
                return result
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Gateway {gateway} refund attempt {retry_count} failed: {e}")
                
                if retry_count >= max_retries:
                    # Try fallback gateway
                    fallback_gateway = await self._get_refund_fallback_gateway(gateway, refund_request.payment_method)
                    if fallback_gateway:
                        logger.info(f"Failing over refund from {gateway} to {fallback_gateway}")
                        refund_request.gateway = fallback_gateway
                        return await self._process_refund_with_gateway(refund_request)
                    else:
                        return RefundResult(
                            refund_id=refund_request.refund_id,
                            status=RefundStatus.FAILED,
                            amount=refund_request.amount,
                            error_message=f"All gateways failed for refund {refund_request.refund_id}",
                            retry_count=retry_count
                        )
                
                # Exponential backoff
                await asyncio.sleep(2 ** retry_count)
    
    # ================================
    # UTILITY METHODS
    # ================================
    
    def _should_auto_approve(
        self,
        refund_request: RefundRequest,
        risk_analysis: Dict[str, Any],
        ml_analysis: Dict[str, Any]
    ) -> bool:
        """
        Determine if refund should be auto-approved
        """
        # Auto-approval criteria
        return (
            refund_request.amount <= self.config["auto_approval_threshold"] and
            risk_analysis["risk_score"] < 0.3 and
            ml_analysis.get("prediction_score", 0) > 0.8 and
            len(risk_analysis["fraud_indicators"]) == 0 and
            refund_request.priority in [RefundPriority.LOW, RefundPriority.MEDIUM]
        )
    
    def _calculate_risk_level(self, risk_score: float) -> RiskLevel:
        """Calculate risk level from risk score"""
        if risk_score < 0.2:
            return RiskLevel.VERY_LOW
        elif risk_score < 0.4:
            return RiskLevel.LOW
        elif risk_score < 0.6:
            return RiskLevel.MEDIUM
        elif risk_score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def _estimate_processing_time(self, refund_request: RefundRequest) -> int:
        """Estimate processing time in minutes"""
        base_time = {
            PaymentMethod.PIX: 5,
            PaymentMethod.CREDIT_CARD: 1440,  # 24 hours
            PaymentMethod.DEBIT_CARD: 720,    # 12 hours
            PaymentMethod.BOLETO: 2880,       # 48 hours
            PaymentMethod.BANK_TRANSFER: 720
        }
        
        return base_time.get(refund_request.payment_method, 1440)
    
    async def _log_refund_event(self, refund_id: str, action: str, **kwargs):
        """Log refund events for audit and monitoring"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": "refund_service",
            "refund_id": refund_id,
            "action": action,
            **kwargs
        }
        logger.info(f"Refund event: {json.dumps(log_data, default=str)}")
        
        # Store in database for audit trail
        # Implementation would store in audit table
    
    # Additional utility methods would be implemented here
    # These are placeholder methods for the core refund functionality
    
    async def _get_transaction_details(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get original transaction details"""
        # Implementation would query transaction database
        return {
            "payment_id": transaction_id,
            "amount": Decimal("100.00"),
            "customer_id": 1,
            "status": "completed",
            "gateway": BankingGateway.MERCADOPAGO,
            "payment_method": PaymentMethod.PIX,
            "created_at": datetime.utcnow() - timedelta(days=1)
        }
    
    async def _store_refund_request(self, refund_request: RefundRequest, analysis: RefundAnalysis):
        """Store refund request in database"""
        # Implementation would store in database
        pass
    
    async def _update_refund_status(self, refund_id: str, status: RefundStatus):
        """Update refund status in database"""
        # Implementation would update database
        logger.info(f"Refund {refund_id} status updated to {status}")
    
    async def _get_refund_request(self, refund_id: str) -> Optional[Dict[str, Any]]:
        """Get refund request from database"""
        # Implementation would query database
        return {"refund_id": refund_id, "status": RefundStatus.PENDING_APPROVAL}
    
    async def _send_refund_notification(self, notification_type: str, refund_request: RefundRequest, result: Any = None, **kwargs):
        """Send refund notifications"""
        await self.notification_service.send_refund_notification(notification_type, refund_request, result, **kwargs)
    
    # More utility methods would be implemented for production use