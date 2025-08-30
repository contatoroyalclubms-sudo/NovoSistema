"""
Ultra-Expert Payment System
Sistema de Pagamentos Avançado Multi-Gateway
"""

import asyncio
import hashlib
import hmac
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import httpx
import qrcode
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PIX = "pix"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    BOLETO = "boleto"

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    DECLINED = "declined"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    EXPIRED = "expired"

class PaymentGateway(Enum):
    STRIPE = "stripe"
    MERCADOPAGO = "mercadopago"
    PAGSEGURO = "pagseguro"
    CIELO = "cielo"
    PAYPAL = "paypal"
    PIX_BACEN = "pix_bacen"

@dataclass
class PaymentRequest:
    amount: Decimal
    currency: str
    method: PaymentMethod
    customer_data: Dict[str, Any]
    event_id: str
    ticket_data: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class PaymentResponse:
    transaction_id: str
    status: PaymentStatus
    gateway: PaymentGateway
    payment_url: Optional[str]
    qr_code: Optional[str]
    expires_at: Optional[datetime]
    gateway_response: Dict[str, Any]

@dataclass
class RefundRequest:
    transaction_id: str
    amount: Optional[Decimal]
    reason: str
    metadata: Dict[str, Any]

class FraudDetector:
    """Sistema de detecção de fraude"""
    
    def __init__(self):
        self.risk_rules = [
            self._check_velocity_fraud,
            self._check_geo_anomaly,
            self._check_amount_anomaly,
            self._check_payment_pattern,
            self._check_blacklist
        ]
    
    async def analyze_transaction(self, payment_request: PaymentRequest, user_history: List[Dict]) -> Dict[str, Any]:
        """Analisa transação para detecção de fraude"""
        risk_score = 0.0
        flags = []
        
        for rule in self.risk_rules:
            score, rule_flags = await rule(payment_request, user_history)
            risk_score += score
            flags.extend(rule_flags)
        
        # Normalizar score
        risk_score = min(risk_score, 1.0)
        
        return {
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
            "flags": flags,
            "recommendation": self._get_recommendation(risk_score),
            "requires_manual_review": risk_score > 0.7
        }
    
    async def _check_velocity_fraud(self, request: PaymentRequest, history: List[Dict]) -> tuple:
        """Verifica fraude por velocidade de transações"""
        recent_transactions = [
            t for t in history 
            if datetime.fromisoformat(t.get('created_at', '2020-01-01'))
            > datetime.now() - timedelta(hours=1)
        ]
        
        if len(recent_transactions) > 5:
            return 0.4, ["high_velocity"]
        elif len(recent_transactions) > 3:
            return 0.2, ["moderate_velocity"]
        
        return 0.0, []
    
    async def _check_geo_anomaly(self, request: PaymentRequest, history: List[Dict]) -> tuple:
        """Verifica anomalias geográficas"""
        # Simulação - integrar com serviço de geo-IP real
        current_country = request.customer_data.get('country', 'BR')
        
        if history:
            last_countries = [t.get('country', 'BR') for t in history[-5:]]
            if current_country not in last_countries:
                return 0.3, ["geo_anomaly"]
        
        return 0.0, []
    
    async def _check_amount_anomaly(self, request: PaymentRequest, history: List[Dict]) -> tuple:
        """Verifica anomalias no valor"""
        if not history:
            return 0.0, []
        
        avg_amount = sum(Decimal(str(t.get('amount', 0))) for t in history) / len(history)
        
        if request.amount > avg_amount * 5:
            return 0.5, ["high_amount"]
        elif request.amount > avg_amount * 3:
            return 0.2, ["elevated_amount"]
        
        return 0.0, []
    
    async def _check_payment_pattern(self, request: PaymentRequest, history: List[Dict]) -> tuple:
        """Verifica padrões suspeitos de pagamento"""
        # Múltiplos cartões diferentes
        card_hashes = set(t.get('card_hash') for t in history if t.get('card_hash'))
        if len(card_hashes) > 3:
            return 0.3, ["multiple_cards"]
        
        return 0.0, []
    
    async def _check_blacklist(self, request: PaymentRequest, history: List[Dict]) -> tuple:
        """Verifica listas negras"""
        # Implementar verificação em blacklists reais
        suspicious_emails = ['test@fraud.com', 'scammer@fake.com']
        
        if request.customer_data.get('email') in suspicious_emails:
            return 0.9, ["blacklisted_email"]
        
        return 0.0, []
    
    def _get_risk_level(self, score: float) -> str:
        """Converte score em nível de risco"""
        if score >= 0.8:
            return "HIGH"
        elif score >= 0.5:
            return "MEDIUM"
        elif score >= 0.2:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _get_recommendation(self, score: float) -> str:
        """Retorna recomendação baseada no score"""
        if score >= 0.8:
            return "BLOCK_TRANSACTION"
        elif score >= 0.6:
            return "MANUAL_REVIEW"
        elif score >= 0.3:
            return "ADDITIONAL_VERIFICATION"
        else:
            return "APPROVE"

