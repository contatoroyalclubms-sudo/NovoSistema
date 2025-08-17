#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
import sqlite3

def add_qr_code_field():
    db_path = "eventos.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("ALTER TABLE transacoes ADD COLUMN qr_code_ticket VARCHAR(100)")
        conn.commit()
        print("✅ Campo qr_code_ticket adicionado à tabela transacoes")
        
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("✅ Campo qr_code_ticket já existe na tabela transacoes")
        else:
            print(f"❌ Erro ao adicionar campo: {e}")
            raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_qr_code_field()
