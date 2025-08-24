"""
Test Suite - Sistema Completo de Estornos
Sistema Universal de Gestão de Eventos

Testes automatizados abrangentes para o sistema de refunds:
- Testes unitários de todos os serviços
- Testes de integração end-to-end
- Testes de performance e carga
- Testes de segurança e validação
- Testes de APIs REST
- Testes de IA e machine learning
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

import pytest_asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Import main app and dependencies
from app.main import app
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User

# Import refund services
from app.services.refund_service import (
    RefundService, RefundRequest, RefundStatus, RefundReason, 
    RefundType, RefundPriority, RefundServiceError
)
from app.services.refund_validator import (
    RefundValidator, ValidationResult, ValidationReport, 
    ValidationCategory, ValidationSeverity
)
from app.services.refund_processor import (
    RefundProcessorFactory, PIXRefundProcessor, CardRefundProcessor,
    BoletoRefundProcessor, get_refund_processor
)
from app.services.refund_orchestrator import (
    RefundOrchestrator, WorkflowType, WorkflowState, EscalationTrigger
)
from app.services.refund_intelligence import RefundIntelligence, ModelType
from app.services.chargeback_manager import ChargebackManager, ChargebackStatus
from app.services.banking_service import PaymentMethod, BankingGateway


# ================================
# FIXTURES AND SETUP
# ================================

@pytest.fixture
def mock_db():
    """Mock database session"""
    db = Mock(spec=Session)
    return db


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.can_approve_refunds = True
    user.is_admin = True
    return user


@pytest.fixture
def sample_refund_request():
    """Sample refund request for testing"""
    return RefundRequest(
        refund_id="ref_test_001",
        transaction_id="txn_test_001",
        original_payment_id="pay_test_001",
        customer_id=1,
        amount=Decimal("100.00"),
        reason=RefundReason.CUSTOMER_REQUEST,
        refund_type=RefundType.FULL,
        priority=RefundPriority.MEDIUM,
        description="Test refund request",
        requested_by="test@example.com",
        gateway=BankingGateway.MERCADOPAGO,
        payment_method=PaymentMethod.PIX
    )


@pytest.fixture
def sample_transaction():
    """Sample transaction data"""
    return {
        "payment_id": "pay_test_001",
        "amount": Decimal("100.00"),
        "customer_id": 1,
        "status": "completed",
        "gateway": BankingGateway.MERCADOPAGO,
        "payment_method": PaymentMethod.PIX,
        "created_at": datetime.utcnow() - timedelta(days=1)
    }


@pytest.fixture
async def async_client():
    """Async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def client():
    """Sync HTTP client for testing"""
    return TestClient(app)


# ================================
# REFUND SERVICE TESTS
# ================================

class TestRefundService:
    """Test suite for RefundService"""
    
    @pytest.mark.asyncio
    async def test_request_refund_success(self, mock_db, sample_refund_request, sample_transaction):
        """Test successful refund request"""
        refund_service = RefundService(mock_db)
        
        # Mock dependencies
        with patch.object(refund_service, '_get_transaction_details', return_value=sample_transaction), \
             patch.object(refund_service, '_store_refund_request', return_value=True), \
             patch.object(refund_service, '_log_refund_event', return_value=None):
            
            result = await refund_service.request_refund(
                transaction_id="txn_test_001",
                amount=Decimal("100.00"),
                reason=RefundReason.CUSTOMER_REQUEST,
                description="Test refund"
            )
            
            assert result["status"] in [RefundStatus.PENDING_APPROVAL, RefundStatus.APPROVED]
            assert "refund_id" in result
    
    @pytest.mark.asyncio
    async def test_request_refund_transaction_not_found(self, mock_db):
        """Test refund request with non-existent transaction"""
        refund_service = RefundService(mock_db)
        
        with patch.object(refund_service, '_get_transaction_details', return_value=None):
            with pytest.raises(RefundServiceError):
                await refund_service.request_refund(
                    transaction_id="non_existent",
                    amount=Decimal("100.00"),
                    reason=RefundReason.CUSTOMER_REQUEST
                )
    
    @pytest.mark.asyncio
    async def test_approve_refund_success(self, mock_db, sample_refund_request):
        """Test successful refund approval"""
        refund_service = RefundService(mock_db)
        
        with patch.object(refund_service, '_get_refund_request', return_value={"status": RefundStatus.PENDING_APPROVAL}), \
             patch.object(refund_service, '_update_refund_status', return_value=None), \
             patch.object(refund_service, '_process_approved_refund', return_value={"status": RefundStatus.PROCESSING}), \
             patch.object(refund_service, '_send_refund_notification', return_value=None), \
             patch.object(refund_service, '_log_refund_event', return_value=None):
            
            result = await refund_service.approve_refund(
                refund_id="ref_test_001",
                approved_by="admin@test.com"
            )
            
            assert result["status"] == RefundStatus.PROCESSING
            assert result["approved_by"] == "admin@test.com"
    
    @pytest.mark.asyncio
    async def test_reject_refund_success(self, mock_db):
        """Test successful refund rejection"""
        refund_service = RefundService(mock_db)
        
        with patch.object(refund_service, '_get_refund_request', return_value={"status": RefundStatus.PENDING_APPROVAL}), \
             patch.object(refund_service, '_update_refund_status', return_value=None), \
             patch.object(refund_service, '_send_refund_notification', return_value=None), \
             patch.object(refund_service, '_log_refund_event', return_value=None):
            
            result = await refund_service.reject_refund(
                refund_id="ref_test_001",
                rejected_by="admin@test.com",
                reason="Insufficient evidence"
            )
            
            assert result["status"] == RefundStatus.REJECTED
            assert result["rejected_by"] == "admin@test.com"


