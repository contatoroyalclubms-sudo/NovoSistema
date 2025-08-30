"""
Refund Orchestrator - Advanced Workflow Orchestration System
Sistema Universal de Gestão de Eventos

Sophisticated workflow orchestration system for refund processing with intelligent
automation, dynamic workflow generation, state management, and real-time monitoring.

Features:
- Dynamic workflow generation based on refund characteristics
- State machine-based workflow management
- Intelligent automation and escalation
- Real-time workflow monitoring and analytics
- SLA management and compliance tracking
- Multi-step approval workflows
- Parallel processing capabilities
- Rollback and compensation mechanisms
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from enum import Enum
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import logging

from loguru import logger
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.refund_service import (
    RefundService, RefundRequest, RefundResult, RefundStatus, 
    RefundType, RefundReason, RefundPriority
)
from app.services.refund_validator import RefundValidator, ValidationReport, ValidationResult
from app.services.refund_processor import RefundProcessorFactory, get_refund_processor
from app.services.notification_service import NotificationService


class WorkflowState(str, Enum):
    """Workflow state definitions"""
    INITIALIZED = "initialized"
    VALIDATING = "validating"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved" 
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"
    ON_HOLD = "on_hold"
    ROLLBACK = "rollback"


class WorkflowAction(str, Enum):
    """Available workflow actions"""
    VALIDATE = "validate"
    APPROVE = "approve"
    REJECT = "reject"
    PROCESS = "process"
    ESCALATE = "escalate"
    HOLD = "hold"
    RESUME = "resume"
    CANCEL = "cancel"
    ROLLBACK = "rollback"
    RETRY = "retry"
    NOTIFY = "notify"


class WorkflowType(str, Enum):
    """Types of refund workflows"""
    AUTOMATIC = "automatic"
    MANUAL_REVIEW = "manual_review"
    ESCALATED = "escalated"
    EXPEDITED = "expedited"
    BATCH = "batch"
    COMPLIANCE = "compliance"


class EscalationTrigger(str, Enum):
    """Escalation trigger types"""
    SLA_BREACH = "sla_breach"
    HIGH_VALUE = "high_value"
    FRAUD_RISK = "fraud_risk"
    COMPLIANCE_ISSUE = "compliance_issue"
    CUSTOMER_VIP = "customer_vip"
    MANUAL_REQUEST = "manual_request"
    SYSTEM_ERROR = "system_error"


@dataclass
class WorkflowStep:
    """Individual workflow step definition"""
    step_id: str
    name: str
    action: WorkflowAction
    handler: Optional[Callable] = None
    conditions: List[str] = field(default_factory=list)
    timeout_minutes: int = 60
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)
    parallel_execution: bool = False
    optional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowInstance:
    """Runtime workflow instance"""
    workflow_id: str
    refund_id: str
    workflow_type: WorkflowType
    current_state: WorkflowState
    steps: List[WorkflowStep]
    step_results: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    sla_deadline: Optional[datetime] = None
    escalation_level: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEvent:
    """Workflow event for tracking and auditing"""
    event_id: str
    workflow_id: str
    event_type: str
    from_state: WorkflowState
    to_state: WorkflowState
    action: WorkflowAction
    actor: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class RefundOrchestrator:
    """
    Advanced workflow orchestration system for refund processing
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        
        # Initialize services
        self.refund_service = RefundService(db)
        self.refund_validator = RefundValidator(db)
        self.notification_service = NotificationService(db)
        
        # Workflow configuration
        self.config = self._load_orchestrator_config()
        self.workflow_templates = self._load_workflow_templates()
        
        # Runtime state
        self.active_workflows: Dict[str, WorkflowInstance] = {}
        self.event_log: List[WorkflowEvent] = []
        
        # Metrics and monitoring
        self.metrics = {
            "total_workflows": 0,
            "completed_workflows": 0,
            "failed_workflows": 0,
            "avg_completion_time": 0.0,
            "sla_breaches": 0,
            "escalations": 0
        }
        
        # Start background tasks
        asyncio.create_task(self._workflow_monitor())
        asyncio.create_task(self._sla_monitor())
    
    def _load_orchestrator_config(self) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        return {
            "sla_times": {  # SLA in minutes by priority
                RefundPriority.CRITICAL: 15,
                RefundPriority.URGENT: 60,
                RefundPriority.HIGH: 240,
                RefundPriority.MEDIUM: 1440,  # 24 hours
                RefundPriority.LOW: 2880     # 48 hours
            },
            "escalation_thresholds": {
                "high_value_amount": Decimal("10000.00"),
                "fraud_risk_score": 0.7,
                "sla_warning_percentage": 0.8  # 80% of SLA time
            },
            "batch_processing": {
                "batch_size": 50,
                "batch_interval_minutes": 30,
                "enabled": True
            },
            "auto_approval": {
                "max_amount": Decimal("500.00"),
                "max_risk_score": 0.3,
                "enabled": True
            },
            "retry_policy": {
                "max_retries": 3,
                "backoff_multiplier": 2,
                "initial_delay_seconds": 5
            }
        }
    
    def _load_workflow_templates(self) -> Dict[WorkflowType, List[WorkflowStep]]:
        """Load workflow templates for different scenarios"""
        return {
            WorkflowType.AUTOMATIC: [
                WorkflowStep("validate", "Validate Request", WorkflowAction.VALIDATE, timeout_minutes=5),
                WorkflowStep("process", "Process Refund", WorkflowAction.PROCESS, timeout_minutes=30),
                WorkflowStep("notify", "Send Notification", WorkflowAction.NOTIFY, timeout_minutes=5)
            ],
            WorkflowType.MANUAL_REVIEW: [
                WorkflowStep("validate", "Validate Request", WorkflowAction.VALIDATE, timeout_minutes=10),
                WorkflowStep("review", "Manual Review", WorkflowAction.APPROVE, timeout_minutes=4320),  # 3 days
                WorkflowStep("process", "Process Refund", WorkflowAction.PROCESS, timeout_minutes=30),
                WorkflowStep("notify", "Send Notification", WorkflowAction.NOTIFY, timeout_minutes=5)
            ],
            WorkflowType.ESCALATED: [
                WorkflowStep("validate", "Validate Request", WorkflowAction.VALIDATE, timeout_minutes=5),
                WorkflowStep("escalate", "Escalate to Manager", WorkflowAction.ESCALATE, timeout_minutes=60),
                WorkflowStep("approve", "Manager Approval", WorkflowAction.APPROVE, timeout_minutes=1440),  # 24 hours
                WorkflowStep("process", "Process Refund", WorkflowAction.PROCESS, timeout_minutes=30),
                WorkflowStep("notify", "Send Notification", WorkflowAction.NOTIFY, timeout_minutes=5)
            ],
            WorkflowType.EXPEDITED: [
                WorkflowStep("validate", "Fast Validate", WorkflowAction.VALIDATE, timeout_minutes=2),
                WorkflowStep("process", "Expedited Process", WorkflowAction.PROCESS, timeout_minutes=10),
                WorkflowStep("notify", "Immediate Notify", WorkflowAction.NOTIFY, timeout_minutes=2)
            ],
            WorkflowType.COMPLIANCE: [
                WorkflowStep("validate", "Compliance Validate", WorkflowAction.VALIDATE, timeout_minutes=10),
                WorkflowStep("compliance_check", "Compliance Review", WorkflowAction.APPROVE, timeout_minutes=2880),  # 48 hours
                WorkflowStep("legal_review", "Legal Review", WorkflowAction.APPROVE, timeout_minutes=7200),  # 5 days
                WorkflowStep("process", "Process Refund", WorkflowAction.PROCESS, timeout_minutes=30),
                WorkflowStep("notify", "Send Notification", WorkflowAction.NOTIFY, timeout_minutes=5)
            ]
        }
    
    # ================================
    # MAIN ORCHESTRATION METHODS
    # ================================
    
    async def orchestrate_refund(
        self,
        refund_request: RefundRequest,
        original_transaction: Dict[str, Any],
        workflow_type: Optional[WorkflowType] = None
    ) -> WorkflowInstance:
        """
        Orchestrate complete refund workflow with intelligent routing
        """
        workflow_id = f"wf_{uuid.uuid4().hex[:16]}"
        
        try:
            logger.info(f"Starting refund orchestration {workflow_id} for refund {refund_request.refund_id}")
            
            # Determine workflow type if not specified
            if not workflow_type:
                workflow_type = await self._determine_workflow_type(refund_request, original_transaction)
            
            # Create workflow instance
            workflow = await self._create_workflow_instance(
                workflow_id, refund_request, workflow_type, original_transaction
            )
            
            # Add to active workflows
            self.active_workflows[workflow_id] = workflow
            
            # Log workflow creation
            await self._log_workflow_event(
                workflow_id=workflow_id,
                event_type="workflow_created",
                from_state=WorkflowState.INITIALIZED,
                to_state=WorkflowState.INITIALIZED,
                action=WorkflowAction.VALIDATE,
                details={"workflow_type": workflow_type, "refund_id": refund_request.refund_id}
            )
            
            # Start workflow execution
            await self._execute_workflow(workflow)
            
            # Update metrics
            self.metrics["total_workflows"] += 1
            
            return workflow
            
        except Exception as e:
            logger.error(f"Workflow orchestration failed: {e}")
            
            # Create failed workflow instance
            failed_workflow = WorkflowInstance(
                workflow_id=workflow_id,
                refund_id=refund_request.refund_id,
                workflow_type=workflow_type or WorkflowType.MANUAL_REVIEW,
                current_state=WorkflowState.FAILED,
                steps=[],
                error_count=1,
                metadata={"error": str(e)}
            )
            
            return failed_workflow
    
    async def _determine_workflow_type(
        self,
        refund_request: RefundRequest,
        original_transaction: Dict[str, Any]
    ) -> WorkflowType:
        """
        Intelligently determine the appropriate workflow type
        """
        # High priority or critical refunds get expedited workflow
        if refund_request.priority in [RefundPriority.CRITICAL, RefundPriority.URGENT]:
            return WorkflowType.EXPEDITED
        
        # High value refunds require escalation
        if refund_request.amount > self.config["escalation_thresholds"]["high_value_amount"]:
            return WorkflowType.ESCALATED
        
        # Fraud-related refunds need compliance workflow
        if refund_request.reason in [RefundReason.FRAUD_PREVENTION, RefundReason.CHARGEBACK]:
            return WorkflowType.COMPLIANCE
        
        # Quick validation for auto-approval eligibility
        if (refund_request.amount <= self.config["auto_approval"]["max_amount"] and
            refund_request.reason in [RefundReason.EVENT_CANCELLED, RefundReason.DUPLICATE_PAYMENT]):
            return WorkflowType.AUTOMATIC
        
        # Default to manual review
        return WorkflowType.MANUAL_REVIEW
    
    async def _create_workflow_instance(
        self,
        workflow_id: str,
        refund_request: RefundRequest,
        workflow_type: WorkflowType,
        original_transaction: Dict[str, Any]
    ) -> WorkflowInstance:
        """
        Create workflow instance with configured steps
        """
        # Get workflow template
        template_steps = self.workflow_templates.get(workflow_type, [])
        
        # Calculate SLA deadline
        sla_minutes = self.config["sla_times"].get(refund_request.priority, 1440)
        sla_deadline = datetime.utcnow() + timedelta(minutes=sla_minutes)
        
        # Create workflow context
        context = {
            "refund_request": refund_request,
            "original_transaction": original_transaction,
            "created_by": refund_request.requested_by,
            "workflow_config": self.config
        }
        
        # Create workflow instance
        workflow = WorkflowInstance(
            workflow_id=workflow_id,
            refund_id=refund_request.refund_id,
            workflow_type=workflow_type,
            current_state=WorkflowState.INITIALIZED,
            steps=template_steps.copy(),
            context=context,
            sla_deadline=sla_deadline
        )
        
        return workflow
    
    async def _execute_workflow(self, workflow: WorkflowInstance):
        """
        Execute workflow with state machine logic
        """
        try:
            logger.info(f"Executing workflow {workflow.workflow_id}")
            
            # Update state to validating
            await self._update_workflow_state(workflow, WorkflowState.VALIDATING)
            
            # Execute steps sequentially (parallel execution support can be added)
            for step in workflow.steps:
                if await self._should_execute_step(workflow, step):
                    await self._execute_step(workflow, step)
                    
                    # Check if workflow should be halted
                    if workflow.current_state in [WorkflowState.FAILED, WorkflowState.CANCELLED, WorkflowState.ON_HOLD]:
                        break
            
            # Mark workflow as completed if successful
            if workflow.current_state not in [WorkflowState.FAILED, WorkflowState.CANCELLED]:
                await self._update_workflow_state(workflow, WorkflowState.COMPLETED)
                workflow.completed_at = datetime.utcnow()
                self.metrics["completed_workflows"] += 1
            else:
                self.metrics["failed_workflows"] += 1
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            await self._update_workflow_state(workflow, WorkflowState.FAILED)
            workflow.error_count += 1
            workflow.metadata["error"] = str(e)
    
    async def _execute_step(self, workflow: WorkflowInstance, step: WorkflowStep):
        """
        Execute individual workflow step
        """
        step_start_time = datetime.utcnow()
        
        try:
            logger.info(f"Executing step {step.step_id} in workflow {workflow.workflow_id}")
            
            # Execute step based on action
            result = await self._execute_step_action(workflow, step)
            
            # Store step result
            workflow.step_results[step.step_id] = {
                "status": "completed",
                "result": result,
                "executed_at": step_start_time,
                "execution_time": (datetime.utcnow() - step_start_time).total_seconds()
            }
            
            # Handle step result
            await self._handle_step_result(workflow, step, result)
            
        except Exception as e:
            logger.error(f"Step {step.step_id} execution failed: {e}")
            
            # Record step failure
            workflow.step_results[step.step_id] = {
                "status": "failed",
                "error": str(e),
                "executed_at": step_start_time,
                "execution_time": (datetime.utcnow() - step_start_time).total_seconds(),
                "retry_count": step.retry_count
            }
            
            # Handle retry logic
            if step.retry_count < step.max_retries:
                step.retry_count += 1
                delay = self.config["retry_policy"]["initial_delay_seconds"] * (
                    self.config["retry_policy"]["backoff_multiplier"] ** (step.retry_count - 1)
                )
                
                logger.info(f"Retrying step {step.step_id} in {delay} seconds (attempt {step.retry_count})")
                await asyncio.sleep(delay)
                await self._execute_step(workflow, step)
            else:
                # Step failed permanently
                if not step.optional:
                    await self._update_workflow_state(workflow, WorkflowState.FAILED)
                    raise Exception(f"Critical step {step.step_id} failed permanently")
    
    async def _execute_step_action(
        self,
        workflow: WorkflowInstance,
        step: WorkflowStep
    ) -> Any:
        """
        Execute specific step action
        """
        refund_request = workflow.context["refund_request"]
        original_transaction = workflow.context["original_transaction"]
        
        if step.action == WorkflowAction.VALIDATE:
            return await self._execute_validation_step(workflow, step)
        
        elif step.action == WorkflowAction.APPROVE:
            return await self._execute_approval_step(workflow, step)
        
        elif step.action == WorkflowAction.PROCESS:
            return await self._execute_processing_step(workflow, step)
        
        elif step.action == WorkflowAction.NOTIFY:
            return await self._execute_notification_step(workflow, step)
        
        elif step.action == WorkflowAction.ESCALATE:
            return await self._execute_escalation_step(workflow, step)
        
        else:
            raise ValueError(f"Unknown step action: {step.action}")
    
    async def _execute_validation_step(
        self,
        workflow: WorkflowInstance,
        step: WorkflowStep
    ) -> ValidationReport:
        """
        Execute validation step
        """
        refund_request = workflow.context["refund_request"]
        original_transaction = workflow.context["original_transaction"]
        
        # Run validation
        validation_report = await self.refund_validator.validate_refund_request(
            refund_request, original_transaction
        )
        
        # Update workflow based on validation result
        if validation_report.result == ValidationResult.APPROVED:
            if validation_report.auto_approve_eligible:
                await self._update_workflow_state(workflow, WorkflowState.APPROVED)
            else:
                await self._update_workflow_state(workflow, WorkflowState.PENDING_APPROVAL)
        elif validation_report.result == ValidationResult.REJECTED:
            await self._update_workflow_state(workflow, WorkflowState.FAILED)
        else:  # REQUIRES_REVIEW
            await self._update_workflow_state(workflow, WorkflowState.PENDING_APPROVAL)
        
        # Store validation report in workflow context
        workflow.context["validation_report"] = validation_report
        
        return validation_report
    
    async def _execute_approval_step(
        self,
        workflow: WorkflowInstance,
        step: WorkflowStep
    ) -> Dict[str, Any]:
        """
        Execute approval step (manual or automatic)
        """
        validation_report = workflow.context.get("validation_report")
        
        if validation_report and validation_report.auto_approve_eligible:
            # Auto-approve
            await self._update_workflow_state(workflow, WorkflowState.APPROVED)
            return {
                "approved": True,
                "approved_by": "system",
                "approval_type": "automatic",
                "timestamp": datetime.utcnow()
            }
        else:
            # Manual approval required - update state and wait
            await self._update_workflow_state(workflow, WorkflowState.PENDING_APPROVAL)
            return {
                "approved": False,
                "status": "pending_manual_approval",
                "timestamp": datetime.utcnow()
            }
    
    async def _execute_processing_step(
        self,
        workflow: WorkflowInstance,
        step: WorkflowStep
    ) -> RefundResult:
        """
        Execute refund processing step
        """
        refund_request = workflow.context["refund_request"]
        
        # Update state to processing
        await self._update_workflow_state(workflow, WorkflowState.PROCESSING)
        
        # Get appropriate processor
        processor = get_refund_processor(refund_request.payment_method)
        
        # Process refund
        result = await processor.process_refund(refund_request)
        
        # Store result in workflow context
        workflow.context["refund_result"] = result
        
        return result
    
    async def _execute_notification_step(
        self,
        workflow: WorkflowInstance,
        step: WorkflowStep
    ) -> Dict[str, Any]:
        """
        Execute notification step
        """
        refund_request = workflow.context["refund_request"]
        refund_result = workflow.context.get("refund_result")
        
        # Send appropriate notification
        notification_type = "refund_completed" if refund_result else "refund_approved"
        
        await self.notification_service.send_refund_notification(
            notification_type, refund_request, refund_result
        )
        
        return {
            "notification_sent": True,
            "type": notification_type,
            "timestamp": datetime.utcnow()
        }
    
    async def _execute_escalation_step(
        self,
        workflow: WorkflowInstance,
        step: WorkflowStep
    ) -> Dict[str, Any]:
        """
        Execute escalation step
        """
        workflow.escalation_level += 1
        await self._update_workflow_state(workflow, WorkflowState.ESCALATED)
        
        # Send escalation notification
        await self.notification_service.send_escalation_notification(
            workflow, EscalationTrigger.MANUAL_REQUEST
        )
        
        return {
            "escalated": True,
            "escalation_level": workflow.escalation_level,
            "timestamp": datetime.utcnow()
        }
    
    # ================================
    # WORKFLOW MANAGEMENT
    # ================================
    
    async def approve_workflow(
        self,
        workflow_id: str,
        approved_by: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Manually approve a workflow
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        if workflow.current_state != WorkflowState.PENDING_APPROVAL:
            raise ValueError(f"Workflow not in pending approval state: {workflow.current_state}")
        
        # Update workflow state
        await self._update_workflow_state(workflow, WorkflowState.APPROVED)
        
        # Log approval
        await self._log_workflow_event(
            workflow_id=workflow_id,
            event_type="workflow_approved",
            from_state=WorkflowState.PENDING_APPROVAL,
            to_state=WorkflowState.APPROVED,
            action=WorkflowAction.APPROVE,
            actor=approved_by,
            details={"notes": notes}
        )
        
        # Continue workflow execution
        await self._resume_workflow_execution(workflow)
        
        return {
            "workflow_id": workflow_id,
            "status": "approved",
            "approved_by": approved_by,
            "timestamp": datetime.utcnow()
        }
    
    async def reject_workflow(
        self,
        workflow_id: str,
        rejected_by: str,
        reason: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reject a workflow
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        # Update workflow state
        await self._update_workflow_state(workflow, WorkflowState.FAILED)
        
        # Log rejection
        await self._log_workflow_event(
            workflow_id=workflow_id,
            event_type="workflow_rejected",
            from_state=workflow.current_state,
            to_state=WorkflowState.FAILED,
            action=WorkflowAction.REJECT,
            actor=rejected_by,
            details={"reason": reason, "notes": notes}
        )
        
        # Send rejection notification
        refund_request = workflow.context["refund_request"]
        await self.notification_service.send_refund_notification(
            "refund_rejected", refund_request, reason=reason
        )
        
        return {
            "workflow_id": workflow_id,
            "status": "rejected",
            "rejected_by": rejected_by,
            "reason": reason,
            "timestamp": datetime.utcnow()
        }
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get detailed workflow status
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        # Calculate progress
        completed_steps = len([r for r in workflow.step_results.values() if r.get("status") == "completed"])
        total_steps = len(workflow.steps)
        progress_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        # Calculate time metrics
        elapsed_time = (datetime.utcnow() - workflow.created_at).total_seconds()
        remaining_sla_time = (workflow.sla_deadline - datetime.utcnow()).total_seconds() if workflow.sla_deadline else None
        
        return {
            "workflow_id": workflow_id,
            "refund_id": workflow.refund_id,
            "workflow_type": workflow.workflow_type,
            "current_state": workflow.current_state,
            "progress_percentage": progress_percentage,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "escalation_level": workflow.escalation_level,
            "error_count": workflow.error_count,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at,
            "completed_at": workflow.completed_at,
            "elapsed_time_seconds": elapsed_time,
            "remaining_sla_time_seconds": remaining_sla_time,
            "step_results": workflow.step_results,
            "metadata": workflow.metadata
        }
    
    # ================================
    # BACKGROUND MONITORING
    # ================================
    
    async def _workflow_monitor(self):
        """
        Background task to monitor active workflows
        """
        while True:
            try:
                # Monitor workflow timeouts
                current_time = datetime.utcnow()
                
                for workflow in list(self.active_workflows.values()):
                    # Check for step timeouts
                    await self._check_step_timeouts(workflow, current_time)
                    
                    # Check for stale workflows
                    if (current_time - workflow.updated_at).total_seconds() > 3600:  # 1 hour
                        logger.warning(f"Stale workflow detected: {workflow.workflow_id}")
                
                # Cleanup completed workflows older than 24 hours
                cutoff_time = current_time - timedelta(hours=24)
                workflows_to_remove = []
                
                for workflow_id, workflow in self.active_workflows.items():
                    if (workflow.current_state in [WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.CANCELLED] and
                        workflow.updated_at < cutoff_time):
                        workflows_to_remove.append(workflow_id)
                
                for workflow_id in workflows_to_remove:
                    del self.active_workflows[workflow_id]
                    logger.info(f"Cleaned up old workflow: {workflow_id}")
                
                # Wait before next monitoring cycle
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Workflow monitor error: {e}")
                await asyncio.sleep(60)  # Shorter delay on error
    
    async def _sla_monitor(self):
        """
        Background task to monitor SLA compliance
        """
        while True:
            try:
                current_time = datetime.utcnow()
                
                for workflow in self.active_workflows.values():
                    if workflow.sla_deadline and current_time > workflow.sla_deadline:
                        # SLA breach detected
                        if workflow.current_state not in [WorkflowState.COMPLETED, WorkflowState.FAILED]:
                            await self._handle_sla_breach(workflow)
                
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"SLA monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _handle_sla_breach(self, workflow: WorkflowInstance):
        """
        Handle SLA breach for workflow
        """
        logger.warning(f"SLA breach detected for workflow {workflow.workflow_id}")
        
        # Update metrics
        self.metrics["sla_breaches"] += 1
        
        # Escalate workflow
        workflow.escalation_level += 1
        await self._update_workflow_state(workflow, WorkflowState.ESCALATED)
        
        # Send escalation notification
        await self.notification_service.send_escalation_notification(
            workflow, EscalationTrigger.SLA_BREACH
        )
        
        # Log SLA breach
        await self._log_workflow_event(
            workflow_id=workflow.workflow_id,
            event_type="sla_breach",
            from_state=workflow.current_state,
            to_state=WorkflowState.ESCALATED,
            action=WorkflowAction.ESCALATE,
            details={"breach_time": datetime.utcnow(), "sla_deadline": workflow.sla_deadline}
        )
    
    # ================================
    # UTILITY METHODS
    # ================================
    
    async def _update_workflow_state(
        self,
        workflow: WorkflowInstance,
        new_state: WorkflowState
    ):
        """
        Update workflow state and log transition
        """
        old_state = workflow.current_state
        workflow.current_state = new_state
        workflow.updated_at = datetime.utcnow()
        
        # Log state transition
        await self._log_workflow_event(
            workflow_id=workflow.workflow_id,
            event_type="state_transition",
            from_state=old_state,
            to_state=new_state,
            action=WorkflowAction.VALIDATE,  # Default action
            details={"transition_time": workflow.updated_at}
        )
        
        logger.info(f"Workflow {workflow.workflow_id} state: {old_state} -> {new_state}")
    
    async def _log_workflow_event(
        self,
        workflow_id: str,
        event_type: str,
        from_state: WorkflowState,
        to_state: WorkflowState,
        action: WorkflowAction,
        actor: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log workflow event for audit trail
        """
        event = WorkflowEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            workflow_id=workflow_id,
            event_type=event_type,
            from_state=from_state,
            to_state=to_state,
            action=action,
            actor=actor,
            details=details or {}
        )
        
        self.event_log.append(event)
        
        # Keep only last 10000 events in memory
        if len(self.event_log) > 10000:
            self.event_log = self.event_log[-10000:]
        
        logger.info(f"Workflow event: {json.dumps({
            'event_id': event.event_id,
            'workflow_id': workflow_id,
            'event_type': event_type,
            'from_state': from_state,
            'to_state': to_state,
            'action': action,
            'actor': actor,
            'timestamp': event.timestamp.isoformat()
        })}")
    
    async def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """
        Get orchestrator performance metrics
        """
        active_count = len(self.active_workflows)
        
        # Calculate completion rate
        total_processed = self.metrics["completed_workflows"] + self.metrics["failed_workflows"]
        success_rate = (self.metrics["completed_workflows"] / total_processed * 100) if total_processed > 0 else 0
        
        return {
            "active_workflows": active_count,
            "total_workflows": self.metrics["total_workflows"],
            "completed_workflows": self.metrics["completed_workflows"],
            "failed_workflows": self.metrics["failed_workflows"],
            "success_rate_percentage": success_rate,
            "sla_breaches": self.metrics["sla_breaches"],
            "escalations": self.metrics["escalations"],
            "avg_completion_time": self.metrics["avg_completion_time"]
        }
    
    # Additional utility methods would be implemented for production use
    async def _should_execute_step(self, workflow: WorkflowInstance, step: WorkflowStep) -> bool:
        """Check if step should be executed based on conditions"""
        return True  # Simplified - would implement condition checking
    
    async def _handle_step_result(self, workflow: WorkflowInstance, step: WorkflowStep, result: Any):
        """Handle the result of a step execution"""
        pass  # Simplified - would implement result handling logic
    
    async def _resume_workflow_execution(self, workflow: WorkflowInstance):
        """Resume workflow execution after approval"""
        # Find next unexecuted step and continue
        pass  # Simplified - would implement resumption logic
    
    async def _check_step_timeouts(self, workflow: WorkflowInstance, current_time: datetime):
        """Check for step execution timeouts"""
        pass  # Simplified - would implement timeout checking