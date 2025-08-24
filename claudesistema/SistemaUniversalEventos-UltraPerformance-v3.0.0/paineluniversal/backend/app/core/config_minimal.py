"""
Configuração mínima para inicialização rápida
Sistema Universal de Gestão de Eventos
"""

import os
from typing import Optional


class Settings:
    """Configurações mínimas"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./eventos.db")
    
    # App
    DEBUG: bool = True
    SECRET_KEY: str = "eventos-2024-super-secret-key-development-only"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000


# Instância global das configurações
settings = Settings()