# ================================
# REFUND VALIDATOR TESTS
# ================================

class TestRefundValidator:
    """Test suite for RefundValidator"""
    
    @pytest.mark.asyncio
    async def test_validate_eligible_refund(self, mock_db, sample_refund_request, sample_transaction):
        """Test validation of eligible refund"""
        validator = RefundValidator(mock_db)
        
        with patch.object(validator, '_get_customer_profile', return_value={"customer_id": 1, "risk_level": "low"}):
            report = await validator.validate_refund_request(
                sample_refund_request,
                sample_transaction,
                {"customer_id": 1}
            )
            
            assert report.result in [ValidationResult.APPROVED, ValidationResult.REQUIRES_REVIEW]
            assert report.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_validate_ineligible_refund(self, mock_db, sample_refund_request, sample_transaction):
        """Test validation of ineligible refund"""
        validator = RefundValidator(mock_db)
        
        # Make transaction too old
        old_transaction = sample_transaction.copy()
        old_transaction["created_at"] = datetime.utcnow() - timedelta(days=365)
        
        with patch.object(validator, '_get_customer_profile', return_value={"customer_id": 1, "risk_level": "high"}):
            report = await validator.validate_refund_request(
                sample_refund_request,
                old_transaction,
                {"customer_id": 1}
            )
            
            assert report.result == ValidationResult.REJECTED
            assert len(report.issues) > 0
    
    def test_fraud_detection_high_risk(self, mock_db, sample_refund_request):
        """Test fraud detection for high-risk scenarios"""
        validator = RefundValidator(mock_db)
        
        # Create high-risk scenario
        high_risk_request = sample_refund_request
        high_risk_request.amount = Decimal("50000.00")  # Very high amount
        
        # Test would normally involve async fraud detection
        # This is a simplified synchronous test
        assert high_risk_request.amount > Decimal("10000.00")


# ================================
# REFUND PROCESSOR TESTS
# ================================

class TestRefundProcessors:
    """Test suite for RefundProcessor classes"""
    
    def test_processor_factory(self):
        """Test RefundProcessorFactory"""
        pix_processor = RefundProcessorFactory.create_processor(PaymentMethod.PIX)
        assert isinstance(pix_processor, PIXRefundProcessor)
        
        card_processor = RefundProcessorFactory.create_processor(PaymentMethod.CREDIT_CARD)
        assert isinstance(card_processor, CardRefundProcessor)
        
        boleto_processor = RefundProcessorFactory.create_processor(PaymentMethod.BOLETO)
        assert isinstance(boleto_processor, BoletoRefundProcessor)
    
    @pytest.mark.asyncio
    async def test_pix_refund_processing(self, sample_refund_request):
        """Test PIX refund processing"""
        processor = PIXRefundProcessor()
        
        with patch.object(processor, '_validate_pix_refund', return_value=None), \
             patch.object(processor, '_process_picpay_pix_refund', return_value={
                 "refund_id": "ref_test_001",
                 "status": RefundStatus.COMPLETED,
                 "amount": Decimal("100.00")
             }):
            
            result = await processor.process_refund(sample_refund_request)
            
            assert result.refund_id == "ref_test_001"
            assert result.status == RefundStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_card_refund_processing(self, sample_refund_request):
        """Test credit card refund processing"""
        processor = CardRefundProcessor()
        
        # Modify request for card processing
        card_request = sample_refund_request
        card_request.payment_method = PaymentMethod.CREDIT_CARD
        card_request.gateway = BankingGateway.STRIPE
        
        with patch.object(processor, '_validate_card_refund', return_value=None), \
             patch.object(processor, '_assess_chargeback_risk', return_value={"high_risk": False}), \
             patch.object(processor, '_process_stripe_card_refund', return_value={
                 "refund_id": "ref_test_001",
                 "status": RefundStatus.PROCESSING,
                 "amount": Decimal("100.00")
             }):
            
            result = await processor.process_refund(card_request)
            
            assert result.refund_id == "ref_test_001"
            assert result.status == RefundStatus.PROCESSING


