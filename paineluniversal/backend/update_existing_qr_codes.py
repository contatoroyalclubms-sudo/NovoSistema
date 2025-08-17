#!/usr/bin/env python3

import sys
import os
import uuid
import sqlite3

def update_existing_qr_codes():
    db_path = "eventos.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, evento_id FROM transacoes 
            WHERE qr_code_ticket IS NULL OR qr_code_ticket = ''
        """)
        
        transacoes = cursor.fetchall()
        
        for transacao in transacoes:
            qr_code = f"TICKET-{str(uuid.uuid4())[:8].upper()}-{transacao[1]}"
            
            cursor.execute("""
                UPDATE transacoes 
                SET qr_code_ticket = ? 
                WHERE id = ?
            """, (qr_code, transacao[0]))
        
        conn.commit()
        print(f"✅ QR codes gerados para {len(transacoes)} transações")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar QR codes: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_existing_qr_codes()
