"""
Router para Sistema de Monitoramento em Tempo Real
Endpoints para métricas, alertas e dashboard
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio

from ..services.monitoramento import MonitoramentoService, TipoMetrica, StatusMetrica
from ..schemas.responses import Response

router = APIRouter(prefix="/monitoramento", tags=["Monitoramento"])

# Instância global do serviço
monitoramento_service = MonitoramentoService()

# Gerenciador de conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        monitoramento_service.subscribers.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        if websocket in monitoramento_service.subscribers:
            monitoramento_service.subscribers.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                await self.disconnect(connection)

manager = ConnectionManager()

@router.on_event("startup")
async def startup_monitoramento():
    """Inicia coleta de métricas automaticamente"""
    await monitoramento_service.iniciar_coleta()

@router.on_event("shutdown")
async def shutdown_monitoramento():
    """Para coleta de métricas"""
    await monitoramento_service.parar_coleta()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para atualizações em tempo real"""
    await manager.connect(websocket)
    try:
        while True:
            # Envia dados atuais
            dashboard_data = monitoramento_service.obter_dashboard_metricas()
            await websocket.send_text(json.dumps({
                "type": "dashboard_update",
                "data": dashboard_data
            }))
            
            await asyncio.sleep(5)  # Atualiza a cada 5 segundos
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.get("/dashboard", summary="Dashboard Principal")
async def obter_dashboard():
    """
    Retorna dados principais do dashboard de monitoramento.
    
    Inclui:
    - Saúde geral do sistema
    - Métricas principais agrupadas por tipo
    - Alertas ativos
    - Estatísticas resumidas
    """
    try:
        dashboard = monitoramento_service.obter_dashboard_metricas()
        
        return Response(
            success=True,
            message="Dashboard obtido com sucesso",
            data=dashboard
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dashboard: {str(e)}")

@router.get("/metricas", summary="Métricas Ativas")
async def obter_metricas_ativas(
    tipo: Optional[TipoMetrica] = Query(None, description="Filtrar por tipo de métrica")
):
    """
    Retorna todas as métricas ativas do sistema.
    
    Parâmetros:
    - tipo: Filtrar métricas por tipo (performance, negocio, sistema, etc.)
    """
    try:
        metricas = monitoramento_service.obter_metricas_ativas()
        
        if tipo:
            metricas = {
                k: v for k, v in metricas.items() 
                if v["tipo"] == tipo
            }
        
        return Response(
            success=True,
            message="Métricas obtidas com sucesso",
            data={
                "total": len(metricas),
                "metricas": metricas,
                "ultima_atualizacao": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter métricas: {str(e)}")

@router.get("/metricas/{metrica_id}/historico", summary="Histórico de Métrica")
async def obter_historico_metrica(
    metrica_id: str,
    limite: int = Query(100, ge=1, le=1000, description="Limite de pontos retornados")
):
    """
    Retorna histórico de uma métrica específica.
    
    Parâmetros:
    - metrica_id: ID da métrica
    - limite: Número máximo de pontos no histórico (1-1000)
    """
    try:
        historico = monitoramento_service.obter_historico_metrica(metrica_id, limite)
        
        if not historico:
            raise HTTPException(status_code=404, detail="Métrica não encontrada")
        
        # Calcula estatísticas do histórico
        valores = [h["valor"] for h in historico]
        estatisticas = {
            "pontos_total": len(valores),
            "valor_medio": sum(valores) / len(valores) if valores else 0,
            "valor_minimo": min(valores) if valores else 0,
            "valor_maximo": max(valores) if valores else 0,
            "ultimo_valor": valores[-1] if valores else 0
        }
        
        return Response(
            success=True,
            message="Histórico obtido com sucesso",
            data={
                "metrica_id": metrica_id,
                "historico": historico,
                "estatisticas": estatisticas
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter histórico: {str(e)}")

@router.get("/alertas", summary="Alertas Ativos")
async def obter_alertas_ativos():
    """
    Retorna todos os alertas ativos do sistema.
    """
    try:
        alertas = monitoramento_service.obter_alertas_ativos()
        
        # Agrupa alertas por nível
        alertas_por_nivel = {}
        for alerta in alertas:
            nivel = alerta["nivel"]
            if nivel not in alertas_por_nivel:
                alertas_por_nivel[nivel] = []
            alertas_por_nivel[nivel].append(alerta)
        
        return Response(
            success=True,
            message="Alertas obtidos com sucesso",
            data={
                "total": len(alertas),
                "alertas": alertas,
                "por_nivel": alertas_por_nivel
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter alertas: {str(e)}")

@router.post("/alertas/{alerta_id}/resolver", summary="Resolver Alerta")
async def resolver_alerta(alerta_id: str):
    """
    Marca um alerta como resolvido.
    
    Parâmetros:
    - alerta_id: ID do alerta a ser resolvido
    """
    try:
        sucesso = await monitoramento_service.resolver_alerta(alerta_id)
        
        if not sucesso:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
        
        return Response(
            success=True,
            message="Alerta resolvido com sucesso",
            data={"alerta_id": alerta_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao resolver alerta: {str(e)}")

@router.get("/relatorio/performance", summary="Relatório de Performance")
async def obter_relatorio_performance(
    periodo_horas: int = Query(24, ge=1, le=168, description="Período em horas (1-168)")
):
    """
    Gera relatório de performance do sistema.
    
    Parâmetros:
    - periodo_horas: Período do relatório em horas (máximo 1 semana)
    """
    try:
        relatorio = monitoramento_service.obter_relatorio_performance(periodo_horas)
        
        return Response(
            success=True,
            message="Relatório gerado com sucesso",
            data=relatorio
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

@router.get("/status/saude", summary="Status de Saúde do Sistema")
async def obter_status_saude():
    """
    Retorna status geral de saúde do sistema.
    """
    try:
        dashboard = monitoramento_service.obter_dashboard_metricas()
        
        # Calcula score de saúde
        saude_geral = dashboard["saude_geral"]
        uptime = dashboard.get("uptime_sistema", 0)
        alertas_ativos = dashboard.get("alertas_ativos", 0)
        
        score_saude = 100
        if saude_geral == "ATENÇÃO":
            score_saude = 75
        elif saude_geral == "CRÍTICO":
            score_saude = 25
        
        # Ajusta score baseado em uptime e alertas
        score_saude = min(100, score_saude * (uptime / 100) - (alertas_ativos * 5))
        
        status_detalhado = {
            "status_geral": saude_geral,
            "score_saude": max(0, score_saude),
            "uptime_percentual": uptime,
            "alertas_ativos": alertas_ativos,
            "componentes": {
                "api": "ONLINE" if dashboard.get("performance_api", 0) < 1000 else "DEGRADADO",
                "banco_dados": "ONLINE",  # Simulado
                "cache": "ONLINE",  # Simulado
                "monitoramento": "ONLINE"
            },
            "ultima_verificacao": datetime.now().isoformat()
        }
        
        return Response(
            success=True,
            message="Status de saúde obtido com sucesso",
            data=status_detalhado
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

@router.post("/alertas/configurar", summary="Configurar Alerta Personalizado")
async def configurar_alerta_personalizado(
    metrica_id: str,
    configuracao: Dict[str, Any]
):
    """
    Configura alerta personalizado para uma métrica.
    
    Corpo da requisição:
    ```json
    {
        "limites": {
            "warning": 70,
            "critical": 90
        },
        "tipo": "threshold"
    }
    ```
    """
    try:
        limites = configuracao.get("limites", {})
        tipo = configuracao.get("tipo", "threshold")
        
        if not limites:
            raise HTTPException(status_code=400, detail="Limites são obrigatórios")
        
        sucesso = monitoramento_service.configurar_alerta_personalizado(
            metrica_id, limites, tipo
        )
        
        return Response(
            success=True,
            message="Alerta configurado com sucesso",
            data={
                "metrica_id": metrica_id,
                "configuracao": configuracao
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao configurar alerta: {str(e)}")

@router.get("/metricas/tipos", summary="Tipos de Métricas Disponíveis")
async def obter_tipos_metricas():
    """
    Retorna os tipos de métricas disponíveis no sistema.
    """
    try:
        tipos = [
            {
                "valor": tipo.value,
                "nome": tipo.value.replace("_", " ").title(),
                "descricao": {
                    "performance": "Métricas de desempenho da aplicação",
                    "negocio": "Métricas de negócio e vendas",
                    "sistema": "Métricas de infraestrutura e sistema",
                    "usuario": "Métricas de usuários e comportamento",
                    "financeiro": "Métricas financeiras e receita",
                    "seguranca": "Métricas de segurança e compliance"
                }.get(tipo.value, "Métrica geral")
            }
            for tipo in TipoMetrica
        ]
        
        return Response(
            success=True,
            message="Tipos de métricas obtidos com sucesso",
            data={"tipos": tipos}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter tipos: {str(e)}")

@router.get("/estatisticas/resumo", summary="Estatísticas Resumidas")
async def obter_estatisticas_resumo():
    """
    Retorna estatísticas resumidas do sistema de monitoramento.
    """
    try:
        metricas_ativas = monitoramento_service.obter_metricas_ativas()
        alertas_ativos = monitoramento_service.obter_alertas_ativos()
        
        # Calcula estatísticas
        total_metricas = len(metricas_ativas)
        metricas_por_tipo = {}
        metricas_por_status = {}
        
        for metrica in metricas_ativas.values():
            tipo = metrica["tipo"]
            status = metrica["status"]
            
            metricas_por_tipo[tipo] = metricas_por_tipo.get(tipo, 0) + 1
            metricas_por_status[status] = metricas_por_status.get(status, 0) + 1
        
        alertas_por_nivel = {}
        for alerta in alertas_ativos:
            nivel = alerta["nivel"]
            alertas_por_nivel[nivel] = alertas_por_nivel.get(nivel, 0) + 1
        
        estatisticas = {
            "metricas": {
                "total": total_metricas,
                "por_tipo": metricas_por_tipo,
                "por_status": metricas_por_status
            },
            "alertas": {
                "total_ativos": len(alertas_ativos),
                "por_nivel": alertas_por_nivel
            },
            "sistema": {
                "tempo_execucao": "15 dias, 7 horas",  # Simulado
                "ultima_coleta": datetime.now().isoformat(),
                "frequencia_coleta": "30 segundos"
            }
        }
        
        return Response(
            success=True,
            message="Estatísticas obtidas com sucesso",
            data=estatisticas
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@router.post("/coleta/reiniciar", summary="Reiniciar Coleta de Métricas")
async def reiniciar_coleta():
    """
    Reinicia o processo de coleta de métricas.
    """
    try:
        await monitoramento_service.parar_coleta()
        await asyncio.sleep(1)  # Aguarda 1 segundo
        await monitoramento_service.iniciar_coleta()
        
        return Response(
            success=True,
            message="Coleta de métricas reiniciada com sucesso",
            data={"reiniciado_em": datetime.now().isoformat()}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reiniciar coleta: {str(e)}")

@router.get("/metricas/{metrica_id}/detalhes", summary="Detalhes de Métrica Específica")
async def obter_detalhes_metrica(metrica_id: str):
    """
    Retorna detalhes completos de uma métrica específica.
    
    Parâmetros:
    - metrica_id: ID da métrica
    """
    try:
        metricas = monitoramento_service.obter_metricas_ativas()
        
        if metrica_id not in metricas:
            raise HTTPException(status_code=404, detail="Métrica não encontrada")
        
        metrica = metricas[metrica_id]
        historico = monitoramento_service.obter_historico_metrica(metrica_id, 50)
        
        # Calcula tendência
        if len(historico) >= 2:
            valores_recentes = [h["valor"] for h in historico[-10:]]
            valores_anteriores = [h["valor"] for h in historico[-20:-10]] if len(historico) >= 20 else []
            
            if valores_anteriores:
                media_recente = sum(valores_recentes) / len(valores_recentes)
                media_anterior = sum(valores_anteriores) / len(valores_anteriores)
                
                if media_recente > media_anterior * 1.05:
                    tendencia = "subindo"
                elif media_recente < media_anterior * 0.95:
                    tendencia = "descendo"
                else:
                    tendencia = "estável"
            else:
                tendencia = "insuficiente"
        else:
            tendencia = "insuficiente"
        
        detalhes = {
            "metrica": metrica,
            "historico_recente": historico[-10:],  # Últimos 10 pontos
            "estatisticas": {
                "tendencia": tendencia,
                "coletas_total": len(historico),
                "ultima_coleta": historico[-1]["timestamp"] if historico else None
            },
            "configuracao_alerta": monitoramento_service.configuracoes_alerta.get(metrica_id, {})
        }
        
        return Response(
            success=True,
            message="Detalhes da métrica obtidos com sucesso",
            data=detalhes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter detalhes: {str(e)}")