class PixGateway:
    """Gateway PIX Brasileiro"""
    
    def __init__(self, api_key: str, webhook_url: str):
        self.api_key = api_key
        self.webhook_url = webhook_url
        self.base_url = "https://api.pix-simulator.com"  # Simulação
    
    async def create_pix_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Cria pagamento PIX"""
        try:
            pix_key = f"evento-{request.event_id}-{uuid.uuid4().hex[:8]}"
            
            # Gerar QR Code PIX
            pix_payload = self._generate_pix_payload(
                amount=request.amount,
                description=f"Ingresso Evento {request.event_id}",
                pix_key=pix_key
            )
            
            qr_code_b64 = self._generate_qr_code(pix_payload)
            
            transaction_id = f"pix_{uuid.uuid4().hex}"
            
            return PaymentResponse(
                transaction_id=transaction_id,
                status=PaymentStatus.PENDING,
                gateway=PaymentGateway.PIX_BACEN,
                payment_url=f"pix://qr/{pix_payload}",
                qr_code=qr_code_b64,
                expires_at=datetime.now() + timedelta(minutes=30),
                gateway_response={
                    "pix_key": pix_key,
                    "payload": pix_payload,
                    "expires_in": 1800
                }
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar pagamento PIX: {e}")
            raise
    
    def _generate_pix_payload(self, amount: Decimal, description: str, pix_key: str) -> str:
        """Gera payload PIX EMV"""
        # Implementação simplificada - usar biblioteca oficial PIX
        payload_data = {
            "version": "01",
            "merchant_account": pix_key,
            "merchant_name": "Sistema de Eventos",
            "merchant_city": "SAO PAULO",
            "transaction_amount": str(amount),
            "currency": "986",  # BRL
            "country_code": "BR",
            "additional_info": description
        }
        
        # Simular payload EMV
        return f"00020101021226580014BR.GOV.BCB.PIX{pix_key}5204000053039865404{amount}5925Sistema de Eventos6009SAO PAULO62070503***6304"
    
    def _generate_qr_code(self, payload: str) -> str:
        """Gera QR Code em base64"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(payload)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()

