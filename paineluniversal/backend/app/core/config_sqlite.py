"""
Configuração SQLite temporária para desenvolvimento rápido
Sistema Universal de Gestão de Eventos - FASE 2
"""

import os
from typing import Optional, List, Dict, Any
from pydantic import validator, Field
from pydantic_settings import BaseSettings
from functools import lru_cache

class SQLiteSettings(BaseSettings):
    """Configurações usando SQLite para desenvolvimento rápido"""
    
    # ================================
    # CONFIGURAÇÕES BÁSICAS
    # ================================
    APP_NAME: str = "Sistema Universal de Gestão de Eventos"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "API para gestão completa de eventos"
    APP_PHASE: str = "FASE 2 - SQLite"
    
    # Ambiente de execução
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Configurações do servidor
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    RELOAD: bool = Field(default=True, env="RELOAD")
    
    # ================================
    # CONFIGURAÇÕES DE SEGURANÇA
    # ================================
    SECRET_KEY: str = Field(
        default="dev-secret-key-eventos-2024-sqlite-temp",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:4200",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:4200", 
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8080"
        ],
        env="BACKEND_CORS_ORIGINS"
    )
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # ================================
    # CONFIGURAÇÕES DO BANCO SQLITE
    # ================================
    
    # SQLite Database Path
    DATABASE_PATH: str = Field(default="eventos.db", env="DATABASE_PATH")
    
    # URL de conexão SQLite
    SQLALCHEMY_DATABASE_URI: str = Field(default="", env="SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_ASYNC_DATABASE_URI: str = Field(default="", env="SQLALCHEMY_ASYNC_DATABASE_URI")
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_sqlite_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if v:
            return v
        db_path = values.get("DATABASE_PATH", "eventos.db")
        return f"sqlite:///./{db_path}"
    
    @validator("SQLALCHEMY_ASYNC_DATABASE_URI", pre=True)
    def assemble_async_sqlite_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if v:
            return v
        db_path = values.get("DATABASE_PATH", "eventos.db")
        return f"sqlite+aiosqlite:///./{db_path}"
    
    # Pool settings (não aplicável ao SQLite mas mantido para compatibilidade)
    DB_POOL_SIZE: int = Field(default=1, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=0, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    DB_POOL_RECYCLE: int = Field(default=3600, env="DB_POOL_RECYCLE")
    
    # ================================
    # CONFIGURAÇÕES SIMPLIFICADAS PARA DEV
    # ================================
    
    # Cache desabilitado (usar memória)
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_URL: str = Field(default="", env="REDIS_URL")
    USE_CACHE: bool = Field(default=False, env="USE_CACHE")  # Desabilitado
    
    # Email desabilitado para dev
    MAIL_USERNAME: str = Field(default="", env="MAIL_USERNAME")
    MAIL_PASSWORD: str = Field(default="", env="MAIL_PASSWORD")
    MAIL_FROM: str = Field(default="dev@eventos.local", env="MAIL_FROM")
    MAIL_PORT: int = Field(default=587, env="MAIL_PORT")
    MAIL_SERVER: str = Field(default="localhost", env="MAIL_SERVER")
    MAIL_TLS: bool = Field(default=False, env="MAIL_TLS")
    MAIL_SSL: bool = Field(default=False, env="MAIL_SSL")
    MAIL_USE_CREDENTIALS: bool = Field(default=False, env="MAIL_USE_CREDENTIALS")
    EMAIL_ENABLED: bool = Field(default=False, env="EMAIL_ENABLED")  # Desabilitado
    
    # Uploads locais
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "pdf"],
        env="ALLOWED_EXTENSIONS"
    )
    USE_CDN: bool = Field(default=False, env="USE_CDN")
    CDN_URL: Optional[str] = Field(default=None, env="CDN_URL")
    
    # ================================
    # LOGS SIMPLIFICADOS
    # ================================
    LOG_LEVEL: str = Field(default="DEBUG", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    LOG_FILE: str = Field(default="logs/eventos.log", env="LOG_FILE")
    LOG_TO_FILE: bool = Field(default=False, env="LOG_TO_FILE")  # Console apenas
    
    # ================================
    # FUNCIONALIDADES HABILITADAS
    # ================================
    ENABLE_CHECKIN: bool = Field(default=True, env="ENABLE_CHECKIN")
    ENABLE_PDV: bool = Field(default=True, env="ENABLE_PDV")
    ENABLE_GAMIFICATION: bool = Field(default=True, env="ENABLE_GAMIFICATION")
    ENABLE_ANALYTICS: bool = Field(default=True, env="ENABLE_ANALYTICS")
    ENABLE_REPORTS: bool = Field(default=True, env="ENABLE_REPORTS")
    ENABLE_WEBSOCKET: bool = Field(default=True, env="ENABLE_WEBSOCKET")
    
    # Funcionalidades desabilitadas para dev
    ENABLE_WEBHOOKS: bool = Field(default=False, env="ENABLE_WEBHOOKS")
    ENABLE_NOTIFICATIONS: bool = Field(default=False, env="ENABLE_NOTIFICATIONS")
    ENABLE_BACKUP: bool = Field(default=False, env="ENABLE_BACKUP")
    ENABLE_MONITORING: bool = Field(default=False, env="ENABLE_MONITORING")
    
    # ================================
    # CONFIGURAÇÕES DE GAMIFICAÇÃO
    # ================================
    GAMIFICATION_ENABLED: bool = Field(default=True, env="GAMIFICATION_ENABLED")
    DEFAULT_CHECKIN_POINTS: int = Field(default=10, env="DEFAULT_CHECKIN_POINTS")
    DEFAULT_PARTICIPATION_POINTS: int = Field(default=5, env="DEFAULT_PARTICIPATION_POINTS")
    
    # ================================
    # CONFIGURAÇÕES DE PAGAMENTO (SIMULADO)
    # ================================
    PAYMENT_ENABLED: bool = Field(default=True, env="PAYMENT_ENABLED")
    PAYMENT_SANDBOX: bool = Field(default=True, env="PAYMENT_SANDBOX")
    PIX_KEY: str = Field(default="pix@eventos.local", env="PIX_KEY")
    
    # ================================
    # WEBSOCKET
    # ================================
    WEBSOCKET_ENABLED: bool = Field(default=True, env="WEBSOCKET_ENABLED")
    WEBSOCKET_PATH: str = Field(default="/ws", env="WEBSOCKET_PATH")
    WEBSOCKET_HEARTBEAT: int = Field(default=30, env="WEBSOCKET_HEARTBEAT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_sqlite_settings() -> SQLiteSettings:
    """Singleton para configurações SQLite"""
    return SQLiteSettings()

# Instância global
sqlite_settings = get_sqlite_settings()