"""
Sistema Universal - Versão Avançada Segura
FASE 3 - Ativação gradual e segura de funcionalidades
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import sys
import traceback

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema Universal - Versão Avançada",
    description="Sistema com ativação segura de funcionalidades",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SISTEMA DE ATIVAÇÃO GRADUAL
MODULES_STATUS = {
    "database": False,
    "auth": False,
    "usuarios": False,
    "eventos": False,
    "business": False,
    "advanced": False,
    "ai": False,
    "integrations": False
}

def safe_import_and_activate(module_name, activation_function):
    """Importa e ativa módulos de forma segura"""
    try:
        result = activation_function()
        MODULES_STATUS[module_name] = True
        logger.info(f"✅ {module_name} ativado com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao ativar {module_name}: {e}")
        MODULES_STATUS[module_name] = False
        return False

def activate_database():
    """Ativa sistema de database"""
    from app.database import create_tables
    create_tables()
    return True

def activate_core_routers():
    """Ativa routers core"""
    from app.routers import auth, usuarios, eventos
    
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(usuarios.router, prefix="/api/usuarios", tags=["usuarios"])
    app.include_router(eventos.router, prefix="/api/eventos", tags=["eventos"])
    return True

def activate_business_routers():
    """Ativa routers de negócio"""
    try:
        from app.routers import pdv, financeiro, estoque, checkins
        
        app.include_router(pdv.router, prefix="/api/pdv", tags=["pdv"])
        app.include_router(financeiro.router, prefix="/api/financeiro", tags=["financeiro"])
        app.include_router(estoque.router, prefix="/api/estoque", tags=["estoque"])
        app.include_router(checkins.router, prefix="/api/checkins", tags=["checkins"])
        return True
    except ImportError as e:
        logger.warning(f"Alguns business routers não disponíveis: {e}")
        return False

def activate_advanced_features():
    """Ativa funcionalidades avançadas"""
    try:
        from app.routers import dashboard, analytics, relatorios
        
        app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
        app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
        app.include_router(relatorios.router, prefix="/api/relatorios", tags=["relatorios"])
        return True
    except ImportError as e:
        logger.warning(f"Funcionalidades avançadas não disponíveis: {e}")
        return False

def activate_ai_features():
    """Ativa funcionalidades de IA"""
    try:
        from app.routers import ai_intelligence, ia_avancada
        
        app.include_router(ai_intelligence.router, prefix="/api/ai", tags=["ai"])
        app.include_router(ia_avancada.router, prefix="/api/ia-avancada", tags=["ia-avancada"])
        return True
    except ImportError as e:
        logger.warning(f"Funcionalidades de IA não disponíveis: {e}")
        return False

# ATIVAÇÃO DOS MÓDULOS
logger.info("🚀 Iniciando ativação de módulos...")

# 1. Database
safe_import_and_activate("database", activate_database)

# 2. Core routers
safe_import_and_activate("auth", activate_core_routers)

# 3. Business routers
safe_import_and_activate("business", activate_business_routers)

# 4. Advanced features
safe_import_and_activate("advanced", activate_advanced_features)

# 5. AI features
safe_import_and_activate("ai", activate_ai_features)

# ENDPOINTS PRINCIPAIS
@app.get("/")
async def root():
    """Homepage com status do sistema"""
    activated_modules = sum(1 for status in MODULES_STATUS.values() if status)
    
    return {
        "message": "Sistema Universal - Versão Avançada Segura",
        "version": "3.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "activated": activated_modules,
            "total": len(MODULES_STATUS),
            "details": MODULES_STATUS
        }
    }

@app.get("/health")
async def health_check():
    """Health check detalhado"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": MODULES_STATUS
    }

@app.get("/activate/{module_name}")
async def activate_module(module_name: str):
    """Endpoint para ativar módulos específicos"""
    if module_name not in MODULES_STATUS:
        raise HTTPException(status_code=404, detail="Módulo não encontrado")
    
    if MODULES_STATUS[module_name]:
        return {"message": f"Módulo {module_name} já está ativo"}
    
    # Tentar ativar o módulo
    activation_functions = {
        "database": activate_database,
        "auth": activate_core_routers,
        "business": activate_business_routers,
        "advanced": activate_advanced_features,
        "ai": activate_ai_features
    }
    
    if module_name in activation_functions:
        success = safe_import_and_activate(module_name, activation_functions[module_name])
        if success:
            return {"message": f"Módulo {module_name} ativado com sucesso"}
        else:
            raise HTTPException(status_code=500, detail=f"Erro ao ativar {module_name}")
    
    return {"message": "Função de ativação não implementada"}

@app.get("/system/info")
async def system_info():
    """Informações detalhadas do sistema"""
    return {
        "system": "Sistema Universal de Gestão",
        "version": "3.0.0",
        "python_version": sys.version,
        "modules": MODULES_STATUS,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_avancado:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
