#!/usr/bin/env python3
"""
Teste rápido do servidor FastAPI
"""
import sys
import os

# Adicionar diretório atual ao path
sys.path.insert(0, os.getcwd())

try:
    print("🔄 Carregando FastAPI...")
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from dotenv import load_dotenv
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    app = FastAPI(
        title="Sistema de Gestão Universal",
        description="API para gestão de eventos e listas",
        version="2.0.0"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Em produção, especificar domínios
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Rota de teste
    @app.get("/")
    async def root():
        return {
            "message": "Sistema de Gestão Universal - API Online",
            "status": "ok",
            "version": "2.0.0"
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "message": "API funcionando perfeitamente!"}
    
    print("✅ FastAPI carregado com sucesso!")
    print("🌐 Iniciando servidor...")
    
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info",
            reload=True
        )
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("💡 Execute: pip install fastapi uvicorn python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)