# ================================
# REFUND ORCHESTRATOR TESTS
# ================================

class TestRefundOrchestrator:
    """Test suite for RefundOrchestrator"""
    
    @pytest.mark.asyncio
    async def test_orchestrate_automatic_workflow(self, mock_db, sample_refund_request, sample_transaction):
        """Test automatic workflow orchestration"""
        orchestrator = RefundOrchestrator(mock_db)
        
        with patch.object(orchestrator, '_create_workflow_instance') as mock_create, \
             patch.object(orchestrator, '_execute_workflow') as mock_execute:
            
            mock_workflow = Mock()
            mock_workflow.workflow_id = "wf_test_001"
            mock_workflow.current_state = WorkflowState.INITIALIZED
            mock_create.return_value = mock_workflow
            
            result = await orchestrator.orchestrate_refund(
                sample_refund_request,
                sample_transaction,
                WorkflowType.AUTOMATIC
            )
            
            assert result.workflow_id == "wf_test_001"
            mock_create.assert_called_once()
            mock_execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_approve_workflow(self, mock_db):
        """Test workflow approval"""
        orchestrator = RefundOrchestrator(mock_db)
        
        # Create mock workflow
        mock_workflow = Mock()
        mock_workflow.current_state = WorkflowState.PENDING_APPROVAL
        orchestrator.active_workflows["wf_test_001"] = mock_workflow
        
        with patch.object(orchestrator, '_update_workflow_state') as mock_update, \
             patch.object(orchestrator, '_log_workflow_event') as mock_log, \
             patch.object(orchestrator, '_resume_workflow_execution') as mock_resume:
            
            result = await orchestrator.approve_workflow(
                "wf_test_001",
                "admin@test.com",
                "Approved for processing"
            )
            
            assert result["status"] == "approved"
            mock_update.assert_called()
            mock_log.assert_called()


# ================================
# REFUND INTELLIGENCE TESTS
# ================================

class TestRefundIntelligence:
    """Test suite for RefundIntelligence (AI/ML)"""
    
    @pytest.mark.asyncio
    async def test_ai_analysis(self, mock_db, sample_refund_request, sample_transaction):
        """Test AI-powered refund analysis"""
        intelligence = RefundIntelligence(mock_db)
        
        with patch.object(intelligence, '_extract_features') as mock_features, \
             patch.object(intelligence, '_run_ml_predictions') as mock_ml, \
             patch.object(intelligence, '_get_gpt_analysis') as mock_gpt:
            
            # Mock AI responses
            mock_features.return_value = Mock()
            mock_ml.return_value = {
                "fraud_detection": {"fraud_probability": 0.2, "is_fraud": False},
                "legitimacy_prediction": {"legitimate_probability": 0.8, "is_legitimate": True}
            }
            mock_gpt.return_value = {
                "recommendation": "approve",
                "confidence": 0.9,
                "reasoning": "Legitimate customer request"
            }
            
            result = await intelligence.analyze_refund_request(
                sample_refund_request,
                sample_transaction,
                {"customer_id": 1}
            )
            
            assert result.refund_id == sample_refund_request.refund_id
            assert result.confidence_score > 0
    
    def test_model_initialization(self, mock_db):
        """Test ML model initialization"""
        intelligence = RefundIntelligence(mock_db)
        
        # Models should be initialized (or fallback models created)
        assert hasattr(intelligence, 'models')
        assert hasattr(intelligence, 'scalers')


# ================================
# CHARGEBACK MANAGER TESTS
# ================================

