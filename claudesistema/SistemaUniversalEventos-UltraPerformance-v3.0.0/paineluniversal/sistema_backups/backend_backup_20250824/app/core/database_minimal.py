"""
Configuração mínima do banco de dados
Sistema Universal de Gestão de Eventos
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config_minimal import settings


class Base(DeclarativeBase):
    """Base class para todos os modelos SQLAlchemy"""
    pass


# Engine assíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

# Session factory
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)


async def get_db():
    """Dependency para obter sessão do banco de dados"""
    async with SessionLocal() as session:
        yield session


async def init_db():
    """Inicializa o banco de dados criando todas as tabelas"""
    try:
        from app.models import Base  # Import aqui para evitar circular imports
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"Aviso: {e}")
        print("Continuando sem criar tabelas...")


async def close_db():
    """Fecha conexões do banco de dados"""
    await engine.dispose()