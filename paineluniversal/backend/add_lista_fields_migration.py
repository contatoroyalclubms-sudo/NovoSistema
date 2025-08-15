#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database import settings

def add_lista_fields():
    """Add new fields to listas table"""
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE listas ADD COLUMN descricao TEXT"))
            print("✅ Added descricao column to listas table")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️ descricao column already exists")
            else:
                print(f"❌ Error adding descricao column: {e}")
        
        try:
            conn.execute(text("ALTER TABLE listas ADD COLUMN codigo_cupom VARCHAR(50)"))
            print("✅ Added codigo_cupom column to listas table")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️ codigo_cupom column already exists")
            else:
                print(f"❌ Error adding codigo_cupom column: {e}")
        
        try:
            conn.execute(text("ALTER TABLE listas ADD COLUMN desconto_percentual NUMERIC(5,2) DEFAULT 0"))
            print("✅ Added desconto_percentual column to listas table")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️ desconto_percentual column already exists")
            else:
                print(f"❌ Error adding desconto_percentual column: {e}")
        
        conn.commit()
        print("✅ Lista fields migration completed successfully!")

if __name__ == "__main__":
    add_lista_fields()
