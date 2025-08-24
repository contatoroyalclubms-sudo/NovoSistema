"""
Redis Caching Service - Sprint 5
Sistema Universal de Gestão de Eventos

Sistema avançado de cache com:
- Cache inteligente por TTL
- Invalidação por padrões
- Compressão automática
- Clusters distribuídos
- Métricas de cache
- Estratégias de cache-aside
"""

import asyncio
import json
import gzip
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
import redis.asyncio as redis
from redis.asyncio import Redis
from contextlib import asynccontextmanager
import hashlib
import logging

logger = logging.getLogger(__name__)


class CacheStrategy:
    """Estratégias de cache disponíveis"""
    CACHE_ASIDE = "cache_aside"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    REFRESH_AHEAD = "refresh_ahead"


class RedisCacheService:
    """
    Serviço avançado de cache Redis com funcionalidades enterprise
    """
    
    def __init__(self, 
                 redis_url: str = "redis://localhost:6379",
                 prefix: str = "eventos_cache:",
                 default_ttl: int = 3600):
        self.redis_url = redis_url
        self.prefix = prefix
        self.default_ttl = default_ttl
        self.redis_client: Optional[Redis] = None
        
        # Métricas de cache
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        
        # Configurações de compressão
        self.compression_threshold = 1024  # Comprimir dados > 1KB
        self.max_value_size = 50 * 1024 * 1024  # Máximo 50MB por chave
        
    async def connect(self) -> bool:
        """Conecta ao Redis"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False,  # Para permitir dados binários
                health_check_interval=30,
                socket_keepalive=True,
                socket_keepalive_options={},
                retry_on_timeout=True,
                retry_on_error=[redis.ConnectionError, redis.TimeoutError]
            )
            
            # Testar conexão
            await self.redis_client.ping()
            logger.info("🔗 Conectado ao Redis com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao Redis: {e}")
            self.redis_client = None
            return False
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info("👋 Desconectado do Redis")
    
    def _make_key(self, key: str) -> str:
        """Cria chave com prefixo"""
        return f"{self.prefix}{key}"
    
    def _hash_key(self, data: Any) -> str:
        """Cria hash MD5 para chaves complexas"""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serializa dados para armazenamento"""
        try:
            # Tentar JSON primeiro (mais eficiente)
            json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            serialized = json_data.encode('utf-8')
            method = b'json'
        except (TypeError, ValueError):
            # Fallback para pickle
            serialized = pickle.dumps(data)
            method = b'pickle'
        
        # Comprimir se necessário
        if len(serialized) > self.compression_threshold:
            compressed = gzip.compress(serialized)
            # Só usar compressão se realmente economizar espaço
            if len(compressed) < len(serialized) * 0.9:  # Pelo menos 10% de economia
                return method + b':gzip:' + compressed
        
        return method + b':raw:' + serialized
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserializa dados do cache"""
        try:
            parts = data.split(b':', 2)
            if len(parts) != 3:
                raise ValueError("Invalid data format")
                
            method, compression, payload = parts
            
            # Descompressão se necessário
            if compression == b'gzip':
                payload = gzip.decompress(payload)
            
            # Deserialização baseada no método
            if method == b'json':
                return json.loads(payload.decode('utf-8'))
            elif method == b'pickle':
                return pickle.loads(payload)
            else:
                raise ValueError(f"Unknown serialization method: {method}")
                
        except Exception as e:
            logger.error(f"Erro na deserialização: {e}")
            raise
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Obtém valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor deserializado ou None se não encontrado
        """
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._make_key(key)
            data = await self.redis_client.get(cache_key)
            
            if data is None:
                self.cache_stats['misses'] += 1
                return None
            
            self.cache_stats['hits'] += 1
            return self._deserialize_data(data)
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Erro ao obter chave {key}: {e}")
            return None
    
    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl: Optional[int] = None,
                  nx: bool = False,
                  xx: bool = False) -> bool:
        """
        Define valor no cache
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl: Tempo de vida em segundos
            nx: Só define se a chave NÃO existe
            xx: Só define se a chave JÁ existe
            
        Returns:
            True se operação foi bem-sucedida
        """
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._make_key(key)
            serialized_data = self._serialize_data(value)
            
            # Verificar tamanho máximo
            if len(serialized_data) > self.max_value_size:
                logger.warning(f"Valor muito grande para cache: {len(serialized_data)} bytes")
                return False
            
            ttl_seconds = ttl if ttl is not None else self.default_ttl
            
            result = await self.redis_client.set(
                cache_key,
                serialized_data,
                ex=ttl_seconds,
                nx=nx,
                xx=xx
            )
            
            if result:
                self.cache_stats['sets'] += 1
                return True
            else:
                return False
                
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Erro ao definir chave {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Remove chave do cache"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._make_key(key)
            result = await self.redis_client.delete(cache_key)
            
            if result > 0:
                self.cache_stats['deletes'] += 1
                return True
            return False
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Erro ao deletar chave {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Remove múltiplas chaves por padrão
        
        Args:
            pattern: Padrão de chave (ex: 'user:*')
            
        Returns:
            Número de chaves removidas
        """
        if not self.redis_client:
            return 0
            
        try:
            cache_pattern = self._make_key(pattern)
            
            # Usar SCAN para encontrar chaves (mais eficiente que KEYS)
            deleted_count = 0
            async for key in self.redis_client.scan_iter(match=cache_pattern, count=100):
                await self.redis_client.delete(key)
                deleted_count += 1
            
            self.cache_stats['deletes'] += deleted_count
            return deleted_count
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Erro ao deletar padrão {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._make_key(key)
            result = await self.redis_client.exists(cache_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Erro ao verificar existência de {key}: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Define tempo de expiração para chave existente"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._make_key(key)
            result = await self.redis_client.expire(cache_key, seconds)
            return result
            
        except Exception as e:
            logger.error(f"Erro ao definir expiração para {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """
        Obtém tempo restante de vida de uma chave
        
        Returns:
            Segundos restantes, -1 se não tem TTL, -2 se chave não existe
        """
        if not self.redis_client:
            return -2
            
        try:
            cache_key = self._make_key(key)
            result = await self.redis_client.ttl(cache_key)
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter TTL de {key}: {e}")
            return -2
    
    # ================================
    # MÉTODOS DE CACHE AVANÇADO
    # ================================
    
    async def get_or_set(self, 
                        key: str, 
                        factory: Callable, 
                        ttl: Optional[int] = None,
                        force_refresh: bool = False) -> Any:
        """
        Padrão cache-aside: obtém do cache ou calcula e armazena
        
        Args:
            key: Chave do cache
            factory: Função que calcula o valor se não estiver no cache
            ttl: Tempo de vida personalizado
            force_refresh: Forçar recálculo mesmo se existir no cache
            
        Returns:
            Valor do cache ou calculado
        """
        # Verificar cache primeiro (a não ser que force_refresh seja True)
        if not force_refresh:
            cached_value = await self.get(key)
            if cached_value is not None:
                return cached_value
        
        # Calcular valor
        try:
            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()
            
            # Armazenar no cache
            await self.set(key, value, ttl)
            return value
            
        except Exception as e:
            logger.error(f"Erro no get_or_set para {key}: {e}")
            # Se falhar, tentar retornar valor do cache mesmo se expirado
            if force_refresh:
                cached_value = await self.get(key)
                if cached_value is not None:
                    return cached_value
            raise
    
    async def cached_function(self, 
                             ttl: int = 3600,
                             key_pattern: str = None):
        """
        Decorator para cache automático de funções
        
        Args:
            ttl: Tempo de vida do cache
            key_pattern: Padrão para gerar chave (usa argumentos se None)
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Gerar chave do cache
                if key_pattern:
                    cache_key = key_pattern.format(*args, **kwargs)
                else:
                    key_data = {
                        'func': func.__name__,
                        'args': args,
                        'kwargs': kwargs
                    }
                    cache_key = f"func:{func.__name__}:{self._hash_key(key_data)}"
                
                # Usar get_or_set
                return await self.get_or_set(
                    cache_key,
                    lambda: func(*args, **kwargs) if not asyncio.iscoroutinefunction(func) else func(*args, **kwargs),
                    ttl
                )
            
            return wrapper
        return decorator
    
    async def multi_get(self, keys: List[str]) -> Dict[str, Any]:
        """
        Obtém múltiplas chaves de uma vez
        
        Args:
            keys: Lista de chaves
            
        Returns:
            Dict com valores encontrados
        """
        if not self.redis_client or not keys:
            return {}
            
        try:
            cache_keys = [self._make_key(key) for key in keys]
            values = await self.redis_client.mget(cache_keys)
            
            result = {}
            for i, value in enumerate(values):
                if value is not None:
                    try:
                        result[keys[i]] = self._deserialize_data(value)
                        self.cache_stats['hits'] += 1
                    except Exception as e:
                        logger.error(f"Erro ao deserializar {keys[i]}: {e}")
                        self.cache_stats['errors'] += 1
                else:
                    self.cache_stats['misses'] += 1
            
            return result
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Erro no multi_get: {e}")
            return {}
    
    async def multi_set(self, 
                       items: Dict[str, Any], 
                       ttl: Optional[int] = None) -> bool:
        """
        Define múltiplas chaves de uma vez
        
        Args:
            items: Dict com chave -> valor
            ttl: Tempo de vida para todas as chaves
            
        Returns:
            True se todas as operações foram bem-sucedidas
        """
        if not self.redis_client or not items:
            return True
            
        try:
            pipe = self.redis_client.pipeline()
            
            for key, value in items.items():
                cache_key = self._make_key(key)
                serialized_data = self._serialize_data(value)
                
                if len(serialized_data) > self.max_value_size:
                    logger.warning(f"Valor muito grande ignorado: {key}")
                    continue
                
                ttl_seconds = ttl if ttl is not None else self.default_ttl
                pipe.setex(cache_key, ttl_seconds, serialized_data)
            
            results = await pipe.execute()
            
            # Contar sucessos
            success_count = sum(1 for result in results if result)
            self.cache_stats['sets'] += success_count
            
            return success_count == len(items)
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Erro no multi_set: {e}")
            return False
    
    # ================================
    # MÉTODOS DE GERENCIAMENTO
    # ================================
    
    async def flush_all(self) -> bool:
        """Remove todos os dados do cache (use com cuidado!)"""
        if not self.redis_client:
            return False
            
        try:
            await self.redis_client.flushdb()
            logger.warning("🗑️ Cache Redis completamente limpo")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False
    
    async def get_info(self) -> Dict[str, Any]:
        """Obtém informações do servidor Redis"""
        if not self.redis_client:
            return {}
            
        try:
            info = await self.redis_client.info()
            return {
                'redis_version': info.get('redis_version'),
                'used_memory_human': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses'),
                'our_stats': self.cache_stats
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter info do Redis: {e}")
            return {'our_stats': self.cache_stats}
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        total_operations = sum(self.cache_stats.values())
        hit_rate = 0
        
        if self.cache_stats['hits'] + self.cache_stats['misses'] > 0:
            hit_rate = self.cache_stats['hits'] / (self.cache_stats['hits'] + self.cache_stats['misses']) * 100
        
        return {
            **self.cache_stats,
            'hit_rate_percent': round(hit_rate, 2),
            'total_operations': total_operations,
            'error_rate_percent': round((self.cache_stats['errors'] / total_operations * 100) if total_operations > 0 else 0, 2)
        }
    
    # ================================
    # CONTEXT MANAGERS
    # ================================
    
    @asynccontextmanager
    async def pipeline(self):
        """Context manager para operações em pipeline"""
        if not self.redis_client:
            raise RuntimeError("Redis não está conectado")
        
        pipe = self.redis_client.pipeline()
        try:
            yield pipe
            await pipe.execute()
        except Exception as e:
            logger.error(f"Erro no pipeline: {e}")
            raise
    
    @asynccontextmanager
    async def lock(self, key: str, timeout: int = 10, blocking_timeout: int = None):
        """Context manager para locks distribuídos"""
        if not self.redis_client:
            raise RuntimeError("Redis não está conectado")
        
        lock_key = self._make_key(f"lock:{key}")
        lock = self.redis_client.lock(
            lock_key, 
            timeout=timeout, 
            blocking_timeout=blocking_timeout
        )
        
        try:
            await lock.acquire()
            yield lock
        finally:
            try:
                await lock.release()
            except Exception:
                pass  # Lock pode ter expirado


# ================================
# CACHE ESPECÍFICO PARA EVENTOS
# ================================

class EventsCacheService(RedisCacheService):
    """Cache especializado para o sistema de eventos"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = "eventos:"
    
    # Cache de eventos
    async def cache_event(self, event_id: str, event_data: Dict, ttl: int = 3600):
        """Cache dados do evento"""
        return await self.set(f"event:{event_id}", event_data, ttl)
    
    async def get_cached_event(self, event_id: str) -> Optional[Dict]:
        """Obtém evento do cache"""
        return await self.get(f"event:{event_id}")
    
    async def invalidate_event_cache(self, event_id: str):
        """Invalida cache relacionado ao evento"""
        await self.delete_pattern(f"event:{event_id}*")
        await self.delete_pattern(f"participants:{event_id}*")
        await self.delete_pattern(f"analytics:{event_id}*")
    
    # Cache de participantes
    async def cache_participants(self, event_id: str, participants: List[Dict], ttl: int = 1800):
        """Cache lista de participantes"""
        return await self.set(f"participants:{event_id}", participants, ttl)
    
    async def get_cached_participants(self, event_id: str) -> Optional[List[Dict]]:
        """Obtém participantes do cache"""
        return await self.get(f"participants:{event_id}")
    
    # Cache de analytics
    async def cache_analytics(self, key: str, data: Dict, ttl: int = 300):
        """Cache dados de analytics (TTL menor por serem mais dinâmicos)"""
        return await self.set(f"analytics:{key}", data, ttl)
    
    async def get_cached_analytics(self, key: str) -> Optional[Dict]:
        """Obtém analytics do cache"""
        return await self.get(f"analytics:{key}")


# ================================
# INSTÂNCIAS GLOBAIS
# ================================

# Instância principal do cache
redis_cache = RedisCacheService()

# Cache especializado para eventos
events_cache = EventsCacheService()

# Funções de inicialização
async def init_redis_cache(redis_url: str = "redis://localhost:6379"):
    """Inicializa conexão com Redis"""
    redis_cache.redis_url = redis_url
    events_cache.redis_url = redis_url
    
    redis_connected = await redis_cache.connect()
    events_connected = await events_cache.connect()
    
    if redis_connected and events_connected:
        logger.info("✅ Sistema de cache Redis inicializado")
        return True
    else:
        logger.error("❌ Falha na inicialização do cache Redis")
        return False

async def close_redis_cache():
    """Fecha conexões Redis"""
    await redis_cache.disconnect()
    await events_cache.disconnect()
    logger.info("👋 Conexões Redis fechadas")