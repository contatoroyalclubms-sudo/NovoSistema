"""
Sistema de Monitoramento e Métricas em Tempo Real
Coleta, armazena e exibe métricas do sistema
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import uuid
from dataclasses import dataclass
from collections import defaultdict, deque

class TipoMetrica(str, Enum):
    """Tipos de métricas coletadas"""
    PERFORMANCE = "performance"
    NEGOCIO = "negocio"
    SISTEMA = "sistema"
    USUARIO = "usuario"
    FINANCEIRO = "financeiro"
    SEGURANCA = "seguranca"

class StatusMetrica(str, Enum):
    """Status de uma métrica"""
    NORMAL = "normal"
    ATENCAO = "atencao"
    CRITICO = "critico"
    INDISPONIVEL = "indisponivel"

@dataclass
class Metrica:
    """Classe para representar uma métrica"""
    id: str
    nome: str
    valor: float
    unidade: str
    tipo: TipoMetrica
    timestamp: datetime
    status: StatusMetrica
    metadata: Dict[str, Any]

@dataclass
class Alerta:
    """Classe para representar um alerta"""
    id: str
    metrica_id: str
    nivel: str  # INFO, WARNING, ERROR, CRITICAL
    titulo: str
    descricao: str
    criado_em: datetime
    resolvido: bool = False
    resolvido_em: Optional[datetime] = None

class MonitoramentoService:
    """Service para monitoramento e métricas em tempo real"""
    
    def __init__(self):
        self.metricas_ativas = {}
        self.historico_metricas = defaultdict(lambda: deque(maxlen=1000))
        self.alertas_ativos = {}
        self.configuracoes_alerta = self._inicializar_alertas()
        self.subscribers = []  # Para WebSocket
        self._coletando = False
        
    def _inicializar_alertas(self) -> Dict[str, Dict]:
        """Inicializa configurações de alertas"""
        return {
            "cpu_usage": {
                "limites": {"warning": 70, "critical": 90},
                "tipo": "threshold"
            },
            "memoria_usage": {
                "limites": {"warning": 80, "critical": 95},
                "tipo": "threshold"
            },
            "vendas_diarias": {
                "limites": {"warning": 50, "critical": 20},  # % abaixo da média
                "tipo": "percentage_below"
            },
            "tempo_resposta_api": {
                "limites": {"warning": 2000, "critical": 5000},  # ms
                "tipo": "threshold"
            },
            "falhas_pagamento": {
                "limites": {"warning": 5, "critical": 10},  # % de falhas
                "tipo": "percentage"
            }
        }
    
    async def iniciar_coleta(self):
        """Inicia coleta automática de métricas"""
        if self._coletando:
            return
        
        self._coletando = True
        asyncio.create_task(self._loop_coleta_metricas())
    
    async def parar_coleta(self):
        """Para coleta automática de métricas"""
        self._coletando = False
    
    async def _loop_coleta_metricas(self):
        """Loop principal de coleta de métricas"""
        while self._coletando:
            try:
                await self._coletar_metricas_sistema()
                await self._coletar_metricas_negocio()
                await self._coletar_metricas_performance()
                await self._verificar_alertas()
                await self._notificar_subscribers()
                
                await asyncio.sleep(30)  # Coleta a cada 30 segundos
                
            except Exception as e:
                print(f"Erro na coleta de métricas: {e}")
                await asyncio.sleep(60)  # Aguarda mais tempo em caso de erro
    
    async def _coletar_metricas_sistema(self):
        """Coleta métricas do sistema"""
        timestamp = datetime.now()
        
        # Simula coleta de métricas de sistema
        metricas_sistema = [
            Metrica(
                id="cpu_usage",
                nome="CPU Usage",
                valor=45.7 + (hash(str(timestamp)) % 30),  # Simula variação
                unidade="%",
                tipo=TipoMetrica.SISTEMA,
                timestamp=timestamp,
                status=StatusMetrica.NORMAL,
                metadata={"cores": 4, "frequency": "2.4GHz"}
            ),
            Metrica(
                id="memoria_usage",
                nome="Memory Usage",
                valor=62.3 + (hash(str(timestamp)) % 25),
                unidade="%",
                tipo=TipoMetrica.SISTEMA,
                timestamp=timestamp,
                status=StatusMetrica.NORMAL,
                metadata={"total_gb": 16, "available_gb": 6.1}
            ),
            Metrica(
                id="disco_usage",
                nome="Disk Usage",
                valor=78.5 + (hash(str(timestamp)) % 10),
                unidade="%",
                tipo=TipoMetrica.SISTEMA,
                timestamp=timestamp,
                status=StatusMetrica.NORMAL,
                metadata={"total_gb": 500, "free_gb": 107.5}
            ),
            Metrica(
                id="conexoes_ativas",
                nome="Conexões Ativas",
                valor=25 + (hash(str(timestamp)) % 50),
                unidade="conexões",
                tipo=TipoMetrica.SISTEMA,
                timestamp=timestamp,
                status=StatusMetrica.NORMAL,
                metadata={"max_conexoes": 1000}
            )
        ]
        
        for metrica in metricas_sistema:
            await self._registrar_metrica(metrica)
    
    async def _coletar_metricas_negocio(self):
        """Coleta métricas de negócio"""
        timestamp = datetime.now()
        
        # Simula métricas de negócio
        metricas_negocio = [
            Metrica(
                id="vendas_hoje",
                nome="Vendas Hoje",
                valor=1250.75 + (hash(str(timestamp)) % 500),
                unidade="R$",
                tipo=TipoMetrica.NEGOCIO,
                timestamp=timestamp,
                status=StatusMetrica.NORMAL,
                metadata={"meta_diaria": 2000, "transacoes": 45}
            ),
            Metrica(
                id="eventos_ativos",
                nome="Eventos Ativos",
                valor=8 + (hash(str(timestamp)) % 5),
                unidade="eventos",
                tipo=TipoMetrica.NEGOCIO,
                timestamp=timestamp,
                status=StatusMetrica.NORMAL,
                metadata={"eventos_mes": 25, "capacidade_maxima": 50}
            ),
            Metrica(
                id="usuarios_online",
                nome="Usuários Online",
                valor=125 + (hash(str(timestamp)) % 100),
                unidade="usuários",
                tipo=TipoMetrica.USUARIO,
                timestamp=timestamp,
                status=StatusMetrica.NORMAL,
                metadata={"pico_hoje": 180, "media_diaria": 95}
            ),
            Metrica(
                id="taxa_conversao",
                nome="Taxa de Conversão",
                valor=15.5 + (hash(str(timestamp)) % 10),
                unidade="%",
                tipo=TipoMetrica.NEGOCIO,
                timestamp=timestamp,
                status=StatusMetrica.NORMAL,
                metadata={"visitantes": 450, "conversoes": 72}
            )
        ]
        
        for metrica in metricas_negocio:
            await self._registrar_metrica(metrica)
    
    async def _coletar_metricas_performance(self):
        """Coleta métricas de performance"""
        timestamp = datetime.now()
        
        # Simula métricas de performance
        metricas_performance = [
            Metrica(
                id="tempo_resposta_api",
                nome="Tempo Resposta API",
                valor=245 + (hash(str(timestamp)) % 200),
                unidade="ms",
                tipo=TipoMetrica.PERFORMANCE,
                timestamp=timestamp,
                status=StatusMetrica.NORMAL,
                metadata={"p95": 850, "p99": 1200}
            ),
            Metrica(
                id="requisicoes_por_minuto",
                nome="Requisições por Minuto",
                valor=180 + (hash(str(timestamp)) % 120),
                unidade="req/min",
                tipo=TipoMetrica.PERFORMANCE,
                timestamp=timestamp,
                status=StatusMetrica.NORMAL,
                metadata={"pico": 350, "media": 220}
            ),
            Metrica(
                id="taxa_erro_api",
                nome="Taxa de Erro API",
                valor=0.5 + (hash(str(timestamp)) % 3),
                unidade="%",
                tipo=TipoMetrica.PERFORMANCE,
                timestamp=timestamp,
                status=StatusMetrica.NORMAL,
                metadata={"total_requests": 10800, "errors": 54}
            ),
            Metrica(
                id="uptime_sistema",
                nome="Uptime do Sistema",
                valor=99.95,
                unidade="%",
                tipo=TipoMetrica.SISTEMA,
                timestamp=timestamp,
                status=StatusMetrica.NORMAL,
                metadata={"dias_uptime": 15.7, "ultima_reinicializacao": "2025-08-01T10:30:00Z"}
            )
        ]
        
        for metrica in metricas_performance:
            await self._registrar_metrica(metrica)
    
    async def _registrar_metrica(self, metrica: Metrica):
        """Registra uma métrica no sistema"""
        # Atualiza métrica ativa
        self.metricas_ativas[metrica.id] = metrica
        
        # Adiciona ao histórico
        self.historico_metricas[metrica.id].append({
            "valor": metrica.valor,
            "timestamp": metrica.timestamp.isoformat(),
            "status": metrica.status
        })
    
    async def _verificar_alertas(self):
        """Verifica se alguma métrica gerou alerta"""
        for metrica_id, metrica in self.metricas_ativas.items():
            if metrica_id in self.configuracoes_alerta:
                config = self.configuracoes_alerta[metrica_id]
                await self._avaliar_alerta(metrica, config)
    
    async def _avaliar_alerta(self, metrica: Metrica, config: Dict):
        """Avalia se uma métrica deve gerar alerta"""
        valor = metrica.valor
        limites = config["limites"]
        tipo_config = config["tipo"]
        
        nivel_alerta = None
        
        if tipo_config == "threshold":
            if valor >= limites["critical"]:
                nivel_alerta = "CRITICAL"
            elif valor >= limites["warning"]:
                nivel_alerta = "WARNING"
                
        elif tipo_config == "percentage_below":
            # Para métricas onde valores baixos são problemáticos
            media_historica = self._calcular_media_historica(metrica.id)
            if media_historica > 0:
                percentual_atual = (valor / media_historica) * 100
                if percentual_atual <= limites["critical"]:
                    nivel_alerta = "CRITICAL"
                elif percentual_atual <= limites["warning"]:
                    nivel_alerta = "WARNING"
        
        if nivel_alerta:
            await self._criar_alerta(metrica, nivel_alerta, config)
    
    def _calcular_media_historica(self, metrica_id: str, dias: int = 7) -> float:
        """Calcula média histórica de uma métrica"""
        historico = self.historico_metricas.get(metrica_id, [])
        if not historico:
            return 0
        
        # Simula cálculo de média dos últimos dias
        valores_recentes = [h["valor"] for h in list(historico)[-100:]]  # Últimos 100 pontos
        return sum(valores_recentes) / len(valores_recentes) if valores_recentes else 0
    
    async def _criar_alerta(self, metrica: Metrica, nivel: str, config: Dict):
        """Cria um novo alerta"""
        alerta_id = f"alert_{metrica.id}_{int(datetime.now().timestamp())}"
        
        # Evita spam de alertas
        alertas_similares = [
            a for a in self.alertas_ativos.values()
            if a.metrica_id == metrica.id and not a.resolvido
        ]
        
        if alertas_similares:
            return  # Já existe alerta ativo para esta métrica
        
        alerta = Alerta(
            id=alerta_id,
            metrica_id=metrica.id,
            nivel=nivel,
            titulo=f"{nivel}: {metrica.nome}",
            descricao=f"{metrica.nome} está em {metrica.valor} {metrica.unidade}",
            criado_em=datetime.now()
        )
        
        self.alertas_ativos[alerta_id] = alerta
        
        # Notifica subscribers
        await self._notificar_alerta(alerta)
    
    async def _notificar_alerta(self, alerta: Alerta):
        """Notifica sobre um novo alerta"""
        # TODO: Implementar notificações (email, Slack, webhook, etc.)
        print(f"🚨 ALERTA {alerta.nivel}: {alerta.titulo}")
    
    async def _notificar_subscribers(self):
        """Notifica subscribers via WebSocket"""
        if not self.subscribers:
            return
        
        dados_atualizacao = {
            "timestamp": datetime.now().isoformat(),
            "metricas": {
                metrica_id: {
                    "valor": metrica.valor,
                    "status": metrica.status,
                    "unidade": metrica.unidade
                }
                for metrica_id, metrica in self.metricas_ativas.items()
            },
            "alertas_ativos": len([a for a in self.alertas_ativos.values() if not a.resolvido])
        }
        
        # TODO: Enviar via WebSocket para subscribers
    
    def obter_metricas_ativas(self) -> Dict[str, Any]:
        """Retorna métricas ativas"""
        return {
            metrica_id: {
                "nome": metrica.nome,
                "valor": metrica.valor,
                "unidade": metrica.unidade,
                "tipo": metrica.tipo,
                "status": metrica.status,
                "timestamp": metrica.timestamp.isoformat(),
                "metadata": metrica.metadata
            }
            for metrica_id, metrica in self.metricas_ativas.items()
        }
    
    def obter_historico_metrica(self, metrica_id: str, limite: int = 100) -> List[Dict]:
        """Retorna histórico de uma métrica"""
        historico = self.historico_metricas.get(metrica_id, [])
        return list(historico)[-limite:]
    
    def obter_alertas_ativos(self) -> List[Dict]:
        """Retorna alertas ativos"""
        return [
            {
                "id": alerta.id,
                "metrica_id": alerta.metrica_id,
                "nivel": alerta.nivel,
                "titulo": alerta.titulo,
                "descricao": alerta.descricao,
                "criado_em": alerta.criado_em.isoformat(),
                "resolvido": alerta.resolvido
            }
            for alerta in self.alertas_ativos.values()
            if not alerta.resolvido
        ]
    
    async def resolver_alerta(self, alerta_id: str, usuario: str = "sistema") -> bool:
        """Resolve um alerta"""
        if alerta_id not in self.alertas_ativos:
            return False
        
        alerta = self.alertas_ativos[alerta_id]
        alerta.resolvido = True
        alerta.resolvido_em = datetime.now()
        
        return True
    
    def obter_dashboard_metricas(self) -> Dict[str, Any]:
        """Retorna dados para dashboard de métricas"""
        metricas_ativas = self.obter_metricas_ativas()
        alertas_ativos = self.obter_alertas_ativos()
        
        # Agrupa métricas por tipo
        metricas_por_tipo = defaultdict(list)
        for metrica_id, metrica in metricas_ativas.items():
            metricas_por_tipo[metrica["tipo"]].append({
                "id": metrica_id,
                "nome": metrica["nome"],
                "valor": metrica["valor"],
                "unidade": metrica["unidade"],
                "status": metrica["status"]
            })
        
        # Calcula saúde geral do sistema
        total_metricas = len(metricas_ativas)
        metricas_criticas = len([m for m in metricas_ativas.values() if m["status"] == StatusMetrica.CRITICO])
        metricas_atencao = len([m for m in metricas_ativas.values() if m["status"] == StatusMetrica.ATENCAO])
        
        if metricas_criticas > 0:
            saude_geral = "CRÍTICO"
        elif metricas_atencao > 0:
            saude_geral = "ATENÇÃO"
        else:
            saude_geral = "NORMAL"
        
        return {
            "saude_geral": saude_geral,
            "total_metricas": total_metricas,
            "alertas_ativos": len(alertas_ativos),
            "ultima_atualizacao": datetime.now().isoformat(),
            "metricas_por_tipo": dict(metricas_por_tipo),
            "alertas_recentes": alertas_ativos[:5],
            "uptime_sistema": metricas_ativas.get("uptime_sistema", {}).get("valor", 0),
            "performance_api": metricas_ativas.get("tempo_resposta_api", {}).get("valor", 0),
            "usuarios_ativos": metricas_ativas.get("usuarios_online", {}).get("valor", 0),
            "vendas_hoje": metricas_ativas.get("vendas_hoje", {}).get("valor", 0)
        }
    
    def obter_relatorio_performance(self, periodo_horas: int = 24) -> Dict[str, Any]:
        """Gera relatório de performance do período"""
        # Simula dados de relatório
        return {
            "periodo": f"Últimas {periodo_horas} horas",
            "resumo": {
                "tempo_resposta_medio": 245,
                "pico_tempo_resposta": 850,
                "disponibilidade": 99.95,
                "total_requisicoes": 125600,
                "taxa_erro": 0.3
            },
            "metricas_principais": [
                {
                    "nome": "Tempo de Resposta",
                    "valor_medio": 245,
                    "unidade": "ms",
                    "tendencia": "estável",
                    "objetivo": 500
                },
                {
                    "nome": "Taxa de Erro",
                    "valor_medio": 0.3,
                    "unidade": "%",
                    "tendencia": "melhorando",
                    "objetivo": 1.0
                },
                {
                    "nome": "Throughput",
                    "valor_medio": 220,
                    "unidade": "req/min",
                    "tendencia": "crescendo",
                    "objetivo": 300
                }
            ],
            "incidentes": [
                {
                    "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                    "tipo": "Lentidão",
                    "duracao": "5 minutos",
                    "impacto": "Baixo"
                }
            ]
        }
    
    def configurar_alerta_personalizado(
        self,
        metrica_id: str,
        limites: Dict[str, float],
        tipo: str = "threshold"
    ) -> bool:
        """Configura alerta personalizado para uma métrica"""
        self.configuracoes_alerta[metrica_id] = {
            "limites": limites,
            "tipo": tipo,
            "personalizado": True
        }
        return True