class CryptoGateway:
    """Gateway para Criptomoedas"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.supported_currencies = ["BTC", "ETH", "USDT", "USDC"]
    
    async def create_crypto_payment(self, request: PaymentRequest, crypto_currency: str) -> PaymentResponse:
        """Cria pagamento em criptomoeda"""
        try:
            if crypto_currency not in self.supported_currencies:
                raise ValueError(f"Criptomoeda {crypto_currency} não suportada")
            
            # Simular conversão de preço
            crypto_amount = await self._convert_to_crypto(request.amount, crypto_currency)
            
            # Gerar endereço da wallet
            wallet_address = self._generate_wallet_address(crypto_currency)
            
            transaction_id = f"crypto_{crypto_currency.lower()}_{uuid.uuid4().hex}"
            
            return PaymentResponse(
                transaction_id=transaction_id,
                status=PaymentStatus.PENDING,
                gateway=PaymentGateway.PAYPAL,  # Usar gateway genérico
                payment_url=f"crypto://{crypto_currency}/{wallet_address}",
                qr_code=self._generate_crypto_qr(wallet_address, crypto_amount, crypto_currency),
                expires_at=datetime.now() + timedelta(hours=2),
                gateway_response={
                    "wallet_address": wallet_address,
                    "crypto_currency": crypto_currency,
                    "crypto_amount": str(crypto_amount),
                    "fiat_amount": str(request.amount),
                    "exchange_rate": await self._get_exchange_rate(crypto_currency)
                }
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar pagamento crypto: {e}")
            raise
    
    async def _convert_to_crypto(self, fiat_amount: Decimal, crypto_currency: str) -> Decimal:
        """Converte valor fiat para crypto"""
        # Simulação - integrar com API real de cotações
        exchange_rates = {
            "BTC": Decimal("0.000015"),  # 1 BRL = 0.000015 BTC
            "ETH": Decimal("0.0003"),    # 1 BRL = 0.0003 ETH
            "USDT": Decimal("0.18"),     # 1 BRL = 0.18 USDT
            "USDC": Decimal("0.18")      # 1 BRL = 0.18 USDC
        }
        
        return fiat_amount * exchange_rates.get(crypto_currency, Decimal("0.18"))
    
    async def _get_exchange_rate(self, crypto_currency: str) -> Dict[str, Any]:
        """Obtém taxa de câmbio atual"""
        return {
            "currency": crypto_currency,
            "rate_brl": "0.18",
            "last_update": datetime.now().isoformat(),
            "source": "crypto_api_simulator"
        }
    
    def _generate_wallet_address(self, crypto_currency: str) -> str:
        """Gera endereço de wallet simulado"""
        prefixes = {
            "BTC": "1",
            "ETH": "0x",
            "USDT": "0x",
            "USDC": "0x"
        }
        
        prefix = prefixes.get(crypto_currency, "0x")
        return f"{prefix}{uuid.uuid4().hex[:32]}"
    
    def _generate_crypto_qr(self, address: str, amount: Decimal, currency: str) -> str:
        """Gera QR Code para pagamento crypto"""
        crypto_uri = f"{currency.lower()}:{address}?amount={amount}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(crypto_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()

class UltraExpertPayments:
    """Sistema de Pagamentos Ultra-Expert"""
    
    def __init__(self):
        self.fraud_detector = FraudDetector()
        self.gateways = {
            PaymentGateway.PIX_BACEN: PixGateway("pix-api-key", "https://webhook.com/pix"),
            PaymentGateway.PAYPAL: CryptoGateway("crypto-api-key")
        }
        self.transactions = {}  # Cache de transações - usar BD real
        self.webhooks = []
    
    async def process_payment(self, request: PaymentRequest, user_history: List[Dict] = None) -> Dict[str, Any]:
        """Processa pagamento com análise de fraude"""
        try:
            # Análise de fraude
            fraud_analysis = await self.fraud_detector.analyze_transaction(
                request, user_history or []
            )
            
            if fraud_analysis["recommendation"] == "BLOCK_TRANSACTION":
                return {
                    "status": "blocked",
                    "reason": "Transaction blocked by fraud detection",
                    "fraud_analysis": fraud_analysis
                }
            
            # Processar pagamento baseado no método
            if request.method == PaymentMethod.PIX:
                response = await self._process_pix_payment(request)
            elif request.method == PaymentMethod.CRYPTOCURRENCY:
                crypto_currency = request.metadata.get("crypto_currency", "BTC")
                response = await self._process_crypto_payment(request, crypto_currency)
            elif request.method == PaymentMethod.CREDIT_CARD:
                response = await self._process_card_payment(request, "credit")
            elif request.method == PaymentMethod.BOLETO:
                response = await self._process_boleto_payment(request)
            else:
                raise ValueError(f"Método de pagamento {request.method} não implementado")
            
            # Salvar transação
            self.transactions[response.transaction_id] = {
                "request": asdict(request),
                "response": asdict(response),
                "fraud_analysis": fraud_analysis,
                "created_at": datetime.now().isoformat(),
                "status_history": [
                    {"status": response.status.value, "timestamp": datetime.now().isoformat()}
                ]
            }
            
            # Agendar verificação de expiração
            if response.expires_at:
                asyncio.create_task(self._schedule_expiration_check(response.transaction_id, response.expires_at))
            
            return {
                "status": "success",
                "transaction_id": response.transaction_id,
                "payment_response": asdict(response),
                "fraud_analysis": fraud_analysis
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar pagamento: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fraud_analysis": fraud_analysis if 'fraud_analysis' in locals() else None
            }
    
    async def _process_pix_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Processa pagamento PIX"""
        gateway = self.gateways[PaymentGateway.PIX_BACEN]
        return await gateway.create_pix_payment(request)
    
    async def _process_crypto_payment(self, request: PaymentRequest, crypto_currency: str) -> PaymentResponse:
        """Processa pagamento em criptomoeda"""
        gateway = self.gateways[PaymentGateway.PAYPAL]  # Usar gateway crypto
        return await gateway.create_crypto_payment(request, crypto_currency)
    
    async def _process_card_payment(self, request: PaymentRequest, card_type: str) -> PaymentResponse:
        """Processa pagamento com cartão"""
        # Implementar integração com Stripe, Cielo, etc.
        transaction_id = f"card_{card_type}_{uuid.uuid4().hex}"
        
        # Simular processamento
        await asyncio.sleep(0.5)
        
        return PaymentResponse(
            transaction_id=transaction_id,
            status=PaymentStatus.APPROVED,  # Simulado como aprovado
            gateway=PaymentGateway.STRIPE,
            payment_url=None,
            qr_code=None,
            expires_at=None,
            gateway_response={
                "card_type": card_type,
                "last_4_digits": "1234",
                "brand": "visa",
                "authorization_code": "AUTH123456"
            }
        )
    
    async def _process_boleto_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Processa pagamento via boleto"""
        transaction_id = f"boleto_{uuid.uuid4().hex}"
        
        # Gerar linha digitável do boleto
        linha_digitavel = self._generate_boleto_line(request)
        
        return PaymentResponse(
            transaction_id=transaction_id,
            status=PaymentStatus.PENDING,
            gateway=PaymentGateway.PAGSEGURO,
            payment_url=f"https://boleto.pagseguro.com/{transaction_id}",
            qr_code=self._generate_boleto_qr(linha_digitavel),
            expires_at=datetime.now() + timedelta(days=3),
            gateway_response={
                "linha_digitavel": linha_digitavel,
                "codigo_barras": f"001902{uuid.uuid4().hex[:20]}",
                "vencimento": (datetime.now() + timedelta(days=3)).strftime("%d/%m/%Y")
            }
        )
    
    def _generate_boleto_line(self, request: PaymentRequest) -> str:
        """Gera linha digitável do boleto"""
        # Implementação simplificada
        banco = "001"  # Banco do Brasil
        moeda = "9"
        dv = "2"
        vencimento = "1234"  # Dias desde 07/10/1997
        valor = f"{int(request.amount * 100):010d}"
        
        return f"{banco}{moeda}.{uuid.uuid4().hex[:5]}{dv} {uuid.uuid4().hex[:5]}.{uuid.uuid4().hex[:6]} {uuid.uuid4().hex[:5]}.{uuid.uuid4().hex[:6]} {dv} {vencimento}{valor}"
    
    def _generate_boleto_qr(self, linha_digitavel: str) -> str:
        """Gera QR Code do boleto"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(linha_digitavel)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    async def process_refund(self, refund_request: RefundRequest) -> Dict[str, Any]:
        """Processa reembolso"""
        try:
            transaction = self.transactions.get(refund_request.transaction_id)
            if not transaction:
                return {"status": "error", "error": "Transaction not found"}
            
            # Verificar se reembolso é possível
            current_status = transaction["response"]["status"]
            if current_status != "approved":
                return {"status": "error", "error": "Cannot refund non-approved transaction"}
            
            refund_amount = refund_request.amount or Decimal(str(transaction["request"]["amount"]))
            
            # Processar reembolso baseado no gateway
            gateway = PaymentGateway(transaction["response"]["gateway"])
            
            refund_id = f"refund_{uuid.uuid4().hex}"
            
            # Simular processamento do reembolso
            await asyncio.sleep(1)
            
            # Atualizar transação
            transaction["status_history"].append({
                "status": "refunded",
                "timestamp": datetime.now().isoformat(),
                "refund_id": refund_id,
                "refund_amount": str(refund_amount)
            })
            
            transaction["response"]["status"] = "refunded"
            
            return {
                "status": "success",
                "refund_id": refund_id,
                "refund_amount": str(refund_amount),
                "estimated_processing_days": 5
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar reembolso: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Obtém status da transação"""
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            return {"status": "not_found"}
        
        return {
            "transaction_id": transaction_id,
            "status": transaction["response"]["status"],
            "created_at": transaction["created_at"],
            "amount": transaction["request"]["amount"],
            "method": transaction["request"]["method"],
            "gateway": transaction["response"]["gateway"],
            "fraud_score": transaction["fraud_analysis"]["risk_score"],
            "status_history": transaction["status_history"]
        }
    
    async def _schedule_expiration_check(self, transaction_id: str, expires_at: datetime):
        """Agenda verificação de expiração"""
        wait_time = (expires_at - datetime.now()).total_seconds()
        if wait_time > 0:
            await asyncio.sleep(wait_time)
            await self._expire_transaction(transaction_id)
    
    async def _expire_transaction(self, transaction_id: str):
        """Expira transação pendente"""
        if transaction_id in self.transactions:
            transaction = self.transactions[transaction_id]
            if transaction["response"]["status"] == "pending":
                transaction["response"]["status"] = "expired"
                transaction["status_history"].append({
                    "status": "expired",
                    "timestamp": datetime.now().isoformat(),
                    "reason": "automatic_expiration"
                })
                logger.info(f"Transação {transaction_id} expirada automaticamente")
    
    async def generate_financial_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Gera relatório financeiro"""
        transactions_in_period = [
            t for t in self.transactions.values()
            if start_date <= datetime.fromisoformat(t["created_at"]) <= end_date
        ]
        
        total_amount = sum(
            Decimal(str(t["request"]["amount"]))
            for t in transactions_in_period
            if t["response"]["status"] in ["approved", "refunded"]
        )
        
        refunded_amount = sum(
            Decimal(str(h.get("refund_amount", 0)))
            for t in transactions_in_period
            for h in t["status_history"]
            if h["status"] == "refunded"
        )
        
        method_breakdown = {}
        for t in transactions_in_period:
            method = t["request"]["method"]
            if method not in method_breakdown:
                method_breakdown[method] = {"count": 0, "amount": Decimal("0")}
            
            method_breakdown[method]["count"] += 1
            method_breakdown[method]["amount"] += Decimal(str(t["request"]["amount"]))
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_transactions": len(transactions_in_period),
                "total_amount": str(total_amount),
                "refunded_amount": str(refunded_amount),
                "net_amount": str(total_amount - refunded_amount)
            },
            "method_breakdown": {
                k: {"count": v["count"], "amount": str(v["amount"])}
                for k, v in method_breakdown.items()
            },
            "fraud_stats": {
                "total_flagged": len([
                    t for t in transactions_in_period
                    if t["fraud_analysis"]["risk_level"] in ["HIGH", "MEDIUM"]
                ]),
                "blocked_transactions": len([
                    t for t in transactions_in_period
                    if t.get("status") == "blocked"
                ])
            }
        }

# Instância global
ultra_expert_payments = UltraExpertPayments()