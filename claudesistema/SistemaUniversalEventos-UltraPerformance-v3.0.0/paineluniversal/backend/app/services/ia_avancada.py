"""
Sistema Avançado de Integração com IA
Inclui análise preditiva, recomendações inteligentes e automação
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import asyncio
from pydantic import BaseModel

class TipoAnaliseIA(str, Enum):
    """Tipos de análise de IA disponíveis"""
    PREVISAO_VENDAS = "previsao_vendas"
    OTIMIZACAO_ESTOQUE = "otimizacao_estoque"
    ANALISE_SENTIMENTO = "analise_sentimento"
    RECOMENDACAO_EVENTOS = "recomendacao_eventos"
    DETECCAO_ANOMALIAS = "deteccao_anomalias"
    SEGMENTACAO_CLIENTES = "segmentacao_clientes"
    PRECIFICACAO_DINAMICA = "precificacao_dinamica"
    ANALISE_COMPETITIVA = "analise_competitiva"

class ModeloIA(str, Enum):
    """Modelos de IA disponíveis"""
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    CLAUDE_3 = "claude-3"
    GEMINI_PRO = "gemini-pro"
    CUSTOM_ML = "custom-ml"

class StatusProcessamento(str, Enum):
    """Status do processamento de IA"""
    INICIADO = "iniciado"
    PROCESSANDO = "processando"
    CONCLUIDO = "concluido"
    ERRO = "erro"
    CANCELADO = "cancelado"

class IAAvancadaService:
    """Service avançado para integração com IA"""
    
    def __init__(self):
        self.processamentos_ativos = {}
        self.cache_resultados = {}
        self.modelos_disponiveis = self._inicializar_modelos()
    
    def _inicializar_modelos(self) -> Dict[str, Dict]:
        """Inicializa configurações dos modelos de IA"""
        return {
            ModeloIA.GPT_4: {
                "nome": "GPT-4",
                "provider": "OpenAI",
                "especialidades": ["análise de texto", "geração de conteúdo", "reasoning"],
                "custo_por_token": 0.00003,
                "limite_tokens": 128000,
                "disponivel": True
            },
            ModeloIA.GPT_3_5_TURBO: {
                "nome": "GPT-3.5 Turbo",
                "provider": "OpenAI", 
                "especialidades": ["análise rápida", "classificação", "sumarização"],
                "custo_por_token": 0.000002,
                "limite_tokens": 16000,
                "disponivel": True
            },
            ModeloIA.CLAUDE_3: {
                "nome": "Claude 3",
                "provider": "Anthropic",
                "especialidades": ["análise detalhada", "reasoning", "código"],
                "custo_por_token": 0.000015,
                "limite_tokens": 200000,
                "disponivel": False
            },
            ModeloIA.CUSTOM_ML: {
                "nome": "Modelo Personalizado",
                "provider": "Local",
                "especialidades": ["previsões específicas", "análise de dados"],
                "custo_por_token": 0,
                "limite_tokens": 0,
                "disponivel": True
            }
        }
    
    async def processar_analise_ia(
        self,
        tipo: TipoAnaliseIA,
        dados: Dict[str, Any],
        modelo: ModeloIA = ModeloIA.GPT_4,
        parametros: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa análise usando IA
        """
        try:
            processamento_id = str(uuid.uuid4())
            
            # Registra processamento
            processamento_info = {
                "id": processamento_id,
                "tipo": tipo,
                "modelo": modelo,
                "status": StatusProcessamento.INICIADO,
                "iniciado_em": datetime.now(),
                "dados_entrada": dados,
                "parametros": parametros or {},
                "progresso": 0
            }
            
            self.processamentos_ativos[processamento_id] = processamento_info
            
            # Processa baseado no tipo
            resultado = await self._executar_analise(tipo, dados, modelo, parametros)
            
            # Atualiza status
            processamento_info.update({
                "status": StatusProcessamento.CONCLUIDO,
                "concluido_em": datetime.now(),
                "resultado": resultado,
                "progresso": 100
            })
            
            # Cache do resultado
            cache_key = f"{tipo}_{hash(json.dumps(dados, sort_keys=True))}"
            self.cache_resultados[cache_key] = {
                "resultado": resultado,
                "timestamp": datetime.now(),
                "valido_ate": datetime.now() + timedelta(hours=6)
            }
            
            return {
                "processamento_id": processamento_id,
                "status": StatusProcessamento.CONCLUIDO,
                "resultado": resultado,
                "metadados": {
                    "modelo_usado": modelo,
                    "tempo_processamento": (datetime.now() - processamento_info["iniciado_em"]).total_seconds(),
                    "tokens_utilizados": resultado.get("tokens_utilizados", 0),
                    "custo_estimado": self._calcular_custo(modelo, resultado.get("tokens_utilizados", 0))
                }
            }
            
        except Exception as e:
            if processamento_id in self.processamentos_ativos:
                self.processamentos_ativos[processamento_id].update({
                    "status": StatusProcessamento.ERRO,
                    "erro": str(e),
                    "concluido_em": datetime.now()
                })
            
            raise Exception(f"Erro no processamento de IA: {str(e)}")
    
    async def _executar_analise(
        self,
        tipo: TipoAnaliseIA,
        dados: Dict[str, Any],
        modelo: ModeloIA,
        parametros: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Executa análise específica baseada no tipo"""
        
        if tipo == TipoAnaliseIA.PREVISAO_VENDAS:
            return await self._previsao_vendas(dados, modelo, parametros)
        elif tipo == TipoAnaliseIA.OTIMIZACAO_ESTOQUE:
            return await self._otimizacao_estoque(dados, modelo, parametros)
        elif tipo == TipoAnaliseIA.ANALISE_SENTIMENTO:
            return await self._analise_sentimento(dados, modelo, parametros)
        elif tipo == TipoAnaliseIA.RECOMENDACAO_EVENTOS:
            return await self._recomendacao_eventos(dados, modelo, parametros)
        elif tipo == TipoAnaliseIA.DETECCAO_ANOMALIAS:
            return await self._deteccao_anomalias(dados, modelo, parametros)
        elif tipo == TipoAnaliseIA.SEGMENTACAO_CLIENTES:
            return await self._segmentacao_clientes(dados, modelo, parametros)
        elif tipo == TipoAnaliseIA.PRECIFICACAO_DINAMICA:
            return await self._precificacao_dinamica(dados, modelo, parametros)
        elif tipo == TipoAnaliseIA.ANALISE_COMPETITIVA:
            return await self._analise_competitiva(dados, modelo, parametros)
        else:
            raise ValueError(f"Tipo de análise não suportado: {tipo}")
    
    async def _previsao_vendas(self, dados: Dict, modelo: ModeloIA, parametros: Dict) -> Dict[str, Any]:
        """Previsão de vendas usando IA"""
        # Simula processamento com IA
        await asyncio.sleep(2)  # Simula tempo de processamento
        
        historico_vendas = dados.get("historico_vendas", [])
        periodo_previsao = parametros.get("periodo_dias", 30)
        
        # Simula resultado de IA
        vendas_previstas = []
        base_vendas = 100
        
        for i in range(periodo_previsao):
            # Simula padrão sazonal e tendência
            tendencia = 1 + (i * 0.02)  # Crescimento 2% ao dia
            sazonalidade = 1 + 0.3 * (i % 7 == 5 or i % 7 == 6)  # Fins de semana melhores
            ruido = 1 + (hash(str(i)) % 20 - 10) / 100  # Variação aleatória
            
            venda_prevista = int(base_vendas * tendencia * sazonalidade * ruido)
            
            vendas_previstas.append({
                "data": (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                "vendas_previstas": venda_prevista,
                "confianca": max(0.6, 0.95 - (i * 0.01)),  # Confiança diminui com o tempo
                "intervalo_min": int(venda_prevista * 0.8),
                "intervalo_max": int(venda_prevista * 1.2)
            })
        
        total_previsto = sum(v["vendas_previstas"] for v in vendas_previstas)
        
        return {
            "previsoes": vendas_previstas,
            "resumo": {
                "total_vendas_previstas": total_previsto,
                "crescimento_esperado": "+12.5%",
                "confianca_media": 0.85,
                "fatores_influencia": [
                    "Sazonalidade de fins de semana",
                    "Tendência de crescimento identificada",
                    "Padrões históricos similares"
                ]
            },
            "recomendacoes": [
                "Aumentar estoque para fins de semana",
                "Preparar campanhas de marketing para dias de baixa previsão",
                "Monitorar indicadores externos que podem afetar as vendas"
            ],
            "modelo_usado": modelo,
            "tokens_utilizados": 2500,
            "precisao_historica": "89.3%"
        }
    
    async def _otimizacao_estoque(self, dados: Dict, modelo: ModeloIA, parametros: Dict) -> Dict[str, Any]:
        """Otimização de estoque usando IA"""
        await asyncio.sleep(1.5)
        
        produtos = dados.get("produtos", [])
        vendas_historicas = dados.get("vendas_historicas", [])
        
        otimizacoes = []
        for produto in produtos[:5]:  # Limita para demonstração
            produto_id = produto.get("id", f"PROD{len(otimizacoes)+1:03d}")
            estoque_atual = produto.get("estoque", 50)
            
            # Simula análise de IA
            otimizacao = {
                "produto_id": produto_id,
                "nome": produto.get("nome", f"Produto {produto_id}"),
                "estoque_atual": estoque_atual,
                "estoque_otimo": int(estoque_atual * (1.2 + (hash(produto_id) % 30) / 100)),
                "acao_recomendada": "AUMENTAR" if estoque_atual < 30 else "MANTER",
                "economia_potencial": abs(hash(produto_id)) % 500 + 100,
                "risco_ruptura": min(0.8, max(0.1, (40 - estoque_atual) / 40)),
                "tempo_reposicao_ideal": f"{(hash(produto_id) % 7) + 3} dias"
            }
            
            otimizacoes.append(otimizacao)
        
        return {
            "otimizacoes": otimizacoes,
            "resumo": {
                "produtos_analisados": len(otimizacoes),
                "economia_total_potencial": sum(o["economia_potencial"] for o in otimizacoes),
                "produtos_criticos": len([o for o in otimizacoes if o["risco_ruptura"] > 0.6]),
                "acoes_prioritarias": len([o for o in otimizacoes if o["acao_recomendada"] != "MANTER"])
            },
            "insights": [
                "Padrão sazonal identificado em bebidas",
                "Produtos de alta rotatividade precisam de estoque maior",
                "Correlação forte entre eventos e vendas de comidas"
            ],
            "modelo_usado": modelo,
            "tokens_utilizados": 1800
        }
    
    async def _analise_sentimento(self, dados: Dict, modelo: ModeloIA, parametros: Dict) -> Dict[str, Any]:
        """Análise de sentimento usando IA"""
        await asyncio.sleep(1)
        
        feedbacks = dados.get("feedbacks", [])
        comentarios = dados.get("comentarios", [])
        
        # Simula análise de sentimento
        sentimentos = []
        sentimento_geral = {"positivo": 0, "neutro": 0, "negativo": 0}
        
        todos_textos = feedbacks + comentarios
        for i, texto in enumerate(todos_textos[:10]):  # Limita para demonstração
            # Simula classificação
            score_hash = hash(str(texto)) % 100
            if score_hash > 60:
                sentimento = "positivo"
                score = 0.6 + (score_hash % 40) / 100
            elif score_hash > 30:
                sentimento = "neutro"
                score = 0.3 + (score_hash % 40) / 100
            else:
                sentimento = "negativo"
                score = 0.1 + (score_hash % 30) / 100
            
            sentimento_geral[sentimento] += 1
            
            sentimentos.append({
                "texto": str(texto)[:100] + "..." if len(str(texto)) > 100 else str(texto),
                "sentimento": sentimento,
                "confianca": round(score, 2),
                "emocoes_detectadas": ["satisfação", "interesse"] if sentimento == "positivo" else 
                                   ["neutralidade"] if sentimento == "neutro" else 
                                   ["frustração", "desapontamento"],
                "temas_principais": ["qualidade", "atendimento", "preço"]
            })
        
        total_analisados = len(sentimentos)
        
        return {
            "analises_individuais": sentimentos,
            "resumo_geral": {
                "total_analisados": total_analisados,
                "distribuicao_sentimentos": {
                    "positivo": round((sentimento_geral["positivo"] / total_analisados) * 100, 1) if total_analisados > 0 else 0,
                    "neutro": round((sentimento_geral["neutro"] / total_analisados) * 100, 1) if total_analisados > 0 else 0,
                    "negativo": round((sentimento_geral["negativo"] / total_analisados) * 100, 1) if total_analisados > 0 else 0
                },
                "score_medio": 7.2,
                "tendencia": "POSITIVA"
            },
            "insights": [
                "Clientes elogiam qualidade dos produtos",
                "Atendimento é ponto forte mencionado",
                "Algumas reclamações sobre tempo de espera",
                "Preços são considerados justos pela maioria"
            ],
            "acoes_recomendadas": [
                "Manter padrão de qualidade dos produtos",
                "Investir em treinamento de atendimento",
                "Otimizar processos para reduzir tempo de espera"
            ],
            "modelo_usado": modelo,
            "tokens_utilizados": 3200
        }
    
    async def _recomendacao_eventos(self, dados: Dict, modelo: ModeloIA, parametros: Dict) -> Dict[str, Any]:
        """Recomendações de eventos usando IA"""
        await asyncio.sleep(2)
        
        historico_eventos = dados.get("historico_eventos", [])
        tendencias_mercado = dados.get("tendencias", [])
        publico_alvo = dados.get("publico_alvo", {})
        
        recomendacoes = [
            {
                "id": "REC001",
                "nome": "Festival de Música Eletrônica de Inverno",
                "tipo": "Festival",
                "publico_estimado": 2500,
                "receita_estimada": 125000.00,
                "investimento_necessario": 75000.00,
                "roi_previsto": 66.7,
                "probabilidade_sucesso": 0.85,
                "melhor_periodo": "Julho-Agosto 2025",
                "locais_sugeridos": ["Arena Central", "Espaço Eventos Premium"],
                "fatores_sucesso": [
                    "Alta demanda por música eletrônica na região",
                    "Período favorável (inverno aquece eventos)",
                    "Público jovem ativo na cidade"
                ],
                "riscos": [
                    "Competição com eventos similares",
                    "Dependência do clima"
                ]
            },
            {
                "id": "REC002", 
                "nome": "Feira Gastronômica de Primavera",
                "tipo": "Feira",
                "publico_estimado": 1200,
                "receita_estimada": 85000.00,
                "investimento_necessario": 45000.00,
                "roi_previsto": 88.9,
                "probabilidade_sucesso": 0.92,
                "melhor_periodo": "Setembro-Outubro 2025",
                "locais_sugeridos": ["Praça Central", "Parque da Cidade"],
                "fatores_sucesso": [
                    "Crescimento do interesse em gastronomia",
                    "Parcerias com restaurantes locais",
                    "Época ideal para eventos ao ar livre"
                ],
                "riscos": [
                    "Dependência de fornecedores",
                    "Variações climáticas"
                ]
            },
            {
                "id": "REC003",
                "nome": "Workshop de Empreendedorismo Digital",
                "tipo": "Educacional",
                "publico_estimado": 300,
                "receita_estimada": 45000.00,
                "investimento_necessario": 15000.00,
                "roi_previsto": 200.0,
                "probabilidade_sucesso": 0.78,
                "melhor_periodo": "Março-Abril 2025",
                "locais_sugeridos": ["Centro de Convenções", "Universidade Local"],
                "fatores_sucesso": [
                    "Alta demanda por capacitação digital",
                    "Parcerias com instituições de ensino",
                    "Baixo investimento inicial"
                ],
                "riscos": [
                    "Concorrência de cursos online",
                    "Necessidade de palestrantes qualificados"
                ]
            }
        ]
        
        return {
            "recomendacoes": recomendacoes,
            "resumo": {
                "total_recomendacoes": len(recomendacoes),
                "receita_potencial_total": sum(r["receita_estimada"] for r in recomendacoes),
                "roi_medio": round(sum(r["roi_previsto"] for r in recomendacoes) / len(recomendacoes), 1),
                "probabilidade_sucesso_media": round(sum(r["probabilidade_sucesso"] for r in recomendacoes) / len(recomendacoes), 2)
            },
            "tendencias_identificadas": [
                "Crescimento de eventos de música eletrônica (+25%)",
                "Alta demanda por experiências gastronômicas (+40%)",
                "Interesse crescente em capacitação profissional (+30%)",
                "Preferência por eventos ao ar livre (+15%)"
            ],
            "fatores_mercado": {
                "sazonalidade": "Inverno e primavera são períodos favoráveis",
                "concorrencia": "Moderada, com oportunidades de diferenciação",
                "publico_alvo": "Jovens adultos 25-40 anos mais ativos",
                "poder_compra": "Em recuperação, com disposição para investir em experiências"
            },
            "modelo_usado": modelo,
            "tokens_utilizados": 4500
        }
    
    async def _deteccao_anomalias(self, dados: Dict, modelo: ModeloIA, parametros: Dict) -> Dict[str, Any]:
        """Detecção de anomalias usando IA"""
        await asyncio.sleep(1)
        
        metricas = dados.get("metricas", {})
        historico = dados.get("historico", [])
        
        anomalias_detectadas = [
            {
                "id": "ANOM001",
                "tipo": "Pico de vendas anômalo",
                "metrica": "vendas_diarias",
                "valor_detectado": 450,
                "valor_esperado": 180,
                "desvio_percentual": 150.0,
                "data_deteccao": "2025-08-15",
                "severidade": "MEDIA",
                "possveis_causas": [
                    "Promoção especial não registrada no sistema",
                    "Evento não programado na região",
                    "Erro no sistema de vendas"
                ],
                "acao_recomendada": "Investigar origem do pico"
            },
            {
                "id": "ANOM002",
                "tipo": "Queda abrupta de estoque",
                "metrica": "estoque_produto_001",
                "valor_detectado": 5,
                "valor_esperado": 45,
                "desvio_percentual": -88.9,
                "data_deteccao": "2025-08-14",
                "severidade": "ALTA",
                "possveis_causas": [
                    "Venda em lote não registrada",
                    "Perda/roubo de estoque",
                    "Erro de inventário"
                ],
                "acao_recomendada": "Auditoria imediata de estoque"
            }
        ]
        
        return {
            "anomalias": anomalias_detectadas,
            "resumo": {
                "total_anomalias": len(anomalias_detectadas),
                "severidade_alta": len([a for a in anomalias_detectadas if a["severidade"] == "ALTA"]),
                "severidade_media": len([a for a in anomalias_detectadas if a["severidade"] == "MEDIA"]),
                "acoes_urgentes": len([a for a in anomalias_detectadas if a["severidade"] == "ALTA"])
            },
            "status_sistema": {
                "saude_geral": "ATENCAO",
                "confiabilidade_dados": 0.87,
                "ultima_verificacao": datetime.now().isoformat()
            },
            "modelo_usado": modelo,
            "tokens_utilizados": 1500
        }
    
    async def _segmentacao_clientes(self, dados: Dict, modelo: ModeloIA, parametros: Dict) -> Dict[str, Any]:
        """Segmentação de clientes usando IA"""
        await asyncio.sleep(2)
        
        clientes = dados.get("clientes", [])
        comportamento_compra = dados.get("comportamento", [])
        
        segmentos = [
            {
                "id": "SEG001",
                "nome": "Jovens Profissionais",
                "descricao": "Profissionais de 25-35 anos com renda média-alta",
                "tamanho": 450,
                "percentual": 32.5,
                "caracteristicas": [
                    "Frequentam eventos noturnos",
                    "Gastam em média R$ 150 por evento",
                    "Preferem música eletrônica e shows",
                    "Ativos em redes sociais"
                ],
                "comportamento_compra": {
                    "frequencia": "2-3 eventos por mês",
                    "ticket_medio": 150.00,
                    "sazonalidade": "Mais ativos em fins de semana",
                    "canais_preferidos": ["Instagram", "WhatsApp"]
                },
                "estrategias_recomendadas": [
                    "Campanhas no Instagram com influencers",
                    "Eventos temáticos após horário comercial",
                    "Promoções para grupos"
                ]
            },
            {
                "id": "SEG002",
                "nome": "Famílias com Filhos",
                "descricao": "Famílias com crianças de 5-15 anos",
                "tamanho": 320,
                "percentual": 23.1,
                "caracteristicas": [
                    "Buscam entretenimento familiar",
                    "Sensíveis a preço",
                    "Preferem eventos diurnos",
                    "Valorizam segurança"
                ],
                "comportamento_compra": {
                    "frequencia": "1-2 eventos por mês",
                    "ticket_medio": 85.00,
                    "sazonalidade": "Mais ativos em feriados e férias",
                    "canais_preferidos": ["Facebook", "WhatsApp"]
                },
                "estrategias_recomendadas": [
                    "Eventos familiares com atividades para crianças",
                    "Pacotes família com desconto",
                    "Marketing no Facebook"
                ]
            }
        ]
        
        return {
            "segmentos": segmentos,
            "resumo": {
                "total_segmentos": len(segmentos),
                "clientes_segmentados": sum(s["tamanho"] for s in segmentos),
                "segmento_principal": max(segmentos, key=lambda x: x["tamanho"]),
                "receita_potencial": sum(s["tamanho"] * s["comportamento_compra"]["ticket_medio"] for s in segmentos)
            },
            "insights_gerais": [
                "Público jovem representa maior oportunidade de receita",
                "Famílias são mais fiéis mas sensíveis a preço",
                "Redes sociais são canal principal de comunicação",
                "Eventos noturnos têm maior margem de lucro"
            ],
            "modelo_usado": modelo,
            "tokens_utilizados": 3800
        }
    
    async def _precificacao_dinamica(self, dados: Dict, modelo: ModeloIA, parametros: Dict) -> Dict[str, Any]:
        """Precificação dinâmica usando IA"""
        await asyncio.sleep(1.5)
        
        produtos = dados.get("produtos", [])
        demanda_historica = dados.get("demanda", [])
        
        recomendacoes_preco = [
            {
                "produto_id": "PROD001",
                "nome": "Cerveja Premium 350ml",
                "preco_atual": 15.00,
                "preco_recomendado": 16.50,
                "ajuste_percentual": 10.0,
                "justificativa": "Alta demanda + baixo estoque",
                "elasticidade_preco": -0.6,
                "impacto_vendas": -8.5,
                "impacto_receita": +1.5,
                "confianca": 0.89,
                "periodo_validade": "7 dias"
            },
            {
                "produto_id": "PROD002",
                "nome": "Hambúrguer Artesanal",
                "preco_atual": 25.00,
                "preco_recomendado": 23.00,
                "ajuste_percentual": -8.0,
                "justificativa": "Aumentar competitividade",
                "elasticidade_preco": -1.2,
                "impacto_vendas": +12.0,
                "impacto_receita": +3.2,
                "confianca": 0.92,
                "periodo_validade": "14 dias"
            }
        ]
        
        return {
            "recomendacoes": recomendacoes_preco,
            "resumo": {
                "produtos_analisados": len(recomendacoes_preco),
                "aumentos_preco": len([r for r in recomendacoes_preco if r["ajuste_percentual"] > 0]),
                "reducoes_preco": len([r for r in recomendacoes_preco if r["ajuste_percentual"] < 0]),
                "impacto_receita_total": sum(r["impacto_receita"] for r in recomendacoes_preco)
            },
            "fatores_considerados": [
                "Elasticidade de demanda por produto",
                "Níveis de estoque atual",
                "Padrões sazonais de consumo",
                "Preços da concorrência",
                "Margem de lucro desejada"
            ],
            "modelo_usado": modelo,
            "tokens_utilizados": 2200
        }
    
    async def _analise_competitiva(self, dados: Dict, modelo: ModeloIA, parametros: Dict) -> Dict[str, Any]:
        """Análise competitiva usando IA"""
        await asyncio.sleep(2)
        
        concorrentes = dados.get("concorrentes", [])
        mercado = dados.get("dados_mercado", {})
        
        analise = {
            "posicao_mercado": {
                "ranking_atual": 3,
                "market_share": 15.5,
                "crescimento_ano": 12.8,
                "principais_vantagens": [
                    "Variedade de eventos oferecidos",
                    "Sistema de gamificação único",
                    "Excelente atendimento ao cliente"
                ],
                "areas_melhoria": [
                    "Presença digital",
                    "Parcerias estratégicas",
                    "Diversificação geográfica"
                ]
            },
            "analise_concorrentes": [
                {
                    "nome": "EventosMaster",
                    "market_share": 25.2,
                    "pontos_fortes": ["Marketing digital forte", "Rede de parceiros"],
                    "pontos_fracos": ["Atendimento automatizado", "Preços altos"],
                    "estrategias_observadas": ["Expansão para cidades menores"],
                    "ameaca_nivel": "ALTA"
                },
                {
                    "nome": "FestaPro",
                    "market_share": 18.7,
                    "pontos_fortes": ["Preços competitivos", "Agilidade"],
                    "pontos_fracos": ["Qualidade inconsistente", "Poucos eventos premium"],
                    "estrategias_observadas": ["Foco em eventos corporativos"],
                    "ameaca_nivel": "MEDIA"
                }
            ],
            "oportunidades": [
                "Mercado de eventos corporativos em crescimento (+35%)",
                "Demanda por eventos sustentáveis aumentando",
                "Espaço para eventos híbridos (presencial + online)",
                "Público jovem buscando experiências únicas"
            ],
            "ameacas": [
                "Entrada de players internacionais",
                "Mudanças na legislação de eventos",
                "Volatilidade econômica afetando gastos",
                "Concorrência por espaços premium"
            ],
            "recomendacoes_estrategicas": [
                "Investir em marketing digital e redes sociais",
                "Desenvolver parcerias com empresas locais",
                "Criar linha de eventos sustentáveis",
                "Expandir para mercado de eventos corporativos",
                "Implementar programa de fidelidade mais robusto"
            ]
        }
        
        return {
            "analise_competitiva": analise,
            "dashboard_metricas": {
                "score_competitividade": 7.2,
                "tendencia": "CRESCIMENTO",
                "proxima_revisao": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            },
            "modelo_usado": modelo,
            "tokens_utilizados": 5200
        }
    
    def _calcular_custo(self, modelo: ModeloIA, tokens: int) -> float:
        """Calcula custo estimado do processamento"""
        if modelo not in self.modelos_disponiveis:
            return 0.0
        
        custo_por_token = self.modelos_disponiveis[modelo]["custo_por_token"]
        return round(tokens * custo_por_token, 4)
    
    def obter_status_processamento(self, processamento_id: str) -> Dict[str, Any]:
        """Obtém status de um processamento"""
        if processamento_id not in self.processamentos_ativos:
            raise ValueError(f"Processamento {processamento_id} não encontrado")
        
        return self.processamentos_ativos[processamento_id]
    
    def listar_modelos_disponiveis(self) -> Dict[str, Any]:
        """Lista modelos de IA disponíveis"""
        return {
            "modelos": self.modelos_disponiveis,
            "total_modelos": len(self.modelos_disponiveis),
            "modelos_ativos": len([m for m in self.modelos_disponiveis.values() if m["disponivel"]])
        }
    
    def obter_estatisticas_uso(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso da IA"""
        processamentos = list(self.processamentos_ativos.values())
        
        return {
            "total_processamentos": len(processamentos),
            "processamentos_concluidos": len([p for p in processamentos if p["status"] == StatusProcessamento.CONCLUIDO]),
            "tempo_medio_processamento": 2.3,  # Simulado
            "custo_total_estimado": 15.75,  # Simulado
            "tipos_mais_usados": [
                {"tipo": "previsao_vendas", "count": 12},
                {"tipo": "analise_sentimento", "count": 8},
                {"tipo": "recomendacao_eventos", "count": 6}
            ],
            "eficiencia_cache": 0.65,  # 65% dos requests usam cache
            "ultima_atualizacao": datetime.now().isoformat()
        }
