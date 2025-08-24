"""
Chargeback Manager - Comprehensive Chargeback and Dispute Management System
Sistema Universal de Gestão de Eventos

Advanced chargeback management system with predictive prevention, automated dispute handling,
evidence collection, representment processing, and intelligent chargeback analytics.

Features:
- Predictive chargeback prevention
- Automated dispute detection and handling
- Evidence collection and documentation
- Representment workflow automation
- Chargeback analytics and reporting
- Real-time monitoring and alerts
- Compliance with card network rules
- Integration with payment processors
- Customer communication management
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import hashlib
import base64

from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.core.config import get_settings
from app.services.banking_service import BankingGateway, PaymentMethod, TransactionStatus
from app.services.refund_service import RefundService, RefundRequest, RefundStatus
from app.services.notification_service import NotificationService
from app.services.openai_service import OpenAIService


class ChargebackStatus(str, Enum):
    """Chargeback status definitions"""
    RECEIVED = "received"
    UNDER_REVIEW = "under_review"
    EVIDENCE_REQUIRED = "evidence_required"
    EVIDENCE_SUBMITTED = "evidence_submitted"
    REPRESENTMENT = "representment"
    WON = "won"
    LOST = "lost"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    PRE_ARBITRATION = "pre_arbitration"
    ARBITRATION = "arbitration"
    FINAL_CHARGEBACK = "final_chargeback"


class ChargebackReason(str, Enum):
    """Standard chargeback reason codes"""
    # Fraud-related
    FRAUD_CARD_NOT_PRESENT = "fraud_cnp"
    FRAUD_CARD_PRESENT = "fraud_cp"
    FRAUD_NO_CARDHOLDER_AUTHORIZATION = "fraud_no_auth"
    
    # Authorization-related
    AUTH_NO_AUTHORIZATION = "auth_no_auth"
    AUTH_DECLINED_AUTHORIZATION = "auth_declined"
    AUTH_EXPIRED_AUTHORIZATION = "auth_expired"
    
    # Processing-related
    PROCESSING_DUPLICATE = "proc_duplicate"
    PROCESSING_CREDIT_NOT_PROCESSED = "proc_credit_not_processed"
    PROCESSING_PAID_BY_OTHER_MEANS = "proc_other_means"
    
    # Consumer disputes
    CONSUMER_PRODUCT_NOT_RECEIVED = "cons_not_received"
    CONSUMER_DEFECTIVE_PRODUCT = "cons_defective"
    CONSUMER_NOT_AS_DESCRIBED = "cons_not_described"
    CONSUMER_CANCELLED_RECURRING = "cons_cancelled_recurring"


class ChargebackType(str, Enum):
    """Types of chargebacks"""
    FIRST_CHARGEBACK = "first_chargeback"
    PRE_ARBITRATION = "pre_arbitration"
    ARBITRATION = "arbitration"
    RETRIEVAL_REQUEST = "retrieval_request"
    REPRESENTMENT = "representment"


class DisputeCategory(str, Enum):
    """Dispute categories"""
    FRAUD = "fraud"
    AUTHORIZATION = "authorization"
    PROCESSING_ERROR = "processing_error"
    CONSUMER_DISPUTE = "consumer_dispute"
    NON_RECEIPT = "non_receipt"
    DUPLICATE_PROCESSING = "duplicate_processing"
    CREDIT_NOT_PROCESSED = "credit_not_processed"


class EvidenceType(str, Enum):
    """Types of evidence for disputes"""
    RECEIPT = "receipt"
    TRANSACTION_RECORD = "transaction_record"
    AUTHORIZATION_PROOF = "authorization_proof"
    SHIPPING_PROOF = "shipping_proof"
    COMMUNICATION_RECORDS = "communication_records"
    REFUND_PROOF = "refund_proof"
    TERMS_OF_SERVICE = "terms_of_service"
    CUSTOMER_SIGNATURE = "customer_signature"
    IP_ADDRESS_LOG = "ip_address_log"
    DEVICE_FINGERPRINT = "device_fingerprint"


@dataclass
class ChargebackCase:
    """Chargeback case data structure"""
    case_id: str
    transaction_id: str
    payment_id: str
    chargeback_id: str  # From payment processor
    amount: Decimal
    currency: str = "BRL"
    reason_code: ChargebackReason = ChargebackReason.FRAUD_CARD_NOT_PRESENT
    reason_description: str = ""
    chargeback_type: ChargebackType = ChargebackType.FIRST_CHARGEBACK
    dispute_category: DisputeCategory = DisputeCategory.FRAUD
    status: ChargebackStatus = ChargebackStatus.RECEIVED
    gateway: Optional[BankingGateway] = None
    payment_method: Optional[PaymentMethod] = None
    customer_id: Optional[int] = None
    merchant_id: Optional[str] = None
    received_date: datetime = field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    response_due_date: Optional[datetime] = None
    case_number: Optional[str] = None
    processor_case_id: Optional[str] = None
    liability_shift: bool = False
    representable: bool = True
    evidence_required: List[EvidenceType] = field(default_factory=list)
    evidence_submitted: Dict[str, Any] = field(default_factory=dict)
    win_probability: float = 0.5
    estimated_cost: Decimal = Decimal("0.00")
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DisputeEvidence:
    """Evidence data structure"""
    evidence_id: str
    case_id: str
    evidence_type: EvidenceType
    title: str
    description: str
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None


@dataclass
class PreventionAlert:
    """Chargeback prevention alert"""
    alert_id: str
    transaction_id: str
    alert_type: str
    risk_score: float
    reason: str
    recommendations: List[str]
    expires_at: datetime
    resolved: bool = False
    resolution_action: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class ChargebackManager:
    """
    Comprehensive chargeback and dispute management system
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        
        # Initialize services
        self.refund_service = RefundService(db)
        self.notification_service = NotificationService(db)
        self.openai_service = OpenAIService()
        
        # Chargeback configuration
        self.config = self._load_chargeback_config()
        
        # Active cases and alerts
        self.active_cases: Dict[str, ChargebackCase] = {}
        self.prevention_alerts: Dict[str, PreventionAlert] = {}
        
        # Performance metrics
        self.metrics = {
            "chargebacks_received": 0,
            "chargebacks_won": 0,
            "chargebacks_lost": 0,
            "win_rate": 0.0,
            "total_disputed_amount": Decimal("0.00"),
            "recovered_amount": Decimal("0.00"),
            "prevention_alerts": 0,
            "prevented_chargebacks": 0
        }
        
        # Start background monitoring
        asyncio.create_task(self._chargeback_monitor())
        asyncio.create_task(self._prevention_monitor())
    
    def _load_chargeback_config(self) -> Dict[str, Any]:
        """Load chargeback management configuration"""
        return {
            "response_time_days": {
                ChargebackType.FIRST_CHARGEBACK: 7,
                ChargebackType.PRE_ARBITRATION: 10,
                ChargebackType.ARBITRATION: 10,
                ChargebackType.RETRIEVAL_REQUEST: 7
            },
            "prevention": {
                "enabled": True,
                "risk_threshold": 0.7,
                "auto_refund_threshold": 0.8,
                "alert_window_hours": 24
            },
            "representment": {
                "auto_represent": True,
                "min_win_probability": 0.6,
                "max_amount_threshold": Decimal("10000.00")
            },
            "evidence_collection": {
                "auto_collect": True,
                "retention_days": 730,  # 2 years
                "required_evidence": {
                    DisputeCategory.FRAUD: [
                        EvidenceType.AUTHORIZATION_PROOF,
                        EvidenceType.TRANSACTION_RECORD,
                        EvidenceType.IP_ADDRESS_LOG
                    ],
                    DisputeCategory.CONSUMER_DISPUTE: [
                        EvidenceType.RECEIPT,
                        EvidenceType.COMMUNICATION_RECORDS,
                        EvidenceType.TERMS_OF_SERVICE
                    ]
                }
            },
            "fees": {
                "chargeback_fee": Decimal("15.00"),
                "representment_fee": Decimal("25.00"),
                "arbitration_fee": Decimal("500.00")
            }
        }
    
    # ================================
    # CHARGEBACK PREVENTION
    # ================================
    
    async def analyze_chargeback_risk(
        self,
        transaction_id: str,
        payment_data: Dict[str, Any],
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze chargeback risk for a transaction
        """
        try:
            logger.info(f"Analyzing chargeback risk for transaction {transaction_id}")
            
            # Calculate risk score
            risk_analysis = await self._calculate_chargeback_risk_score(
                payment_data, customer_data
            )
            
            # Get AI-powered risk assessment
            ai_analysis = await self._get_ai_chargeback_analysis(
                transaction_id, payment_data, customer_data, risk_analysis
            )
            
            # Generate prevention recommendations
            recommendations = await self._generate_prevention_recommendations(
                risk_analysis, ai_analysis
            )
            
            # Create prevention alert if high risk
            if risk_analysis["risk_score"] > self.config["prevention"]["risk_threshold"]:
                alert = await self._create_prevention_alert(
                    transaction_id, risk_analysis, recommendations
                )
            else:
                alert = None
            
            return {
                "transaction_id": transaction_id,
                "risk_score": risk_analysis["risk_score"],
                "risk_level": self._get_risk_level(risk_analysis["risk_score"]),
                "risk_factors": risk_analysis["risk_factors"],
                "ai_analysis": ai_analysis,
                "recommendations": recommendations,
                "prevention_alert": alert,
                "preventive_actions": await self._suggest_preventive_actions(risk_analysis)
            }
            
        except Exception as e:
            logger.error(f"Chargeback risk analysis failed: {e}")
            return {
                "transaction_id": transaction_id,
                "risk_score": 0.5,
                "risk_level": "medium",
                "error": str(e)
            }
    
    async def _calculate_chargeback_risk_score(
        self,
        payment_data: Dict[str, Any],
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive chargeback risk score
        """
        risk_factors = []
        risk_score = 0.0
        
        # Amount-based risk
        amount = payment_data.get("amount", 0)
        if amount > 5000:
            risk_factors.append("high_amount")
            risk_score += 0.3
        elif amount > 1000:
            risk_factors.append("medium_amount")
            risk_score += 0.1
        
        # Payment method risk
        payment_method = payment_data.get("payment_method")
        if payment_method in ["credit_card", "debit_card"]:
            # Card payments have higher chargeback risk
            risk_score += 0.2
        
        # Customer behavior risk
        customer_age_days = (datetime.utcnow() - customer_data.get("created_at", datetime.utcnow())).days
        if customer_age_days < 30:
            risk_factors.append("new_customer")
            risk_score += 0.3
        
        previous_chargebacks = customer_data.get("previous_chargebacks", 0)
        if previous_chargebacks > 0:
            risk_factors.append("previous_chargebacks")
            risk_score += 0.4
        
        # Geographic risk
        country = customer_data.get("country", "BR")
        if country != "BR":
            risk_factors.append("international_customer")
            risk_score += 0.2
        
        # Velocity risk
        recent_transactions = customer_data.get("recent_transactions_count", 0)
        if recent_transactions > 10:
            risk_factors.append("high_velocity")
            risk_score += 0.2
        
        # Device and IP risk
        if customer_data.get("suspicious_device", False):
            risk_factors.append("suspicious_device")
            risk_score += 0.3
        
        if customer_data.get("proxy_or_vpn", False):
            risk_factors.append("proxy_vpn")
            risk_score += 0.2
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        
        return {
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "components": {
                "amount_risk": min(amount / 10000, 0.3),
                "customer_risk": 0.3 if customer_age_days < 30 else 0.1,
                "behavioral_risk": min(previous_chargebacks * 0.2, 0.4),
                "geographic_risk": 0.2 if country != "BR" else 0.0,
                "device_risk": 0.3 if customer_data.get("suspicious_device") else 0.0
            }
        }
    
    async def _get_ai_chargeback_analysis(
        self,
        transaction_id: str,
        payment_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get AI-powered chargeback risk analysis
        """
        try:
            # Prepare context for AI
            context = {
                "transaction": {
                    "id": transaction_id,
                    "amount": payment_data.get("amount"),
                    "payment_method": payment_data.get("payment_method"),
                    "gateway": payment_data.get("gateway"),
                    "timestamp": payment_data.get("created_at", datetime.utcnow()).isoformat()
                },
                "customer": {
                    "id": customer_data.get("customer_id"),
                    "account_age_days": (datetime.utcnow() - customer_data.get("created_at", datetime.utcnow())).days,
                    "previous_chargebacks": customer_data.get("previous_chargebacks", 0),
                    "total_transactions": customer_data.get("total_transactions", 0),
                    "country": customer_data.get("country", "BR")
                },
                "risk_analysis": risk_analysis
            }
            
            # Get AI analysis
            prompt = self._create_chargeback_analysis_prompt(context)
            
            response = await self.openai_service.chat_completion(
                messages=[
                    {"role": "system", "content": self._get_chargeback_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                model="gpt-4",
                temperature=0.1,
                max_tokens=800
            )
            
            # Parse AI response
            ai_analysis = self._parse_ai_chargeback_response(response)
            
            return ai_analysis
            
        except Exception as e:
            logger.error(f"AI chargeback analysis failed: {e}")
            return {
                "chargeback_probability": risk_analysis.get("risk_score", 0.5),
                "confidence": 0.0,
                "reasoning": f"AI analysis failed: {str(e)}",
                "recommended_actions": ["Manual review recommended"]
            }
    
    def _create_chargeback_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for AI chargeback analysis"""
        return f"""
Analyze this transaction for chargeback risk:

TRANSACTION DETAILS:
- ID: {context['transaction']['id']}
- Amount: R$ {context['transaction']['amount']:.2f}
- Payment Method: {context['transaction']['payment_method']}
- Gateway: {context['transaction']['gateway']}
- Timestamp: {context['transaction']['timestamp']}

CUSTOMER PROFILE:
- Customer ID: {context['customer']['id']}
- Account Age: {context['customer']['account_age_days']} days
- Previous Chargebacks: {context['customer']['previous_chargebacks']}
- Total Transactions: {context['customer']['total_transactions']}
- Country: {context['customer']['country']}

RISK ANALYSIS:
- Risk Score: {context['risk_analysis']['risk_score']:.2f}
- Risk Factors: {', '.join(context['risk_analysis']['risk_factors'])}

Please provide:
1. Chargeback probability (0.0 to 1.0)
2. Confidence in assessment (0.0 to 1.0)
3. Detailed reasoning
4. Recommended preventive actions
5. Early warning indicators
6. Dispute categories most likely

Format as JSON:
{{
    "chargeback_probability": 0.0-1.0,
    "confidence": 0.0-1.0,
    "reasoning": "detailed analysis",
    "recommended_actions": ["action1", "action2"],
    "early_warnings": ["warning1", "warning2"],
    "likely_dispute_categories": ["category1", "category2"],
    "prevention_strategy": "immediate|proactive|monitor"
}}
"""
    
    def _get_chargeback_system_prompt(self) -> str:
        """Get system prompt for chargeback analysis"""
        return """
You are an expert in payment fraud and chargeback prevention with extensive experience in:
- Card payment fraud patterns
- Customer behavior analysis
- Chargeback reason codes and dispute categories
- Risk assessment and prevention strategies
- Payment industry compliance

Analyze transactions for chargeback risk considering:
- Transaction characteristics and patterns
- Customer behavior and history
- Payment method and gateway risks
- Geographic and temporal factors
- Industry benchmarks and trends

Provide actionable insights for chargeback prevention while balancing customer experience.
"""
    
    def _parse_ai_chargeback_response(self, response: str) -> Dict[str, Any]:
        """Parse AI chargeback analysis response"""
        try:
            # Try to parse as JSON
            if response.startswith("{") and response.endswith("}"):
                return json.loads(response)
            
            # Extract JSON from response
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            
            # Fallback parsing
            return {
                "chargeback_probability": 0.5,
                "confidence": 0.3,
                "reasoning": response,
                "recommended_actions": ["Manual review"],
                "prevention_strategy": "monitor"
            }
            
        except Exception as e:
            logger.error(f"Failed to parse AI chargeback response: {e}")
            return {
                "chargeback_probability": 0.5,
                "confidence": 0.0,
                "reasoning": "Failed to parse AI analysis",
                "error": str(e)
            }
    
    async def _create_prevention_alert(
        self,
        transaction_id: str,
        risk_analysis: Dict[str, Any],
        recommendations: List[str]
    ) -> PreventionAlert:
        """Create chargeback prevention alert"""
        alert_id = f"alert_{uuid.uuid4().hex[:12]}"
        
        alert = PreventionAlert(
            alert_id=alert_id,
            transaction_id=transaction_id,
            alert_type="chargeback_risk",
            risk_score=risk_analysis["risk_score"],
            reason=f"High chargeback risk detected: {', '.join(risk_analysis['risk_factors'])}",
            recommendations=recommendations,
            expires_at=datetime.utcnow() + timedelta(hours=self.config["prevention"]["alert_window_hours"])
        )
        
        # Store alert
        self.prevention_alerts[alert_id] = alert
        
        # Update metrics
        self.metrics["prevention_alerts"] += 1
        
        # Send alert notification
        await self._send_prevention_alert_notification(alert)
        
        logger.info(f"Prevention alert created: {alert_id} for transaction {transaction_id}")
        return alert
    
    # ================================
    # CHARGEBACK PROCESSING
    # ================================
    
    async def receive_chargeback(
        self,
        chargeback_data: Dict[str, Any],
        gateway: BankingGateway
    ) -> ChargebackCase:
        """
        Process incoming chargeback notification
        """
        try:
            logger.info(f"Receiving chargeback from {gateway}: {chargeback_data.get('chargeback_id')}")
            
            # Create chargeback case
            case = await self._create_chargeback_case(chargeback_data, gateway)
            
            # Store in active cases
            self.active_cases[case.case_id] = case
            
            # Determine response strategy
            response_strategy = await self._determine_response_strategy(case)
            
            # Auto-collect evidence if enabled
            if self.config["evidence_collection"]["auto_collect"]:
                await self._auto_collect_evidence(case)
            
            # Check for automatic representment
            if (response_strategy["represent"] and 
                self.config["representment"]["auto_represent"] and
                case.win_probability >= self.config["representment"]["min_win_probability"]):
                await self._initiate_representment(case)
            
            # Send notifications
            await self._send_chargeback_notification(case, "received")
            
            # Update metrics
            self.metrics["chargebacks_received"] += 1
            self.metrics["total_disputed_amount"] += case.amount
            
            logger.info(f"Chargeback case created: {case.case_id}")
            return case
            
        except Exception as e:
            logger.error(f"Chargeback processing failed: {e}")
            raise
    
    async def _create_chargeback_case(
        self,
        chargeback_data: Dict[str, Any],
        gateway: BankingGateway
    ) -> ChargebackCase:
        """Create chargeback case from incoming data"""
        case_id = f"cb_{uuid.uuid4().hex[:16]}"
        
        # Parse chargeback data
        reason_code = self._parse_reason_code(chargeback_data.get("reason_code"))
        dispute_category = self._determine_dispute_category(reason_code)
        
        # Calculate due dates
        chargeback_type = ChargebackType(chargeback_data.get("type", ChargebackType.FIRST_CHARGEBACK))
        response_days = self.config["response_time_days"][chargeback_type]
        response_due_date = datetime.utcnow() + timedelta(days=response_days)
        
        # Calculate win probability
        win_probability = await self._calculate_win_probability(chargeback_data, reason_code)
        
        # Determine required evidence
        evidence_required = self.config["evidence_collection"]["required_evidence"].get(
            dispute_category, []
        )
        
        case = ChargebackCase(
            case_id=case_id,
            transaction_id=chargeback_data.get("transaction_id"),
            payment_id=chargeback_data.get("payment_id"),
            chargeback_id=chargeback_data.get("chargeback_id"),
            amount=Decimal(str(chargeback_data.get("amount", "0"))),
            reason_code=reason_code,
            reason_description=chargeback_data.get("reason_description", ""),
            chargeback_type=chargeback_type,
            dispute_category=dispute_category,
            gateway=gateway,
            payment_method=PaymentMethod(chargeback_data.get("payment_method", "credit_card")),
            customer_id=chargeback_data.get("customer_id"),
            merchant_id=chargeback_data.get("merchant_id"),
            due_date=datetime.fromisoformat(chargeback_data["due_date"]) if chargeback_data.get("due_date") else None,
            response_due_date=response_due_date,
            case_number=chargeback_data.get("case_number"),
            processor_case_id=chargeback_data.get("processor_case_id"),
            liability_shift=chargeback_data.get("liability_shift", False),
            evidence_required=evidence_required,
            win_probability=win_probability,
            estimated_cost=self.config["fees"]["chargeback_fee"]
        )
        
        return case
    
    async def _determine_response_strategy(self, case: ChargebackCase) -> Dict[str, Any]:
        """Determine optimal response strategy for chargeback"""
        strategy = {
            "represent": False,
            "accept": False,
            "settle": False,
            "escalate": False,
            "priority": "normal"
        }
        
        # High win probability cases should be represented
        if case.win_probability >= self.config["representment"]["min_win_probability"]:
            strategy["represent"] = True
            strategy["priority"] = "high"
        
        # Low amount cases might be accepted
        elif case.amount < Decimal("100.00"):
            strategy["accept"] = True
            strategy["priority"] = "low"
        
        # High amount cases get escalated
        elif case.amount > self.config["representment"]["max_amount_threshold"]:
            strategy["escalate"] = True
            strategy["priority"] = "urgent"
        
        # Fraud cases with strong evidence should be represented
        elif case.dispute_category == DisputeCategory.FRAUD and case.win_probability > 0.4:
            strategy["represent"] = True
            strategy["priority"] = "high"
        
        else:
            # Default to manual review
            strategy["priority"] = "normal"
        
        return strategy
    
    async def _auto_collect_evidence(self, case: ChargebackCase):
        """Automatically collect evidence for chargeback case"""
        try:
            logger.info(f"Auto-collecting evidence for case {case.case_id}")
            
            evidence_items = []
            
            # Collect transaction records
            transaction_evidence = await self._collect_transaction_evidence(case)
            if transaction_evidence:
                evidence_items.append(transaction_evidence)
            
            # Collect authorization proof
            if EvidenceType.AUTHORIZATION_PROOF in case.evidence_required:
                auth_evidence = await self._collect_authorization_evidence(case)
                if auth_evidence:
                    evidence_items.append(auth_evidence)
            
            # Collect shipping/delivery proof
            if EvidenceType.SHIPPING_PROOF in case.evidence_required:
                shipping_evidence = await self._collect_shipping_evidence(case)
                if shipping_evidence:
                    evidence_items.append(shipping_evidence)
            
            # Collect communication records
            if EvidenceType.COMMUNICATION_RECORDS in case.evidence_required:
                comm_evidence = await self._collect_communication_evidence(case)
                if comm_evidence:
                    evidence_items.append(comm_evidence)
            
            # Store collected evidence
            for evidence in evidence_items:
                case.evidence_submitted[evidence.evidence_type] = evidence
            
            logger.info(f"Collected {len(evidence_items)} evidence items for case {case.case_id}")
            
        except Exception as e:
            logger.error(f"Evidence collection failed for case {case.case_id}: {e}")
    
    async def submit_representment(
        self,
        case_id: str,
        additional_evidence: List[DisputeEvidence] = None,
        custom_message: str = None
    ) -> Dict[str, Any]:
        """
        Submit chargeback representment
        """
        try:
            case = self.active_cases.get(case_id)
            if not case:
                raise ValueError(f"Chargeback case not found: {case_id}")
            
            if case.status != ChargebackStatus.EVIDENCE_REQUIRED:
                raise ValueError(f"Case not ready for representment: {case.status}")
            
            logger.info(f"Submitting representment for case {case_id}")
            
            # Add additional evidence
            if additional_evidence:
                for evidence in additional_evidence:
                    case.evidence_submitted[evidence.evidence_type] = evidence
            
            # Generate representment package
            representment_package = await self._generate_representment_package(case, custom_message)
            
            # Submit to payment processor
            submission_result = await self._submit_to_processor(case, representment_package)
            
            # Update case status
            case.status = ChargebackStatus.REPRESENTMENT
            case.updated_at = datetime.utcnow()
            
            # Log representment submission
            await self._log_chargeback_event(case_id, "representment_submitted", submission_result)
            
            # Send notification
            await self._send_chargeback_notification(case, "representment_submitted")
            
            return {
                "case_id": case_id,
                "status": "submitted",
                "submission_id": submission_result.get("submission_id"),
                "expected_response_date": submission_result.get("expected_response_date"),
                "evidence_count": len(case.evidence_submitted)
            }
            
        except Exception as e:
            logger.error(f"Representment submission failed: {e}")
            raise
    
    async def update_chargeback_outcome(
        self,
        case_id: str,
        outcome: str,
        outcome_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update chargeback outcome from processor
        """
        try:
            case = self.active_cases.get(case_id)
            if not case:
                raise ValueError(f"Chargeback case not found: {case_id}")
            
            logger.info(f"Updating chargeback outcome for case {case_id}: {outcome}")
            
            # Update case status
            if outcome.lower() == "won":
                case.status = ChargebackStatus.WON
                self.metrics["chargebacks_won"] += 1
                self.metrics["recovered_amount"] += case.amount
            elif outcome.lower() == "lost":
                case.status = ChargebackStatus.LOST
                self.metrics["chargebacks_lost"] += 1
            else:
                case.status = ChargebackStatus(outcome.lower())
            
            case.updated_at = datetime.utcnow()
            case.metadata["outcome_data"] = outcome_data
            
            # Calculate updated win rate
            total_resolved = self.metrics["chargebacks_won"] + self.metrics["chargebacks_lost"]
            if total_resolved > 0:
                self.metrics["win_rate"] = self.metrics["chargebacks_won"] / total_resolved * 100
            
            # Log outcome
            await self._log_chargeback_event(case_id, "outcome_updated", {
                "outcome": outcome,
                "outcome_data": outcome_data
            })
            
            # Send notification
            await self._send_chargeback_notification(case, f"outcome_{outcome.lower()}")
            
            # Remove from active cases if final
            if case.status in [ChargebackStatus.WON, ChargebackStatus.LOST, ChargebackStatus.FINAL_CHARGEBACK]:
                # Move to archived cases (would be stored in database)
                pass
            
            return {
                "case_id": case_id,
                "outcome": outcome,
                "final_status": case.status,
                "updated_at": case.updated_at
            }
            
        except Exception as e:
            logger.error(f"Outcome update failed: {e}")
            raise
    
    # ================================
    # MONITORING AND ANALYTICS
    # ================================
    
    async def _chargeback_monitor(self):
        """Background monitoring for chargeback cases"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                for case in self.active_cases.values():
                    # Check for approaching due dates
                    if case.response_due_date and case.response_due_date <= current_time + timedelta(hours=24):
                        await self._handle_approaching_deadline(case)
                    
                    # Check for expired cases
                    if case.response_due_date and case.response_due_date <= current_time:
                        await self._handle_expired_case(case)
                
                # Clean up old prevention alerts
                expired_alerts = [
                    alert_id for alert_id, alert in self.prevention_alerts.items()
                    if alert.expires_at <= current_time
                ]
                
                for alert_id in expired_alerts:
                    del self.prevention_alerts[alert_id]
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Chargeback monitor error: {e}")
                await asyncio.sleep(300)  # Shorter delay on error
    
    async def _prevention_monitor(self):
        """Background monitoring for prevention opportunities"""
        while True:
            try:
                # Monitor for patterns that indicate chargeback risk
                await self._analyze_chargeback_patterns()
                
                # Update prevention models
                await self._update_prevention_models()
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Prevention monitor error: {e}")
                await asyncio.sleep(300)
    
    async def get_chargeback_analytics(self) -> Dict[str, Any]:
        """Get comprehensive chargeback analytics"""
        return {
            "overview": {
                "total_cases": len(self.active_cases),
                "chargebacks_received": self.metrics["chargebacks_received"],
                "win_rate_percentage": self.metrics["win_rate"],
                "total_disputed_amount": float(self.metrics["total_disputed_amount"]),
                "recovered_amount": float(self.metrics["recovered_amount"]),
                "prevention_alerts": self.metrics["prevention_alerts"],
                "prevented_chargebacks": self.metrics["prevented_chargebacks"]
            },
            "by_status": self._get_cases_by_status(),
            "by_category": self._get_cases_by_category(),
            "by_gateway": self._get_cases_by_gateway(),
            "trends": await self._calculate_chargeback_trends(),
            "prevention_metrics": {
                "active_alerts": len(self.prevention_alerts),
                "prevention_rate": self._calculate_prevention_rate()
            }
        }
    
    # ================================
    # UTILITY METHODS
    # ================================
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.6:
            return "medium"
        elif risk_score < 0.8:
            return "high"
        else:
            return "critical"
    
    def _parse_reason_code(self, reason_code: str) -> ChargebackReason:
        """Parse reason code from processor"""
        # Mapping would be more comprehensive in production
        mapping = {
            "4853": ChargebackReason.FRAUD_CARD_NOT_PRESENT,
            "4855": ChargebackReason.CONSUMER_PRODUCT_NOT_RECEIVED,
            "4834": ChargebackReason.PROCESSING_DUPLICATE,
            "4808": ChargebackReason.AUTH_NO_AUTHORIZATION
        }
        return mapping.get(reason_code, ChargebackReason.FRAUD_CARD_NOT_PRESENT)
    
    def _determine_dispute_category(self, reason_code: ChargebackReason) -> DisputeCategory:
        """Determine dispute category from reason code"""
        if reason_code.value.startswith("fraud"):
            return DisputeCategory.FRAUD
        elif reason_code.value.startswith("auth"):
            return DisputeCategory.AUTHORIZATION
        elif reason_code.value.startswith("proc"):
            return DisputeCategory.PROCESSING_ERROR
        else:
            return DisputeCategory.CONSUMER_DISPUTE
    
    # Additional utility methods would be implemented for production use
    async def _calculate_win_probability(self, chargeback_data: Dict[str, Any], reason_code: ChargebackReason) -> float:
        """Calculate win probability for chargeback case"""
        # Simplified calculation - would use ML models in production
        base_probability = 0.5
        
        # Adjust based on reason code
        if reason_code in [ChargebackReason.FRAUD_CARD_NOT_PRESENT]:
            base_probability = 0.3  # Fraud cases are harder to win
        elif reason_code in [ChargebackReason.PROCESSING_DUPLICATE]:
            base_probability = 0.8  # Processing errors easier to dispute
        
        return base_probability
    
    async def _log_chargeback_event(self, case_id: str, event_type: str, details: Dict[str, Any]):
        """Log chargeback events for audit"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "case_id": case_id,
            "event_type": event_type,
            "details": details
        }
        logger.info(f"Chargeback event: {json.dumps(log_data, default=str)}")
    
    # More utility methods would be implemented for production use...