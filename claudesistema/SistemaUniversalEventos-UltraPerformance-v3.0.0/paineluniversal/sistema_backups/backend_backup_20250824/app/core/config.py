"""
Módulo de configurações da aplicação
Sistema Universal de Gestão de Eventos - FASE 2

Configurações de ambiente, banco de dados e segurança
"""

import os
from typing import Optional, List, Dict, Any
from pydantic import BaseSettings, PostgresDsn, validator, Field
from functools import lru_cache

class Settings(BaseSettings):
    """
    Configurações da aplicação usando Pydantic Settings
    
    Todas as configurações podem ser definidas via variáveis de ambiente
    ou arquivo .env na raiz do projeto
    """
    
    # ================================
    # CONFIGURAÇÕES BÁSICAS
    # ================================
    APP_NAME: str = "Sistema Universal de Gestão de Eventos"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "API para gestão completa de eventos"
    APP_PHASE: str = "FASE 2"
    
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
        default="sua-chave-secreta-super-segura-aqui-troque-em-producao",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # 24 horas
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
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
    # CONFIGURAÇÕES DO BANCO DE DADOS
    # ================================
    
    # PostgreSQL Principal
    DB_HOST: str = Field(default="localhost", env="DB_HOST")
    DB_PORT: int = Field(default=5432, env="DB_PORT")
    DB_USER: str = Field(default="postgres", env="DB_USER")
    DB_PASSWORD: str = Field(default="postgres", env="DB_PASSWORD")
    DB_NAME: str = Field(default="eventos_db", env="DB_NAME")
    
    # Pool de conexões
    DB_POOL_SIZE: int = Field(default=10, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=20, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    DB_POOL_RECYCLE: int = Field(default=3600, env="DB_POOL_RECYCLE")
    
    # URLs de conexão (construídas automaticamente)
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    SQLALCHEMY_ASYNC_DATABASE_URI: Optional[str] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=str(values.get("DB_PORT")),
            path=f"/{values.get('DB_NAME') or ''}",
        )
    
    @validator("SQLALCHEMY_ASYNC_DATABASE_URI", pre=True)
    def assemble_async_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql+asyncpg://{values.get('DB_USER')}:{values.get('DB_PASSWORD')}@{values.get('DB_HOST')}:{values.get('DB_PORT')}/{values.get('DB_NAME')}"
    
    # ================================
    # CONFIGURAÇÕES DE CACHE/REDIS
    # ================================
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_URL: Optional[str] = None
    
    @validator("REDIS_URL", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        
        password_part = ""
        if values.get("REDIS_PASSWORD"):
            password_part = f":{values.get('REDIS_PASSWORD')}@"
        
        return f"redis://{password_part}{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
    
    # ================================
    # CONFIGURAÇÕES DE EMAIL
    # ================================
    MAIL_USERNAME: str = Field(default="", env="MAIL_USERNAME")
    MAIL_PASSWORD: str = Field(default="", env="MAIL_PASSWORD")
    MAIL_FROM: str = Field(default="noreply@eventos.com", env="MAIL_FROM")
    MAIL_PORT: int = Field(default=587, env="MAIL_PORT")
    MAIL_SERVER: str = Field(default="smtp.gmail.com", env="MAIL_SERVER")
    MAIL_TLS: bool = Field(default=True, env="MAIL_TLS")
    MAIL_SSL: bool = Field(default=False, env="MAIL_SSL")
    MAIL_USE_CREDENTIALS: bool = Field(default=True, env="MAIL_USE_CREDENTIALS")
    
    # Templates de email
    EMAIL_TEMPLATES_DIR: str = Field(default="app/templates/email", env="EMAIL_TEMPLATES_DIR")
    
    # ================================
    # CONFIGURAÇÕES DE UPLOAD
    # ================================
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # CDN/Storage
    USE_CDN: bool = Field(default=False, env="USE_CDN")
    CDN_URL: Optional[str] = Field(default=None, env="CDN_URL")
    
    # ================================
    # CONFIGURAÇÕES DE LOGS
    # ================================
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        env="LOG_FORMAT"
    )
    LOG_FILE: str = Field(default="logs/app.log", env="LOG_FILE")
    LOG_ROTATION: str = Field(default="1 day", env="LOG_ROTATION")
    LOG_RETENTION: str = Field(default="30 days", env="LOG_RETENTION")
    
    # ================================
    # CONFIGURAÇÕES DE WEBHOOK
    # ================================
    WEBHOOK_SECRET: Optional[str] = Field(default=None, env="WEBHOOK_SECRET")
    WEBHOOK_TIMEOUT: int = Field(default=30, env="WEBHOOK_TIMEOUT")
    
    # ================================
    # CONFIGURAÇÕES DE GAMIFICAÇÃO
    # ================================
    GAMIFICATION_ENABLED: bool = Field(default=True, env="GAMIFICATION_ENABLED")
    DEFAULT_CHECKIN_POINTS: int = Field(default=10, env="DEFAULT_CHECKIN_POINTS")
    DEFAULT_PARTICIPATION_POINTS: int = Field(default=5, env="DEFAULT_PARTICIPATION_POINTS")
    
    # ================================
    # CONFIGURAÇÕES DE PAGAMENTO
    # ================================
    PAYMENT_ENABLED: bool = Field(default=True, env="PAYMENT_ENABLED")
    PAYMENT_SANDBOX: bool = Field(default=True, env="PAYMENT_SANDBOX")
    
    # PIX
    PIX_KEY: Optional[str] = Field(default=None, env="PIX_KEY")
    PIX_BANK_CODE: Optional[str] = Field(default=None, env="PIX_BANK_CODE")
    
    # Cartão (integração futura)
    STRIPE_PUBLIC_KEY: Optional[str] = Field(default=None, env="STRIPE_PUBLIC_KEY")
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    
    # ================================
    # CONFIGURAÇÕES DE IA E INTEGRAÇÕES
    # ================================
    # OpenAI API
    OPENAI_API_KEY: str = Field(
        default="your-openai-api-key-here",
        env="OPENAI_API_KEY"
    )
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    OPENAI_MAX_TOKENS: int = Field(default=1500, env="OPENAI_MAX_TOKENS")
    OPENAI_TEMPERATURE: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # WhatsApp Business API
    WHATSAPP_TOKEN: Optional[str] = Field(default=None, env="WHATSAPP_TOKEN")
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = Field(default=None, env="WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = Field(default="webhook_token", env="WHATSAPP_WEBHOOK_VERIFY_TOKEN")
    
    # N8N Automation
    N8N_WEBHOOK_URL: Optional[str] = Field(default=None, env="N8N_WEBHOOK_URL")
    N8N_API_KEY: Optional[str] = Field(default=None, env="N8N_API_KEY")
    
    # ================================
    # CONFIGURAÇÕES DE MONITORAMENTO
    # ================================
    MONITORING_ENABLED: bool = Field(default=False, env="MONITORING_ENABLED")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    # Métricas
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    METRICS_PORT: int = Field(default=9000, env="METRICS_PORT")
    
    # ================================
    # CONFIGURAÇÕES DE BACKUP
    # ================================
    BACKUP_ENABLED: bool = Field(default=False, env="BACKUP_ENABLED")
    BACKUP_DIR: str = Field(default="backups", env="BACKUP_DIR")
    BACKUP_SCHEDULE: str = Field(default="0 2 * * *", env="BACKUP_SCHEDULE")  # Daily at 2AM
    BACKUP_RETENTION_DAYS: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    
    # ================================
    # CONFIGURAÇÕES DE WEBSOCKET
    # ================================
    WEBSOCKET_ENABLED: bool = Field(default=True, env="WEBSOCKET_ENABLED")
    WEBSOCKET_PATH: str = Field(default="/ws", env="WEBSOCKET_PATH")
    WEBSOCKET_HEARTBEAT: int = Field(default=30, env="WEBSOCKET_HEARTBEAT")
    
    # ================================
    # CONFIGURAÇÕES ESPECÍFICAS DE FASE
    # ================================
    # FASE 2 - Funcionalidades ativas
    ENABLE_CHECKIN: bool = Field(default=True, env="ENABLE_CHECKIN")
    ENABLE_PDV: bool = Field(default=True, env="ENABLE_PDV")
    ENABLE_GAMIFICATION: bool = Field(default=True, env="ENABLE_GAMIFICATION")
    ENABLE_ANALYTICS: bool = Field(default=True, env="ENABLE_ANALYTICS")
    ENABLE_REPORTS: bool = Field(default=True, env="ENABLE_REPORTS")
    
    # Futuras fases
    ENABLE_MOBILE_APP: bool = Field(default=False, env="ENABLE_MOBILE_APP")
    ENABLE_AI_INSIGHTS: bool = Field(default=False, env="ENABLE_AI_INSIGHTS")
    ENABLE_MULTI_TENANT: bool = Field(default=False, env="ENABLE_MULTI_TENANT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Singleton para obter configurações da aplicação
    
    Returns:
        Instância única das configurações
    """
    return Settings()

# Configurações para diferentes ambientes
class DevelopmentSettings(Settings):
    """Configurações para ambiente de desenvolvimento"""
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

class ProductionSettings(Settings):
    """Configurações para ambiente de produção"""
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    RELOAD: bool = False

class TestingSettings(Settings):
    """Configurações para ambiente de testes"""
    ENVIRONMENT: str = "testing"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DB_NAME: str = "eventos_test_db"

def get_settings_by_environment(env: str = None) -> Settings:
    """
    Obtém configurações baseadas no ambiente
    
    Args:
        env: Nome do ambiente (development, production, testing)
        
    Returns:
        Configurações apropriadas para o ambiente
    """
    if env is None:
        env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

# Singleton global
settings = get_settings()
