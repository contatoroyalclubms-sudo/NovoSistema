"""
DATABASE CONNECTION PERFORMANCE OPTIMIZATION
Sistema Universal de Gestão de Eventos - ULTRA PERFORMANCE

Implementação de database com:
- Connection pooling otimizado
- Query optimization com indexes
- Async operations
- Caching layer integration
- Performance monitoring
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any
from sqlalchemy import create_engine, MetaData, Index, text
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession, 
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine.events import event
from prometheus_client import Counter, Histogram, Gauge
import time

from .config import settings

# Performance Metrics
db_query_counter = Counter('db_queries_total', 'Total database queries', ['table', 'operation'])
db_query_duration = Histogram('db_query_duration_seconds', 'Query execution time')
db_connection_pool_size = Gauge('db_connection_pool_size', 'Current connection pool size')
db_connection_pool_checked_out = Gauge('db_connection_pool_checked_out', 'Checked out connections')

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """Base model with performance optimizations"""
    pass

class DatabaseManager:
    """
    Ultra-performance database manager with:
    - Optimized connection pooling
    - Query performance monitoring
    - Automatic index management
    - Connection lifecycle management
    """
    
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.sync_engine = None
        self.session_factory: Optional[async_sessionmaker] = None
        self.sync_session_factory = None
        self.is_initialized = False
        self._connection_metrics = {
            'total_connections': 0,
            'active_connections': 0,
            'query_count': 0,
            'slow_queries': 0
        }
    
    async def initialize(self):
        """Initialize database with ultra performance configuration"""
        if self.is_initialized:
            return
        
        logger.info("🚀 Initializing Ultra-Performance Database Manager...")
        
        # Use DATABASE_URL or build from components
        database_url = settings.DATABASE_URL
        if not database_url:
            if hasattr(settings, 'SQLALCHEMY_ASYNC_DATABASE_URI') and settings.SQLALCHEMY_ASYNC_DATABASE_URI:
                database_url = settings.SQLALCHEMY_ASYNC_DATABASE_URI
            else:
                # Fallback to SQLite for development
                database_url = "sqlite+aiosqlite:///./eventos.db"
        
        # Configure async engine with optimized pool settings
        if database_url.startswith('postgresql'):
            # PostgreSQL with connection pooling
            self.engine = create_async_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=settings.DB_POOL_SIZE if hasattr(settings, 'DB_POOL_SIZE') else 10,
                max_overflow=settings.DB_MAX_OVERFLOW if hasattr(settings, 'DB_MAX_OVERFLOW') else 20,
                pool_timeout=settings.DB_POOL_TIMEOUT if hasattr(settings, 'DB_POOL_TIMEOUT') else 30,
                pool_recycle=settings.DB_POOL_RECYCLE if hasattr(settings, 'DB_POOL_RECYCLE') else 3600,
                pool_pre_ping=True,
                echo=settings.DEBUG,
                echo_pool=settings.DEBUG,
                future=True,
                connect_args={
                    "server_settings": {
                        "application_name": "SistemaEventos_v2",
                        "jit": "off",
                    },
                    "command_timeout": 60,
                }
            )
        else:
            # SQLite or other databases
            self.engine = create_async_engine(
                database_url,
                echo=settings.DEBUG,
                pool_pre_ping=True
            )
        
        # Create session factory
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False
        )
        
        # Setup performance monitoring
        self._setup_performance_monitoring()
        
        # Create database indexes for performance (only for PostgreSQL)
        if database_url.startswith('postgresql'):
            await self._create_performance_indexes()
        
        self.is_initialized = True
        logger.info("✅ Ultra-Performance Database Manager initialized successfully")
    
    def _setup_performance_monitoring(self):
        """Setup database performance monitoring"""
        
        @event.listens_for(self.engine.sync_engine if hasattr(self.engine, 'sync_engine') else self.engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            self._connection_metrics['total_connections'] += 1
            db_connection_pool_size.set(self._connection_metrics['total_connections'])
        
        logger.info("✅ Database performance monitoring setup completed")
    
    async def _create_performance_indexes(self):
        """Create optimized database indexes for performance"""
        try:
            async with self.engine.begin() as conn:
                # Indexes for eventos table
                await conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_organizador_id 
                    ON eventos(organizador_id);
                """))
                
                await conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_data_inicio 
                    ON eventos(data_inicio);
                """))
                
                await conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_status 
                    ON eventos(status);
                """))
                
                # Composite index for common query patterns
                await conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_org_status_data 
                    ON eventos(organizador_id, status, data_inicio);
                """))
                
                # Indexes for participantes table
                await conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participantes_evento_id 
                    ON participantes(evento_id);
                """))
                
                await conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participantes_qr_code 
                    ON participantes(qr_code);
                """))
                
                # Indexes for checkins table
                await conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_checkins_participante_id 
                    ON checkins(participante_id);
                """))
                
                # Indexes for transacoes_pdv table
                await conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transacoes_evento_id 
                    ON transacoes_pdv(evento_id);
                """))
                
                logger.info("✅ Performance indexes created successfully")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not create some indexes (may already exist): {e}")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with performance monitoring"""
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        session = self.session_factory()
        
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()
            
            # Record metrics
            duration = time.time() - start_time
            db_query_duration.observe(duration)
            
            if duration > 1.0:  # Slow query threshold
                self._connection_metrics['slow_queries'] += 1
                logger.warning(f"Slow database session detected: {duration:.2f}s")
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive database health check"""
        try:
            start_time = time.time()
            
            async with self.get_session() as session:
                # Simple connectivity test
                result = await session.execute(text("SELECT 1 as health_check"))
                health_result = result.fetchone()
                
                response_time = time.time() - start_time
                
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time * 1000, 2),
                    "metrics": self._connection_metrics,
                    "database_url": str(self.engine.url).replace(str(self.engine.url.password), "***") if self.engine.url.password else str(self.engine.url)
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "metrics": self._connection_metrics
            }
    
    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
        
        self.is_initialized = False
        logger.info("✅ Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

# Legacy compatibility
engine = None
SessionLocal = None

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session"""
    async with db_manager.get_session() as session:
        yield session

async def init_db():
    """Initialize database with performance optimizations"""
    await db_manager.initialize()
    
    # Create all tables
    from app.models import Base
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """Close database connections"""
    await db_manager.close()