"""
Sistema de Cache Inteligente
Gerencia cache distribuído com estratégias adaptáveis
"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import hashlib
import pickle
import time
from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict
import uuid

class TipoCache(str, Enum):
    """Tipos de cache disponíveis"""
    MEMORIA = "memoria"
    REDIS = "redis"
    ARQUIVO = "arquivo"
    DISTRIBUIDO = "distribuido"

class EstrategiaCache(str, Enum):
    """Estratégias de cache"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live
    ADAPTATIVO = "adaptativo"

class PrioridadeCache(str, Enum):
    """Prioridades de cache"""
    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    CRITICA = "critica"

@dataclass
class ConfigCache:
    """Configuração de uma área de cache"""
    nome: str
    tipo: TipoCache
    estrategia: EstrategiaCache
    tamanho_max_mb: int
    ttl_padrao_segundos: int
    prioridade: PrioridadeCache
    compressao: bool = False
    persistencia: bool = False
    replicacao: bool = False

@dataclass
class ItemCache:
    """Item armazenado no cache"""
    chave: str
    valor: Any
    criado_em: datetime
    ultimo_acesso: datetime
    acessos: int = 0
    ttl_segundos: Optional[int] = None
    tamanho_bytes: int = 0
    tags: List[str] = field(default_factory=list)
    prioridade: PrioridadeCache = PrioridadeCache.NORMAL

