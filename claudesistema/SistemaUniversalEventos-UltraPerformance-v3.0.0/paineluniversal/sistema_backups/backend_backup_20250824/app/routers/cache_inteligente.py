"""
Router para Sistema de Cache Inteligente
Endpoints para gerenciar cache distribuído e otimização
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..services.cache_inteligente import CacheInteligenteService, TipoCache, EstrategiaCache, PrioridadeCache
from ..schemas.responses import Response

router = APIRouter(prefix="/cache", tags=["Cache Inteligente"])

# Instância global do serviço
cache_service = CacheInteligenteService()

@router.on_event("startup")
async def startup_cache():
    """Inicia serviço de cache automaticamente"""
    await cache_service.iniciar_servico()

@router.on_event("shutdown")
async def shutdown_cache():
    """Para serviço de cache"""
    await cache_service.parar_servico()

@router.get("/dashboard", summary="Dashboard de Cache")
async def obter_dashboard_cache():
    """
    Retorna dashboard principal com estatísticas de cache.
    
    Inclui:
    - Resumo geral do cache
    - Estatísticas por área
    - Performance e hit rates
    - Recomendações de otimização
    """
    try:
        estatisticas = cache_service.obter_estatisticas_cache()
        
        return Response(
            success=True,
            message="Dashboard de cache obtido com sucesso",
            data=estatisticas
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dashboard: {str(e)}")

@router.get("/areas", summary="Áreas de Cache")
async def obter_areas_cache():
    """
    Retorna todas as áreas de cache configuradas.
    """
    try:
        areas = {}
        for area in cache_service.areas_cache.keys():
            config = cache_service.configuracoes[area]
            metrics = cache_service.metricas[area]
            
            areas[area] = {
                "configuracao": {
                    "nome": config.nome,
                    "tipo": config.tipo,
                    "estrategia": config.estrategia,
                    "tamanho_max_mb": config.tamanho_max_mb,
                    "ttl_padrao_segundos": config.ttl_padrao_segundos,
                    "prioridade": config.prioridade,
                    "compressao": config.compressao,
                    "persistencia": config.persistencia
                },
                "estatisticas": {
                    "items": metrics.items_total,
                    "tamanho_mb": round(metrics.tamanho_atual_mb, 2),
                    "hits": metrics.hits,
                    "misses": metrics.misses,
                    "hit_rate": round(metrics.hits / (metrics.hits + metrics.misses) * 100, 2) if metrics.hits + metrics.misses > 0 else 0
                }
            }
        
        return Response(
            success=True,
            message="Áreas de cache obtidas com sucesso",
            data={
                "total_areas": len(areas),
                "areas": areas
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter áreas: {str(e)}")

@router.get("/areas/{area}/items", summary="Itens de uma Área")
async def obter_items_area(
    area: str,
    limite: int = Query(50, ge=1, le=500, description="Limite de itens retornados")
):
    """
    Retorna itens de uma área específica de cache.
    
    Parâmetros:
    - area: Nome da área de cache
    - limite: Número máximo de itens (1-500)
    """
    try:
        if area not in cache_service.areas_cache:
            raise HTTPException(status_code=404, detail="Área de cache não encontrada")
        
        items = cache_service.obter_items_area(area, limite)
        
        return Response(
            success=True,
            message="Itens da área obtidos com sucesso",
            data={
                "area": area,
                "total_items": len(items),
                "items": items
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter itens: {str(e)}")

@router.post("/set", summary="Armazenar Item no Cache")
async def set_cache_item(dados: Dict[str, Any]):
    """
    Armazena um item no cache.
    
    Corpo da requisição:
    ```json
    {
        "area": "dados_usuario",
        "chave": "user_123_profile",
        "valor": {"nome": "João", "email": "joao@email.com"},
        "ttl": 3600,
        "tags": ["usuario", "perfil"],
        "prioridade": "alta"
    }
    ```
    """
    try:
        # Validações
        campos_obrigatorios = ["area", "chave", "valor"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                raise HTTPException(status_code=400, detail=f"Campo obrigatório: {campo}")
        
        area = dados["area"]
        chave = dados["chave"]
        valor = dados["valor"]
        ttl = dados.get("ttl")
        tags = dados.get("tags", [])
        prioridade = PrioridadeCache(dados["prioridade"]) if "prioridade" in dados else None
        
        sucesso = await cache_service.set(area, chave, valor, ttl, tags, prioridade)
        
        if not sucesso:
            raise HTTPException(status_code=400, detail="Falha ao armazenar item no cache")
        
        return Response(
            success=True,
            message="Item armazenado no cache com sucesso",
            data={
                "area": area,
                "chave": chave,
                "armazenado_em": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao armazenar item: {str(e)}")

@router.get("/get/{area}/{chave}", summary="Recuperar Item do Cache")
async def get_cache_item(area: str, chave: str):
    """
    Recupera um item do cache.
    
    Parâmetros:
    - area: Nome da área de cache
    - chave: Chave do item
    """
    try:
        valor = await cache_service.get(area, chave)
        
        if valor is None:
            return Response(
                success=False,
                message="Item não encontrado no cache",
                data=None
            )
        
        return Response(
            success=True,
            message="Item recuperado do cache com sucesso",
            data={
                "area": area,
                "chave": chave,
                "valor": valor,
                "recuperado_em": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar item: {str(e)}")

@router.delete("/delete/{area}/{chave}", summary="Remover Item do Cache")
async def delete_cache_item(area: str, chave: str):
    """
    Remove um item específico do cache.
    
    Parâmetros:
    - area: Nome da área de cache
    - chave: Chave do item
    """
    try:
        sucesso = await cache_service.delete(area, chave)
        
        if not sucesso:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        
        return Response(
            success=True,
            message="Item removido do cache com sucesso",
            data={
                "area": area,
                "chave": chave,
                "removido_em": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover item: {str(e)}")

@router.delete("/delete-by-tags/{area}", summary="Remover Itens por Tags")
async def delete_cache_by_tags(area: str, tags: Dict[str, List[str]]):
    """
    Remove itens do cache baseado em tags.
    
    Parâmetros:
    - area: Nome da área de cache
    
    Corpo da requisição:
    ```json
    {
        "tags": ["usuario", "temporario"]
    }
    ```
    """
    try:
        if "tags" not in tags or not tags["tags"]:
            raise HTTPException(status_code=400, detail="Lista de tags é obrigatória")
        
        items_removidos = await cache_service.delete_by_tags(area, tags["tags"])
        
        return Response(
            success=True,
            message=f"{items_removidos} itens removidos do cache",
            data={
                "area": area,
                "tags": tags["tags"],
                "items_removidos": items_removidos,
                "removidos_em": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover itens: {str(e)}")

@router.delete("/clear/{area}", summary="Limpar Área de Cache")
async def clear_cache_area(area: str):
    """
    Limpa completamente uma área de cache.
    
    Parâmetros:
    - area: Nome da área de cache
    """
    try:
        sucesso = await cache_service.clear_area(area)
        
        if not sucesso:
            raise HTTPException(status_code=404, detail="Área de cache não encontrada")
        
        return Response(
            success=True,
            message="Área de cache limpa com sucesso",
            data={
                "area": area,
                "limpa_em": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar área: {str(e)}")

@router.get("/estatisticas/performance", summary="Estatísticas de Performance")
async def obter_estatisticas_performance():
    """
    Retorna estatísticas detalhadas de performance do cache.
    """
    try:
        estatisticas = cache_service.obter_estatisticas_cache()
        
        # Calcula métricas adicionais de performance
        total_requests = sum(
            area["metricas"]["hits"] + area["metricas"]["misses"]
            for area in estatisticas["areas"].values()
        )
        
        total_hits = sum(
            area["metricas"]["hits"]
            for area in estatisticas["areas"].values()
        )
        
        performance_detalhada = {
            "overview": {
                "hit_rate_global": round((total_hits / total_requests * 100) if total_requests > 0 else 0, 2),
                "requests_total": total_requests,
                "memory_efficiency": estatisticas["performance"]["cache_efficiency"],
                "areas_ativas": len([a for a in estatisticas["areas"].values() if a["metricas"]["items"] > 0])
            },
            "por_area": {},
            "trends": {
                "areas_com_melhor_performance": [],
                "areas_precisando_otimizacao": [],
                "recomendacoes": estatisticas["performance"]["optimization_opportunities"]
            }
        }
        
        # Analisa performance por área
        for area, dados in estatisticas["areas"].items():
            hit_rate = dados["metricas"]["hit_rate"]
            utilizacao = dados["metricas"]["utilizacao"]
            
            performance_detalhada["por_area"][area] = {
                "hit_rate": hit_rate,
                "utilizacao_memoria": utilizacao,
                "eficiencia": "alta" if hit_rate > 80 else "media" if hit_rate > 50 else "baixa",
                "pressao_memoria": "alta" if utilizacao > 80 else "media" if utilizacao > 50 else "baixa"
            }
            
            # Identifica trends
            if hit_rate > 85:
                performance_detalhada["trends"]["areas_com_melhor_performance"].append(area)
            elif hit_rate < 50:
                performance_detalhada["trends"]["areas_precisando_otimizacao"].append(area)
        
        return Response(
            success=True,
            message="Estatísticas de performance obtidas com sucesso",
            data=performance_detalhada
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@router.get("/configuracoes/tipos", summary="Tipos e Estratégias Disponíveis")
async def obter_tipos_configuracoes():
    """
    Retorna tipos de cache e estratégias disponíveis.
    """
    try:
        configuracoes = {
            "tipos_cache": [
                {
                    "valor": tipo.value,
                    "nome": tipo.value.replace("_", " ").title(),
                    "descricao": {
                        "memoria": "Cache em memória RAM (mais rápido)",
                        "redis": "Cache distribuído com Redis",
                        "arquivo": "Cache persistente em arquivo",
                        "distribuido": "Cache distribuído entre múltiplos nós"
                    }.get(tipo.value, "Tipo de cache")
                }
                for tipo in TipoCache
            ],
            "estrategias": [
                {
                    "valor": estrategia.value,
                    "nome": estrategia.value.upper(),
                    "descricao": {
                        "lru": "Least Recently Used - Remove itens menos recentemente acessados",
                        "lfu": "Least Frequently Used - Remove itens menos frequentemente acessados",
                        "fifo": "First In, First Out - Remove itens mais antigos",
                        "ttl": "Time To Live - Remove itens baseado no tempo de vida",
                        "adaptativo": "Estratégia adaptativa baseada em padrões de uso"
                    }.get(estrategia.value, "Estratégia de cache")
                }
                for estrategia in EstrategiaCache
            ],
            "prioridades": [
                {
                    "valor": prioridade.value,
                    "nome": prioridade.value.title(),
                    "descricao": {
                        "baixa": "Prioridade baixa - primeiro a ser removido",
                        "normal": "Prioridade normal - comportamento padrão",
                        "alta": "Prioridade alta - protegido contra remoção",
                        "critica": "Prioridade crítica - persistido em shutdown"
                    }.get(prioridade.value, "Nível de prioridade")
                }
                for prioridade in PrioridadeCache
            ]
        }
        
        return Response(
            success=True,
            message="Configurações disponíveis obtidas com sucesso",
            data=configuracoes
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter configurações: {str(e)}")

@router.post("/otimizar", summary="Otimizar Cache Automaticamente")
async def otimizar_cache():
    """
    Executa otimização automática do cache baseada em padrões de uso.
    """
    try:
        # Simula otimização
        await cache_service._otimizar_cache_automatico()
        await cache_service._executar_limpeza_inteligente()
        
        estatisticas_pos = cache_service.obter_estatisticas_cache()
        
        return Response(
            success=True,
            message="Otimização de cache executada com sucesso",
            data={
                "otimizado_em": datetime.now().isoformat(),
                "areas_otimizadas": len(cache_service.areas_cache),
                "estatisticas_atuais": estatisticas_pos["resumo_geral"]
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao otimizar cache: {str(e)}")

@router.get("/health", summary="Saúde do Sistema de Cache")
async def obter_saude_cache():
    """
    Retorna indicadores de saúde do sistema de cache.
    """
    try:
        estatisticas = cache_service.obter_estatisticas_cache()
        
        # Calcula indicadores de saúde
        hit_rate_global = estatisticas["resumo_geral"]["hit_rate_geral"]
        memory_usage = sum(
            area["metricas"]["utilizacao"] for area in estatisticas["areas"].values()
        ) / len(estatisticas["areas"]) if estatisticas["areas"] else 0
        
        # Determina status geral
        if hit_rate_global > 80 and memory_usage < 80:
            status_geral = "saudável"
        elif hit_rate_global > 60 and memory_usage < 90:
            status_geral = "atenção"
        else:
            status_geral = "crítico"
        
        saude = {
            "status_geral": status_geral,
            "indicadores": {
                "hit_rate_global": hit_rate_global,
                "uso_memoria_medio": round(memory_usage, 1),
                "areas_funcionando": len([a for a in estatisticas["areas"].values() if a["metricas"]["items"] > 0]),
                "servico_ativo": estatisticas["resumo_geral"]["servico_ativo"]
            },
            "alertas": [],
            "recomendacoes": []
        }
        
        # Adiciona alertas
        if hit_rate_global < 50:
            saude["alertas"].append("Taxa de hit muito baixa - revisar estratégias de cache")
        
        if memory_usage > 85:
            saude["alertas"].append("Uso de memória alto - considerar aumentar limites ou limpeza")
        
        # Adiciona recomendações
        areas_baixa_performance = [
            area for area, dados in estatisticas["areas"].items()
            if dados["metricas"]["hit_rate"] < 50
        ]
        
        if areas_baixa_performance:
            saude["recomendacoes"].append(f"Otimizar áreas: {', '.join(areas_baixa_performance)}")
        
        return Response(
            success=True,
            message="Saúde do cache obtida com sucesso",
            data=saude
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter saúde: {str(e)}")
