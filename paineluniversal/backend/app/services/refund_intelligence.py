"""
Refund Intelligence - AI-Powered Refund Analysis System
Sistema Universal de Gestão de Eventos

Advanced AI and machine learning system for intelligent refund processing with
predictive analytics, pattern recognition, fraud detection, and automated decision making.

Features:
- GPT-4 powered refund analysis and recommendations
- Machine learning fraud detection models
- Behavioral pattern recognition
- Predictive risk scoring
- Intelligent automation rules
- Real-time decision making
- Continuous learning and model improvement
- Explainable AI decisions
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import hashlib
import math

from loguru import logger
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.openai_service import OpenAIService
from app.services.refund_service import RefundRequest, RefundReason, RefundType, RefundPriority
from app.services.banking_service import PaymentMethod, BankingGateway


class ModelType(str, Enum):
    """ML model types"""
    FRAUD_DETECTION = "fraud_detection"
    LEGITIMACY_PREDICTION = "legitimacy_prediction"
    RISK_SCORING = "risk_scoring"
    CHARGEBACK_PREDICTION = "chargeback_prediction"
    CUSTOMER_BEHAVIOR = "customer_behavior"


class PredictionConfidence(str, Enum):
    """Confidence levels for predictions"""
    VERY_LOW = "very_low"    # < 0.3
    LOW = "low"              # 0.3 - 0.5
    MEDIUM = "medium"        # 0.5 - 0.7
    HIGH = "high"            # 0.7 - 0.9
    VERY_HIGH = "very_high"  # > 0.9


@dataclass
class AIAnalysisResult:
    """AI analysis result structure"""
    analysis_id: str
    refund_id: str
    model_predictions: Dict[str, Any] = field(default_factory=dict)
    ai_recommendation: Dict[str, Any] = field(default_factory=dict)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    fraud_indicators: List[str] = field(default_factory=list)
    behavioral_patterns: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    explainability: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FeatureVector:
    """Feature vector for ML models"""
    # Transaction features
    amount: float
    original_amount: float
    amount_ratio: float
    
    # Temporal features
    transaction_age_hours: float
    refund_request_hour: int
    refund_request_day_of_week: int
    
    # Customer features
    customer_age_days: float
    previous_refunds_count: int
    previous_refunds_amount: float
    avg_transaction_amount: float
    refund_frequency_30d: int
    
    # Payment features
    payment_method_encoded: int
    gateway_encoded: int
    
    # Behavioral features
    immediate_refund: int  # 1 if requested within 1 hour
    round_amount: int      # 1 if amount is round number
    weekend_request: int   # 1 if requested on weekend
    
    # Risk indicators
    velocity_score: float
    location_risk_score: float
    device_risk_score: float
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for ML models"""
        return np.array([
            self.amount, self.original_amount, self.amount_ratio,
            self.transaction_age_hours, self.refund_request_hour, self.refund_request_day_of_week,
            self.customer_age_days, self.previous_refunds_count, self.previous_refunds_amount,
            self.avg_transaction_amount, self.refund_frequency_30d,
            self.payment_method_encoded, self.gateway_encoded,
            self.immediate_refund, self.round_amount, self.weekend_request,
            self.velocity_score, self.location_risk_score, self.device_risk_score
        ])