@dataclass
class MetricasCache:
    """Métricas de performance do cache"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    tamanho_atual_mb: float = 0
    items_total: int = 0
    ultima_limpeza: Optional[datetime] = None

class CacheInteligenteService:
    """Service para cache inteligente com múltiplas estratégias"""
    
    def __init__(self):
        self.areas_cache = {}
        self.configuracoes = {}
        self.metricas = defaultdict(MetricasCache)
        self.analisador_patterns = PatternAnalyzer()
        self._limpeza_automatica_ativa = False
        
        # Inicializa áreas padrão
        self._inicializar_areas_padrao()
    
    def _inicializar_areas_padrao(self):
        """Inicializa áreas de cache padrão"""
        areas_padrao = [
            ConfigCache(
                nome="dados_usuario",
                tipo=TipoCache.MEMORIA,
                estrategia=EstrategiaCache.LRU,
                tamanho_max_mb=50,
                ttl_padrao_segundos=3600,  # 1 hora
                prioridade=PrioridadeCache.ALTA,
                compressao=True
            ),
            ConfigCache(
                nome="consultas_db",
                tipo=TipoCache.MEMORIA,
                estrategia=EstrategiaCache.ADAPTATIVO,
                tamanho_max_mb=100,
                ttl_padrao_segundos=1800,  # 30 minutos
                prioridade=PrioridadeCache.NORMAL,
                compressao=True,
                persistencia=True
            ),
            ConfigCache(
                nome="relatorios",
                tipo=TipoCache.ARQUIVO,
                estrategia=EstrategiaCache.TTL,
                tamanho_max_mb=200,
                ttl_padrao_segundos=7200,  # 2 horas
                prioridade=PrioridadeCache.NORMAL,
                compressao=True,
                persistencia=True
            ),
            ConfigCache(
                nome="sessoes",
                tipo=TipoCache.MEMORIA,
                estrategia=EstrategiaCache.LRU,
                tamanho_max_mb=25,
                ttl_padrao_segundos=86400,  # 24 horas
                prioridade=PrioridadeCache.CRITICA
            ),
            ConfigCache(
                nome="configuracoes",
                tipo=TipoCache.MEMORIA,
                estrategia=EstrategiaCache.FIFO,
                tamanho_max_mb=10,
                ttl_padrao_segundos=3600,  # 1 hora
                prioridade=PrioridadeCache.ALTA,
                persistencia=True
            )
        ]
        
        for config in areas_padrao:
            self._criar_area_cache(config)
    
    def _criar_area_cache(self, config: ConfigCache):
        """Cria uma nova área de cache"""
        self.configuracoes[config.nome] = config
        
        if config.estrategia == EstrategiaCache.LRU:
            self.areas_cache[config.nome] = OrderedDict()
        else:
            self.areas_cache[config.nome] = {}
        
        self.metricas[config.nome] = MetricasCache()
    
    async def iniciar_servico(self):
        """Inicia serviços de cache"""
        if not self._limpeza_automatica_ativa:
            self._limpeza_automatica_ativa = True
            asyncio.create_task(self._loop_limpeza_automatica())
        
        print("✅ Serviço de cache inteligente iniciado")
    
    async def parar_servico(self):
        """Para serviços de cache"""
        self._limpeza_automatica_ativa = False
        
        # Persiste dados críticos
        await self._persistir_dados_criticos()
        print("🔄 Serviço de cache parado")
    
    async def _loop_limpeza_automatica(self):
        """Loop de limpeza automática do cache"""
        while self._limpeza_automatica_ativa:
            try:
                await self._executar_limpeza_inteligente()
                await self._otimizar_cache_automatico()
                await self._analisar_patterns_uso()
                
                # Executa limpeza a cada 5 minutos
                await asyncio.sleep(300)
                
            except Exception as e:
                print(f"Erro na limpeza automática: {e}")
                await asyncio.sleep(300)
    
    async def set(
        self,
        area: str,
        chave: str,
        valor: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
        prioridade: Optional[PrioridadeCache] = None
    ) -> bool:
        """
        Armazena item no cache
        
        Args:
            area: Nome da área de cache
            chave: Chave única do item
            valor: Valor a ser armazenado
            ttl: Time to live em segundos (opcional)
            tags: Tags para organização (opcional)
            prioridade: Prioridade do item (opcional)
        """
        if area not in self.areas_cache:
            return False
        
        config = self.configuracoes[area]
        cache_area = self.areas_cache[area]
        
        # Calcula tamanho do item
        tamanho_bytes = len(str(valor).encode('utf-8'))
        
        # Verifica se precisa liberar espaço
        if await self._precisa_liberar_espaco(area, tamanho_bytes):
            await self._liberar_espaco(area, tamanho_bytes)
        
        # Cria item de cache
        item = ItemCache(
            chave=chave,
            valor=valor,
            criado_em=datetime.now(),
            ultimo_acesso=datetime.now(),
            acessos=1,
            ttl_segundos=ttl or config.ttl_padrao_segundos,
            tamanho_bytes=tamanho_bytes,
            tags=tags or [],
            prioridade=prioridade or config.prioridade
        )
        
        # Armazena no cache
        if config.estrategia == EstrategiaCache.LRU:
            cache_area[chave] = item
            cache_area.move_to_end(chave)
        else:
            cache_area[chave] = item
        
        # Atualiza métricas
        metrics = self.metricas[area]
        metrics.items_total += 1
        metrics.tamanho_atual_mb += tamanho_bytes / (1024 * 1024)
        
        # Registra padrão de uso
        self.analisador_patterns.registrar_escrita(area, chave, tags or [])
        
        return True
    
    async def get(self, area: str, chave: str) -> Optional[Any]:
        """
        Recupera item do cache
        
        Args:
            area: Nome da área de cache
            chave: Chave do item
        """
        if area not in self.areas_cache:
            return None
        
        cache_area = self.areas_cache[area]
        config = self.configuracoes[area]
        
        if chave not in cache_area:
            # Cache miss
            self.metricas[area].misses += 1
            return None
        
        item = cache_area[chave]
        
        # Verifica se item expirou
        if self._item_expirado(item):
            await self._remover_item(area, chave)
            self.metricas[area].misses += 1
            return None
        
        # Atualiza estatísticas de acesso
        item.ultimo_acesso = datetime.now()
        item.acessos += 1
        
        # Move para o final se LRU
        if config.estrategia == EstrategiaCache.LRU:
            cache_area.move_to_end(chave)
        
        # Cache hit
        self.metricas[area].hits += 1
        
        # Registra padrão de uso
        self.analisador_patterns.registrar_leitura(area, chave)
        
        return item.valor
    
    async def delete(self, area: str, chave: str) -> bool:
        """Remove item do cache"""
        if area not in self.areas_cache or chave not in self.areas_cache[area]:
            return False
        
        await self._remover_item(area, chave)
        return True
    
    async def delete_by_tags(self, area: str, tags: List[str]) -> int:
        """Remove itens por tags"""
        if area not in self.areas_cache:
            return 0
        
        cache_area = self.areas_cache[area]
        chaves_remover = []
        
        for chave, item in cache_area.items():
            if any(tag in item.tags for tag in tags):
                chaves_remover.append(chave)
        
        for chave in chaves_remover:
            await self._remover_item(area, chave)
        
        return len(chaves_remover)
    
    async def clear_area(self, area: str) -> bool:
        """Limpa uma área de cache completamente"""
        if area not in self.areas_cache:
            return False
        
        self.areas_cache[area].clear()
        self.metricas[area] = MetricasCache()
        
        return True
    
    def _item_expirado(self, item: ItemCache) -> bool:
        """Verifica se um item expirou"""
        if not item.ttl_segundos:
            return False
        
        idade = (datetime.now() - item.criado_em).total_seconds()
        return idade > item.ttl_segundos
    
    async def _remover_item(self, area: str, chave: str):
        """Remove um item do cache e atualiza métricas"""
        if area not in self.areas_cache or chave not in self.areas_cache[area]:
            return
        
        item = self.areas_cache[area][chave]
        del self.areas_cache[area][chave]
        
        # Atualiza métricas
        metrics = self.metricas[area]
        metrics.items_total -= 1
        metrics.tamanho_atual_mb -= item.tamanho_bytes / (1024 * 1024)
    
    async def _precisa_liberar_espaco(self, area: str, tamanho_novo: int) -> bool:
        """Verifica se precisa liberar espaço"""
        config = self.configuracoes[area]
        metrics = self.metricas[area]
        
        tamanho_novo_mb = tamanho_novo / (1024 * 1024)
        return (metrics.tamanho_atual_mb + tamanho_novo_mb) > config.tamanho_max_mb
    
    async def _liberar_espaco(self, area: str, espaco_necessario: int):
        """Libera espaço no cache baseado na estratégia"""
        config = self.configuracoes[area]
        cache_area = self.areas_cache[area]
        
        espaco_liberado = 0
        itens_removidos = 0
        
        if config.estrategia == EstrategiaCache.LRU:
            # Remove itens menos recentemente usados
            while espaco_liberado < espaco_necessario and cache_area:
                chave, item = cache_area.popitem(last=False)
                espaco_liberado += item.tamanho_bytes
                itens_removidos += 1
                
        elif config.estrategia == EstrategiaCache.LFU:
            # Remove itens menos frequentemente usados
            itens_ordenados = sorted(cache_area.items(), key=lambda x: x[1].acessos)
            for chave, item in itens_ordenados:
                if espaco_liberado >= espaco_necessario:
                    break
                await self._remover_item(area, chave)
                espaco_liberado += item.tamanho_bytes
                itens_removidos += 1
                
        elif config.estrategia == EstrategiaCache.FIFO:
            # Remove itens mais antigos
            itens_ordenados = sorted(cache_area.items(), key=lambda x: x[1].criado_em)
            for chave, item in itens_ordenados:
                if espaco_liberado >= espaco_necessario:
                    break
                await self._remover_item(area, chave)
                espaco_liberado += item.tamanho_bytes
                itens_removidos += 1
        
        # Atualiza métricas
        self.metricas[area].evictions += itens_removidos
    
    async def _executar_limpeza_inteligente(self):
        """Executa limpeza inteligente de itens expirados"""
        for area in self.areas_cache:
            cache_area = self.areas_cache[area]
            chaves_expiradas = []
            
            for chave, item in cache_area.items():
                if self._item_expirado(item):
                    chaves_expiradas.append(chave)
            
            for chave in chaves_expiradas:
                await self._remover_item(area, chave)
            
            if chaves_expiradas:
                self.metricas[area].ultima_limpeza = datetime.now()
    
    async def _otimizar_cache_automatico(self):
        """Otimiza configurações de cache automaticamente"""
        for area in self.areas_cache:
            metrics = self.metricas[area]
            config = self.configuracoes[area]
            
            if metrics.hits + metrics.misses == 0:
                continue
            
            hit_rate = metrics.hits / (metrics.hits + metrics.misses)
            
            # Ajusta TTL baseado na taxa de hit
            if hit_rate < 0.5:
                # Hit rate baixo - aumenta TTL
                config.ttl_padrao_segundos = min(config.ttl_padrao_segundos * 1.2, 86400)
            elif hit_rate > 0.9:
                # Hit rate muito alto - pode diminuir TTL
                config.ttl_padrao_segundos = max(config.ttl_padrao_segundos * 0.9, 300)
    
    async def _analisar_patterns_uso(self):
        """Analisa padrões de uso para otimização"""
        self.analisador_patterns.analisar_patterns()
    
    async def _persistir_dados_criticos(self):
        """Persiste dados críticos antes do shutdown"""
        for area, config in self.configuracoes.items():
            if config.persistencia and config.prioridade == PrioridadeCache.CRITICA:
                # Simula persistência
                pass
    
    def obter_estatisticas_cache(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas do cache"""
        estatisticas = {
            "resumo_geral": {
                "areas_total": len(self.areas_cache),
                "items_total": sum(m.items_total for m in self.metricas.values()),
                "tamanho_total_mb": round(sum(m.tamanho_atual_mb for m in self.metricas.values()), 2),
                "hit_rate_geral": 0,
                "servico_ativo": self._limpeza_automatica_ativa
            },
            "areas": {},
            "performance": {},
            "recomendacoes": []
        }
        
        total_hits = sum(m.hits for m in self.metricas.values())
        total_misses = sum(m.misses for m in self.metricas.values())
        
        if total_hits + total_misses > 0:
            estatisticas["resumo_geral"]["hit_rate_geral"] = round(
                total_hits / (total_hits + total_misses) * 100, 2
            )
        
        # Estatísticas por área
        for area, metrics in self.metricas.items():
            config = self.configuracoes[area]
            hit_rate = 0
            
            if metrics.hits + metrics.misses > 0:
                hit_rate = round(metrics.hits / (metrics.hits + metrics.misses) * 100, 2)
            
            estatisticas["areas"][area] = {
                "configuracao": {
                    "tipo": config.tipo,
                    "estrategia": config.estrategia,
                    "tamanho_max_mb": config.tamanho_max_mb,
                    "ttl_padrao": config.ttl_padrao_segundos,
                    "prioridade": config.prioridade
                },
                "metricas": {
                    "items": metrics.items_total,
                    "tamanho_mb": round(metrics.tamanho_atual_mb, 2),
                    "hits": metrics.hits,
                    "misses": metrics.misses,
                    "evictions": metrics.evictions,
                    "hit_rate": hit_rate,
                    "utilizacao": round((metrics.tamanho_atual_mb / config.tamanho_max_mb) * 100, 1),
                    "ultima_limpeza": metrics.ultima_limpeza.isoformat() if metrics.ultima_limpeza else None
                }
            }
        
        # Performance geral
        estatisticas["performance"] = {
            "cache_efficiency": "alta" if estatisticas["resumo_geral"]["hit_rate_geral"] > 80 else "media",
            "memory_pressure": "baixa",  # Calculado baseado na utilização
            "optimization_opportunities": self.analisador_patterns.obter_oportunidades()
        }
        
        return estatisticas
    
    def obter_items_area(self, area: str, limite: int = 50) -> List[Dict[str, Any]]:
        """Retorna itens de uma área específica"""
        if area not in self.areas_cache:
            return []
        
        cache_area = self.areas_cache[area]
        items = []
        
        for chave, item in list(cache_area.items())[:limite]:
            items.append({
                "chave": chave,
                "tamanho_bytes": item.tamanho_bytes,
                "criado_em": item.criado_em.isoformat(),
                "ultimo_acesso": item.ultimo_acesso.isoformat(),
                "acessos": item.acessos,
                "ttl_segundos": item.ttl_segundos,
                "tags": item.tags,
                "prioridade": item.prioridade,
                "expirado": self._item_expirado(item)
            })
        
        return items

