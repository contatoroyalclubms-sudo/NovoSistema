
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Transaction, SplitRule, Participant

class SplitPaymentService:
    """
    Serviço de Split de Pagamentos
    Divide automaticamente pagamentos entre participantes
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_split_rule(
        self,
        evento_id: int,
        rules: List[Dict]
    ) -> SplitRule:
        """Cria regras de divisão para um evento"""
        split_rule = SplitRule(
            evento_id=evento_id,
            rules=rules,
            created_at=datetime.utcnow()
        )
        self.db.add(split_rule)
        self.db.commit()
        return split_rule
    
    async def process_split_payment(
        self,
        transaction_id: int,
        amount: Decimal
    ) -> List[Transaction]:
        """Processa divisão de pagamento"""
        transaction = self.db.query(Transaction).filter_by(id=transaction_id).first()
        split_rule = self.db.query(SplitRule).filter_by(evento_id=transaction.evento_id).first()
        
        if not split_rule:
            return [transaction]
        
        split_transactions = []
        for rule in split_rule.rules:
            participant_amount = amount * Decimal(str(rule['percentage'] / 100))
            
            split_tx = Transaction(
                evento_id=transaction.evento_id,
                participant_id=rule['participant_id'],
                amount=participant_amount,
                type='split_payment',
                parent_transaction_id=transaction_id,
                status='pending',
                created_at=datetime.utcnow()
            )
            self.db.add(split_tx)
            split_transactions.append(split_tx)
        
        self.db.commit()
        return split_transactions
    
    async def process_refund(
        self,
        transaction_id: int,
        reason: str
    ) -> Transaction:
        """Processa reembolso automático"""
        original = self.db.query(Transaction).filter_by(id=transaction_id).first()
        
        refund = Transaction(
            evento_id=original.evento_id,
            user_id=original.user_id,
            amount=-original.amount,
            type='refund',
            parent_transaction_id=transaction_id,
            metadata={'reason': reason},
            status='completed',
            created_at=datetime.utcnow()
        )
        self.db.add(refund)
        self.db.commit()
        
        # Notificar usuário
        await self.notify_refund(original.user_id, refund)
        
        return refund
    
    async def notify_refund(self, user_id: int, refund: Transaction):
        """Notifica usuário sobre reembolso"""
        # Implementação de notificação via email/SMS/WhatsApp
        pass

# Adicionar ao router de transações
from fastapi import APIRouter, Depends
from app.services.split_payment import SplitPaymentService

router = APIRouter()

@router.post("/split-rules/{evento_id}")
async def create_split_rules(
    evento_id: int,
    rules: List[Dict],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = SplitPaymentService(db)
    return await service.create_split_rule(evento_id, rules)

@router.post("/process-split/{transaction_id}")
async def process_split(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    service = SplitPaymentService(db)
    transaction = db.query(Transaction).filter_by(id=transaction_id).first()
    return await service.process_split_payment(transaction_id, transaction.amount)

@router.post("/refund/{transaction_id}")
async def process_refund(
    transaction_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = SplitPaymentService(db)
    return await service.process_refund(transaction_id, reason)
