"""
Router para Analytics e Relatórios do Sistema
Fornece métricas, estatísticas e relatórios em tempo real
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import sqlite3
import logging
from ..database_sqlite import create_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_date_range(periodo: str = "7d"):
    """Calcula range de datas baseado no período"""
    hoje = datetime.now()
    
    if periodo == "1d":
        inicio = hoje - timedelta(days=1)
    elif periodo == "7d":
        inicio = hoje - timedelta(days=7)
    elif periodo == "30d":
        inicio = hoje - timedelta(days=30)
    elif periodo == "90d":
        inicio = hoje - timedelta(days=90)
    else:
        inicio = hoje - timedelta(days=7)
    
    return inicio.strftime("%Y-%m-%d"), hoje.strftime("%Y-%m-%d")

@router.get("/dashboard-metrics")
async def get_dashboard_metrics(periodo: str = Query("7d", description="Período: 1d, 7d, 30d, 90d")):
    """Métricas principais do dashboard"""
    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Erro na conexão com banco")
        
        cursor = conn.cursor()
        data_inicio, data_fim = get_date_range(periodo)
        
        # Métricas de Eventos
        cursor.execute("""
            SELECT 
                COUNT(*) as total_eventos,
                COUNT(CASE WHEN ativo = 1 THEN 1 END) as eventos_ativos,
                SUM(CASE WHEN ativo = 1 THEN capacidade ELSE 0 END) as capacidade_total
            FROM eventos 
            WHERE data_criacao >= ? AND data_criacao <= ?
        """, (data_inicio, data_fim))
        
        eventos_data = cursor.fetchone()
        
        # Métricas de Check-ins
        cursor.execute("""
            SELECT 
                COUNT(*) as total_checkins,
                COUNT(DISTINCT participante_id) as participantes_unicos
            FROM checkins 
            WHERE data_checkin >= ? AND data_checkin <= ?
        """, (data_inicio, data_fim))
        
        checkins_data = cursor.fetchone() or (0, 0)
        
        # Métricas de Vendas PDV
        cursor.execute("""
            SELECT 
                COUNT(*) as total_vendas,
                COALESCE(SUM(valor_total), 0) as receita_total,
                COALESCE(AVG(valor_total), 0) as ticket_medio
            FROM vendas 
            WHERE data_venda >= ? AND data_venda <= ?
        """, (data_inicio, data_fim))
        
        vendas_data = cursor.fetchone() or (0, 0, 0)
        
        # Métricas WhatsApp
        cursor.execute("""
            SELECT 
                COUNT(*) as total_mensagens,
                COUNT(CASE WHEN status = 'entregue' THEN 1 END) as mensagens_entregues,
                COUNT(CASE WHEN status = 'lido' THEN 1 END) as mensagens_lidas
            FROM whatsapp_mensagens 
            WHERE data_criacao >= ? AND data_criacao <= ?
        """, (data_inicio, data_fim))
        
        whatsapp_data = cursor.fetchone() or (0, 0, 0)
        
        conn.close()
        
        return {
            "periodo": periodo,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "eventos": {
                "total": eventos_data[0] if eventos_data else 0,
                "ativos": eventos_data[1] if eventos_data else 0,
                "capacidade_total": eventos_data[2] if eventos_data else 0
            },
            "checkins": {
                "total": checkins_data[0],
                "participantes_unicos": checkins_data[1]
            },
            "vendas": {
                "total": vendas_data[0],
                "receita": float(vendas_data[1]),
                "ticket_medio": float(vendas_data[2])
            },
            "whatsapp": {
                "total_mensagens": whatsapp_data[0],
                "entregues": whatsapp_data[1],
                "lidas": whatsapp_data[2],
                "taxa_entrega": (whatsapp_data[1] / whatsapp_data[0] * 100) if whatsapp_data[0] > 0 else 0,
                "taxa_leitura": (whatsapp_data[2] / whatsapp_data[0] * 100) if whatsapp_data[0] > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar métricas do dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/real-time-stats")
async def get_real_time_stats():
    """Estatísticas em tempo real para WebSocket"""
    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Erro na conexão com banco")
        
        cursor = conn.cursor()
        agora = datetime.now()
        uma_hora_atras = agora - timedelta(hours=1)
        
        # Estatísticas da última hora
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM checkins WHERE data_checkin >= ?) as checkins_ultima_hora,
                (SELECT COUNT(*) FROM vendas WHERE data_venda >= ?) as vendas_ultima_hora,
                (SELECT COALESCE(SUM(valor_total), 0) FROM vendas WHERE data_venda >= ?) as receita_ultima_hora,
                (SELECT COUNT(*) FROM whatsapp_mensagens WHERE data_criacao >= ?) as mensagens_ultima_hora
        """, (uma_hora_atras, uma_hora_atras, uma_hora_atras, uma_hora_atras))
        
        stats = cursor.fetchone()
        
        # Eventos ativos agora
        cursor.execute("""
            SELECT COUNT(*) FROM eventos 
            WHERE ativo = 1 
            AND datetime(data_evento) <= datetime('now', '+3 hours')
            AND datetime(data_evento, '+4 hours') >= datetime('now')
        """)
        
        eventos_ativos = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "timestamp": agora.isoformat(),
            "checkins_ultima_hora": stats[0] if stats else 0,
            "vendas_ultima_hora": stats[1] if stats else 0,
            "receita_ultima_hora": float(stats[2]) if stats else 0,
            "mensagens_ultima_hora": stats[3] if stats else 0,
            "eventos_ativos_agora": eventos_ativos
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas em tempo real: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/eventos-analytics")
async def get_eventos_analytics(periodo: str = Query("30d", description="Período: 1d, 7d, 30d, 90d")):
    """Analytics detalhadas de eventos"""
    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Erro na conexão com banco")
        
        cursor = conn.cursor()
        data_inicio, data_fim = get_date_range(periodo)
        
        # Analytics de eventos por categoria
        cursor.execute("""
            SELECT 
                categoria,
                COUNT(*) as total,
                COUNT(CASE WHEN ativo = 1 THEN 1 END) as ativos,
                SUM(capacidade) as capacidade_total,
                AVG(capacidade) as capacidade_media
            FROM eventos 
            WHERE data_criacao >= ? AND data_criacao <= ?
            GROUP BY categoria
            ORDER BY total DESC
        """, (data_inicio, data_fim))
        
        eventos_por_categoria = [
            {
                "categoria": row[0] or "Sem Categoria",
                "total": row[1],
                "ativos": row[2],
                "capacidade_total": row[3] or 0,
                "capacidade_media": round(row[4] or 0, 2)
            }
            for row in cursor.fetchall()
        ]
        
        # Eventos mais populares (com mais check-ins)
        cursor.execute("""
            SELECT 
                e.nome,
                e.categoria,
                COUNT(c.id) as total_checkins,
                e.capacidade,
                ROUND(COUNT(c.id) * 100.0 / e.capacidade, 2) as taxa_ocupacao
            FROM eventos e
            LEFT JOIN checkins c ON e.id = c.evento_id
            WHERE e.data_criacao >= ? AND e.data_criacao <= ?
            GROUP BY e.id, e.nome, e.categoria, e.capacidade
            ORDER BY total_checkins DESC
            LIMIT 10
        """, (data_inicio, data_fim))
        
        eventos_populares = [
            {
                "nome": row[0],
                "categoria": row[1] or "Sem Categoria",
                "total_checkins": row[2],
                "capacidade": row[3],
                "taxa_ocupacao": row[4] or 0
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "periodo": periodo,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "eventos_por_categoria": eventos_por_categoria,
            "eventos_populares": eventos_populares
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar analytics de eventos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vendas-analytics")
async def get_vendas_analytics(periodo: str = Query("30d", description="Período: 1d, 7d, 30d, 90d")):
    """Analytics detalhadas de vendas"""
    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Erro na conexão com banco")
        
        cursor = conn.cursor()
        data_inicio, data_fim = get_date_range(periodo)
        
        # Vendas por dia
        cursor.execute("""
            SELECT 
                DATE(data_venda) as dia,
                COUNT(*) as total_vendas,
                SUM(valor_total) as receita_dia,
                AVG(valor_total) as ticket_medio_dia
            FROM vendas 
            WHERE data_venda >= ? AND data_venda <= ?
            GROUP BY DATE(data_venda)
            ORDER BY dia DESC
        """, (data_inicio, data_fim))
        
        vendas_por_dia = [
            {
                "dia": row[0],
                "total_vendas": row[1],
                "receita": float(row[2] or 0),
                "ticket_medio": float(row[3] or 0)
            }
            for row in cursor.fetchall()
        ]
        
        # Produtos mais vendidos
        cursor.execute("""
            SELECT 
                item_nome,
                SUM(quantidade) as total_vendido,
                SUM(valor_total) as receita_item,
                COUNT(*) as num_vendas
            FROM vendas 
            WHERE data_venda >= ? AND data_venda <= ?
            GROUP BY item_nome
            ORDER BY total_vendido DESC
            LIMIT 10
        """, (data_inicio, data_fim))
        
        produtos_populares = [
            {
                "produto": row[0],
                "quantidade_vendida": row[1],
                "receita": float(row[2] or 0),
                "num_vendas": row[3]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "periodo": periodo,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "vendas_por_dia": vendas_por_dia,
            "produtos_populares": produtos_populares
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar analytics de vendas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/whatsapp-analytics")
async def get_whatsapp_analytics(periodo: str = Query("30d", description="Período: 1d, 7d, 30d, 90d")):
    """Analytics detalhadas do WhatsApp"""
    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Erro na conexão com banco")
        
        cursor = conn.cursor()
        data_inicio, data_fim = get_date_range(periodo)
        
        # Mensagens por dia
        cursor.execute("""
            SELECT 
                DATE(data_criacao) as dia,
                COUNT(*) as total_mensagens,
                COUNT(CASE WHEN status = 'entregue' THEN 1 END) as entregues,
                COUNT(CASE WHEN status = 'lido' THEN 1 END) as lidas
            FROM whatsapp_mensagens 
            WHERE data_criacao >= ? AND data_criacao <= ?
            GROUP BY DATE(data_criacao)
            ORDER BY dia DESC
        """, (data_inicio, data_fim))
        
        mensagens_por_dia = [
            {
                "dia": row[0],
                "total": row[1],
                "entregues": row[2],
                "lidas": row[3],
                "taxa_entrega": (row[2] / row[1] * 100) if row[1] > 0 else 0,
                "taxa_leitura": (row[3] / row[1] * 100) if row[1] > 0 else 0
            }
            for row in cursor.fetchall()
        ]
        
        # Contatos mais ativos
        cursor.execute("""
            SELECT 
                c.nome,
                c.telefone,
                COUNT(m.id) as total_mensagens,
                MAX(m.data_criacao) as ultima_mensagem
            FROM whatsapp_contatos c
            LEFT JOIN whatsapp_mensagens m ON c.id = m.contato_id
            WHERE m.data_criacao >= ? AND m.data_criacao <= ?
            GROUP BY c.id, c.nome, c.telefone
            ORDER BY total_mensagens DESC
            LIMIT 10
        """, (data_inicio, data_fim))
        
        contatos_ativos = [
            {
                "nome": row[0],
                "telefone": row[1],
                "total_mensagens": row[2],
                "ultima_mensagem": row[3]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "periodo": periodo,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "mensagens_por_dia": mensagens_por_dia,
            "contatos_ativos": contatos_ativos
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar analytics do WhatsApp: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def analytics_health_check():
    """Verifica saúde do sistema de analytics"""
    try:
        conn = create_connection()
        if not conn:
            return {
                "status": "unhealthy",
                "service": "analytics",
                "database": "error",
                "timestamp": datetime.now().isoformat()
            }
        
        # Teste básico de conexão
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM eventos")
        eventos_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vendas")
        vendas_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM whatsapp_mensagens")
        whatsapp_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "healthy",
            "service": "analytics",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "database": "ok",
            "data_counts": {
                "eventos": eventos_count,
                "vendas": vendas_count,
                "whatsapp_mensagens": whatsapp_count
            }
        }
        
    except Exception as e:
        logger.error(f"Erro no health check de analytics: {e}")
        return {
            "status": "unhealthy",
            "service": "analytics",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
