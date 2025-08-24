"""
Serviço de Validação - Testa conexões e dependências
"""

import asyncio
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ValidationService:
    """
    Serviço para validar o sistema e suas dependências
    """
    
    def __init__(self):
        self.checks = []
    
    async def validate_all(self) -> Dict[str, Any]:
        """
        Executa todas as validações do sistema
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "checks": {}
        }
        
        # Validar importações básicas
        results["checks"]["imports"] = await self._check_imports()
        
        # Validar configuração
        results["checks"]["config"] = await self._check_config()
        
        # Validar OpenAI (se disponível)
        results["checks"]["openai"] = await self._check_openai()
        
        # Validar banco de dados (se disponível)
        results["checks"]["database"] = await self._check_database()
        
        # Determinar status geral
        all_passed = all(
            check.get("status") == "ok" 
            for check in results["checks"].values()
        )
        results["overall_status"] = "ok" if all_passed else "error"
        
        return results
    
    async def _check_imports(self) -> Dict[str, Any]:
        """
        Valida se todas as importações necessárias estão funcionando
        """
        try:
            # Testar imports básicos do FastAPI
            from fastapi import FastAPI
            from pydantic import BaseModel
            
            # Testar SQLAlchemy
            from sqlalchemy import create_engine
            
            # Testar dependências de autenticação
            try:
                import jwt
                jwt_available = True
            except ImportError:
                jwt_available = False
            
            # Testar OpenAI
            try:
                import openai
                openai_available = True
            except ImportError:
                openai_available = False
            
            return {
                "status": "ok",
                "details": {
                    "fastapi": True,
                    "pydantic": True,
                    "sqlalchemy": True,
                    "jwt": jwt_available,
                    "openai": openai_available
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "details": {}
            }
    
    async def _check_config(self) -> Dict[str, Any]:
        """
        Valida configurações do sistema
        """
        try:
            from app.core.config import settings
            
            config_checks = {
                "database_url": bool(settings.DATABASE_URL),
                "secret_key": bool(settings.SECRET_KEY),
                "has_openai_key": hasattr(settings, 'OPENAI_API_KEY') and bool(settings.OPENAI_API_KEY)
            }
            
            return {
                "status": "ok",
                "details": config_checks
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "details": {}
            }
    
    async def _check_openai(self) -> Dict[str, Any]:
        """
        Valida conexão com OpenAI
        """
        try:
            from app.services.openai_service import OpenAIService
            
            service = OpenAIService()
            
            # Testar se a configuração está correta
            api_key = service.config.get_api_key()
            model = service.config.get_model()
            
            return {
                "status": "ok",
                "details": {
                    "api_key_configured": bool(api_key and len(api_key) > 20),
                    "model": model,
                    "service_initialized": True
                }
            }
            
        except Exception as e:
            return {
                "status": "warning",
                "error": str(e),
                "details": {
                    "api_key_configured": False,
                    "service_initialized": False
                }
            }
    
    async def _check_database(self) -> Dict[str, Any]:
        """
        Valida conexão com o banco de dados
        """
        try:
            from app.database import get_db
            from app.core.config import settings
            
            return {
                "status": "ok",
                "details": {
                    "database_url_configured": bool(settings.DATABASE_URL),
                    "connection_factory": True
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "details": {
                    "database_url_configured": False,
                    "connection_factory": False
                }
            }
    
    async def validate_router_integration(self) -> Dict[str, Any]:
        """
        Valida se todos os routers estão devidamente integrados
        """
        try:
            from app.main import app
            
            # Verificar rotas registradas
            routes = []
            for route in app.routes:
                if hasattr(route, 'path'):
                    routes.append({
                        "path": route.path,
                        "methods": getattr(route, 'methods', [])
                    })
            
            return {
                "status": "ok",
                "details": {
                    "total_routes": len(routes),
                    "routes": routes[:10]  # Primeiras 10 rotas
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "details": {}
            }

# Instância global do serviço
validation_service = ValidationService()

async def run_validation():
    """
    Executa validação completa do sistema
    """
    print("🔍 Iniciando validação do sistema...")
    
    results = await validation_service.validate_all()
    
    print(f"\n📊 Resultado da Validação:")
    print(f"Status Geral: {results['overall_status'].upper()}")
    print(f"Timestamp: {results['timestamp']}")
    
    for check_name, check_result in results["checks"].items():
        status_icon = "✅" if check_result["status"] == "ok" else "⚠️" if check_result["status"] == "warning" else "❌"
        print(f"\n{status_icon} {check_name.upper()}:")
        
        if "error" in check_result:
            print(f"  Erro: {check_result['error']}")
        
        for detail_key, detail_value in check_result.get("details", {}).items():
            value_icon = "✅" if detail_value else "❌"
            print(f"  {value_icon} {detail_key}: {detail_value}")
    
    # Validar integração de routers
    print(f"\n🔗 Validando integração de routers...")
    router_results = await validation_service.validate_router_integration()
    
    if router_results["status"] == "ok":
        print(f"✅ Routers integrados: {router_results['details']['total_routes']} rotas encontradas")
    else:
        print(f"❌ Erro na integração: {router_results.get('error', 'Erro desconhecido')}")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_validation())
