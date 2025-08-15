from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from ..database import get_db
from ..models import Evento, Transacao, Checkin, Usuario, Lista, PromoterEvento
from ..schemas import DashboardResumo, RankingPromoter, DashboardAvancado, FiltrosDashboard, RankingPromoterAvancado, DadosGrafico
from ..auth import obter_usuario_atual

router = APIRouter()

@router.get("/resumo", response_model=DashboardResumo)
async def obter_resumo_dashboard(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter resumo do dashboard"""
    
    if usuario_atual.tipo.value == "admin":
        eventos_query = db.query(Evento)
        transacoes_query = db.query(Transacao)
        checkins_query = db.query(Checkin)
    else:
        eventos_query = db.query(Evento).filter(Evento.empresa_id == usuario_atual.empresa_id)
        transacoes_query = db.query(Transacao).join(Evento).filter(Evento.empresa_id == usuario_atual.empresa_id)
        checkins_query = db.query(Checkin).join(Evento).filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    total_eventos = eventos_query.count()
    total_vendas = transacoes_query.filter(Transacao.status == "aprovada").count()
    total_checkins = checkins_query.count()
    
    receita_total = transacoes_query.filter(Transacao.status == "aprovada").with_entities(
        func.sum(Transacao.valor)
    ).scalar() or Decimal('0.00')
    
    hoje = date.today()
    eventos_hoje = eventos_query.filter(func.date(Evento.data_evento) == hoje).count()
    vendas_hoje = transacoes_query.filter(
        func.date(Transacao.criado_em) == hoje,
        Transacao.status == "aprovada"
    ).count()
    
    return DashboardResumo(
        total_eventos=total_eventos,
        total_vendas=total_vendas,
        total_checkins=total_checkins,
        receita_total=receita_total,
        eventos_hoje=eventos_hoje,
        vendas_hoje=vendas_hoje
    )

@router.get("/ranking-promoters", response_model=List[RankingPromoter])
async def obter_ranking_promoters(
    evento_id: Optional[int] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter ranking de promoters por vendas"""
    
    query = db.query(
        Usuario.id.label('promoter_id'),
        Usuario.nome.label('nome_promoter'),
        func.count(Transacao.id).label('total_vendas'),
        func.sum(Transacao.valor).label('receita_gerada')
    ).join(
        Lista, Lista.promoter_id == Usuario.id
    ).join(
        Transacao, Transacao.lista_id == Lista.id
    ).filter(
        Transacao.status == "aprovada",
        Usuario.tipo == "promoter"
    )
    
    if usuario_atual.tipo.value != "admin":
        query = query.join(Evento, Evento.id == Transacao.evento_id).filter(
            Evento.empresa_id == usuario_atual.empresa_id
        )
    
    if evento_id:
        query = query.filter(Transacao.evento_id == evento_id)
    
    ranking_data = query.group_by(
        Usuario.id, Usuario.nome
    ).order_by(
        desc('total_vendas')
    ).limit(limit).all()
    
    ranking = []
    for i, row in enumerate(ranking_data, 1):
        ranking.append(RankingPromoter(
            promoter_id=row.promoter_id,
            nome_promoter=row.nome_promoter,
            total_vendas=row.total_vendas,
            receita_gerada=row.receita_gerada or Decimal('0.00'),
            posicao=i
        ))
    
    return ranking

@router.get("/vendas-tempo-real")
async def obter_vendas_tempo_real(
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter dados de vendas em tempo real"""
    
    query = db.query(Transacao)
    
    if usuario_atual.tipo.value != "admin":
        query = query.join(Evento).filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    if evento_id:
        query = query.filter(Transacao.evento_id == evento_id)
    
    vendas_por_hora = query.filter(
        Transacao.criado_em >= datetime.now() - timedelta(hours=24),
        Transacao.status == "aprovada"
    ).with_entities(
        func.extract('hour', Transacao.criado_em).label('hora'),
        func.count(Transacao.id).label('vendas'),
        func.sum(Transacao.valor).label('receita')
    ).group_by('hora').order_by('hora').all()
    
    vendas_por_lista = query.join(Lista).filter(
        Transacao.status == "aprovada"
    ).with_entities(
        Lista.tipo.label('tipo_lista'),
        func.count(Transacao.id).label('vendas'),
        func.sum(Transacao.valor).label('receita')
    ).group_by(Lista.tipo).all()
    
    return {
        "vendas_por_hora": [
            {
                "hora": int(row.hora),
                "vendas": row.vendas,
                "receita": float(row.receita or 0)
            }
            for row in vendas_por_hora
        ],
        "vendas_por_lista": [
            {
                "tipo": row.tipo_lista.value,
                "vendas": row.vendas,
                "receita": float(row.receita or 0)
            }
            for row in vendas_por_lista
        ]
    }

@router.get("/aniversariantes")
async def obter_aniversariantes(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter lista de aniversariantes do evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    
    return {
        "evento_id": evento_id,
        "data_evento": evento.data_evento,
        "aniversariantes": [],
        "total": 0,
        "observacao": "Funcionalidade requer integração com API de validação de CPF"
    }

@router.get("/tempo-real/{evento_id}")
async def obter_dados_tempo_real(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter dados em tempo real para dashboard"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    uma_hora_atras = datetime.now() - timedelta(hours=1)
    vendas_ultima_hora = db.query(func.count(Transacao.id)).filter(
        Transacao.evento_id == evento_id,
        Transacao.status == "aprovada",
        Transacao.criado_em >= uma_hora_atras
    ).scalar() or 0
    
    checkins_ultima_hora = db.query(func.count(Checkin.id)).filter(
        Checkin.evento_id == evento_id,
        Checkin.checkin_em >= uma_hora_atras
    ).scalar() or 0
    
    ranking_atual = await obter_ranking_promoters(evento_id, 5, db, usuario_atual)
    
    return {
        "evento_id": evento_id,
        "timestamp": datetime.now().isoformat(),
        "vendas_ultima_hora": vendas_ultima_hora,
        "checkins_ultima_hora": checkins_ultima_hora,
        "ranking_promoters": ranking_atual,
        "status_evento": evento.status.value
    }

@router.get("/avancado", response_model=DashboardAvancado)
async def obter_dashboard_avancado(
    evento_id: Optional[int] = None,
    promoter_id: Optional[int] = None,
    tipo_lista: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    metodo_pagamento: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Dashboard avançado com métricas completas"""
    
    eventos_query = db.query(Evento)
    transacoes_query = db.query(Transacao)
    checkins_query = db.query(Checkin)
    
    if usuario_atual.tipo.value != "admin":
        eventos_query = eventos_query.filter(Evento.empresa_id == usuario_atual.empresa_id)
        transacoes_query = transacoes_query.join(Evento).filter(Evento.empresa_id == usuario_atual.empresa_id)
        checkins_query = checkins_query.join(Evento).filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    if evento_id:
        transacoes_query = transacoes_query.filter(Transacao.evento_id == evento_id)
        checkins_query = checkins_query.filter(Checkin.evento_id == evento_id)
        eventos_query = eventos_query.filter(Evento.id == evento_id)
    
    if data_inicio:
        transacoes_query = transacoes_query.filter(Transacao.criado_em >= data_inicio)
        checkins_query = checkins_query.filter(Checkin.checkin_em >= data_inicio)
    
    if data_fim:
        transacoes_query = transacoes_query.filter(Transacao.criado_em <= data_fim)
        checkins_query = checkins_query.filter(Checkin.checkin_em <= data_fim)
    
    if metodo_pagamento:
        transacoes_query = transacoes_query.filter(Transacao.metodo_pagamento == metodo_pagamento)
    
    total_vendas = transacoes_query.filter(Transacao.status == "aprovada").count()
    total_checkins = checkins_query.count()
    receita_total = transacoes_query.filter(Transacao.status == "aprovada").with_entities(
        func.sum(Transacao.valor)
    ).scalar() or Decimal('0.00')
    
    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = hoje.replace(day=1)
    
    vendas_hoje = transacoes_query.filter(
        func.date(Transacao.criado_em) == hoje,
        Transacao.status == "aprovada"
    ).count()
    
    vendas_semana = transacoes_query.filter(
        Transacao.criado_em >= inicio_semana,
        Transacao.status == "aprovada"
    ).count()
    
    vendas_mes = transacoes_query.filter(
        Transacao.criado_em >= inicio_mes,
        Transacao.status == "aprovada"
    ).count()
    
    receita_hoje = transacoes_query.filter(
        func.date(Transacao.criado_em) == hoje,
        Transacao.status == "aprovada"
    ).with_entities(func.sum(Transacao.valor)).scalar() or Decimal('0.00')
    
    receita_semana = transacoes_query.filter(
        Transacao.criado_em >= inicio_semana,
        Transacao.status == "aprovada"
    ).with_entities(func.sum(Transacao.valor)).scalar() or Decimal('0.00')
    
    receita_mes = transacoes_query.filter(
        Transacao.criado_em >= inicio_mes,
        Transacao.status == "aprovada"
    ).with_entities(func.sum(Transacao.valor)).scalar() or Decimal('0.00')
    
    checkins_hoje = checkins_query.filter(
        func.date(Checkin.checkin_em) == hoje
    ).count()
    
    checkins_semana = checkins_query.filter(
        Checkin.checkin_em >= inicio_semana
    ).count()
    
    taxa_conversao = (total_checkins / total_vendas * 100) if total_vendas > 0 else 0
    taxa_presenca = taxa_conversao
    
    vendas_sem_checkin = db.query(Transacao).outerjoin(
        Checkin, Transacao.cpf_comprador == Checkin.cpf
    ).filter(
        Transacao.status == "aprovada",
        Checkin.id.is_(None)
    )
    
    if evento_id:
        vendas_sem_checkin = vendas_sem_checkin.filter(Transacao.evento_id == evento_id)
    
    fila_espera = vendas_sem_checkin.count()
    
    cortesias = transacoes_query.filter(
        Transacao.status == "aprovada",
        Transacao.valor == 0
    ).count()
    
    inadimplentes = transacoes_query.filter(
        Transacao.status == "pendente"
    ).count()
    
    aniversariantes_mes = 0
    
    consumo_medio = receita_total / total_vendas if total_vendas > 0 else Decimal('0.00')
    
    return DashboardAvancado(
        total_eventos=eventos_query.count(),
        total_vendas=total_vendas,
        total_checkins=total_checkins,
        receita_total=receita_total,
        taxa_conversao=round(taxa_conversao, 2),
        vendas_hoje=vendas_hoje,
        vendas_semana=vendas_semana,
        vendas_mes=vendas_mes,
        receita_hoje=receita_hoje,
        receita_semana=receita_semana,
        receita_mes=receita_mes,
        checkins_hoje=checkins_hoje,
        checkins_semana=checkins_semana,
        taxa_presenca=round(taxa_presenca, 2),
        fila_espera=fila_espera,
        cortesias=cortesias,
        inadimplentes=inadimplentes,
        aniversariantes_mes=aniversariantes_mes,
        consumo_medio=consumo_medio
    )

@router.get("/graficos/vendas-tempo")
async def obter_grafico_vendas_tempo(
    periodo: str = "7d",
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Gráfico de vendas ao longo do tempo"""
    
    transacoes_query = db.query(Transacao).filter(Transacao.status == "aprovada")
    
    if usuario_atual.tipo.value != "admin":
        transacoes_query = transacoes_query.join(Evento).filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    if evento_id:
        transacoes_query = transacoes_query.filter(Transacao.evento_id == evento_id)
    
    hoje = datetime.now().date()
    
    if periodo == "24h":
        inicio = datetime.now() - timedelta(hours=24)
        dados = []
        for i in range(24):
            hora_inicio = inicio + timedelta(hours=i)
            hora_fim = hora_inicio + timedelta(hours=1)
            vendas = transacoes_query.filter(
                Transacao.criado_em >= hora_inicio,
                Transacao.criado_em < hora_fim
            ).count()
            receita = transacoes_query.filter(
                Transacao.criado_em >= hora_inicio,
                Transacao.criado_em < hora_fim
            ).with_entities(func.sum(Transacao.valor)).scalar() or 0
            
            dados.append({
                "data": hora_inicio.strftime("%H:00"),
                "vendas": vendas,
                "receita": float(receita)
            })
    elif periodo == "7d":
        dados = []
        for i in range(7):
            data_atual = hoje - timedelta(days=6-i)
            vendas = transacoes_query.filter(
                func.date(Transacao.criado_em) == data_atual
            ).count()
            receita = transacoes_query.filter(
                func.date(Transacao.criado_em) == data_atual
            ).with_entities(func.sum(Transacao.valor)).scalar() or 0
            
            dados.append({
                "data": data_atual.strftime("%d/%m"),
                "vendas": vendas,
                "receita": float(receita)
            })
    else:
        dados = []
        for i in range(30):
            data_atual = hoje - timedelta(days=29-i)
            vendas = transacoes_query.filter(
                func.date(Transacao.criado_em) == data_atual
            ).count()
            receita = transacoes_query.filter(
                func.date(Transacao.criado_em) == data_atual
            ).with_entities(func.sum(Transacao.valor)).scalar() or 0
            
            dados.append({
                "data": data_atual.strftime("%d/%m"),
                "vendas": vendas,
                "receita": float(receita)
            })
    
    return dados

@router.get("/graficos/vendas-lista")
async def obter_grafico_vendas_lista(
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Gráfico de vendas por lista"""
    
    query = db.query(
        Lista.nome,
        func.count(Transacao.id).label('vendas'),
        func.sum(Transacao.valor).label('receita')
    ).join(Transacao, Lista.id == Transacao.lista_id).filter(
        Transacao.status == "aprovada"
    )
    
    if usuario_atual.tipo.value != "admin":
        query = query.join(Evento).filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    if evento_id:
        query = query.filter(Transacao.evento_id == evento_id)
    
    resultados = query.group_by(Lista.nome).all()
    
    dados = []
    cores = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']
    
    for i, resultado in enumerate(resultados):
        dados.append({
            "name": resultado.nome,
            "value": resultado.vendas,
            "receita": float(resultado.receita or 0),
            "fill": cores[i % len(cores)]
        })
    
    return dados

@router.get("/ranking-promoters-avancado", response_model=List[RankingPromoterAvancado])
async def obter_ranking_promoters_avancado(
    evento_id: Optional[int] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Ranking avançado de promoters com métricas de conversão"""
    
    query = db.query(
        Usuario.id.label('promoter_id'),
        Usuario.nome.label('nome_promoter'),
        func.count(Transacao.id).label('total_vendas'),
        func.sum(Transacao.valor).label('receita_gerada'),
        func.count(Checkin.id).label('total_checkins')
    ).join(
        Lista, Lista.promoter_id == Usuario.id
    ).join(
        Transacao, Transacao.lista_id == Lista.id
    ).outerjoin(
        Checkin, Transacao.cpf_comprador == Checkin.cpf
    ).filter(
        Transacao.status == "aprovada",
        Usuario.tipo == "promoter"
    )
    
    if usuario_atual.tipo.value != "admin":
        query = query.join(Evento).filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    if evento_id:
        query = query.filter(Transacao.evento_id == evento_id)
    
    resultados = query.group_by(
        Usuario.id, Usuario.nome
    ).order_by(
        desc(func.sum(Transacao.valor))
    ).limit(limit).all()
    
    ranking = []
    for i, resultado in enumerate(resultados):
        taxa_presenca = (resultado.total_checkins / resultado.total_vendas * 100) if resultado.total_vendas > 0 else 0
        taxa_conversao = taxa_presenca
        
        if i == 0:
            badge = "ouro"
        elif i == 1:
            badge = "prata"
        elif i == 2:
            badge = "bronze"
        else:
            badge = "participante"
        
        ranking.append(RankingPromoterAvancado(
            promoter_id=resultado.promoter_id,
            nome_promoter=resultado.nome_promoter,
            total_vendas=resultado.total_vendas,
            receita_gerada=resultado.receita_gerada or Decimal('0.00'),
            total_checkins=resultado.total_checkins or 0,
            taxa_presenca=round(taxa_presenca, 2),
            taxa_conversao=round(taxa_conversao, 2),
            posicao=i + 1,
            badge=badge
        ))
    
    return ranking
