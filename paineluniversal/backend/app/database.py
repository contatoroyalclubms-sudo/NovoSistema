"""
Configuração da base de dados PostgreSQL
Sistema Universal de Gestão de Eventos
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging
from typing import Generator
import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base para os modelos
Base = declarative_base()

# ================================
# CONFIGURAÇÕES DO BANCO
# ================================

# Configurações do banco de dados
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "eventos_db"),
    "username": os.getenv("DB_USER", "eventos_user"),
    "password": os.getenv("DB_PASSWORD", "eventos_2024_secure!"),
}

# URLs de conexão
SYNC_DATABASE_URL = (
    f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
)

ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
)

# Override com variável de ambiente se disponível
DATABASE_URL = os.getenv("DATABASE_URL", SYNC_DATABASE_URL)
ASYNC_DATABASE_URL_ENV = os.getenv("ASYNC_DATABASE_URL", ASYNC_DATABASE_URL)

# ================================
# ENGINES E SESSÕES SÍNCRONAS
# ================================

# Configurações do engine
ENGINE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 1800,  # 30 minutos
    "pool_pre_ping": True,
    "echo": os.getenv("DEBUG", "false").lower() == "true",
}

# Engine síncrono
engine = create_engine(DATABASE_URL, **ENGINE_CONFIG)

# SessionLocal para sessões síncronas
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# ================================
# ENGINES E SESSÕES ASSÍNCRONAS
# ================================

# Engine assíncrono
async_engine = create_async_engine(
    ASYNC_DATABASE_URL_ENV,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=os.getenv("DEBUG", "false").lower() == "true",
)

# SessionLocal assíncrona
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# ================================
# DEPENDENCY INJECTION
# ================================

def get_db() -> Generator:
    """
    Dependency injection para FastAPI - Sessões síncronas
    
    Yields:
        Session: Sessão do SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def get_async_db() -> Generator:
    """
    Dependency injection para FastAPI - Sessões assíncronas
    
    Yields:
        AsyncSession: Sessão assíncrona do SQLAlchemy
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Erro na sessão assíncrona do banco: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

# ================================
# FUNÇÕES DE UTILIDADE
# ================================

def create_tables():
    """
    Cria todas as tabelas no banco de dados
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        raise

def drop_tables():
    """
    Remove todas as tabelas do banco de dados
    ⚠️ CUIDADO: Isso apagará todos os dados!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("🗑️ Tabelas removidas com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao remover tabelas: {e}")
        raise

async def test_connection():
    """
    Testa a conexão com o banco de dados
    
    Returns:
        bool: True se a conexão foi bem-sucedida
    """
    try:
        # Teste síncrono
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1
        
        # Teste assíncrono
        async with async_engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            row = result.fetchone()
            assert row[0] == 1
        
        logger.info("✅ Conexão com banco de dados OK!")
        return True
    
    except Exception as e:
        logger.error(f"❌ Erro na conexão com banco: {e}")
        return False

def get_database_info():
    """
    Retorna informações sobre o banco de dados
    
    Returns:
        dict: Informações do banco
    """
    return {
        "host": DATABASE_CONFIG["host"],
        "port": DATABASE_CONFIG["port"],
        "database": DATABASE_CONFIG["database"],
        "username": DATABASE_CONFIG["username"],
        "engine_pool_size": engine.pool.size(),
        "engine_checked_out": engine.pool.checkedout(),
        "async_engine_available": async_engine is not None,
    }

# ================================
# TRANSAÇÕES E CONTEXTOS
# ================================

class DatabaseTransaction:
    """
    Context manager para transações de banco de dados
    """
    
    def __init__(self, session=None):
        self.session = session or SessionLocal()
        self.should_close = session is None
    
    def __enter__(self):
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        
        if self.should_close:
            self.session.close()

class AsyncDatabaseTransaction:
    """
    Context manager assíncrono para transações
    """
    
    def __init__(self, session=None):
        self.session = session
        self.should_close = session is None
    
    async def __aenter__(self):
        if self.session is None:
            self.session = AsyncSessionLocal()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        
        if self.should_close:
            await self.session.close()

# ================================
# HEALTH CHECK
# ================================

async def health_check():
    """
    Verifica a saúde da conexão com o banco
    
    Returns:
        dict: Status da conexão
    """
    try:
        start_time = time.time()
        
        # Teste de conectividade
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        
        response_time = (time.time() - start_time) * 1000  # em ms
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "database": DATABASE_CONFIG["database"],
            "host": DATABASE_CONFIG["host"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": DATABASE_CONFIG["database"],
            "host": DATABASE_CONFIG["host"],
            "timestamp": datetime.utcnow().isoformat()
        }

# ================================
# INICIALIZAÇÃO
# ================================

def init_database():
    """
    Inicializa o banco de dados com configurações básicas
    """
    try:
        logger.info("🔄 Inicializando banco de dados...")
        
        # Criar tabelas se não existirem
        create_tables()
        
        # Configurações básicas do PostgreSQL
        with engine.connect() as conn:
            # Configurar timezone
            conn.execute("SET timezone = 'America/Sao_Paulo'")
            
            # Instalar extensões necessárias (se não existirem)
            try:
                conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
                conn.execute("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\"")
                conn.execute("CREATE EXTENSION IF NOT EXISTS \"unaccent\"")
                logger.info("✅ Extensões PostgreSQL verificadas")
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível instalar extensões: {e}")
        
        logger.info("✅ Banco de dados inicializado com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização do banco: {e}")
        raise

# Importações tardias para evitar dependências circulares
import time
from datetime import datetime

# Metadata para migrações
metadata = MetaData()

# Configurações de logging para SQLAlchemy
if os.getenv("DEBUG", "false").lower() == "true":
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Teste de inicialização (apenas para desenvolvimento)
if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("🔍 Testando conexões...")
        
        # Teste síncrono
        try:
            with engine.connect() as conn:
                result = conn.execute("SELECT version()")
                version = result.fetchone()[0]
                print(f"✅ PostgreSQL Sync: {version}")
        except Exception as e:
            print(f"❌ Erro Sync: {e}")
        
        # Teste assíncrono
        health = await health_check()
        print(f"🏥 Health Check: {health}")
        
        # Informações do banco
        info = get_database_info()
        print(f"📊 Database Info: {info}")
    
    asyncio.run(main())