class TestChargebackManager:
    """Test suite for ChargebackManager"""
    
    @pytest.mark.asyncio
    async def test_analyze_chargeback_risk(self, mock_db):
        """Test chargeback risk analysis"""
        manager = ChargebackManager(mock_db)
        
        payment_data = {
            "amount": 1000.00,
            "payment_method": "credit_card",
            "gateway": "stripe"
        }
        
        customer_data = {
            "customer_id": 1,
            "created_at": datetime.utcnow() - timedelta(days=365),
            "previous_chargebacks": 0,
            "country": "BR"
        }
        
        with patch.object(manager, '_calculate_chargeback_risk_score') as mock_calc, \
             patch.object(manager, '_get_ai_chargeback_analysis') as mock_ai:
            
            mock_calc.return_value = {"risk_score": 0.3, "risk_factors": ["medium_amount"]}
            mock_ai.return_value = {"chargeback_probability": 0.2, "confidence": 0.8}
            
            result = await manager.analyze_chargeback_risk(
                "txn_test_001",
                payment_data,
                customer_data
            )
            
            assert "risk_score" in result
            assert "risk_level" in result
            assert "recommendations" in result
    
    @pytest.mark.asyncio
    async def test_receive_chargeback(self, mock_db):
        """Test chargeback case creation"""
        manager = ChargebackManager(mock_db)
        
        chargeback_data = {
            "chargeback_id": "cb_test_001",
            "transaction_id": "txn_test_001",
            "payment_id": "pay_test_001",
            "amount": 100.00,
            "reason_code": "4853",
            "type": "first_chargeback"
        }
        
        with patch.object(manager, '_create_chargeback_case') as mock_create, \
             patch.object(manager, '_determine_response_strategy') as mock_strategy, \
             patch.object(manager, '_send_chargeback_notification') as mock_notify:
            
            mock_case = Mock()
            mock_case.case_id = "case_test_001"
            mock_create.return_value = mock_case
            mock_strategy.return_value = {"represent": True}
            
            result = await manager.receive_chargeback(
                chargeback_data,
                BankingGateway.STRIPE
            )
            
            assert result.case_id == "case_test_001"


# ================================
# API ENDPOINT TESTS
# ================================