class PatternAnalyzer:
    """Analisador de padrões de uso do cache"""
    
    def __init__(self):
        self.patterns_leitura = defaultdict(int)
        self.patterns_escrita = defaultdict(int)
        self.tags_populares = defaultdict(int)
        self.horarios_pico = defaultdict(int)
    
    def registrar_leitura(self, area: str, chave: str):
        """Registra padrão de leitura"""
        self.patterns_leitura[f"{area}:{chave}"] += 1
        hora = datetime.now().hour
        self.horarios_pico[hora] += 1
    
    def registrar_escrita(self, area: str, chave: str, tags: List[str]):
        """Registra padrão de escrita"""
        self.patterns_escrita[f"{area}:{chave}"] += 1
        for tag in tags:
            self.tags_populares[tag] += 1
    
    def analisar_patterns(self):
        """Analisa padrões coletados"""
        # Simula análise de padrões
        pass
    
    def obter_oportunidades(self) -> List[str]:
        """Retorna oportunidades de otimização"""
        oportunidades = []
        
        # Chaves mais acessadas
        if self.patterns_leitura:
            chave_mais_acessada = max(self.patterns_leitura.items(), key=lambda x: x[1])
            if chave_mais_acessada[1] > 100:
                oportunidades.append(f"Considere cache persistente para: {chave_mais_acessada[0]}")
        
        # Tags populares
        if self.tags_populares:
            tag_popular = max(self.tags_populares.items(), key=lambda x: x[1])
            if tag_popular[1] > 50:
                oportunidades.append(f"Otimize cache para tag: {tag_popular[0]}")
        
        return oportunidades
