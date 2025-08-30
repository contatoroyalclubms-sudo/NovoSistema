#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models import Base

def create_meep_client_tables():
    """Criar tabelas para o sistema de clientes MEEP"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas de clientes MEEP criadas com sucesso!")
        print("- ClientCategory")
        print("- MeepClient") 
        print("- ClientBlockHistory")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")

if __name__ == "__main__":
    create_meep_client_tables()
