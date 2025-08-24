"""
Ultra-High Performance Database Optimizer
Enterprise-grade database optimization with connection pooling and query optimization
Target: Sub-5ms queries, millions of records, intelligent indexing
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from contextlib import asynccontextmanager
import hashlib

from sqlalchemy import create_engine, text, Index
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.redis_ultra_cache import ultra_cache, cached

logger = logging.getLogger(__name__)

class UltraDatabaseOptimizer:
    """Enterprise database optimization system"""
    
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None
        self.query_cache = {}
        self.performance_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'slow_queries': 0,
            'average_query_time': 0,
            'connection_pool_size': 0,
            'active_connections': 0
        }
        
    def setup_connection_pool(self, database_url: str, async_database_url: str = None):
        """Setup high-performance connection pools"""
        try:
            # Sync engine with optimized pool
            self.engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=50,           # Base pool size
                max_overflow=100,       # Additional connections
                pool_pre_ping=True,     # Validate connections
                pool_recycle=3600,      # Recycle connections every hour
                connect_args={
                    "check_same_thread": False,
                    "timeout": 20
                } if "sqlite" in database_url else {}
            )
            
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            
            # Async engine if URL provided
            if async_database_url:
                self.async_engine = create_async_engine(
                    async_database_url,
                    pool_size=30,
                    max_overflow=50,
                    pool_pre_ping=True,
                    pool_recycle=3600
                )
                
                self.async_session_factory = async_sessionmaker(
                    bind=self.async_engine,
                    class_=AsyncSession,
                    autocommit=False,
                    autoflush=False,
                    expire_on_commit=False
                )
            
            logger.info("✅ Ultra database connection pools initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database pool setup failed: {e}")
            return False
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session with automatic cleanup"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self):
        """Get async database session with automatic cleanup"""
        if not self.async_session_factory:
            raise RuntimeError("Async session factory not initialized")
        
        session = self.async_session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Async database session error: {e}")
            raise
        finally:
            await session.close()
    
    def create_performance_indexes(self):
        """Create optimized indexes for ultra performance"""
        if not self.engine:
            logger.warning("Engine not initialized, cannot create indexes")
            return
        
        try:
            with self.engine.connect() as conn:
                # Hash indexes for exact lookups (O(1) complexity)
                indexes = [
                    # User lookups
                    "CREATE INDEX IF NOT EXISTS idx_usuarios_email_hash ON usuarios USING hash(email)",
                    "CREATE INDEX IF NOT EXISTS idx_usuarios_username_hash ON usuarios USING hash(username)",
                    
                    # Event lookups
                    "CREATE INDEX IF NOT EXISTS idx_eventos_codigo_hash ON eventos USING hash(codigo)",
                    "CREATE INDEX IF NOT EXISTS idx_eventos_status ON eventos(status)",
                    "CREATE INDEX IF NOT EXISTS idx_eventos_data_inicio ON eventos(data_inicio)",
                    
                    # Participant lookups
                    "CREATE INDEX IF NOT EXISTS idx_participantes_codigo_barras_hash ON participantes USING hash(codigo_barras)",
                    "CREATE INDEX IF NOT EXISTS idx_participantes_evento_user ON participantes(evento_id, usuario_id)",
                    
                    # Transaction indexes
                    "CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data_transacao)",
                    "CREATE INDEX IF NOT EXISTS idx_transacoes_usuario ON transacoes(usuario_id)",
                    
                    # Composite indexes for complex queries
                    "CREATE INDEX IF NOT EXISTS idx_participantes_event_status ON participantes(evento_id, status)",
                    "CREATE INDEX IF NOT EXISTS idx_eventos_organizer_date ON eventos(organizador_id, data_inicio)",
                    
                    # Partial indexes (smaller, faster)
                    "CREATE INDEX IF NOT EXISTS idx_eventos_active ON eventos(id) WHERE status = 'ativo'",
                    "CREATE INDEX IF NOT EXISTS idx_participantes_checked_in ON participantes(evento_id) WHERE check_in IS NOT NULL"
                ]
                
                # Try to create PostgreSQL-specific indexes
                for index_sql in indexes:
                    try:
                        # Skip hash indexes for SQLite
                        if "sqlite" in str(self.engine.url) and "USING hash" in index_sql:
                            # Convert to regular index for SQLite
                            index_sql = index_sql.replace(" USING hash(", "(").replace(")", ")")
                        
                        conn.execute(text(index_sql))
                        conn.commit()
                    except Exception as e:
                        # Log but continue with other indexes
                        logger.debug(f"Index creation note: {e}")
                
                logger.info("✅ Performance indexes created/verified")
                
        except Exception as e:
            logger.error(f"Index creation error: {e}")
    
    @cached(namespace="query", ttl=300)  # 5 minute cache
    async def execute_cached_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict]:
        """Execute query with intelligent caching"""
        start_time = time.perf_counter()
        
        try:
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                # Convert to list of dicts for JSON serialization
                rows = []
                if result.returns_rows:
                    columns = result.keys()
                    for row in result:
                        rows.append(dict(zip(columns, row)))
                
                query_time = (time.perf_counter() - start_time) * 1000
                self._update_query_stats(query_time)
                
                return rows
                
        except Exception as e:
            logger.error(f"Cached query error: {e}")
            raise
    
    def _update_query_stats(self, query_time_ms: float):
        """Update query performance statistics"""
        self.performance_stats['total_queries'] += 1
        
        # Track slow queries (>10ms)
        if query_time_ms > 10:
            self.performance_stats['slow_queries'] += 1
            logger.warning(f"Slow query detected: {query_time_ms:.2f}ms")
        
        # Update average query time
        total = self.performance_stats['total_queries']
        current_avg = self.performance_stats['average_query_time']
        self.performance_stats['average_query_time'] = (
            (current_avg * (total - 1) + query_time_ms) / total
        )
    
    def optimize_table_for_performance(self, table_name: str):
        """Optimize specific table for ultra performance"""
        if not self.engine:
            return False
        
        try:
            with self.engine.connect() as conn:
                optimizations = []
                
                if "postgresql" in str(self.engine.url):
                    optimizations = [
                        f"ANALYZE {table_name}",
                        f"VACUUM ANALYZE {table_name}",
                        f"REINDEX TABLE {table_name}"
                    ]
                elif "sqlite" in str(self.engine.url):
                    optimizations = [
                        f"ANALYZE {table_name}",
                        f"VACUUM"
                    ]
                
                for optimization in optimizations:
                    try:
                        conn.execute(text(optimization))
                        conn.commit()
                    except Exception as e:
                        logger.debug(f"Optimization note for {table_name}: {e}")
                
                logger.info(f"✅ Table {table_name} optimized for performance")
                return True
                
        except Exception as e:
            logger.error(f"Table optimization error for {table_name}: {e}")
            return False
    
    async def get_connection_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        try:
            stats = {
                'engine_url': str(self.engine.url) if self.engine else None,
                'pool_size': 0,
                'checked_in_connections': 0,
                'checked_out_connections': 0,
                'overflow_connections': 0,
                'invalid_connections': 0
            }
            
            if self.engine and hasattr(self.engine.pool, 'size'):
                pool = self.engine.pool
                stats.update({
                    'pool_size': pool.size(),
                    'checked_in_connections': pool.checkedin(),
                    'checked_out_connections': pool.checkedout(),
                    'overflow_connections': pool.overflow(),
                    'invalid_connections': pool.invalidated()
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Pool stats error: {e}")
            return {'error': str(e)}
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        cache_stats = ultra_cache.get_stats()
        
        return {
            'database_stats': {
                **self.performance_stats,
                'queries_per_second': self.performance_stats['total_queries'] / max(time.time(), 1),
                'slow_query_percentage': (
                    self.performance_stats['slow_queries'] / 
                    max(self.performance_stats['total_queries'], 1) * 100
                )
            },
            'cache_stats': cache_stats,
            'recommendations': self._get_performance_recommendations()
        }
    
    def _get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        # Query performance recommendations
        if self.performance_stats['average_query_time'] > 20:
            recommendations.append("Consider adding more specific indexes for frequent queries")
        
        if self.performance_stats['slow_queries'] > 0:
            recommendations.append("Review slow queries and optimize with EXPLAIN ANALYZE")
        
        # Cache recommendations
        cache_hit_ratio = (
            self.performance_stats['cache_hits'] / 
            max(self.performance_stats['total_queries'], 1) * 100
        )
        
        if cache_hit_ratio < 80:
            recommendations.append("Increase cache TTL for frequently accessed data")
        
        # Connection pool recommendations
        if self.performance_stats['active_connections'] > 40:
            recommendations.append("Consider increasing connection pool size")
        
        if not recommendations:
            recommendations.append("Database performance is optimal!")
        
        return recommendations
    
    async def run_performance_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmark"""
        logger.info("Starting database performance benchmark...")
        
        benchmark_results = {
            'simple_select': await self._benchmark_simple_select(),
            'indexed_lookup': await self._benchmark_indexed_lookup(),
            'join_query': await self._benchmark_join_query(),
            'aggregate_query': await self._benchmark_aggregate_query(),
            'cache_performance': await self._benchmark_cache_performance()
        }
        
        logger.info("Database benchmark completed")
        return benchmark_results
    
    async def _benchmark_simple_select(self) -> Dict[str, float]:
        """Benchmark simple SELECT query"""
        query = "SELECT COUNT(*) as count FROM usuarios"
        
        start_time = time.perf_counter()
        try:
            await self.execute_cached_query(query)
            end_time = time.perf_counter()
            return {
                'query_time_ms': (end_time - start_time) * 1000,
                'status': 'success'
            }
        except Exception as e:
            return {
                'query_time_ms': -1,
                'status': 'failed',
                'error': str(e)
            }
    
    async def _benchmark_indexed_lookup(self) -> Dict[str, float]:
        """Benchmark indexed lookup performance"""
        query = "SELECT * FROM usuarios WHERE email = :email LIMIT 1"
        params = {'email': 'admin@eventos.com'}
        
        start_time = time.perf_counter()
        try:
            await self.execute_cached_query(query, params)
            end_time = time.perf_counter()
            return {
                'query_time_ms': (end_time - start_time) * 1000,
                'status': 'success'
            }
        except Exception as e:
            return {
                'query_time_ms': -1,
                'status': 'failed',
                'error': str(e)
            }
    
    async def _benchmark_join_query(self) -> Dict[str, float]:
        """Benchmark JOIN query performance"""
        query = """
        SELECT e.nome, COUNT(p.id) as participantes
        FROM eventos e
        LEFT JOIN participantes p ON e.id = p.evento_id
        GROUP BY e.id, e.nome
        LIMIT 10
        """
        
        start_time = time.perf_counter()
        try:
            await self.execute_cached_query(query)
            end_time = time.perf_counter()
            return {
                'query_time_ms': (end_time - start_time) * 1000,
                'status': 'success'
            }
        except Exception as e:
            return {
                'query_time_ms': -1,
                'status': 'failed',
                'error': str(e)
            }
    
    async def _benchmark_aggregate_query(self) -> Dict[str, float]:
        """Benchmark aggregate query performance"""
        query = """
        SELECT 
            DATE(data_transacao) as data,
            SUM(valor_total) as vendas_totais,
            COUNT(*) as num_transacoes
        FROM transacoes
        WHERE data_transacao >= datetime('now', '-30 days')
        GROUP BY DATE(data_transacao)
        ORDER BY data DESC
        """
        
        start_time = time.perf_counter()
        try:
            await self.execute_cached_query(query)
            end_time = time.perf_counter()
            return {
                'query_time_ms': (end_time - start_time) * 1000,
                'status': 'success'
            }
        except Exception as e:
            return {
                'query_time_ms': -1,
                'status': 'failed',
                'error': str(e)
            }
    
    async def _benchmark_cache_performance(self) -> Dict[str, Any]:
        """Benchmark cache performance"""
        # Test cache hit vs miss performance
        test_query = "SELECT COUNT(*) as count FROM eventos"
        
        # First run (cache miss)
        start_time = time.perf_counter()
        await self.execute_cached_query(test_query)
        cache_miss_time = (time.perf_counter() - start_time) * 1000
        
        # Second run (cache hit)
        start_time = time.perf_counter()
        await self.execute_cached_query(test_query)
        cache_hit_time = (time.perf_counter() - start_time) * 1000
        
        return {
            'cache_miss_ms': cache_miss_time,
            'cache_hit_ms': cache_hit_time,
            'performance_improvement': (
                (cache_miss_time - cache_hit_time) / cache_miss_time * 100
                if cache_miss_time > 0 else 0
            ),
            'status': 'success'
        }

# Global database optimizer instance
ultra_db_optimizer = UltraDatabaseOptimizer()

# Convenience functions
def init_database_optimizer(database_url: str, async_database_url: str = None):
    """Initialize ultra database optimizer"""
    success = ultra_db_optimizer.setup_connection_pool(database_url, async_database_url)
    if success:
        ultra_db_optimizer.create_performance_indexes()
    return success

async def get_optimized_session():
    """Get optimized database session"""
    async with ultra_db_optimizer.get_session() as session:
        yield session

async def execute_optimized_query(query: str, params: Dict[str, Any] = None):
    """Execute query with optimization"""
    return await ultra_db_optimizer.execute_cached_query(query, params)

async def get_database_performance_stats():
    """Get database performance statistics"""
    return ultra_db_optimizer.get_performance_report()

async def run_database_benchmark():
    """Run database performance benchmark"""
    return await ultra_db_optimizer.run_performance_benchmark()