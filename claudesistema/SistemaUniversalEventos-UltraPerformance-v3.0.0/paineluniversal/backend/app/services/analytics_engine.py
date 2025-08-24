"""
Advanced Analytics Engine - Sprint 5
Sistema Universal de Gestão de Eventos

Sistema completo de analytics com:
- Métricas de eventos em tempo real
- Analytics financeiros avançados
- Comportamento de usuários
- Métricas operacionais
- Dashboards customizáveis
- Alertas automáticos
- Relatórios programados
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_, case, extract
from decimal import Decimal
import json
import logging

from ..models import (
    Evento, Usuario, Participante, Transacao, VendaPDV, CheckinLog, 
    CheckinSession, Pontuacao, PromoterConquista, RankingGamificacao,
    StatusEvento, StatusParticipante, TipoUsuario, StatusTransacao
)
from ..services.websocket_events import websocket_event_manager, EventType, WebSocketEvent

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Sistema avançado de analytics e métricas para o sistema de eventos
    """
    
    def __init__(self):
        self.cache = {}  # Cache em memória para métricas frequentes
        self.cache_ttl = 300  # 5 minutos de TTL para cache
        
    async def get_dashboard_summary(self, user_id: str, db: Session) -> Dict[str, Any]:
        """
        Obtém resumo completo do dashboard para o usuário
        """
        try:
            # Buscar dados do usuário
            usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
            if not usuario:
                return {}
            
            # Métricas gerais da empresa/usuário
            summary = {
                "overview": await self._get_overview_metrics(usuario, db),
                "events": await self._get_events_metrics(usuario, db),
                "financial": await self._get_financial_metrics(usuario, db),
                "checkin": await self._get_checkin_metrics(usuario, db),
                "gamification": await self._get_gamification_metrics(usuario, db),
                "recent_activity": await self._get_recent_activity(usuario, db),
                "alerts": await self._get_system_alerts(usuario, db),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard summary: {e}")
            return {}

    async def _get_overview_metrics(self, usuario: Usuario, db: Session) -> Dict[str, Any]:
        """Métricas de visão geral"""
        try:
            # Filtros baseados no tipo de usuário
            event_filter = self._get_event_filter(usuario)
            
            # Contadores básicos
            total_eventos = db.query(func.count(Evento.id)).filter(event_filter).scalar() or 0
            
            eventos_ativos = db.query(func.count(Evento.id)).filter(
                and_(event_filter, Evento.status == StatusEvento.ATIVO)
            ).scalar() or 0
            
            total_participantes = db.query(func.count(Participante.id)).join(
                Evento, Participante.evento_id == Evento.id
            ).filter(event_filter).scalar() or 0
            
            # Métricas de período (último mês)
            last_month = datetime.utcnow() - timedelta(days=30)
            
            eventos_mes = db.query(func.count(Evento.id)).filter(
                and_(event_filter, Evento.created_at >= last_month)
            ).scalar() or 0
            
            checkins_mes = db.query(func.count(CheckinLog.id)).join(
                Participante, CheckinLog.participante_id == Participante.id
            ).join(
                Evento, Participante.evento_id == Evento.id
            ).filter(
                and_(event_filter, CheckinLog.tentativa_em >= last_month, CheckinLog.sucesso == True)
            ).scalar() or 0
            
            # Taxa de presença média
            taxa_presenca = 0
            if total_participantes > 0:
                participantes_presentes = db.query(func.count(Participante.id)).filter(
                    and_(
                        Participante.status == StatusParticipante.PRESENTE,
                        Participante.evento_id.in_(
                            db.query(Evento.id).filter(event_filter)
                        )
                    )
                ).scalar() or 0
                taxa_presenca = (participantes_presentes / total_participantes) * 100
            
            return {
                "total_eventos": total_eventos,
                "eventos_ativos": eventos_ativos,
                "total_participantes": total_participantes,
                "eventos_ultimo_mes": eventos_mes,
                "checkins_ultimo_mes": checkins_mes,
                "taxa_presenca_media": round(taxa_presenca, 2),
                "crescimento_eventos": await self._calculate_growth_rate(
                    "eventos", usuario, db
                ),
                "crescimento_participantes": await self._calculate_growth_rate(
                    "participantes", usuario, db
                )
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas overview: {e}")
            return {}

    async def _get_events_metrics(self, usuario: Usuario, db: Session) -> Dict[str, Any]:
        """Métricas específicas de eventos"""
        try:
            event_filter = self._get_event_filter(usuario)
            
            # Eventos por status
            eventos_por_status = db.query(
                Evento.status,
                func.count(Evento.id).label('count')
            ).filter(event_filter).group_by(Evento.status).all()
            
            status_dict = {status.value: 0 for status in StatusEvento}
            for status, count in eventos_por_status:
                status_dict[status.value] = count
            
            # Eventos por tipo
            eventos_por_tipo = db.query(
                Evento.tipo_evento,
                func.count(Evento.id).label('count')
            ).filter(event_filter).group_by(Evento.tipo_evento).all()
            
            # Top 5 eventos por participantes
            top_eventos = db.query(
                Evento.nome,
                Evento.id,
                func.count(Participante.id).label('participantes')
            ).outerjoin(
                Participante, Evento.id == Participante.evento_id
            ).filter(event_filter).group_by(
                Evento.id, Evento.nome
            ).order_by(desc('participantes')).limit(5).all()
            
            # Eventos próximos (próximos 30 dias)
            proximos_30_dias = datetime.utcnow() + timedelta(days=30)
            eventos_proximos = db.query(
                Evento.nome,
                Evento.data_inicio,
                func.count(Participante.id).label('participantes')
            ).outerjoin(
                Participante, Evento.id == Participante.evento_id
            ).filter(
                and_(
                    event_filter,
                    Evento.data_inicio >= datetime.utcnow(),
                    Evento.data_inicio <= proximos_30_dias,
                    Evento.status == StatusEvento.ATIVO
                )
            ).group_by(
                Evento.id, Evento.nome, Evento.data_inicio
            ).order_by(Evento.data_inicio).limit(10).all()
            
            return {
                "por_status": status_dict,
                "por_tipo": [
                    {"tipo": tipo.value, "count": count}
                    for tipo, count in eventos_por_tipo
                ],
                "top_eventos": [
                    {
                        "nome": nome,
                        "id": str(evento_id),
                        "participantes": participantes
                    }
                    for nome, evento_id, participantes in top_eventos
                ],
                "proximos_eventos": [
                    {
                        "nome": nome,
                        "data_inicio": data_inicio.isoformat(),
                        "participantes": participantes
                    }
                    for nome, data_inicio, participantes in eventos_proximos
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de eventos: {e}")
            return {}

    async def _get_financial_metrics(self, usuario: Usuario, db: Session) -> Dict[str, Any]:
        """Métricas financeiras avançadas"""
        try:
            event_filter = self._get_event_filter(usuario)
            
            # Receita total
            receita_total = db.query(func.sum(Transacao.valor_liquido)).join(
                Evento, Transacao.evento_id == Evento.id
            ).filter(
                and_(event_filter, Transacao.status == StatusTransacao.APROVADA)
            ).scalar() or Decimal('0')
            
            # Receita do mês atual
            inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            receita_mes = db.query(func.sum(Transacao.valor_liquido)).join(
                Evento, Transacao.evento_id == Evento.id
            ).filter(
                and_(
                    event_filter, 
                    Transacao.status == StatusTransacao.APROVADA,
                    Transacao.data_transacao >= inicio_mes
                )
            ).scalar() or Decimal('0')
            
            # Receita por forma de pagamento
            receita_por_pagamento = db.query(
                Transacao.forma_pagamento,
                func.sum(Transacao.valor_liquido).label('total')
            ).join(
                Evento, Transacao.evento_id == Evento.id
            ).filter(
                and_(event_filter, Transacao.status == StatusTransacao.APROVADA)
            ).group_by(Transacao.forma_pagamento).all()
            
            # Ticket médio
            ticket_medio = db.query(func.avg(Transacao.valor_liquido)).join(
                Evento, Transacao.evento_id == Evento.id
            ).filter(
                and_(event_filter, Transacao.status == StatusTransacao.APROVADA)
            ).scalar() or Decimal('0')
            
            # Receita diária dos últimos 30 dias
            last_30_days = datetime.utcnow() - timedelta(days=30)
            receita_diaria = db.query(
                func.date(Transacao.data_transacao).label('data'),
                func.sum(Transacao.valor_liquido).label('receita')
            ).join(
                Evento, Transacao.evento_id == Evento.id
            ).filter(
                and_(
                    event_filter,
                    Transacao.status == StatusTransacao.APROVADA,
                    Transacao.data_transacao >= last_30_days
                )
            ).group_by(func.date(Transacao.data_transacao)).all()
            
            # Top produtos vendidos (PDV)
            top_produtos = db.query(
                VendaPDV.id.label('produto_nome'),  # Simplificado - seria necessário join com produtos
                func.sum(VendaPDV.valor_liquido).label('receita_produto')
            ).join(
                Evento, VendaPDV.evento_id == Evento.id
            ).filter(
                and_(event_filter, VendaPDV.status == "APROVADA")
            ).group_by('produto_nome').order_by(desc('receita_produto')).limit(5).all()
            
            return {
                "receita_total": float(receita_total),
                "receita_mes_atual": float(receita_mes),
                "ticket_medio": float(ticket_medio),
                "crescimento_receita": await self._calculate_revenue_growth(usuario, db),
                "por_forma_pagamento": [
                    {
                        "forma": forma.value,
                        "valor": float(total),
                        "percentual": float((total / receita_total * 100)) if receita_total > 0 else 0
                    }
                    for forma, total in receita_por_pagamento
                ],
                "receita_diaria": [
                    {
                        "data": data.isoformat(),
                        "receita": float(receita)
                    }
                    for data, receita in receita_diaria
                ],
                "top_produtos": [
                    {
                        "produto": produto_nome,
                        "receita": float(receita_produto)
                    }
                    for produto_nome, receita_produto in top_produtos
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas financeiras: {e}")
            return {}

    async def _get_checkin_metrics(self, usuario: Usuario, db: Session) -> Dict[str, Any]:
        """Métricas de check-in e presença"""
        try:
            event_filter = self._get_event_filter(usuario)
            
            # Total de check-ins realizados
            total_checkins = db.query(func.count(CheckinLog.id)).join(
                Participante, CheckinLog.participante_id == Participante.id
            ).join(
                Evento, Participante.evento_id == Evento.id
            ).filter(
                and_(event_filter, CheckinLog.sucesso == True)
            ).scalar() or 0
            
            # Check-ins por tipo
            checkins_por_tipo = db.query(
                CheckinLog.tipo_checkin,
                func.count(CheckinLog.id).label('count')
            ).join(
                Participante, CheckinLog.participante_id == Participante.id
            ).join(
                Evento, Participante.evento_id == Evento.id
            ).filter(
                and_(event_filter, CheckinLog.sucesso == True)
            ).group_by(CheckinLog.tipo_checkin).all()
            
            # Tempo médio de permanência
            tempo_medio = db.query(
                func.avg(CheckinSession.tempo_permanencia_minutos)
            ).join(
                Participante, CheckinSession.participante_id == Participante.id
            ).join(
                Evento, Participante.evento_id == Evento.id
            ).filter(
                and_(
                    event_filter,
                    CheckinSession.checkout_em.isnot(None),
                    CheckinSession.tempo_permanencia_minutos.isnot(None)
                )
            ).scalar() or 0
            
            # Check-ins por hora do dia (últimos 7 dias)
            last_week = datetime.utcnow() - timedelta(days=7)
            checkins_por_hora = db.query(
                extract('hour', CheckinLog.tentativa_em).label('hora'),
                func.count(CheckinLog.id).label('count')
            ).join(
                Participante, CheckinLog.participante_id == Participante.id
            ).join(
                Evento, Participante.evento_id == Evento.id
            ).filter(
                and_(
                    event_filter,
                    CheckinLog.sucesso == True,
                    CheckinLog.tentativa_em >= last_week
                )
            ).group_by('hora').all()
            
            # Taxa de sucesso de check-ins
            total_tentativas = db.query(func.count(CheckinLog.id)).join(
                Participante, CheckinLog.participante_id == Participante.id
            ).join(
                Evento, Participante.evento_id == Evento.id
            ).filter(event_filter).scalar() or 0
            
            taxa_sucesso = (total_checkins / total_tentativas * 100) if total_tentativas > 0 else 0
            
            # Eventos com maior taxa de presença
            eventos_alta_presenca = db.query(
                Evento.nome,
                (func.count(case([(Participante.status == StatusParticipante.PRESENTE, 1)])) * 100.0 / 
                 func.count(Participante.id)).label('taxa_presenca')
            ).outerjoin(
                Participante, Evento.id == Participante.evento_id
            ).filter(event_filter).group_by(
                Evento.id, Evento.nome
            ).having(func.count(Participante.id) > 0).order_by(
                desc('taxa_presenca')
            ).limit(5).all()
            
            return {
                "total_checkins": total_checkins,
                "taxa_sucesso": round(taxa_sucesso, 2),
                "tempo_medio_permanencia": round(float(tempo_medio), 1),
                "por_tipo": [
                    {"tipo": tipo.value, "count": count}
                    for tipo, count in checkins_por_tipo
                ],
                "por_hora": [
                    {"hora": int(hora), "count": count}
                    for hora, count in checkins_por_hora
                ],
                "eventos_alta_presenca": [
                    {
                        "nome": nome,
                        "taxa_presenca": round(float(taxa), 1)
                    }
                    for nome, taxa in eventos_alta_presenca
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de check-in: {e}")
            return {}

    async def _get_gamification_metrics(self, usuario: Usuario, db: Session) -> Dict[str, Any]:
        """Métricas de gamificação"""
        try:
            # Pontos totais distribuídos
            total_pontos = db.query(func.sum(Pontuacao.pontos_total)).join(
                Usuario, Pontuacao.usuario_id == Usuario.id
            ).filter(self._get_user_filter(usuario)).scalar() or 0
            
            # Conquistas desbloqueadas
            total_conquistas = db.query(func.count(PromoterConquista.id)).join(
                Usuario, PromoterConquista.usuario_id == Usuario.id
            ).filter(
                and_(
                    self._get_user_filter(usuario),
                    PromoterConquista.desbloqueada == True
                )
            ).scalar() or 0
            
            # Top 5 usuários por pontos (mês atual)
            inicio_mes = datetime.utcnow().replace(day=1)
            top_usuarios = db.query(
                Usuario.nome,
                func.sum(Pontuacao.pontos_total).label('pontos')
            ).outerjoin(
                Pontuacao, and_(
                    Pontuacao.usuario_id == Usuario.id,
                    Pontuacao.created_at >= inicio_mes
                )
            ).filter(self._get_user_filter(usuario)).group_by(
                Usuario.id, Usuario.nome
            ).order_by(desc('pontos')).limit(5).all()
            
            # Ações mais realizadas
            top_acoes = db.query(
                Pontuacao.tipo_acao,
                func.count(Pontuacao.id).label('count')
            ).join(
                Usuario, Pontuacao.usuario_id == Usuario.id
            ).filter(self._get_user_filter(usuario)).group_by(
                Pontuacao.tipo_acao
            ).order_by(desc('count')).limit(10).all()
            
            # Distribuição por badges
            badges_distribuicao = db.query(
                RankingGamificacao.badge_atual,
                func.count(RankingGamificacao.id).label('count')
            ).join(
                Usuario, RankingGamificacao.usuario_id == Usuario.id
            ).filter(self._get_user_filter(usuario)).group_by(
                RankingGamificacao.badge_atual
            ).all()
            
            return {
                "total_pontos_distribuidos": int(total_pontos),
                "total_conquistas_desbloqueadas": total_conquistas,
                "top_usuarios_mes": [
                    {"nome": nome, "pontos": int(pontos or 0)}
                    for nome, pontos in top_usuarios
                ],
                "top_acoes": [
                    {"acao": acao, "count": count}
                    for acao, count in top_acoes
                ],
                "badges_distribuicao": [
                    {"badge": badge, "count": count}
                    for badge, count in badges_distribuicao
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de gamificação: {e}")
            return {}

    async def _get_recent_activity(self, usuario: Usuario, db: Session) -> List[Dict]:
        """Atividades recentes do sistema"""
        try:
            activities = []
            
            # Últimos eventos criados
            eventos_recentes = db.query(
                Evento.nome, Evento.created_at, Usuario.nome.label('criador')
            ).join(
                Usuario, Evento.usuario_criador_id == Usuario.id
            ).filter(self._get_event_filter(usuario)).order_by(
                desc(Evento.created_at)
            ).limit(5).all()
            
            for evento in eventos_recentes:
                activities.append({
                    "type": "evento_criado",
                    "title": f"Evento '{evento.nome}' criado",
                    "description": f"Criado por {evento.criador}",
                    "timestamp": evento.created_at.isoformat(),
                    "icon": "🎪"
                })
            
            # Últimos check-ins
            checkins_recentes = db.query(
                CheckinLog.tentativa_em,
                Participante.usuario_id,
                Usuario.nome,
                Evento.nome.label('evento_nome')
            ).join(
                Participante, CheckinLog.participante_id == Participante.id
            ).join(
                Usuario, Participante.usuario_id == Usuario.id
            ).join(
                Evento, Participante.evento_id == Evento.id
            ).filter(
                and_(
                    self._get_event_filter(usuario),
                    CheckinLog.sucesso == True
                )
            ).order_by(desc(CheckinLog.tentativa_em)).limit(5).all()
            
            for checkin in checkins_recentes:
                activities.append({
                    "type": "checkin",
                    "title": f"Check-in realizado",
                    "description": f"{checkin.nome} no evento {checkin.evento_nome}",
                    "timestamp": checkin.tentativa_em.isoformat(),
                    "icon": "✅"
                })
            
            # Ordenar por timestamp
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return activities[:10]  # Últimas 10 atividades
            
        except Exception as e:
            logger.error(f"Erro ao buscar atividades recentes: {e}")
            return []

    async def _get_system_alerts(self, usuario: Usuario, db: Session) -> List[Dict]:
        """Alertas do sistema baseados em métricas"""
        try:
            alerts = []
            
            # Verificar eventos com baixa taxa de presença
            baixa_presenca = db.query(
                Evento.nome,
                Evento.id,
                (func.count(case([(Participante.status == StatusParticipante.PRESENTE, 1)])) * 100.0 / 
                 func.count(Participante.id)).label('taxa_presenca')
            ).outerjoin(
                Participante, Evento.id == Participante.evento_id
            ).filter(
                and_(
                    self._get_event_filter(usuario),
                    Evento.status == StatusEvento.ATIVO
                )
            ).group_by(
                Evento.id, Evento.nome
            ).having(
                and_(
                    func.count(Participante.id) > 10,  # Apenas eventos com mais de 10 participantes
                    (func.count(case([(Participante.status == StatusParticipante.PRESENTE, 1)])) * 100.0 / 
                     func.count(Participante.id)) < 60  # Taxa menor que 60%
                )
            ).limit(3).all()
            
            for evento in baixa_presenca:
                alerts.append({
                    "type": "warning",
                    "title": "Taxa de Presença Baixa",
                    "description": f"O evento '{evento.nome}' tem taxa de presença de {evento.taxa_presenca:.1f}%",
                    "action_url": f"/eventos/{evento.id}",
                    "severity": "medium"
                })
            
            # Verificar eventos próximos sem participantes
            proximos_sem_participantes = db.query(
                Evento.nome,
                Evento.data_inicio
            ).outerjoin(
                Participante, Evento.id == Participante.evento_id
            ).filter(
                and_(
                    self._get_event_filter(usuario),
                    Evento.data_inicio >= datetime.utcnow(),
                    Evento.data_inicio <= datetime.utcnow() + timedelta(days=7),
                    Evento.status == StatusEvento.ATIVO
                )
            ).group_by(
                Evento.id, Evento.nome, Evento.data_inicio
            ).having(func.count(Participante.id) == 0).limit(3).all()
            
            for evento in proximos_sem_participantes:
                days_until = (evento.data_inicio - datetime.utcnow()).days
                alerts.append({
                    "type": "warning",
                    "title": "Evento Sem Participantes",
                    "description": f"O evento '{evento.nome}' está em {days_until} dias e ainda não tem participantes",
                    "severity": "high"
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Erro ao gerar alertas do sistema: {e}")
            return []

    def _get_event_filter(self, usuario: Usuario):
        """Filtro de eventos baseado no tipo de usuário"""
        if usuario.tipo == TipoUsuario.ADMIN:
            return True  # Admin vê todos os eventos
        else:
            return Evento.empresa_id == usuario.empresa_id

    def _get_user_filter(self, usuario: Usuario):
        """Filtro de usuários baseado no tipo de usuário"""
        if usuario.tipo == TipoUsuario.ADMIN:
            return True  # Admin vê todos os usuários
        else:
            return Usuario.empresa_id == usuario.empresa_id

    async def _calculate_growth_rate(self, metric: str, usuario: Usuario, db: Session) -> float:
        """Calcula taxa de crescimento para uma métrica"""
        try:
            # Período atual (últimos 30 dias) vs período anterior (30-60 dias atrás)
            now = datetime.utcnow()
            current_start = now - timedelta(days=30)
            previous_start = now - timedelta(days=60)
            
            if metric == "eventos":
                current = db.query(func.count(Evento.id)).filter(
                    and_(
                        self._get_event_filter(usuario),
                        Evento.created_at >= current_start
                    )
                ).scalar() or 0
                
                previous = db.query(func.count(Evento.id)).filter(
                    and_(
                        self._get_event_filter(usuario),
                        Evento.created_at >= previous_start,
                        Evento.created_at < current_start
                    )
                ).scalar() or 0
                
            elif metric == "participantes":
                current = db.query(func.count(Participante.id)).join(
                    Evento, Participante.evento_id == Evento.id
                ).filter(
                    and_(
                        self._get_event_filter(usuario),
                        Participante.data_inscricao >= current_start
                    )
                ).scalar() or 0
                
                previous = db.query(func.count(Participante.id)).join(
                    Evento, Participante.evento_id == Evento.id
                ).filter(
                    and_(
                        self._get_event_filter(usuario),
                        Participante.data_inscricao >= previous_start,
                        Participante.data_inscricao < current_start
                    )
                ).scalar() or 0
            else:
                return 0.0
            
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            
            return ((current - previous) / previous) * 100
            
        except Exception as e:
            logger.error(f"Erro ao calcular taxa de crescimento: {e}")
            return 0.0

    async def _calculate_revenue_growth(self, usuario: Usuario, db: Session) -> float:
        """Calcula crescimento de receita"""
        try:
            now = datetime.utcnow()
            current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Mês anterior
            if current_month_start.month == 1:
                previous_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
            else:
                previous_month_start = current_month_start.replace(month=current_month_start.month - 1)
            
            # Receita do mês atual
            current_revenue = db.query(func.sum(Transacao.valor_liquido)).join(
                Evento, Transacao.evento_id == Evento.id
            ).filter(
                and_(
                    self._get_event_filter(usuario),
                    Transacao.status == StatusTransacao.APROVADA,
                    Transacao.data_transacao >= current_month_start
                )
            ).scalar() or Decimal('0')
            
            # Receita do mês anterior
            previous_revenue = db.query(func.sum(Transacao.valor_liquido)).join(
                Evento, Transacao.evento_id == Evento.id
            ).filter(
                and_(
                    self._get_event_filter(usuario),
                    Transacao.status == StatusTransacao.APROVADA,
                    Transacao.data_transacao >= previous_month_start,
                    Transacao.data_transacao < current_month_start
                )
            ).scalar() or Decimal('0')
            
            if previous_revenue == 0:
                return 100.0 if current_revenue > 0 else 0.0
            
            return float(((current_revenue - previous_revenue) / previous_revenue) * 100)
            
        except Exception as e:
            logger.error(f"Erro ao calcular crescimento de receita: {e}")
            return 0.0

    async def generate_custom_report(
        self, 
        user_id: str, 
        report_config: Dict[str, Any], 
        db: Session
    ) -> Dict[str, Any]:
        """
        Gera relatório customizado baseado na configuração
        """
        try:
            usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
            if not usuario:
                return {}
            
            report_type = report_config.get("type", "summary")
            date_range = report_config.get("date_range", {})
            filters = report_config.get("filters", {})
            
            # Implementar diferentes tipos de relatório
            if report_type == "events_detailed":
                return await self._generate_events_detailed_report(usuario, date_range, filters, db)
            elif report_type == "financial_analysis":
                return await self._generate_financial_analysis_report(usuario, date_range, filters, db)
            elif report_type == "user_engagement":
                return await self._generate_user_engagement_report(usuario, date_range, filters, db)
            else:
                return await self.get_dashboard_summary(user_id, db)
                
        except Exception as e:
            logger.error(f"Erro ao gerar relatório customizado: {e}")
            return {}


# Instância global do analytics engine
analytics_engine = AnalyticsEngine()