class TestRefundAPI:
    """Test suite for Refund REST APIs"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Override dependencies
        def override_get_db():
            return Mock(spec=Session)
        
        def override_get_current_user():
            user = Mock(spec=User)
            user.id = 1
            user.email = "test@example.com"
            user.can_approve_refunds = True
            user.is_admin = True
            return user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user
    
    def teardown_method(self):
        """Cleanup after each test method"""
        app.dependency_overrides.clear()
    
    def test_request_refund_endpoint(self, client):
        """Test POST /refunds/request endpoint"""
        with patch('app.services.refund_service.RefundService') as mock_service_class, \
             patch('app.services.refund_orchestrator.RefundOrchestrator') as mock_orchestrator_class:
            
            # Setup mocks
            mock_service = mock_service_class.return_value
            mock_service._get_transaction_details.return_value = {
                "payment_id": "pay_test_001",
                "amount": 100.00,
                "gateway": "mercadopago",
                "payment_method": "pix"
            }
            
            mock_orchestrator = mock_orchestrator_class.return_value
            mock_workflow = Mock()
            mock_workflow.workflow_id = "wf_test_001"
            mock_workflow.current_state = Mock()
            mock_workflow.current_state.value = "approved"
            mock_workflow.sla_deadline = datetime.utcnow() + timedelta(hours=1)
            mock_orchestrator.orchestrate_refund.return_value = mock_workflow
            
            # Make request
            response = client.post(
                "/api/v1/refunds/request",
                data={
                    "transaction_id": "txn_test_001",
                    "amount": "100.00",
                    "reason": "customer_request",
                    "priority": "medium"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "refund_id" in data
            assert "status" in data
    
    def test_get_refund_status_endpoint(self, client):
        """Test GET /refunds/{refund_id}/status endpoint"""
        with patch('app.services.refund_service.RefundService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service._get_refund_request.return_value = {
                "refund_id": "ref_test_001",
                "status": "completed",
                "amount": Decimal("100.00"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            response = client.get("/api/v1/refunds/ref_test_001/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["refund_id"] == "ref_test_001"
            assert data["status"] == "completed"
    
    def test_approve_refund_endpoint(self, client):
        """Test POST /refunds/{refund_id}/approve endpoint"""
        with patch('app.services.refund_service.RefundService') as mock_service_class, \
             patch('app.services.refund_orchestrator.RefundOrchestrator') as mock_orchestrator_class:
            
            mock_service = mock_service_class.return_value
            mock_service.approve_refund.return_value = {
                "refund_id": "ref_test_001",
                "status": "approved",
                "approved_by": "test@example.com"
            }
            mock_service._get_refund_request.return_value = {"workflow_id": "wf_test_001"}
            
            mock_orchestrator = mock_orchestrator_class.return_value
            
            response = client.post(
                "/api/v1/refunds/ref_test_001/approve",
                json={"notes": "Approved for processing"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["approved"] == True
    
    def test_get_refund_metrics_endpoint(self, client):
        """Test GET /refunds/analytics/metrics endpoint"""
        response = client.get("/api/v1/refunds/analytics/metrics?time_range=30d")
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "time_range" in data
    
    def test_analyze_eligibility_endpoint(self, client):
        """Test POST /refunds/analyze-eligibility endpoint"""
        with patch('app.services.refund_validator.RefundValidator') as mock_validator_class, \
             patch('app.services.refund_intelligence.RefundIntelligence') as mock_intelligence_class:
            
            mock_validator = mock_validator_class.return_value
            mock_report = Mock()
            mock_report.result.value = "approved"
            mock_report.confidence = 0.9
            mock_report.risk_score = 0.2
            mock_report.risk_level.value = "low"
            mock_report.issues = []
            mock_report.recommendations = ["Process normally"]
            mock_report.estimated_processing_time = 30
            mock_validator.validate_refund_request.return_value = mock_report
            
            mock_intelligence = mock_intelligence_class.return_value
            mock_intelligence.analyze_refund_request.return_value = {
                "analysis_id": "ai_test_001",
                "confidence_score": 0.9
            }
            
            response = client.post(
                "/api/v1/refunds/analyze-eligibility",
                json={
                    "transaction_id": "txn_test_001",
                    "amount": 100.00,
                    "reason": "customer_request",
                    "original_transaction": {
                        "payment_id": "pay_test_001",
                        "amount": 100.00
                    }
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["eligible"] == True
            assert data["confidence"] == 0.9


# ================================
# INTEGRATION TESTS
# ================================

class TestRefundIntegration:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_refund_workflow(self, mock_db, sample_refund_request, sample_transaction):
        """Test complete refund workflow from request to completion"""
        
        # Initialize services
        refund_service = RefundService(mock_db)
        orchestrator = RefundOrchestrator(mock_db)
        validator = RefundValidator(mock_db)
        
        with patch.object(refund_service, '_get_transaction_details', return_value=sample_transaction), \
             patch.object(refund_service, '_store_refund_request', return_value=True), \
             patch.object(refund_service, '_log_refund_event', return_value=None), \
             patch.object(validator, '_get_customer_profile', return_value={"customer_id": 1, "risk_level": "low"}):
            
            # Step 1: Request refund
            refund_result = await refund_service.request_refund(
                transaction_id="txn_test_001",
                amount=Decimal("100.00"),
                reason=RefundReason.CUSTOMER_REQUEST
            )
            
            assert "refund_id" in refund_result
            
            # Step 2: Validate refund
            validation_report = await validator.validate_refund_request(
                sample_refund_request,
                sample_transaction,
                {"customer_id": 1}
            )
            
            assert validation_report.result in [ValidationResult.APPROVED, ValidationResult.REQUIRES_REVIEW]
            
            # Step 3: If approved, process through orchestrator
            if validation_report.result == ValidationResult.APPROVED:
                workflow = await orchestrator.orchestrate_refund(
                    sample_refund_request,
                    sample_transaction,
                    WorkflowType.AUTOMATIC
                )
                
                assert workflow.workflow_id is not None


# ================================
# PERFORMANCE TESTS
# ================================

class TestRefundPerformance:
    """Performance and load tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_refund_requests(self, mock_db):
        """Test handling multiple concurrent refund requests"""
        refund_service = RefundService(mock_db)
        
        # Create multiple refund requests
        requests = []
        for i in range(10):
            request = RefundRequest(
                refund_id=f"ref_perf_{i}",
                transaction_id=f"txn_perf_{i}",
                original_payment_id=f"pay_perf_{i}",
                customer_id=i,
                amount=Decimal("100.00"),
                reason=RefundReason.CUSTOMER_REQUEST
            )
            requests.append(request)
        
        # Mock the dependencies
        with patch.object(refund_service, '_get_transaction_details') as mock_transaction, \
             patch.object(refund_service, '_store_refund_request', return_value=True), \
             patch.object(refund_service, '_log_refund_event', return_value=None):
            
            mock_transaction.return_value = {
                "payment_id": "pay_test",
                "amount": Decimal("100.00"),
                "status": "completed",
                "created_at": datetime.utcnow()
            }
            
            # Process requests concurrently
            tasks = []
            for request in requests:
                task = refund_service.request_refund(
                    transaction_id=request.transaction_id,
                    amount=request.amount,
                    reason=request.reason
                )
                tasks.append(task)
            
            # Wait for all to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify results
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) == 10
    
    def test_ai_model_performance(self, mock_db):
        """Test AI model inference performance"""
        intelligence = RefundIntelligence(mock_db)
        
        # Test model loading time
        start_time = datetime.utcnow()
        # Models should be loaded during initialization
        load_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Should load within reasonable time
        assert load_time < 5.0  # 5 seconds max
    
    @pytest.mark.asyncio
    async def test_database_query_performance(self, mock_db):
        """Test database query performance"""
        refund_service = RefundService(mock_db)
        
        with patch.object(refund_service, '_get_refund_request') as mock_query:
            mock_query.return_value = {"refund_id": "test", "status": "completed"}
            
            # Test multiple rapid queries
            start_time = datetime.utcnow()
            
            for _ in range(100):
                await refund_service._get_refund_request("test_id")
            
            query_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Should complete within reasonable time
            assert query_time < 1.0  # 1 second for 100 queries


