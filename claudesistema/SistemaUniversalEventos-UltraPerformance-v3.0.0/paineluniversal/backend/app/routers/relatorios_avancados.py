"""
Router para Sistema de Relatórios Avançados
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

# Simulação de dados para demonstração
relatorios_mock = {}

# ================== SCHEMAS ==================

class ParametrosBase(BaseModel):
    """Parâmetros base para relatórios"""
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    limite: Optional[int] = Field(default=100, ge=1, le=1000)

class ParametrosVendas(ParametrosBase):
    """Parâmetros específicos para relatório de vendas"""
    incluir_detalhes: bool = True
    agrupar_por: str = Field(default="dia", pattern="^(dia|semana|mes)$")

class ParametrosEstoque(BaseModel):
    """Parâmetros para relatório de estoque"""
    limite_critico: int = Field(default=10, ge=1)
    categoria: Optional[str] = None
    incluir_custos: bool = True

class SolicitacaoRelatorio(BaseModel):
    """Schema para solicitação de relatório"""
    tipo: str
    parametros: Dict[str, Any] = {}
    formato: str = "json"
    nome_personalizado: Optional[str] = None
    enviar_email: bool = False

class RespostaRelatorio(BaseModel):
    """Schema para resposta de relatório"""
    relatorio_id: str
    status: str
    tipo: str
    criado_em: datetime
    concluido_em: Optional[datetime] = None
    url_download: Optional[str] = None

# ================== ENDPOINTS ==================

@router.get("/tipos")
async def listar_tipos_relatorios():
    """
    Lista todos os tipos de relatórios disponíveis
    """
    tipos = [
        {
            "codigo": "vendas_periodo",
            "nome": "Vendas por Período",
            "descricao": "Relatório detalhado de vendas por período com métricas de performance",
            "parametros_aceitos": ["data_inicio", "data_fim", "agrupar_por", "incluir_detalhes"],
            "exemplo": {
                "data_inicio": "2025-01-01",
                "data_fim": "2025-01-31",
                "agrupar_por": "dia"
            }
        },
        {
            "codigo": "estoque_baixo", 
            "nome": "Produtos com Estoque Baixo",
            "descricao": "Lista produtos com estoque abaixo do mínimo definido",
            "parametros_aceitos": ["limite_critico", "categoria", "incluir_custos"],
            "exemplo": {
                "limite_critico": 10,
                "categoria": "bebidas"
            }
        },
        {
            "codigo": "performance_eventos",
            "nome": "Performance de Eventos", 
            "descricao": "Análise completa de performance dos eventos realizados",
            "parametros_aceitos": ["data_inicio", "data_fim", "promoter_id", "incluir_financeiro"],
            "exemplo": {
                "data_inicio": "2025-01-01",
                "incluir_financeiro": True
            }
        },
        {
            "codigo": "ranking_promoters",
            "nome": "Ranking de Promoters",
            "descricao": "Ranking de promoters por performance e métricas",
            "parametros_aceitos": ["periodo", "limite", "ordenar_por"],
            "exemplo": {
                "periodo": 30,
                "limite": 20,
                "ordenar_por": "vendas"
            }
        },
        {
            "codigo": "analise_financeira",
            "nome": "Análise Financeira",
            "descricao": "Análise financeira completa com receitas, custos e lucros",
            "parametros_aceitos": ["data_inicio", "data_fim", "incluir_projecoes"],
            "exemplo": {
                "data_inicio": "2025-01-01",
                "incluir_projecoes": True
            }
        },
        {
            "codigo": "produtos_mais_vendidos",
            "nome": "Produtos Mais Vendidos",
            "descricao": "Ranking dos produtos mais vendidos por período",
            "parametros_aceitos": ["limite", "categoria", "periodo"],
            "exemplo": {
                "limite": 20,
                "periodo": 30
            }
        }
    ]
    
    return {
        "tipos_disponiveis": tipos,
        "formatos_suportados": ["json", "csv", "pdf", "excel"],
        "total_tipos": len(tipos),
        "ultima_atualizacao": datetime.now().isoformat()
    }

@router.post("/gerar", response_model=Dict[str, Any])
async def gerar_relatorio(
    solicitacao: SolicitacaoRelatorio,
    background_tasks: BackgroundTasks
):
    """
    Gera um novo relatório baseado nos parâmetros fornecidos
    """
    try:
        relatorio_id = str(uuid.uuid4())
        
        # Simula processamento baseado no tipo
        dados_relatorio = await _processar_relatorio(solicitacao.tipo, solicitacao.parametros)
        
        # Armazena o relatório
        relatorio_info = {
            "id": relatorio_id,
            "tipo": solicitacao.tipo,
            "parametros": solicitacao.parametros,
            "formato": solicitacao.formato,
            "status": "concluido",
            "criado_em": datetime.now(),
            "concluido_em": datetime.now(),
            "dados": dados_relatorio
        }
        
        relatorios_mock[relatorio_id] = relatorio_info
        
        # Se solicitado envio por email, agenda task
        if solicitacao.enviar_email:
            background_tasks.add_task(_enviar_relatorio_por_email, relatorio_id)
        
        return {
            "sucesso": True,
            "relatorio_id": relatorio_id,
            "status": "concluido",
            "mensagem": f"Relatório '{solicitacao.tipo}' gerado com sucesso",
            "metadados": {
                "total_registros": _contar_registros(dados_relatorio),
                "gerado_em": datetime.now().isoformat(),
                "formato": solicitacao.formato
            },
            "dados": dados_relatorio if solicitacao.formato == "json" else None,
            "url_download": f"/api/v1/relatorios/download/{relatorio_id}" if solicitacao.formato != "json" else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )

@router.get("/status/{relatorio_id}")
async def obter_status_relatorio(relatorio_id: str):
    """
    Obtém o status de processamento de um relatório
    """
    if relatorio_id not in relatorios_mock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relatório {relatorio_id} não encontrado"
        )
    
    relatorio = relatorios_mock[relatorio_id]
    return {
        "sucesso": True,
        "relatorio": {
            "id": relatorio["id"],
            "tipo": relatorio["tipo"],
            "status": relatorio["status"],
            "criado_em": relatorio["criado_em"].isoformat(),
            "concluido_em": relatorio.get("concluido_em").isoformat() if relatorio.get("concluido_em") else None,
            "progresso": 100 if relatorio["status"] == "concluido" else 0
        }
    }

@router.get("/listar")
async def listar_relatorios(
    pagina: int = 1,
    por_pagina: int = 20,
    tipo: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Lista relatórios gerados com filtros opcionais
    """
    relatorios = list(relatorios_mock.values())
    
    # Aplica filtros
    if tipo:
        relatorios = [r for r in relatorios if r["tipo"] == tipo]
    
    if status:
        relatorios = [r for r in relatorios if r["status"] == status]
    
    # Ordena por data de criação (mais recentes primeiro)
    relatorios.sort(key=lambda x: x["criado_em"], reverse=True)
    
    # Paginação
    inicio = (pagina - 1) * por_pagina
    fim = inicio + por_pagina
    relatorios_pagina = relatorios[inicio:fim]
    
    return {
        "total": len(relatorios),
        "relatorios": [
            {
                "id": r["id"],
                "tipo": r["tipo"],
                "status": r["status"],
                "criado_em": r["criado_em"].isoformat(),
                "formato": r["formato"]
            } for r in relatorios_pagina
        ],
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total_paginas": (len(relatorios) + por_pagina - 1) // por_pagina
    }