class RefundIntelligence:
    """
    AI-powered refund intelligence system
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.openai_service = OpenAIService()
        
        # Initialize ML models
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
        # Load or train models
        asyncio.create_task(self._initialize_models())
        
        # AI configuration
        self.ai_config = {
            "fraud_threshold": 0.7,
            "legitimacy_threshold": 0.6,
            "high_confidence_threshold": 0.8,
            "auto_approval_threshold": 0.9,
            "model_retrain_interval_days": 7,
            "feature_importance_update_interval_hours": 24
        }
        
        # Prediction cache
        self.prediction_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Analytics and metrics
        self.analytics = {
            "predictions_made": 0,
            "fraud_prevented": 0,
            "auto_approvals": 0,
            "model_accuracy": {},
            "processing_times": []
        }
    
    # ================================
    # MAIN AI ANALYSIS METHODS
    # ================================
    
    async def analyze_refund_request(
        self,
        refund_request: RefundRequest,
        original_transaction: Dict[str, Any],
        customer_profile: Dict[str, Any]
    ) -> AIAnalysisResult:
        """
        Comprehensive AI-powered refund analysis
        """
        analysis_id = f"ai_{uuid.uuid4().hex[:16]}"
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting AI analysis {analysis_id} for refund {refund_request.refund_id}")
            
            # Extract features for ML models
            features = await self._extract_features(
                refund_request, original_transaction, customer_profile
            )
            
            # Run ML model predictions
            ml_predictions = await self._run_ml_predictions(features)
            
            # Get GPT-4 analysis
            gpt_analysis = await self._get_gpt_analysis(
                refund_request, original_transaction, customer_profile, ml_predictions
            )
            
            # Combine predictions and generate final analysis
            risk_assessment = await self._generate_risk_assessment(ml_predictions, gpt_analysis)
            
            # Generate explainable AI insights
            explainability = await self._generate_explainability(
                features, ml_predictions, gpt_analysis
            )
            
            # Calculate processing time
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Create analysis result
            result = AIAnalysisResult(
                analysis_id=analysis_id,
                refund_id=refund_request.refund_id,
                model_predictions=ml_predictions,
                ai_recommendation=gpt_analysis,
                risk_assessment=risk_assessment,
                fraud_indicators=self._extract_fraud_indicators(ml_predictions, gpt_analysis),
                behavioral_patterns=self._extract_behavioral_patterns(features, ml_predictions),
                confidence_score=self._calculate_overall_confidence(ml_predictions, gpt_analysis),
                explainability=explainability,
                processing_time_ms=processing_time
            )
            
            # Update analytics
            self.analytics["predictions_made"] += 1
            self.analytics["processing_times"].append(processing_time)
            
            # Cache result
            await self._cache_analysis_result(analysis_id, result)
            
            logger.info(f"AI analysis {analysis_id} completed in {processing_time}ms")
            return result
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            
            # Return fallback analysis
            return AIAnalysisResult(
                analysis_id=analysis_id,
                refund_id=refund_request.refund_id,
                model_predictions={"error": str(e)},
                ai_recommendation={"recommendation": "manual_review", "confidence": 0.0},
                risk_assessment={"risk_score": 0.8, "risk_level": "high"},
                fraud_indicators=["ai_analysis_error"],
                confidence_score=0.0
            )
    
    async def _extract_features(
        self,
        refund_request: RefundRequest,
        original_transaction: Dict[str, Any],
        customer_profile: Dict[str, Any]
    ) -> FeatureVector:
        """
        Extract comprehensive features for ML models
        """
        now = datetime.utcnow()
        original_amount = float(original_transaction.get("amount", 0))
        refund_amount = float(refund_request.amount)
        
        # Get customer history
        customer_history = await self._get_customer_history(refund_request.customer_id)
        
        # Calculate temporal features
        transaction_created = original_transaction.get("created_at", now)
        transaction_age_hours = (now - transaction_created).total_seconds() / 3600
        
        # Calculate customer features
        customer_created = customer_profile.get("created_at", now - timedelta(days=365))
        customer_age_days = (now - customer_created).total_seconds() / 86400
        
        # Calculate behavioral features
        is_immediate = transaction_age_hours < 1
        is_round_amount = refund_amount == round(refund_amount) and refund_amount % 10 == 0
        is_weekend = now.weekday() >= 5
        
        # Calculate risk scores
        velocity_score = await self._calculate_velocity_score(refund_request.customer_id)
        location_risk = await self._calculate_location_risk_score(refund_request.customer_id, original_transaction)
        device_risk = await self._calculate_device_risk_score(refund_request.customer_id, original_transaction)
        
        # Encode categorical features
        payment_method_encoded = self._encode_payment_method(refund_request.payment_method)
        gateway_encoded = self._encode_gateway(refund_request.gateway)
        
        return FeatureVector(
            amount=refund_amount,
            original_amount=original_amount,
            amount_ratio=refund_amount / original_amount if original_amount > 0 else 0,
            transaction_age_hours=transaction_age_hours,
            refund_request_hour=now.hour,
            refund_request_day_of_week=now.weekday(),
            customer_age_days=customer_age_days,
            previous_refunds_count=len(customer_history.get("refunds", [])),
            previous_refunds_amount=sum(r.get("amount", 0) for r in customer_history.get("refunds", [])),
            avg_transaction_amount=customer_history.get("avg_transaction_amount", 0),
            refund_frequency_30d=len([r for r in customer_history.get("refunds", []) 
                                    if (now - r.get("created_at", now)).days <= 30]),
            payment_method_encoded=payment_method_encoded,
            gateway_encoded=gateway_encoded,
            immediate_refund=1 if is_immediate else 0,
            round_amount=1 if is_round_amount else 0,
            weekend_request=1 if is_weekend else 0,
            velocity_score=velocity_score,
            location_risk_score=location_risk,
            device_risk_score=device_risk
        )
    
    async def _run_ml_predictions(self, features: FeatureVector) -> Dict[str, Any]:
        """
        Run all ML model predictions
        """
        predictions = {}
        
        try:
            # Prepare feature array
            feature_array = features.to_array().reshape(1, -1)
            
            # Fraud detection prediction
            if ModelType.FRAUD_DETECTION in self.models:
                fraud_model = self.models[ModelType.FRAUD_DETECTION]
                fraud_scaler = self.scalers.get(ModelType.FRAUD_DETECTION)
                
                if fraud_scaler:
                    scaled_features = fraud_scaler.transform(feature_array)
                else:
                    scaled_features = feature_array
                
                fraud_prob = fraud_model.predict_proba(scaled_features)[0]
                predictions["fraud_detection"] = {
                    "fraud_probability": float(fraud_prob[1]) if len(fraud_prob) > 1 else 0.0,
                    "is_fraud": fraud_prob[1] > self.ai_config["fraud_threshold"] if len(fraud_prob) > 1 else False,
                    "confidence": float(max(fraud_prob))
                }
            
            # Legitimacy prediction
            if ModelType.LEGITIMACY_PREDICTION in self.models:
                legitimacy_model = self.models[ModelType.LEGITIMACY_PREDICTION]
                legitimacy_scaler = self.scalers.get(ModelType.LEGITIMACY_PREDICTION)
                
                if legitimacy_scaler:
                    scaled_features = legitimacy_scaler.transform(feature_array)
                else:
                    scaled_features = feature_array
                
                legitimacy_prob = legitimacy_model.predict_proba(scaled_features)[0]
                predictions["legitimacy_prediction"] = {
                    "legitimate_probability": float(legitimacy_prob[1]) if len(legitimacy_prob) > 1 else 0.5,
                    "is_legitimate": legitimacy_prob[1] > self.ai_config["legitimacy_threshold"] if len(legitimacy_prob) > 1 else False,
                    "confidence": float(max(legitimacy_prob))
                }
            
            # Risk scoring
            predictions["risk_scoring"] = await self._calculate_composite_risk_score(features)
            
            # Chargeback prediction
            predictions["chargeback_prediction"] = await self._predict_chargeback_risk(features)
            
            # Customer behavior analysis
            predictions["customer_behavior"] = await self._analyze_customer_behavior(features)
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            predictions["error"] = str(e)
        
        return predictions
    
    async def _get_gpt_analysis(
        self,
        refund_request: RefundRequest,
        original_transaction: Dict[str, Any],
        customer_profile: Dict[str, Any],
        ml_predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get GPT-4 powered refund analysis
        """
        try:
            # Prepare context for GPT-4
            context = {
                "refund_details": {
                    "amount": float(refund_request.amount),
                    "reason": refund_request.reason.value,
                    "type": refund_request.refund_type.value,
                    "priority": refund_request.priority.value,
                    "description": refund_request.description
                },
                "transaction_details": {
                    "original_amount": float(original_transaction.get("amount", 0)),
                    "payment_method": original_transaction.get("payment_method"),
                    "gateway": original_transaction.get("gateway"),
                    "transaction_age_hours": (
                        datetime.utcnow() - original_transaction.get("created_at", datetime.utcnow())
                    ).total_seconds() / 3600
                },
                "customer_profile": {
                    "customer_id": refund_request.customer_id,
                    "account_age_days": customer_profile.get("account_age_days", 0),
                    "risk_level": customer_profile.get("risk_level", "unknown"),
                    "previous_refunds": customer_profile.get("previous_refunds", 0)
                },
                "ml_insights": {
                    "fraud_probability": ml_predictions.get("fraud_detection", {}).get("fraud_probability", 0),
                    "legitimacy_score": ml_predictions.get("legitimacy_prediction", {}).get("legitimate_probability", 0.5),
                    "risk_score": ml_predictions.get("risk_scoring", {}).get("overall_risk", 0.5)
                }
            }
            
            # Create GPT-4 prompt
            prompt = self._create_gpt_analysis_prompt(context)
            
            # Get GPT-4 response
            response = await self.openai_service.chat_completion(
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                model="gpt-4",
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse response
            gpt_analysis = self._parse_gpt_response(response)
            
            return gpt_analysis
            
        except Exception as e:
            logger.error(f"GPT analysis failed: {e}")
            return {
                "recommendation": "manual_review",
                "confidence": 0.0,
                "reasoning": f"AI analysis failed: {str(e)}",
                "risk_factors": ["ai_unavailable"]
            }
    
    def _create_gpt_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """
        Create detailed prompt for GPT-4 analysis
        """
        return f"""
Analyze this refund request and provide a comprehensive assessment:

REFUND REQUEST:
- Amount: R$ {context['refund_details']['amount']:.2f}
- Reason: {context['refund_details']['reason']}
- Type: {context['refund_details']['type']}
- Priority: {context['refund_details']['priority']}
- Description: {context['refund_details'].get('description', 'N/A')}

ORIGINAL TRANSACTION:
- Original Amount: R$ {context['transaction_details']['original_amount']:.2f}
- Payment Method: {context['transaction_details']['payment_method']}
- Gateway: {context['transaction_details']['gateway']}
- Transaction Age: {context['transaction_details']['transaction_age_hours']:.1f} hours

CUSTOMER PROFILE:
- Customer ID: {context['customer_profile']['customer_id']}
- Account Age: {context['customer_profile']['account_age_days']} days
- Risk Level: {context['customer_profile']['risk_level']}
- Previous Refunds: {context['customer_profile']['previous_refunds']}

ML MODEL INSIGHTS:
- Fraud Probability: {context['ml_insights']['fraud_probability']:.2f}
- Legitimacy Score: {context['ml_insights']['legitimacy_score']:.2f}
- Risk Score: {context['ml_insights']['risk_score']:.2f}

Please provide:
1. Overall recommendation (approve/reject/manual_review)
2. Confidence level (0.0 to 1.0)
3. Detailed reasoning
4. Risk factors identified
5. Recommendations for processing
6. Any red flags or concerns

Format your response as JSON with the following structure:
{{
    "recommendation": "approve|reject|manual_review",
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation",
    "risk_factors": ["factor1", "factor2"],
    "processing_recommendations": ["rec1", "rec2"],
    "red_flags": ["flag1", "flag2"],
    "estimated_processing_time": minutes,
    "suggested_approval_level": "automatic|supervisor|manager"
}}
"""
    
    def _get_system_prompt(self) -> str:
        """
        Get system prompt for GPT-4
        """
        return """
You are an expert financial analyst specializing in refund fraud detection and risk assessment. 
You have extensive experience in e-commerce, payment processing, and customer behavior analysis.

Your role is to analyze refund requests and provide intelligent recommendations based on:
- Transaction patterns and anomalies
- Customer behavior and history
- Risk indicators and fraud patterns
- Business rules and compliance requirements
- Market context and industry best practices

Always provide balanced, data-driven analysis with clear reasoning. Consider both customer satisfaction and business risk protection.
Be conservative with high-risk scenarios but supportive of legitimate customer requests.
"""
    
    def _parse_gpt_response(self, response: str) -> Dict[str, Any]:
        """
        Parse GPT-4 response into structured format
        """
        try:
            # Try to parse as JSON
            if response.startswith("{") and response.endswith("}"):
                return json.loads(response)
            
            # Extract JSON from response if wrapped in text
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            
            # Fallback parsing
            return {
                "recommendation": "manual_review",
                "confidence": 0.5,
                "reasoning": response,
                "risk_factors": [],
                "processing_recommendations": ["Manual review recommended"],
                "red_flags": [],
                "estimated_processing_time": 60,
                "suggested_approval_level": "supervisor"
            }
            
        except Exception as e:
            logger.error(f"Failed to parse GPT response: {e}")
            return {
                "recommendation": "manual_review",
                "confidence": 0.0,
                "reasoning": "Failed to parse AI analysis",
                "error": str(e)
            }
    
    # ================================
    # ML MODEL MANAGEMENT
    # ================================
    
    async def _initialize_models(self):
        """
        Initialize or load ML models
        """
        try:
            logger.info("Initializing AI models...")
            
            # Try to load existing models
            model_loaded = await self._load_models()
            
            if not model_loaded:
                # Train new models if none exist
                await self._train_initial_models()
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            # Create dummy models for fallback
            await self._create_fallback_models()
    
    async def _load_models(self) -> bool:
        """
        Load pre-trained models from storage
        """
        try:
            # In production, this would load from persistent storage
            # For now, we'll create dummy models
            return False
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            return False
    
    async def _train_initial_models(self):
        """
        Train initial ML models with synthetic data
        """
        logger.info("Training initial ML models...")
        
        # Generate synthetic training data
        training_data = await self._generate_synthetic_training_data(1000)
        
        # Train fraud detection model
        await self._train_fraud_detection_model(training_data)
        
        # Train legitimacy prediction model
        await self._train_legitimacy_model(training_data)
        
        logger.info("Initial model training completed")
    
    async def _generate_synthetic_training_data(self, n_samples: int) -> pd.DataFrame:
        """
        Generate synthetic training data for model training
        """
        np.random.seed(42)
        
        data = []
        for _ in range(n_samples):
            # Generate synthetic features
            amount = np.random.exponential(100)  # Most refunds are small
            original_amount = amount * np.random.uniform(1, 3)  # Original is usually larger
            
            # Generate labels (legitimate vs fraudulent)
            # Simple rule-based labeling for synthetic data
            is_fraud = (
                amount > 5000 or  # Very high amounts
                amount / original_amount > 0.8 or  # Nearly full refund
                np.random.random() < 0.1  # 10% random fraud
            )
            
            feature_vector = FeatureVector(
                amount=amount,
                original_amount=original_amount,
                amount_ratio=amount / original_amount,
                transaction_age_hours=np.random.exponential(48),
                refund_request_hour=np.random.randint(0, 24),
                refund_request_day_of_week=np.random.randint(0, 7),
                customer_age_days=np.random.exponential(365),
                previous_refunds_count=np.random.poisson(1),
                previous_refunds_amount=np.random.exponential(200),
                avg_transaction_amount=np.random.exponential(150),
                refund_frequency_30d=np.random.poisson(0.5),
                payment_method_encoded=np.random.randint(0, 5),
                gateway_encoded=np.random.randint(0, 4),
                immediate_refund=np.random.choice([0, 1], p=[0.8, 0.2]),
                round_amount=np.random.choice([0, 1], p=[0.7, 0.3]),
                weekend_request=np.random.choice([0, 1], p=[0.7, 0.3]),
                velocity_score=np.random.beta(2, 5),
                location_risk_score=np.random.beta(2, 8),
                device_risk_score=np.random.beta(2, 8)
            )
            
            row = list(feature_vector.to_array())
            row.append(1 if is_fraud else 0)  # Add label
            data.append(row)
        
        # Create DataFrame
        columns = [
            'amount', 'original_amount', 'amount_ratio', 'transaction_age_hours',
            'refund_request_hour', 'refund_request_day_of_week', 'customer_age_days',
            'previous_refunds_count', 'previous_refunds_amount', 'avg_transaction_amount',
            'refund_frequency_30d', 'payment_method_encoded', 'gateway_encoded',
            'immediate_refund', 'round_amount', 'weekend_request',
            'velocity_score', 'location_risk_score', 'device_risk_score', 'is_fraud'
        ]
        
        return pd.DataFrame(data, columns=columns)
    
    async def _train_fraud_detection_model(self, training_data: pd.DataFrame):
        """
        Train fraud detection model
        """
        logger.info("Training fraud detection model...")
        
        # Prepare features and labels
        X = training_data.drop('is_fraud', axis=1)
        y = training_data['is_fraud']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        logger.info(f"Fraud detection model trained - Train: {train_score:.3f}, Test: {test_score:.3f}")
        
        # Store model and scaler
        self.models[ModelType.FRAUD_DETECTION] = model
        self.scalers[ModelType.FRAUD_DETECTION] = scaler
        self.analytics["model_accuracy"][ModelType.FRAUD_DETECTION] = test_score
        
        # Store feature importance
        self.feature_importance[ModelType.FRAUD_DETECTION] = {
            feature: importance for feature, importance 
            in zip(X.columns, model.feature_importances_)
        }
    
    async def _train_legitimacy_model(self, training_data: pd.DataFrame):
        """
        Train legitimacy prediction model
        """
        logger.info("Training legitimacy prediction model...")
        
        # Prepare features and labels (inverse of fraud)
        X = training_data.drop('is_fraud', axis=1)
        y = 1 - training_data['is_fraud']  # Legitimate is inverse of fraud
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        test_score = model.score(X_test_scaled, y_test)
        
        logger.info(f"Legitimacy model trained - Test accuracy: {test_score:.3f}")
        
        # Store model and scaler
        self.models[ModelType.LEGITIMACY_PREDICTION] = model
        self.scalers[ModelType.LEGITIMACY_PREDICTION] = scaler
        self.analytics["model_accuracy"][ModelType.LEGITIMACY_PREDICTION] = test_score
    
    async def _create_fallback_models(self):
        """
        Create simple fallback models if training fails
        """
        logger.warning("Creating fallback models...")
        
        # Create dummy models that return reasonable defaults
        class DummyModel:
            def predict_proba(self, X):
                # Return moderate risk predictions
                n_samples = X.shape[0] if hasattr(X, 'shape') else 1
                return np.array([[0.7, 0.3]] * n_samples)  # 30% fraud probability
            
            def predict(self, X):
                return np.array([0] * (X.shape[0] if hasattr(X, 'shape') else 1))
        
        self.models[ModelType.FRAUD_DETECTION] = DummyModel()
        self.models[ModelType.LEGITIMACY_PREDICTION] = DummyModel()
    
    # ================================
    # UTILITY METHODS
    # ================================
    
    async def _generate_risk_assessment(
        self,
        ml_predictions: Dict[str, Any],
        gpt_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive risk assessment
        """
        # Extract risk scores from different sources
        fraud_risk = ml_predictions.get("fraud_detection", {}).get("fraud_probability", 0.5)
        legitimacy_risk = 1.0 - ml_predictions.get("legitimacy_prediction", {}).get("legitimate_probability", 0.5)
        gpt_confidence = gpt_analysis.get("confidence", 0.5)
        
        # Calculate weighted risk score
        risk_score = (fraud_risk * 0.4 + legitimacy_risk * 0.4 + (1 - gpt_confidence) * 0.2)
        
        # Determine risk level
        if risk_score < 0.2:
            risk_level = "very_low"
        elif risk_score < 0.4:
            risk_level = "low"
        elif risk_score < 0.6:
            risk_level = "medium"
        elif risk_score < 0.8:
            risk_level = "high"
        else:
            risk_level = "very_high"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "components": {
                "fraud_risk": fraud_risk,
                "legitimacy_risk": legitimacy_risk,
                "ai_confidence_risk": 1 - gpt_confidence
            },
            "recommendation": self._get_risk_recommendation(risk_score)
        }
    
    def _get_risk_recommendation(self, risk_score: float) -> str:
        """
        Get recommendation based on risk score
        """
        if risk_score < 0.2:
            return "auto_approve"
        elif risk_score < 0.5:
            return "approve_with_monitoring"
        elif risk_score < 0.7:
            return "manual_review"
        else:
            return "reject_or_escalate"
    
    def _extract_fraud_indicators(
        self,
        ml_predictions: Dict[str, Any],
        gpt_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Extract fraud indicators from predictions
        """
        indicators = []
        
        # ML-based indicators
        fraud_prob = ml_predictions.get("fraud_detection", {}).get("fraud_probability", 0)
        if fraud_prob > 0.7:
            indicators.append("high_ml_fraud_score")
        
        # GPT-based indicators
        gpt_risks = gpt_analysis.get("risk_factors", [])
        indicators.extend(gpt_risks)
        
        return list(set(indicators))  # Remove duplicates
    
    def _extract_behavioral_patterns(
        self,
        features: FeatureVector,
        ml_predictions: Dict[str, Any]
    ) -> List[str]:
        """
        Extract behavioral patterns from features
        """
        patterns = []
        
        if features.immediate_refund:
            patterns.append("immediate_refund_request")
        
        if features.round_amount:
            patterns.append("round_amount_refund")
        
        if features.weekend_request:
            patterns.append("weekend_request")
        
        if features.refund_frequency_30d > 3:
            patterns.append("frequent_refunder")
        
        if features.amount_ratio > 0.9:
            patterns.append("near_full_refund")
        
        return patterns
    
    def _calculate_overall_confidence(
        self,
        ml_predictions: Dict[str, Any],
        gpt_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate overall confidence score
        """
        confidences = []
        
        # ML model confidences
        for prediction in ml_predictions.values():
            if isinstance(prediction, dict) and "confidence" in prediction:
                confidences.append(prediction["confidence"])
        
        # GPT confidence
        gpt_confidence = gpt_analysis.get("confidence", 0.5)
        confidences.append(gpt_confidence)
        
        # Return average confidence
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    # Additional helper methods would be implemented for production use
    async def _calculate_velocity_score(self, customer_id: int) -> float:
        """Calculate velocity-based risk score"""
        # Implementation would analyze customer transaction velocity
        return np.random.beta(2, 5)  # Placeholder
    
    async def _calculate_location_risk_score(self, customer_id: int, transaction: Dict[str, Any]) -> float:
        """Calculate location-based risk score"""
        # Implementation would analyze location patterns
        return np.random.beta(2, 8)  # Placeholder
    
    async def _calculate_device_risk_score(self, customer_id: int, transaction: Dict[str, Any]) -> float:
        """Calculate device-based risk score"""
        # Implementation would analyze device fingerprints
        return np.random.beta(2, 8)  # Placeholder
    
    def _encode_payment_method(self, payment_method: PaymentMethod) -> int:
        """Encode payment method for ML"""
        encoding = {
            PaymentMethod.PIX: 0,
            PaymentMethod.CREDIT_CARD: 1,
            PaymentMethod.DEBIT_CARD: 2,
            PaymentMethod.BOLETO: 3,
            PaymentMethod.BANK_TRANSFER: 4
        }
        return encoding.get(payment_method, 0)
    
    def _encode_gateway(self, gateway: BankingGateway) -> int:
        """Encode gateway for ML"""
        encoding = {
            BankingGateway.MERCADOPAGO: 0,
            BankingGateway.PAGSEGURO: 1,
            BankingGateway.ASAAS: 2,
            BankingGateway.PICPAY: 3
        }
        return encoding.get(gateway, 0)
    
    async def _get_customer_history(self, customer_id: int) -> Dict[str, Any]:
        """Get customer transaction history"""
        # Implementation would query database
        return {
            "refunds": [],
            "avg_transaction_amount": 150.0,
            "total_transactions": 10
        }
    
    async def get_intelligence_metrics(self) -> Dict[str, Any]:
        """Get AI intelligence performance metrics"""
        avg_processing_time = (
            sum(self.analytics["processing_times"]) / len(self.analytics["processing_times"])
            if self.analytics["processing_times"] else 0
        )
        
        return {
            "predictions_made": self.analytics["predictions_made"],
            "fraud_prevented": self.analytics["fraud_prevented"],
            "auto_approvals": self.analytics["auto_approvals"],
            "avg_processing_time_ms": avg_processing_time,
            "model_accuracy": self.analytics["model_accuracy"],
            "active_models": list(self.models.keys()),
            "feature_importance": self.feature_importance
        }