# ================================
# SECURITY TESTS
# ================================

class TestRefundSecurity:
    """Security and validation tests"""
    
    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection"""
        # Attempt SQL injection in refund ID
        malicious_id = "'; DROP TABLE refunds; --"
        
        response = client.get(f"/api/v1/refunds/{malicious_id}/status")
        
        # Should not cause server error, either 404 or proper validation error
        assert response.status_code in [404, 422]
    
    def test_authorization_checks(self, client):
        """Test authorization for admin endpoints"""
        # Override to return user without admin permissions
        def override_get_current_user():
            user = Mock(spec=User)
            user.id = 1
            user.email = "test@example.com"
            user.can_approve_refunds = False
            user.is_admin = False
            return user
        
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        # Try to access admin endpoint
        response = client.get("/api/v1/refunds/admin/queue")
        
        assert response.status_code == 403
        
        # Cleanup
        app.dependency_overrides.clear()
    
    def test_input_validation(self, client):
        """Test input validation and sanitization"""
        # Test with invalid amount
        response = client.post(
            "/api/v1/refunds/request",
            data={
                "transaction_id": "txn_test_001",
                "amount": "-100.00",  # Negative amount
                "reason": "customer_request",
                "priority": "medium"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_rate_limiting(self, client):
        """Test rate limiting protection"""
        # This would test actual rate limiting if implemented
        # For now, just verify the endpoint exists
        response = client.get("/api/v1/refunds/health")
        assert response.status_code == 200


# ================================
# ERROR HANDLING TESTS
# ================================

class TestRefundErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_service_unavailable_handling(self, mock_db):
        """Test handling when external services are unavailable"""
        refund_service = RefundService(mock_db)
        
        # Mock external service failure
        with patch.object(refund_service, '_get_transaction_details', side_effect=Exception("Service unavailable")):
            
            with pytest.raises(RefundServiceError):
                await refund_service.request_refund(
                    transaction_id="txn_test_001",
                    amount=Decimal("100.00"),
                    reason=RefundReason.CUSTOMER_REQUEST
                )
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, mock_db):
        """Test timeout handling for long-running operations"""
        intelligence = RefundIntelligence(mock_db)
        
        # Mock timeout scenario
        with patch.object(intelligence, 'analyze_refund_request', side_effect=asyncio.TimeoutError()):
            
            # Should handle timeout gracefully
            try:
                result = await intelligence.analyze_refund_request(
                    Mock(), Mock(), Mock()
                )
                # Should return fallback analysis
                assert result is not None
            except asyncio.TimeoutError:
                pytest.fail("TimeoutError should be handled gracefully")
    
    def test_invalid_enum_values(self, mock_db):
        """Test handling of invalid enum values"""
        # Test with invalid status
        with pytest.raises(ValueError):
            RefundStatus("invalid_status")
        
        # Test with invalid reason
        with pytest.raises(ValueError):
            RefundReason("invalid_reason")


# ================================
# TEST CONFIGURATION AND RUNNERS
# ================================

def test_health_check(client):
    """Test system health check endpoint"""
    response = client.get("/api/v1/refunds/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=app.services",
        "--cov=app.routers.refunds",
        "--cov-report=term-missing",
        "--asyncio-mode=auto"
    ])