@router.delete("/{relatorio_id}")
async def excluir_relatorio(relatorio_id: str):
    """
    Exclui um relatório gerado
    """
    if relatorio_id not in relatorios_mock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relatório {relatorio_id} não encontrado"
        )
    
    del relatorios_mock[relatorio_id]
    
    return {
        "sucesso": True,
        "mensagem": f"Relatório {relatorio_id} excluído com sucesso"
    }

@router.get("/download/{relatorio_id}")
async def download_relatorio(relatorio_id: str):
    """
    Download de relatório em formato específico
    """
    if relatorio_id not in relatorios_mock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relatório {relatorio_id} não encontrado"
        )
    
    relatorio = relatorios_mock[relatorio_id]
    
    return {
        "relatorio_id": relatorio_id,
        "formato": relatorio["formato"],
        "dados": relatorio["dados"],
        "gerado_em": relatorio["criado_em"].isoformat(),
        "observacao": "Download simulado - implementação completa pendente"
    }

# ================== ENDPOINTS ESPECÍFICOS ==================

@router.post("/vendas", response_model=Dict[str, Any])
async def gerar_relatorio_vendas(parametros: ParametrosVendas):
    """
    Endpoint específico para relatório de vendas
    """
    solicitacao = SolicitacaoRelatorio(
        tipo="vendas_periodo",
        parametros=parametros.dict(exclude_none=True)
    )
    
    return await gerar_relatorio(solicitacao, BackgroundTasks())

