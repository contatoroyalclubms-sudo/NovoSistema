#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from datetime import datetime, date
from app.database import settings
from app.models import (
    MovimentacaoFinanceira, CaixaEvento, Evento, Usuario,
    TipoMovimentacaoFinanceira, StatusMovimentacaoFinanceira
)

def seed_financeiro_data():
    """Seed financial data for testing"""
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        evento = db.query(Evento).first()
        if not evento:
            print("❌ Nenhum evento encontrado. Execute setup_test_events.py primeiro.")
            return
        
        usuario = db.query(Usuario).filter(Usuario.tipo == "admin").first()
        if not usuario:
            print("❌ Nenhum usuário admin encontrado. Execute setup_test_users.py primeiro.")
            return
        
        print(f"📊 Criando dados financeiros para evento: {evento.nome}")
        
        movimentacoes = [
            {
                "evento_id": evento.id,
                "tipo": TipoMovimentacaoFinanceira.ENTRADA,
                "categoria": "Patrocínio",
                "descricao": "Patrocínio Empresa ABC",
                "valor": Decimal("5000.00"),
                "status": StatusMovimentacaoFinanceira.APROVADA,
                "usuario_responsavel_id": usuario.id,
                "numero_documento": "PAT-001",
                "metodo_pagamento": "transferencia"
            },
            {
                "evento_id": evento.id,
                "tipo": TipoMovimentacaoFinanceira.SAIDA,
                "categoria": "Segurança",
                "descricao": "Contratação equipe de segurança",
                "valor": Decimal("1200.00"),
                "status": StatusMovimentacaoFinanceira.APROVADA,
                "usuario_responsavel_id": usuario.id,
                "numero_documento": "SEG-001",
                "metodo_pagamento": "pix"
            },
            {
                "evento_id": evento.id,
                "tipo": TipoMovimentacaoFinanceira.SAIDA,
                "categoria": "Bebidas",
                "descricao": "Compra de bebidas para o evento",
                "valor": Decimal("800.00"),
                "status": StatusMovimentacaoFinanceira.APROVADA,
                "usuario_responsavel_id": usuario.id,
                "numero_documento": "BEB-001",
                "metodo_pagamento": "cartao_credito"
            },
            {
                "evento_id": evento.id,
                "tipo": TipoMovimentacaoFinanceira.ENTRADA,
                "categoria": "Venda Antecipada",
                "descricao": "Vendas online antecipadas",
                "valor": Decimal("2500.00"),
                "status": StatusMovimentacaoFinanceira.APROVADA,
                "usuario_responsavel_id": usuario.id,
                "numero_documento": "VEN-001",
                "metodo_pagamento": "pix"
            },
            {
                "evento_id": evento.id,
                "tipo": TipoMovimentacaoFinanceira.SAIDA,
                "categoria": "Marketing",
                "descricao": "Impulsionamento redes sociais",
                "valor": Decimal("300.00"),
                "status": StatusMovimentacaoFinanceira.PENDENTE,
                "usuario_responsavel_id": usuario.id,
                "numero_documento": "MKT-001",
                "metodo_pagamento": "cartao_credito"
            },
            {
                "evento_id": evento.id,
                "tipo": TipoMovimentacaoFinanceira.REPASSE_PROMOTER,
                "categoria": "Comissão",
                "descricao": "Comissão promoter João",
                "valor": Decimal("150.00"),
                "status": StatusMovimentacaoFinanceira.APROVADA,
                "usuario_responsavel_id": usuario.id,
                "promoter_id": usuario.id,
                "numero_documento": "COM-001",
                "metodo_pagamento": "pix"
            }
        ]
        
        for mov_data in movimentacoes:
            movimentacao = MovimentacaoFinanceira(**mov_data)
            db.add(movimentacao)
        
        caixa = CaixaEvento(
            evento_id=evento.id,
            saldo_inicial=Decimal("500.00"),
            usuario_abertura_id=usuario.id,
            observacoes_abertura="Caixa aberto para o evento de teste"
        )
        db.add(caixa)
        
        db.commit()
        
        print("✅ Dados financeiros criados com sucesso!")
        print("📈 Movimentações criadas:")
        for mov in movimentacoes:
            print(f"  - {mov['tipo'].value}: {mov['categoria']} - R$ {mov['valor']}")
        print(f"💰 Caixa aberto com saldo inicial: R$ {caixa.saldo_inicial}")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados financeiros: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_financeiro_data()
