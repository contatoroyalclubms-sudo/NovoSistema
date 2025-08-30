#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models import Base

def create_tablet_tables():
    """Criar tabelas para o sistema de tablets"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas de tablets criadas com sucesso!")
        print("- Tablet")
        print("- TabletLog") 
        print("- ConfiguracaoMeep")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")

if __name__ == "__main__":
    create_tablet_tables()