@router.post("/estoque-baixo", response_model=Dict[str, Any])
async def gerar_relatorio_estoque_baixo(parametros: ParametrosEstoque):
    """
    Endpoint específico para relatório de estoque baixo
    """
    solicitacao = SolicitacaoRelatorio(
        tipo="estoque_baixo",
        parametros=parametros.dict(exclude_none=True)
    )
    
    return await gerar_relatorio(solicitacao, BackgroundTasks())

@router.post("/performance-eventos")
async def gerar_relatorio_performance_eventos(
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    promoter_id: Optional[str] = None,
    incluir_financeiro: bool = True
):
    """
    Endpoint específico para relatório de performance de eventos
    """
    parametros = {
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "promoter_id": promoter_id,
        "incluir_financeiro": incluir_financeiro
    }
    
    # Remove valores None
    parametros = {k: v for k, v in parametros.items() if v is not None}
    
    solicitacao = SolicitacaoRelatorio(
        tipo="performance_eventos",
        parametros=parametros
    )
    
    return await gerar_relatorio(solicitacao, BackgroundTasks())

@router.get("/dashboard")
async def obter_dashboard_relatorios():
    """
    Retorna dados para dashboard de relatórios
    """
    total_relatorios = len(relatorios_mock)
    concluidos = len([r for r in relatorios_mock.values() if r["status"] == "concluido"])
    
    # Relatórios por tipo
    tipos_count = {}
    for relatorio in relatorios_mock.values():
        tipo = relatorio["tipo"]
        tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
    
    # Relatórios recentes
    relatorios_recentes = sorted(
        relatorios_mock.values(),
        key=lambda x: x["criado_em"],
        reverse=True
    )[:5]
    
    return {
        "estatisticas": {
            "total_relatorios": total_relatorios,
            "concluidos": concluidos,
            "pendentes": total_relatorios - concluidos,
            "taxa_sucesso": (concluidos / total_relatorios * 100) if total_relatorios > 0 else 100
        },
        "distribuicao_tipos": tipos_count,
        "relatorios_recentes": [
            {
                "id": r["id"],
                "tipo": r["tipo"],
                "status": r["status"],
                "criado_em": r["criado_em"].isoformat()
            } for r in relatorios_recentes
        ],
        "metricas_periodo": {
            "relatorios_hoje": len([r for r in relatorios_mock.values() 
                                  if r["criado_em"].date() == datetime.now().date()]),
            "relatorios_semana": len([r for r in relatorios_mock.values() 
                                    if (datetime.now() - r["criado_em"]).days <= 7]),
            "tipo_mais_gerado": max(tipos_count.items(), key=lambda x: x[1])[0] if tipos_count else None
        },
        "recomendacoes": [
            "✅ Sistema de relatórios funcionando normalmente",
            "📊 Considere gerar relatório de vendas mensal",
            "🎯 3 produtos com estoque baixo detectados",
            "📈 Performance de eventos acima da média este mês"
        ]
    }

# ================== FUNÇÕES AUXILIARES ==================

