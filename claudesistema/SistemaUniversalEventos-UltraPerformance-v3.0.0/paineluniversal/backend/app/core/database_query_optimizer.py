"""
Database Query Optimizer - AI-Powered Query Enhancement
Advanced features: Query analysis, index recommendations, automatic optimization
"""

import asyncio
import json
import logging
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import re

from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select, Insert, Update, Delete
from sqlalchemy.engine import Result
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa

logger = logging.getLogger(__name__)

@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query_hash: str
    query_type: str
    execution_time: float
    rows_affected: int
    cpu_cost: float
    memory_usage: int
    cache_hits: int
    cache_misses: int
    index_usage: List[str]
    timestamp: datetime
    optimization_score: float = 0.0

@dataclass
class IndexRecommendation:
    """Database index recommendation"""
    table_name: str
    columns: List[str]
    index_type: str
    estimated_performance_gain: float
    query_patterns: List[str]
    priority: str  # 'high', 'medium', 'low'
    size_estimate: int  # bytes

class QueryPattern:
    """Query pattern analysis for optimization"""
    
    def __init__(self):
        self.patterns = {
            'frequent_filters': defaultdict(int),
            'join_patterns': defaultdict(int),
            'sort_patterns': defaultdict(int),
            'aggregate_patterns': defaultdict(int),
            'subquery_patterns': defaultdict(int)
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to identify optimization opportunities"""
        query_upper = query.upper()
        
        analysis = {
            'type': self._get_query_type(query_upper),
            'complexity': self._calculate_complexity(query_upper),
            'tables': self._extract_tables(query_upper),
            'filters': self._extract_filters(query),
            'joins': self._extract_joins(query_upper),
            'sorts': self._extract_sorts(query_upper),
            'aggregates': self._extract_aggregates(query_upper),
            'estimated_cost': self._estimate_cost(query_upper)
        }
        
        # Update patterns
        self._update_patterns(analysis)
        
        return analysis
    
    def _get_query_type(self, query: str) -> str:
        """Identify query type"""
        if query.strip().startswith('SELECT'):
            if 'COUNT(' in query:
                return 'SELECT_COUNT'
            elif 'JOIN' in query:
                return 'SELECT_JOIN'
            elif 'GROUP BY' in query:
                return 'SELECT_GROUP'
            return 'SELECT_SIMPLE'
        elif query.strip().startswith('INSERT'):
            return 'INSERT'
        elif query.strip().startswith('UPDATE'):
            return 'UPDATE'
        elif query.strip().startswith('DELETE'):
            return 'DELETE'
        return 'OTHER'
    
    def _calculate_complexity(self, query: str) -> int:
        """Calculate query complexity score"""
        complexity = 0
        
        # Base complexity
        complexity += query.count('SELECT') * 10
        complexity += query.count('JOIN') * 20
        complexity += query.count('SUBSELECT') * 30
        complexity += query.count('UNION') * 25
        complexity += query.count('GROUP BY') * 15
        complexity += query.count('ORDER BY') * 10
        complexity += query.count('HAVING') * 15
        complexity += query.count('CASE WHEN') * 5
        
        # Function complexity
        complexity += query.count('COUNT(') * 5
        complexity += query.count('SUM(') * 5
        complexity += query.count('AVG(') * 10
        complexity += query.count('MAX(') * 5
        complexity += query.count('MIN(') * 5
        
        return complexity
    
    def _extract_tables(self, query: str) -> List[str]:
        """Extract table names from query"""
        tables = []
        
        # Simple regex patterns for table extraction
        from_pattern = re.compile(r'FROM\s+(\w+)', re.IGNORECASE)
        join_pattern = re.compile(r'JOIN\s+(\w+)', re.IGNORECASE)
        update_pattern = re.compile(r'UPDATE\s+(\w+)', re.IGNORECASE)
        insert_pattern = re.compile(r'INSERT\s+INTO\s+(\w+)', re.IGNORECASE)
        
        tables.extend(from_pattern.findall(query))
        tables.extend(join_pattern.findall(query))
        tables.extend(update_pattern.findall(query))
        tables.extend(insert_pattern.findall(query))
        
        return list(set(tables))
    
    def _extract_filters(self, query: str) -> List[str]:
        """Extract WHERE conditions for index recommendations"""
        filters = []
        
        # Find WHERE clause
        where_match = re.search(r'WHERE\s+(.*?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1)
            
            # Extract column conditions
            column_conditions = re.findall(r'(\w+)\s*(?:=|<|>|<=|>=|LIKE|IN)\s*', where_clause, re.IGNORECASE)
            filters.extend(column_conditions)
        
        return filters
    
    def _extract_joins(self, query: str) -> List[str]:
        """Extract JOIN patterns"""
        joins = []
        join_patterns = re.findall(r'(\w+\s+JOIN\s+\w+\s+ON\s+[\w\.]+\s*=\s*[\w\.]+)', query, re.IGNORECASE)
        joins.extend(join_patterns)
        return joins
    
    def _extract_sorts(self, query: str) -> List[str]:
        """Extract ORDER BY columns"""
        sorts = []
        order_match = re.search(r'ORDER\s+BY\s+(.*?)(?:\s+LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
        if order_match:
            order_clause = order_match.group(1)
            sort_columns = re.findall(r'(\w+)', order_clause)
            sorts.extend(sort_columns)
        return sorts
    
    def _extract_aggregates(self, query: str) -> List[str]:
        """Extract aggregate functions"""
        aggregates = []
        agg_patterns = re.findall(r'(COUNT|SUM|AVG|MAX|MIN)\s*\(\s*(\w+)\s*\)', query, re.IGNORECASE)
        aggregates.extend([f"{func}({col})" for func, col in agg_patterns])
        return aggregates
    
    def _estimate_cost(self, query: str) -> int:
        """Estimate query execution cost"""
        base_cost = 100
        
        # Table scan costs
        base_cost += query.count('FROM') * 1000
        base_cost += query.count('JOIN') * 2000
        
        # Function costs
        base_cost += query.count('COUNT(') * 500
        base_cost += query.count('SUM(') * 300
        base_cost += query.count('AVG(') * 600
        
        # Sort costs
        base_cost += query.count('ORDER BY') * 800
        base_cost += query.count('GROUP BY') * 1000
        
        return base_cost
    
    def _update_patterns(self, analysis: Dict[str, Any]):
        """Update pattern statistics"""
        # Update frequent filters
        for filter_col in analysis['filters']:
            self.patterns['frequent_filters'][filter_col] += 1
        
        # Update join patterns
        for join in analysis['joins']:
            self.patterns['join_patterns'][join] += 1
        
        # Update sort patterns
        for sort_col in analysis['sorts']:
            self.patterns['sort_patterns'][sort_col] += 1
        
        # Update aggregate patterns
        for agg in analysis['aggregates']:
            self.patterns['aggregate_patterns'][agg] += 1

class IntelligentQueryOptimizer:
    """AI-powered query optimization system"""
    
    def __init__(self):
        self.query_metrics: Dict[str, List[QueryMetrics]] = defaultdict(list)
        self.query_patterns = QueryPattern()
        self.index_recommendations: List[IndexRecommendation] = []
        self.optimization_cache: Dict[str, str] = {}
        self.performance_baselines: Dict[str, float] = {}
        
    def register_query_execution(
        self,
        query: str,
        execution_time: float,
        rows_affected: int = 0,
        result_info: Optional[Dict[str, Any]] = None
    ):
        """Register query execution for analysis"""
        query_hash = self._hash_query(query)
        
        # Analyze query patterns
        analysis = self.query_patterns.analyze_query(query)
        
        # Create metrics
        metrics = QueryMetrics(
            query_hash=query_hash,
            query_type=analysis['type'],
            execution_time=execution_time,
            rows_affected=rows_affected,
            cpu_cost=analysis['estimated_cost'],
            memory_usage=result_info.get('memory_usage', 0) if result_info else 0,
            cache_hits=result_info.get('cache_hits', 0) if result_info else 0,
            cache_misses=result_info.get('cache_misses', 0) if result_info else 0,
            index_usage=result_info.get('indexes_used', []) if result_info else [],
            timestamp=datetime.now(),
            optimization_score=self._calculate_optimization_score(analysis, execution_time)
        )
        
        self.query_metrics[query_hash].append(metrics)
        
        # Keep only recent metrics (last 1000 executions per query)
        if len(self.query_metrics[query_hash]) > 1000:
            self.query_metrics[query_hash] = self.query_metrics[query_hash][-1000:]
        
        # Update performance baselines
        self._update_baselines(query_hash, execution_time)
        
        # Generate recommendations if query is slow
        if execution_time > 0.1:  # 100ms threshold
            self._generate_optimization_recommendations(query, analysis, metrics)
    
    def _hash_query(self, query: str) -> str:
        """Generate consistent hash for query (normalized)"""
        # Normalize query for consistent hashing
        normalized = re.sub(r'\s+', ' ', query.upper().strip())
        normalized = re.sub(r'=\s*[\'"]\w+[\'"]', '= ?', normalized)  # Replace values with placeholders
        normalized = re.sub(r'IN\s*\([^)]+\)', 'IN (?)', normalized)  # Replace IN clauses
        
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _calculate_optimization_score(self, analysis: Dict[str, Any], execution_time: float) -> float:
        """Calculate optimization score (0-100)"""
        score = 100.0
        
        # Penalize slow queries
        if execution_time > 1.0:
            score -= 50
        elif execution_time > 0.5:
            score -= 30
        elif execution_time > 0.1:
            score -= 15
        
        # Penalize complex queries without proper optimization
        complexity = analysis['complexity']
        if complexity > 100:
            score -= min(30, complexity / 10)
        
        # Reward simple, fast queries
        if execution_time < 0.01 and complexity < 50:
            score = min(100, score + 10)
        
        return max(0, score)
    
    def _update_baselines(self, query_hash: str, execution_time: float):
        """Update performance baselines"""
        if query_hash not in self.performance_baselines:
            self.performance_baselines[query_hash] = execution_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.performance_baselines[query_hash] = (
                alpha * execution_time + 
                (1 - alpha) * self.performance_baselines[query_hash]
            )
    
    def _generate_optimization_recommendations(
        self,
        query: str,
        analysis: Dict[str, Any],
        metrics: QueryMetrics
    ):
        """Generate optimization recommendations for slow queries"""
        recommendations = []
        
        # Index recommendations based on filters
        for table in analysis['tables']:
            for filter_col in analysis['filters']:
                if filter_col not in [idx.columns[0] for idx in self.index_recommendations 
                                     if idx.table_name == table]:
                    rec = IndexRecommendation(
                        table_name=table,
                        columns=[filter_col],
                        index_type='btree',
                        estimated_performance_gain=min(80, metrics.execution_time * 50),
                        query_patterns=[analysis['type']],
                        priority='high' if metrics.execution_time > 1.0 else 'medium',
                        size_estimate=1024 * 1024  # 1MB estimate
                    )
                    recommendations.append(rec)
        
        # Composite index recommendations for joins
        if analysis['joins'] and len(analysis['tables']) > 1:
            for table in analysis['tables']:
                join_columns = self._extract_join_columns(analysis['joins'], table)
                if join_columns:
                    rec = IndexRecommendation(
                        table_name=table,
                        columns=join_columns,
                        index_type='btree',
                        estimated_performance_gain=min(90, metrics.execution_time * 60),
                        query_patterns=['JOIN'],
                        priority='high',
                        size_estimate=2 * 1024 * 1024  # 2MB estimate
                    )
                    recommendations.append(rec)
        
        # Sort index recommendations
        if analysis['sorts']:
            for table in analysis['tables']:
                for sort_col in analysis['sorts']:
                    rec = IndexRecommendation(
                        table_name=table,
                        columns=[sort_col],
                        index_type='btree',
                        estimated_performance_gain=min(60, metrics.execution_time * 30),
                        query_patterns=['ORDER_BY'],
                        priority='medium',
                        size_estimate=512 * 1024  # 512KB estimate
                    )
                    recommendations.append(rec)
        
        # Add unique recommendations to the list
        for rec in recommendations:
            if not any(
                existing.table_name == rec.table_name and 
                existing.columns == rec.columns 
                for existing in self.index_recommendations
            ):
                self.index_recommendations.append(rec)
    
    def _extract_join_columns(self, joins: List[str], table: str) -> List[str]:
        """Extract join columns for a specific table"""
        columns = []
        for join in joins:
            if table.upper() in join.upper():
                # Extract column names from join condition
                match = re.search(rf'{table}\.(\w+)', join, re.IGNORECASE)
                if match:
                    columns.append(match.group(1))
        return columns
    
    async def optimize_query(self, query: str) -> Tuple[str, List[str]]:
        """Apply automatic query optimizations"""
        query_hash = self._hash_query(query)
        
        # Check cache first
        if query_hash in self.optimization_cache:
            return self.optimization_cache[query_hash], []
        
        optimized_query = query
        optimizations_applied = []
        
        # Apply optimizations based on patterns
        analysis = self.query_patterns.analyze_query(query)
        
        # 1. Add LIMIT if missing for potentially large result sets
        if ('SELECT' in query.upper() and 
            'LIMIT' not in query.upper() and 
            'COUNT(' not in query.upper()):
            optimized_query += " LIMIT 1000"
            optimizations_applied.append("Added default LIMIT")
        
        # 2. Optimize ORDER BY with LIMIT
        if ('ORDER BY' in query.upper() and 
            'LIMIT' in query.upper() and 
            'OFFSET' not in query.upper()):
            # Suggest using offset pagination for better performance
            optimizations_applied.append("Consider using cursor-based pagination")
        
        # 3. Optimize COUNT queries
        if 'SELECT COUNT(*)' in query.upper():
            # Suggest using approximate counts for very large tables
            optimizations_applied.append("Consider using estimated counts for large tables")
        
        # 4. Optimize EXISTS vs IN
        if ' IN (SELECT ' in query.upper():
            optimized_query = re.sub(
                r'(\w+)\s+IN\s*\(\s*SELECT\s+(\w+)\s+FROM\s+(\w+)([^)]*)\)',
                r'EXISTS (SELECT 1 FROM \3 WHERE \3.\2 = \1\4)',
                optimized_query,
                flags=re.IGNORECASE
            )
            optimizations_applied.append("Replaced IN subquery with EXISTS")
        
        # Cache the optimization
        self.optimization_cache[query_hash] = optimized_query
        
        return optimized_query, optimizations_applied
    
    async def analyze_database_performance(self, session: AsyncSession) -> Dict[str, Any]:
        """Comprehensive database performance analysis"""
        try:
            analysis = {
                'query_performance': await self._analyze_query_performance(),
                'index_recommendations': [asdict(rec) for rec in self.get_top_index_recommendations()],
                'slow_queries': await self._get_slow_queries(),
                'resource_usage': await self._analyze_resource_usage(session),
                'optimization_opportunities': await self._find_optimization_opportunities(),
                'performance_trends': self._analyze_performance_trends(),
                'timestamp': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Database performance analysis error: {e}")
            return {'error': str(e)}
    
    async def _analyze_query_performance(self) -> Dict[str, Any]:
        """Analyze overall query performance"""
        if not self.query_metrics:
            return {'message': 'No query metrics available'}
        
        all_metrics = []
        for metrics_list in self.query_metrics.values():
            all_metrics.extend(metrics_list)
        
        if not all_metrics:
            return {'message': 'No query metrics available'}
        
        # Calculate statistics
        execution_times = [m.execution_time for m in all_metrics]
        optimization_scores = [m.optimization_score for m in all_metrics]
        
        return {
            'total_queries_analyzed': len(all_metrics),
            'average_execution_time': sum(execution_times) / len(execution_times),
            'median_execution_time': sorted(execution_times)[len(execution_times) // 2],
            'slowest_execution_time': max(execution_times),
            'fastest_execution_time': min(execution_times),
            'average_optimization_score': sum(optimization_scores) / len(optimization_scores),
            'queries_needing_optimization': len([s for s in optimization_scores if s < 70]),
            'performance_grade': self._calculate_performance_grade(optimization_scores)
        }
    
    def get_top_index_recommendations(self, limit: int = 10) -> List[IndexRecommendation]:
        """Get top index recommendations by performance impact"""
        return sorted(
            self.index_recommendations,
            key=lambda x: x.estimated_performance_gain,
            reverse=True
        )[:limit]
    
    async def _get_slow_queries(self) -> List[Dict[str, Any]]:
        """Get list of slowest queries"""
        slow_queries = []
        
        for query_hash, metrics_list in self.query_metrics.items():
            if metrics_list:
                latest_metrics = metrics_list[-1]
                avg_time = sum(m.execution_time for m in metrics_list) / len(metrics_list)
                
                if avg_time > 0.1:  # 100ms threshold
                    slow_queries.append({
                        'query_hash': query_hash,
                        'query_type': latest_metrics.query_type,
                        'average_execution_time': avg_time,
                        'latest_execution_time': latest_metrics.execution_time,
                        'execution_count': len(metrics_list),
                        'optimization_score': latest_metrics.optimization_score
                    })
        
        return sorted(slow_queries, key=lambda x: x['average_execution_time'], reverse=True)[:20]
    
    async def _analyze_resource_usage(self, session: AsyncSession) -> Dict[str, Any]:
        """Analyze database resource usage"""
        try:
            # Get database statistics
            stats_query = text("""
                SELECT 
                    datname as database_name,
                    numbackends as active_connections,
                    xact_commit as transactions_committed,
                    xact_rollback as transactions_rolled_back,
                    blks_read as blocks_read,
                    blks_hit as blocks_hit,
                    tup_returned as tuples_returned,
                    tup_fetched as tuples_fetched,
                    tup_inserted as tuples_inserted,
                    tup_updated as tuples_updated,
                    tup_deleted as tuples_deleted
                FROM pg_stat_database 
                WHERE datname = current_database()
            """)
            
            result = await session.execute(stats_query)
            db_stats = result.fetchone()
            
            if db_stats:
                return {
                    'database_name': db_stats.database_name,
                    'active_connections': db_stats.active_connections,
                    'transactions': {
                        'committed': db_stats.transactions_committed,
                        'rolled_back': db_stats.transactions_rolled_back,
                        'success_rate': (
                            db_stats.transactions_committed / 
                            (db_stats.transactions_committed + db_stats.transactions_rolled_back) * 100
                        ) if (db_stats.transactions_committed + db_stats.transactions_rolled_back) > 0 else 0
                    },
                    'cache_performance': {
                        'blocks_read': db_stats.blocks_read,
                        'blocks_hit': db_stats.blocks_hit,
                        'hit_ratio': (
                            db_stats.blocks_hit / (db_stats.blocks_read + db_stats.blocks_hit) * 100
                        ) if (db_stats.blocks_read + db_stats.blocks_hit) > 0 else 0
                    },
                    'tuple_operations': {
                        'returned': db_stats.tuples_returned,
                        'fetched': db_stats.tuples_fetched,
                        'inserted': db_stats.tuples_inserted,
                        'updated': db_stats.tuples_updated,
                        'deleted': db_stats.tuples_deleted
                    }
                }
            
            return {'message': 'No resource usage data available'}
            
        except Exception as e:
            logger.error(f"Resource usage analysis error: {e}")
            return {'error': str(e)}
    
    async def _find_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Find optimization opportunities"""
        opportunities = []
        
        # Analyze query patterns for optimization
        patterns = self.query_patterns.patterns
        
        # Frequent filter opportunities
        frequent_filters = sorted(
            patterns['frequent_filters'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        for column, count in frequent_filters:
            opportunities.append({
                'type': 'index_opportunity',
                'description': f"Column '{column}' is frequently filtered ({count} times)",
                'recommendation': f"Consider adding index on {column}",
                'impact': 'medium' if count < 100 else 'high',
                'effort': 'low'
            })
        
        # Join pattern opportunities
        frequent_joins = sorted(
            patterns['join_patterns'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        for join_pattern, count in frequent_joins:
            opportunities.append({
                'type': 'join_optimization',
                'description': f"Frequent join pattern detected ({count} times)",
                'recommendation': "Consider optimizing join order or adding composite indexes",
                'impact': 'high',
                'effort': 'medium'
            })
        
        return opportunities
    
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if not self.query_metrics:
            return {'message': 'No trend data available'}
        
        # Get metrics from last 24 hours
        now = datetime.now()
        recent_metrics = []
        
        for metrics_list in self.query_metrics.values():
            recent_metrics.extend([
                m for m in metrics_list 
                if m.timestamp > now - timedelta(hours=24)
            ])
        
        if not recent_metrics:
            return {'message': 'No recent metrics available'}
        
        # Group by hour
        hourly_performance = defaultdict(list)
        for metrics in recent_metrics:
            hour_key = metrics.timestamp.strftime('%Y-%m-%d %H:00')
            hourly_performance[hour_key].append(metrics.execution_time)
        
        # Calculate hourly averages
        hourly_averages = {
            hour: sum(times) / len(times)
            for hour, times in hourly_performance.items()
        }
        
        return {
            'hourly_performance': hourly_averages,
            'performance_degradation': self._detect_performance_degradation(hourly_averages),
            'peak_hours': sorted(hourly_averages.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    def _detect_performance_degradation(self, hourly_averages: Dict[str, float]) -> bool:
        """Detect if performance is degrading"""
        if len(hourly_averages) < 4:
            return False
        
        values = list(hourly_averages.values())
        recent = values[-2:]
        baseline = values[:-2]
        
        recent_avg = sum(recent) / len(recent)
        baseline_avg = sum(baseline) / len(baseline)
        
        # If recent performance is 50% worse than baseline
        return recent_avg > baseline_avg * 1.5
    
    def _calculate_performance_grade(self, scores: List[float]) -> str:
        """Calculate overall performance grade"""
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 90:
            return 'A+'
        elif avg_score >= 80:
            return 'A'
        elif avg_score >= 70:
            return 'B'
        elif avg_score >= 60:
            return 'C'
        elif avg_score >= 50:
            return 'D'
        else:
            return 'F'
    
    def get_optimizer_stats(self) -> Dict[str, Any]:
        """Get optimizer statistics"""
        return {
            'queries_analyzed': sum(len(metrics) for metrics in self.query_metrics.values()),
            'unique_queries': len(self.query_metrics),
            'index_recommendations': len(self.index_recommendations),
            'optimization_cache_size': len(self.optimization_cache),
            'performance_baselines': len(self.performance_baselines),
            'patterns': {
                'frequent_filters': len(self.query_patterns.patterns['frequent_filters']),
                'join_patterns': len(self.query_patterns.patterns['join_patterns']),
                'sort_patterns': len(self.query_patterns.patterns['sort_patterns']),
                'aggregate_patterns': len(self.query_patterns.patterns['aggregate_patterns'])
            }
        }

# Global query optimizer instance
query_optimizer = IntelligentQueryOptimizer()

# Decorator for automatic query optimization
def optimize_query_execution(session_getter=None):
    """Decorator to automatically optimize and monitor query execution"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = None
            error = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = e
                raise
            finally:
                execution_time = time.time() - start_time
                
                # Try to extract query information
                try:
                    # This is a simplified approach - in real implementation,
                    # you'd need to intercept SQL queries more sophisticatedly
                    if hasattr(func, '__name__'):
                        query_info = f"Function: {func.__name__}"
                        query_optimizer.register_query_execution(
                            query_info,
                            execution_time,
                            rows_affected=getattr(result, 'rowcount', 0) if result else 0
                        )
                except Exception as e:
                    logger.debug(f"Query optimization tracking error: {e}")
        
        return wrapper
    return decorator

async def get_query_optimizer_stats():
    """Get query optimizer statistics"""
    return query_optimizer.get_optimizer_stats()

async def analyze_database_performance(session: AsyncSession):
    """Get comprehensive database performance analysis"""
    return await query_optimizer.analyze_database_performance(session)

async def get_optimization_recommendations():
    """Get top optimization recommendations"""
    return {
        'index_recommendations': [asdict(rec) for rec in query_optimizer.get_top_index_recommendations()],
        'optimizer_stats': query_optimizer.get_optimizer_stats()
    }