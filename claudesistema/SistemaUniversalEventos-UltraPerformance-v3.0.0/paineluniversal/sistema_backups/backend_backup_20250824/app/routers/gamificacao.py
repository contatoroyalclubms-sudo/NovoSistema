from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from ..database import get_db
from ..models import (
    Usuario, Evento, Transacao, PromoterEvento, Conquista, 
    PromoterConquista, RankingGamificacao, TipoUsuario
)
from ..schemas import (
    RankingPromoterResponse, ConquistaResponse, PromoterConquistaResponse,
    DashboardGamificacao, BadgeResponse, MetricasGamificacao
)
from ..auth import obter_usuario_atual

router = APIRouter(prefix="/gamificacao", tags=["Gamificação"])

@router.get("/ranking", response_model=List[RankingPromoterResponse])
async def obter_ranking_gamificado(
    evento_id: Optional[int] = None,
    periodo: str = Query("mes", description="mes, semana, dia, total"),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter ranking gamificado de promoters"""
    
    # Calcular período
    agora = datetime.now()
    if periodo == "dia":
        data_inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == "semana":
        data_inicio = agora - timedelta(days=agora.weekday())
        data_inicio = data_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == "mes":
        data_inicio = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # total
        data_inicio = datetime(2020, 1, 1)
    
    # Query base
    ranking_query = db.query(
        Usuario.id.label('promoter_id'),
        Usuario.nome.label('nome_promoter'),
        Usuario.avatar_url,
        func.count(Transacao.id).label('total_vendas'),
        func.coalesce(func.sum(Transacao.valor), 0).label('receita_gerada'),
        func.avg(Transacao.valor).label('ticket_medio'),
        func.count(func.distinct(Transacao.evento_id)).label('eventos_trabalhados')
    ).outerjoin(
        Transacao, and_(
            Transacao.promoter_id == Usuario.id,
            Transacao.status == "aprovada",
            Transacao.criado_em >= data_inicio
        )
    ).filter(
        Usuario.tipo == TipoUsuario.PROMOTER
    )
    
    # Filtros de acesso
    if usuario_atual.tipo.value != "admin":
        ranking_query = ranking_query.filter(Usuario.empresa_id == usuario_atual.empresa_id)
    
    if evento_id:
        ranking_query = ranking_query.filter(Transacao.evento_id == evento_id)
    
    ranking_query = ranking_query.group_by(
        Usuario.id, Usuario.nome, Usuario.avatar_url
    ).order_by(
        desc('total_vendas'), desc('receita_gerada')
    ).limit(limit)
    
    resultados = ranking_query.all()
    
    # Calcular badges e métricas adicionais
    ranking_final = []
    for i, resultado in enumerate(resultados, 1):
        # Determinar badge principal
        vendas = resultado.total_vendas
        if vendas >= 100:
            badge_principal = "diamante"
            badge_icone = "💎"
        elif vendas >= 50:
            badge_principal = "ouro"
            badge_icone = "🥇"
        elif vendas >= 25:
            badge_principal = "prata"
            badge_icone = "🥈"
        elif vendas >= 10:
            badge_principal = "bronze"
            badge_icone = "🥉"
        else:
            badge_principal = "iniciante"
            badge_icone = "🌟"
        
        # Calcular nível de experiência
        pontos_xp = vendas * 10 + float(resultado.receita_gerada or 0) / 10
        nivel = min(int(pontos_xp / 1000) + 1, 50)
        
        # Crescimento (comparar com período anterior)
        periodo_anterior = data_inicio - (agora - data_inicio)
        vendas_anterior = db.query(func.count(Transacao.id)).filter(
            and_(
                Transacao.promoter_id == resultado.promoter_id,
                Transacao.status == "aprovada",
                Transacao.criado_em >= periodo_anterior,
                Transacao.criado_em < data_inicio
            )
        ).scalar() or 0
        
        crescimento = 0
        if vendas_anterior > 0:
            crescimento = round(((vendas - vendas_anterior) / vendas_anterior) * 100, 1)
        elif vendas > 0:
            crescimento = 100
        
        ranking_final.append(RankingPromoterResponse(
            promoter_id=resultado.promoter_id,
            nome_promoter=resultado.nome_promoter,
            avatar_url=resultado.avatar_url,
            badge_principal=badge_principal,
            badge_icone=badge_icone,
            nivel_experiencia=nivel,
            pontos_xp=int(pontos_xp),
            total_vendas=vendas,
            receita_gerada=float(resultado.receita_gerada or 0),
            ticket_medio=float(resultado.ticket_medio or 0),
            eventos_trabalhados=resultado.eventos_trabalhados,
            taxa_presenca=0,  # Será calculado separadamente se necessário
            taxa_conversao=0,  # Será calculado separadamente se necessário
            crescimento_mensal=crescimento,
            posicao_atual=i,
            posicao_anterior=None,
            streak_vendas=0,  # Implementar se necessário
            ultima_venda=None
        ))
    
    return ranking_final

@router.get("/conquistas", response_model=List[ConquistaResponse])
async def listar_conquistas(
    ativa: Optional[bool] = None,
    categoria: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar todas as conquistas disponíveis"""
    
    query = db.query(Conquista)
    
    if ativa is not None:
        query = query.filter(Conquista.ativa == ativa)
    
    if categoria:
        query = query.filter(Conquista.categoria == categoria)
    
    conquistas = query.order_by(Conquista.pontos_necessarios).all()
    
    return [ConquistaResponse(
        id=c.id,
        nome=c.nome,
        descricao=c.descricao,
        categoria=c.categoria,
        badge_nivel=c.badge_nivel.value,
        icone=c.icone,
        pontos_necessarios=c.pontos_necessarios,
        recompensa_creditos=c.recompensa_creditos,
        ativa=c.ativa,
        criado_em=c.criado_em
    ) for c in conquistas]

@router.get("/conquistas/promoter/{promoter_id}", response_model=List[PromoterConquistaResponse])
async def obter_conquistas_promoter(
    promoter_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter conquistas de um promoter específico"""
    
    # Verificar acesso
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.id != promoter_id and
        usuario_atual.empresa_id != db.query(Usuario.empresa_id).filter(Usuario.id == promoter_id).scalar()):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    conquistas = db.query(
        PromoterConquista.id,
        Conquista.nome.label('conquista_nome'),
        Conquista.descricao.label('conquista_descricao'),
        Conquista.badge_nivel,
        Conquista.icone,
        PromoterConquista.valor_alcancado,
        PromoterConquista.data_conquista,
        Evento.nome.label('evento_nome')
    ).join(
        Conquista, PromoterConquista.conquista_id == Conquista.id
    ).outerjoin(
        Evento, PromoterConquista.evento_id == Evento.id
    ).filter(
        PromoterConquista.promoter_id == promoter_id
    ).order_by(
        desc(PromoterConquista.data_conquista)
    ).all()
    
    return [PromoterConquistaResponse(
        id=c.id,
        conquista_nome=c.conquista_nome,
        conquista_descricao=c.conquista_descricao,
        badge_nivel=c.badge_nivel.value,
        icone=c.icone,
        valor_alcancado=c.valor_alcancado,
        data_conquista=c.data_conquista,
        evento_nome=c.evento_nome
    ) for c in conquistas]

@router.post("/verificar-conquistas/{promoter_id}")
async def verificar_conquistas_promoter(
    promoter_id: int,
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Verificar e atribuir novas conquistas para um promoter"""
    
    # Verificar se o promoter existe
    promoter = db.query(Usuario).filter(Usuario.id == promoter_id).first()
    if not promoter:
        raise HTTPException(status_code=404, detail="Promoter não encontrado")
    
    # Verificar acesso
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != promoter.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    novas_conquistas = []
    
    # Obter conquistas ativas que o promoter ainda não possui
    conquistas_disponíveis = db.query(Conquista).filter(
        Conquista.ativa == True,
        ~Conquista.id.in_(
            db.query(PromoterConquista.conquista_id).filter(
                PromoterConquista.promoter_id == promoter_id
            )
        )
    ).all()
    
    for conquista in conquistas_disponíveis:
        valor_atual = 0
        
        # Calcular valor atual baseado na categoria da conquista
        if conquista.categoria == "vendas":
            query = db.query(func.count(Transacao.id)).filter(
                Transacao.promoter_id == promoter_id,
                Transacao.status == "aprovada"
            )
            if evento_id and conquista.escopo_evento:
                query = query.filter(Transacao.evento_id == evento_id)
            valor_atual = query.scalar() or 0
            
        elif conquista.categoria == "receita":
            query = db.query(func.sum(Transacao.valor)).filter(
                Transacao.promoter_id == promoter_id,
                Transacao.status == "aprovada"
            )
            if evento_id and conquista.escopo_evento:
                query = query.filter(Transacao.evento_id == evento_id)
            valor_atual = float(query.scalar() or 0)
            
        elif conquista.categoria == "eventos":
            valor_atual = db.query(func.count(func.distinct(Transacao.evento_id))).filter(
                Transacao.promoter_id == promoter_id,
                Transacao.status == "aprovada"
            ).scalar() or 0
        
        # Verificar se atingiu a meta
        if valor_atual >= conquista.pontos_necessarios:
            nova_conquista = PromoterConquista(
                promoter_id=promoter_id,
                conquista_id=conquista.id,
                valor_alcancado=valor_atual,
                evento_id=evento_id if conquista.escopo_evento else None
            )
            db.add(nova_conquista)
            novas_conquistas.append({
                "conquista_nome": conquista.nome,
                "conquista_descricao": conquista.descricao,
                "badge_nivel": conquista.badge_nivel.value,
                "valor_alcancado": valor_atual,
                "recompensa_creditos": conquista.recompensa_creditos
            })
    
    db.commit()
    
    return {
        "promoter_id": promoter_id,
        "novas_conquistas": novas_conquistas,
        "total_novas": len(novas_conquistas)
    }

@router.get("/dashboard", response_model=DashboardGamificacao)
async def obter_dashboard_gamificacao(
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Dashboard completo de gamificação"""
    
    ranking_geral = await obter_ranking_gamificado(
        evento_id=evento_id, limit=10, db=db, usuario_atual=usuario_atual
    )
    
    # Conquistas recentes (última semana)
    conquistas_recentes = db.query(
        PromoterConquista.id,
        Conquista.nome.label('conquista_nome'),
        Conquista.descricao.label('conquista_descricao'),
        Conquista.badge_nivel,
        Conquista.icone,
        PromoterConquista.valor_alcancado,
        PromoterConquista.data_conquista,
        Usuario.nome.label('promoter_nome'),
        Evento.nome.label('evento_nome')
    ).join(
        Conquista, PromoterConquista.conquista_id == Conquista.id
    ).join(
        Usuario, PromoterConquista.promoter_id == Usuario.id
    ).outerjoin(
        Evento, PromoterConquista.evento_id == Evento.id
    ).filter(
        PromoterConquista.data_conquista >= datetime.now() - timedelta(days=7)
    )
    
    if usuario_atual.tipo.value != "admin":
        conquistas_recentes = conquistas_recentes.filter(
            Usuario.empresa_id == usuario_atual.empresa_id
        )
    
    conquistas_recentes = conquistas_recentes.order_by(
        desc(PromoterConquista.data_conquista)
    ).limit(20).all()
    
    conquistas_list = [
        PromoterConquistaResponse(
            id=c.id,
            conquista_nome=c.conquista_nome,
            conquista_descricao=c.conquista_descricao,
            badge_nivel=c.badge_nivel.value,
            icone=c.icone,
            valor_alcancado=c.valor_alcancado,
            data_conquista=c.data_conquista,
            evento_nome=c.evento_nome
        ) for c in conquistas_recentes
    ]
    
    # Métricas do período
    total_promoters = len(ranking_geral)
    badges_ouro = len([r for r in ranking_geral if r.badge_principal == "ouro"])
    badges_prata = len([r for r in ranking_geral if r.badge_principal == "prata"])
    badges_bronze = len([r for r in ranking_geral if r.badge_principal == "bronze"])
    
    return DashboardGamificacao(
        ranking_geral=ranking_geral,
        conquistas_recentes=conquistas_list,
        metricas_periodo={
            "total_promoters": total_promoters,
            "conquistas_semana": len(conquistas_list),
            "badge_ouro": badges_ouro,
            "badge_prata": badges_prata,
            "badge_bronze": badges_bronze,
            "crescimento_medio": 15.5
        },
        badges_disponiveis=[
            {"nome": "Diamante", "descricao": "100+ vendas", "icone": "💎", "cor": "#b9f2ff"},
            {"nome": "Ouro", "descricao": "50+ vendas", "icone": "🥇", "cor": "#ffd700"},
            {"nome": "Prata", "descricao": "25+ vendas", "icone": "🥈", "cor": "#c0c0c0"},
            {"nome": "Bronze", "descricao": "10+ vendas", "icone": "🥉", "cor": "#cd7f32"},
            {"nome": "Iniciante", "descricao": "Primeiras vendas", "icone": "🌟", "cor": "#87ceeb"}
        ]
    )

@router.get("/metricas/{promoter_id}", response_model=MetricasGamificacao)
async def obter_metricas_promoter(
    promoter_id: int,
    periodo: str = Query("mes", description="mes, semana, dia, total"),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter métricas detalhadas de gamificação de um promoter"""
    
    # Verificar acesso
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.id != promoter_id):
        promoter = db.query(Usuario).filter(Usuario.id == promoter_id).first()
        if not promoter or usuario_atual.empresa_id != promoter.empresa_id:
            raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Calcular período
    agora = datetime.now()
    if periodo == "dia":
        data_inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == "semana":
        data_inicio = agora - timedelta(days=agora.weekday())
        data_inicio = data_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == "mes":
        data_inicio = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # total
        data_inicio = datetime(2020, 1, 1)
    
    # Calcular métricas
    vendas_total = db.query(func.count(Transacao.id)).filter(
        Transacao.promoter_id == promoter_id,
        Transacao.status == "aprovada",
        Transacao.criado_em >= data_inicio
    ).scalar() or 0
    
    receita_total = db.query(func.sum(Transacao.valor)).filter(
        Transacao.promoter_id == promoter_id,
        Transacao.status == "aprovada",
        Transacao.criado_em >= data_inicio
    ).scalar() or Decimal(0)
    
    eventos_trabalhados = db.query(func.count(func.distinct(Transacao.evento_id))).filter(
        Transacao.promoter_id == promoter_id,
        Transacao.status == "aprovada",
        Transacao.criado_em >= data_inicio
    ).scalar() or 0
    
    conquistas_obtidas = db.query(func.count(PromoterConquista.id)).filter(
        PromoterConquista.promoter_id == promoter_id,
        PromoterConquista.data_conquista >= data_inicio
    ).scalar() or 0
    
    # XP e nível
    pontos_xp = vendas_total * 10 + float(receita_total) / 10
    nivel = min(int(pontos_xp / 1000) + 1, 50)
    xp_proximo_nivel = 1000 - (pontos_xp % 1000)
    
    return MetricasGamificacao(
        promoter_id=promoter_id,
        vendas_total=vendas_total,
        receita_total=float(receita_total),
        eventos_trabalhados=eventos_trabalhados,
        conquistas_obtidas=conquistas_obtidas,
        nivel_atual=nivel,
        pontos_xp=int(pontos_xp),
        xp_proximo_nivel=int(xp_proximo_nivel),
        ticket_medio=float(receita_total / vendas_total) if vendas_total > 0 else 0,
        periodo_consultado=periodo,
        data_inicio=data_inicio,
        data_fim=agora
    )