async def _processar_relatorio(tipo: str, parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Processa relatório baseado no tipo"""
    
    if tipo == "vendas_periodo":
        return await _gerar_dados_vendas(parametros)
    elif tipo == "estoque_baixo":
        return await _gerar_dados_estoque_baixo(parametros)
    elif tipo == "performance_eventos":
        return await _gerar_dados_performance_eventos(parametros)
    elif tipo == "ranking_promoters":
        return await _gerar_dados_ranking_promoters(parametros)
    elif tipo == "analise_financeira":
        return await _gerar_dados_analise_financeira(parametros)
    elif tipo == "produtos_mais_vendidos":
        return await _gerar_dados_produtos_vendidos(parametros)
    else:
        return {"erro": f"Tipo de relatório '{tipo}' não suportado"}

async def _gerar_dados_vendas(parametros: Dict) -> Dict[str, Any]:
    """Gera dados simulados de vendas"""
    data_inicio = parametros.get("data_inicio", datetime.now() - timedelta(days=30))
    data_fim = parametros.get("data_fim", datetime.now())
    
    vendas_diarias = []
    for i in range(30):
        data = data_inicio + timedelta(days=i) if isinstance(data_inicio, datetime) else datetime.now() - timedelta(days=30-i)
        vendas_diarias.append({
            "data": data.strftime("%Y-%m-%d"),
            "vendas": 15 + (i % 10) * 3,
            "receita": 2500.50 + (i % 10) * 500,
            "ticket_medio": 166.70 + (i % 5) * 25,
            "crescimento": round((i % 15) - 7.5, 2)
        })
    
    return {
        "periodo": {
            "inicio": data_inicio.strftime("%Y-%m-%d") if isinstance(data_inicio, datetime) else str(data_inicio),
            "fim": data_fim.strftime("%Y-%m-%d") if isinstance(data_fim, datetime) else str(data_fim)
        },
        "vendas_diarias": vendas_diarias,
        "resumo": {
            "total_vendas": sum(v["vendas"] for v in vendas_diarias),
            "receita_total": sum(v["receita"] for v in vendas_diarias),
            "ticket_medio_periodo": round(sum(v["ticket_medio"] for v in vendas_diarias) / len(vendas_diarias), 2),
            "melhor_dia": max(vendas_diarias, key=lambda x: x["receita"]),
            "crescimento_percentual": 15.5
        }
    }

async def _gerar_dados_estoque_baixo(parametros: Dict) -> Dict[str, Any]:
    """Gera dados simulados de estoque baixo"""
    limite_critico = parametros.get("limite_critico", 10)
    
    produtos_baixo_estoque = [
        {
            "id": "PROD001",
            "nome": "Cerveja Premium 350ml",
            "categoria": "Bebidas",
            "estoque_atual": 5,
            "estoque_minimo": 20,
            "criticidade": "ALTA",
            "custo_reposicao": 450.00,
            "fornecedor": "Distribuidora XYZ",
            "ultima_venda": "2025-08-15"
        },
        {
            "id": "PROD002", 
            "nome": "Hambúrguer Artesanal",
            "categoria": "Comidas",
            "estoque_atual": 8,
            "estoque_minimo": 15,
            "criticidade": "MÉDIA",
            "custo_reposicao": 320.00,
            "fornecedor": "Fornecedor ABC",
            "ultima_venda": "2025-08-14"
        },
        {
            "id": "PROD003",
            "nome": "Refrigerante Artesanal",
            "categoria": "Bebidas",
            "estoque_atual": 3,
            "estoque_minimo": 12,
            "criticidade": "ALTA",
            "custo_reposicao": 180.00,
            "fornecedor": "Distribuidora XYZ",
            "ultima_venda": "2025-08-16"
        }
    ]
    
    return {
        "produtos_criticos": produtos_baixo_estoque,
        "resumo": {
            "total_produtos_baixo": len(produtos_baixo_estoque),
            "custo_total_reposicao": sum(p["custo_reposicao"] for p in produtos_baixo_estoque),
            "categorias_afetadas": list(set(p["categoria"] for p in produtos_baixo_estoque)),
            "prioridades": {
                "ALTA": len([p for p in produtos_baixo_estoque if p["criticidade"] == "ALTA"]),
                "MÉDIA": len([p for p in produtos_baixo_estoque if p["criticidade"] == "MÉDIA"]),
                "BAIXA": len([p for p in produtos_baixo_estoque if p["criticidade"] == "BAIXA"])
            },
            "acao_recomendada": "Reabastecer produtos de criticidade ALTA imediatamente"
        }
    }

async def _gerar_dados_performance_eventos(parametros: Dict) -> Dict[str, Any]:
    """Gera dados simulados de performance de eventos"""
    eventos_performance = [
        {
            "id": "EVT001",
            "nome": "Festival de Verão 2025",
            "data": "2025-01-15",
            "participantes": 1500,
            "receita": 75000.00,
            "custos": 45000.00,
            "lucro": 30000.00,
            "roi": 66.67,
            "satisfacao": 4.5,
            "promoter": "João Silva",
            "categoria": "Festival"
        },
        {
            "id": "EVT002",
            "nome": "Show Acústico",
            "data": "2025-01-20",
            "participantes": 300,
            "receita": 15000.00,
            "custos": 8000.00,
            "lucro": 7000.00,
            "roi": 87.50,
            "satisfacao": 4.8,
            "promoter": "Maria Santos",
            "categoria": "Show"
        },
        {
            "id": "EVT003",
            "nome": "Festa Corporativa",
            "data": "2025-02-05",
            "participantes": 800,
            "receita": 40000.00,
            "custos": 25000.00,
            "lucro": 15000.00,
            "roi": 60.00,
            "satisfacao": 4.3,
            "promoter": "Carlos Lima",
            "categoria": "Corporativo"
        }
    ]
    
    return {
        "eventos": eventos_performance,
        "resumo": {
            "total_eventos": len(eventos_performance),
            "participantes_total": sum(e["participantes"] for e in eventos_performance),
            "receita_total": sum(e["receita"] for e in eventos_performance),
            "lucro_total": sum(e["lucro"] for e in eventos_performance),
            "roi_medio": round(sum(e["roi"] for e in eventos_performance) / len(eventos_performance), 2),
            "satisfacao_media": round(sum(e["satisfacao"] for e in eventos_performance) / len(eventos_performance), 2),
            "evento_mais_lucrativo": max(eventos_performance, key=lambda x: x["lucro"]),
            "categoria_performance": {
                "Festival": {"eventos": 1, "receita": 75000.00},
                "Show": {"eventos": 1, "receita": 15000.00},
                "Corporativo": {"eventos": 1, "receita": 40000.00}
            }
        }
    }

async def _gerar_dados_ranking_promoters(parametros: Dict) -> Dict[str, Any]:
    """Gera dados simulados de ranking de promoters"""
    ranking_promoters = [
        {
            "id": "PROM001",
            "nome": "João Silva",
            "eventos_organizados": 5,
            "vendas_total": 125000.00,
            "participantes_total": 2500,
            "xp": 8500,
            "nivel": 15,
            "badges": ["Organizador Gold", "Vendedor Premium"],
            "media_satisfacao": 4.6,
            "crescimento_mes": 12.5,
            "posicao": 1
        },
        {
            "id": "PROM002",
            "nome": "Maria Santos", 
            "eventos_organizados": 3,
            "vendas_total": 85000.00,
            "participantes_total": 1200,
            "xp": 6200,
            "nivel": 12,
            "badges": ["Organizador Silver", "Inovação"],
            "media_satisfacao": 4.8,
            "crescimento_mes": 25.0,
            "posicao": 2
        },
        {
            "id": "PROM003",
            "nome": "Carlos Lima",
            "eventos_organizados": 4,
            "vendas_total": 95000.00,
            "participantes_total": 1800,
            "xp": 7100,
            "nivel": 13,
            "badges": ["Organizador Gold", "Networking Master"],
            "media_satisfacao": 4.4,
            "crescimento_mes": 8.5,
            "posicao": 3
        }
    ]
    
    return {
        "ranking": ranking_promoters,
        "resumo": {
            "total_promoters": len(ranking_promoters),
            "xp_total": sum(p["xp"] for p in ranking_promoters),
            "vendas_totais": sum(p["vendas_total"] for p in ranking_promoters),
            "melhor_promoter": max(ranking_promoters, key=lambda x: x["xp"]),
            "maior_crescimento": max(ranking_promoters, key=lambda x: x["crescimento_mes"]),
            "melhor_satisfacao": max(ranking_promoters, key=lambda x: x["media_satisfacao"])
        }
    }

async def _gerar_dados_analise_financeira(parametros: Dict) -> Dict[str, Any]:
    """Gera dados simulados de análise financeira"""
    return {
        "receitas": {
            "eventos": 250000.00,
            "pdv": 180000.00,
            "assinaturas": 45000.00,
            "outros": 35000.00,
            "total": 510000.00
        },
        "custos": {
            "operacionais": 120000.00,
            "marketing": 45000.00,
            "pessoal": 85000.00,
            "infraestrutura": 30000.00,
            "outros": 25000.00,
            "total": 305000.00
        },
        "lucro": {
            "bruto": 205000.00,
            "liquido": 180000.00,
            "margem_bruta": 40.20,
            "margem_liquida": 35.29
        },
        "indicadores": {
            "roi": 59.02,
            "crescimento_receita": 15.5,
            "eficiencia_operacional": 78.5,
            "break_even": "R$ 305.000,00"
        },
        "projecoes": {
            "receita_projetada_mes": 525000.00,
            "crescimento_esperado": 18.2,
            "meta_lucro": 195000.00
        }
    }

async def _gerar_dados_produtos_vendidos(parametros: Dict) -> Dict[str, Any]:
    """Gera dados simulados de produtos mais vendidos"""
    limite = parametros.get("limite", 10)
    
    produtos_vendidos = [
        {
            "id": "PROD001",
            "nome": "Cerveja Premium 350ml",
            "categoria": "Bebidas",
            "quantidade_vendida": 850,
            "receita": 25500.00,
            "margem": 45.0,
            "lucro": 11475.00,
            "posicao": 1
        },
        {
            "id": "PROD002",
            "nome": "Hambúrguer Artesanal",
            "categoria": "Comidas",
            "quantidade_vendida": 420,
            "receita": 16800.00,
            "margem": 60.0,
            "lucro": 10080.00,
            "posicao": 2
        },
        {
            "id": "PROD003",
            "nome": "Refrigerante Artesanal",
            "categoria": "Bebidas",
            "quantidade_vendida": 650,
            "receita": 9750.00,
            "margem": 55.0,
            "lucro": 5362.50,
            "posicao": 3
        }
    ]
    
    return {
        "produtos": produtos_vendidos[:limite],
        "resumo": {
            "total_produtos_analisados": len(produtos_vendidos),
            "receita_top_produtos": sum(p["receita"] for p in produtos_vendidos[:limite]),
            "categoria_top": "Bebidas",
            "produto_estrela": produtos_vendidos[0] if produtos_vendidos else None,
            "margem_media": round(sum(p["margem"] for p in produtos_vendidos[:limite]) / len(produtos_vendidos[:limite]), 2)
        },
        "analise_categorias": {
            "Bebidas": {
                "produtos": 2,
                "receita": 35250.00,
                "quantidade": 1500
            },
            "Comidas": {
                "produtos": 1,
                "receita": 16800.00,
                "quantidade": 420
            }
        }
    }

def _contar_registros(dados: Dict) -> int:
    """Conta registros nos dados"""
    for key, value in dados.items():
        if isinstance(value, list):
            return len(value)
    return 1

async def _enviar_relatorio_por_email(relatorio_id: str):
    """Envia relatório por email (implementação futura)"""
    # TODO: Implementar envio por email
    print(f"📧 Enviando relatório {relatorio_id} por email...")
    pass
