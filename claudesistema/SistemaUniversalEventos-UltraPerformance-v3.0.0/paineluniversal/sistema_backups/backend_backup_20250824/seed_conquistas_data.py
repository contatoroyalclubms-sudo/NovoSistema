#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import Conquista, TipoConquista, NivelBadge

def seed_conquistas():
    """Criar conquistas padrão do sistema"""
    db = next(get_db())
    
    conquistas_padrao = [
        {
            "nome": "Primeiro Passo",
            "descricao": "Realize sua primeira venda",
            "tipo": TipoConquista.VENDAS,
            "criterio_valor": 1,
            "badge_nivel": NivelBadge.BRONZE,
            "icone": "🎯"
        },
        {
            "nome": "Vendedor Bronze",
            "descricao": "Realize 10 vendas",
            "tipo": TipoConquista.VENDAS,
            "criterio_valor": 10,
            "badge_nivel": NivelBadge.BRONZE,
            "icone": "🥉"
        },
        {
            "nome": "Vendedor Prata",
            "descricao": "Realize 50 vendas",
            "tipo": TipoConquista.VENDAS,
            "criterio_valor": 50,
            "badge_nivel": NivelBadge.PRATA,
            "icone": "🥈"
        },
        {
            "nome": "Vendedor Ouro",
            "descricao": "Realize 100 vendas",
            "tipo": TipoConquista.VENDAS,
            "criterio_valor": 100,
            "badge_nivel": NivelBadge.OURO,
            "icone": "🥇"
        },
        {
            "nome": "Super Vendedor",
            "descricao": "Realize 500 vendas",
            "tipo": TipoConquista.VENDAS,
            "criterio_valor": 500,
            "badge_nivel": NivelBadge.DIAMANTE,
            "icone": "💎"
        },
        {
            "nome": "Presença Garantida",
            "descricao": "Mantenha 80% de presença",
            "tipo": TipoConquista.PRESENCA,
            "criterio_valor": 80,
            "badge_nivel": NivelBadge.PRATA,
            "icone": "✅"
        },
        {
            "nome": "Presença VIP",
            "descricao": "Mantenha 90% de presença",
            "tipo": TipoConquista.PRESENCA,
            "criterio_valor": 90,
            "badge_nivel": NivelBadge.OURO,
            "icone": "⭐"
        },
        {
            "nome": "Lenda dos Promoters",
            "descricao": "1000+ vendas e múltiplas conquistas",
            "tipo": TipoConquista.ESPECIAL,
            "criterio_valor": 1000,
            "badge_nivel": NivelBadge.LENDA,
            "icone": "👑"
        }
    ]
    
    for conquista_data in conquistas_padrao:
        existing = db.query(Conquista).filter(
            Conquista.nome == conquista_data["nome"]
        ).first()
        
        if not existing:
            conquista = Conquista(**conquista_data)
            db.add(conquista)
    
    db.commit()
    print("✅ Conquistas padrão criadas com sucesso!")

if __name__ == "__main__":
    seed_conquistas()
