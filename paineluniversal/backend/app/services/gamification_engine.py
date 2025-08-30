"""
Advanced Gamification Engine - Sprint 5
Sistema Universal de Gestão de Eventos

Ultra-modern gamification system with:
- Real-time point calculations
- Dynamic badge system
- Multi-tier leaderboards
- Achievement tracking
- Streak bonuses
- Event-based rewards
- AI-powered recommendations
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
import logging

from ..models import (
    Usuario, Evento, Participante, Transacao, Pontuacao, 
    PromoterConquista, RankingGamificacao, CheckinLog, VendaPDV,
    TipoUsuario, StatusParticipante, StatusTransacao
)
from ..core.database import get_db
from ..websocket import websocket_manager

logger = logging.getLogger(__name__)


class GamificationEngine:
    """
    Sistema avançado de gamificação com processamento em tempo real
    """
    
    def __init__(self):
        self.point_rules = {
            'checkin': {'base': 25, 'multiplier': 1.0, 'max_daily': 100},
            'checkout': {'base': 10, 'multiplier': 1.0, 'max_daily': 50},
            'participation': {'base': 15, 'multiplier': 1.2, 'max_daily': 150},
            'sale_completed': {'base': 50, 'multiplier': 1.5, 'max_daily': 500},
            'event_created': {'base': 100, 'multiplier': 2.0, 'max_daily': 1000},
            'social_share': {'base': 5, 'multiplier': 1.0, 'max_daily': 25},
            'feedback_given': {'base': 20, 'multiplier': 1.1, 'max_daily': 100},
            'referral': {'base': 200, 'multiplier': 3.0, 'max_daily': 2000}
        }
        
        self.achievement_rules = {
            'first_checkin': {'name': 'Primeira Presença', 'icon': '🎯', 'points': 50},
            'early_bird': {'name': 'Chegou Cedo', 'icon': '🐦', 'points': 25},
            'social_butterfly': {'name': 'Sociável', 'icon': '🦋', 'points': 100},
            'sales_champion': {'name': 'Campeão de Vendas', 'icon': '👑', 'points': 300},
            'perfect_attendance': {'name': 'Presença Perfeita', 'icon': '💯', 'points': 500},
            'streak_master': {'name': 'Mestre da Sequência', 'icon': '🔥', 'points': 200}
        }
        
        self.badge_tiers = {
            'bronze': {'min_points': 0, 'max_points': 999, 'color': '#CD7F32', 'icon': '🥉'},
            'silver': {'min_points': 1000, 'max_points': 4999, 'color': '#C0C0C0', 'icon': '🥈'},
            'gold': {'min_points': 5000, 'max_points': 19999, 'color': '#FFD700', 'icon': '🥇'},
            'platinum': {'min_points': 20000, 'max_points': 49999, 'color': '#E5E4E2', 'icon': '🏆'},
            'diamond': {'min_points': 50000, 'max_points': float('inf'), 'color': '#B9F2FF', 'icon': '💎'}
        }

    async def calculate_points(self, user_id: str, action: str, context: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Calcula pontos para uma ação específica com regras avançadas
        
        Args:
            user_id: ID do usuário
            action: Tipo de ação (checkin, sale_completed, etc.)
            context: Contexto da ação (evento_id, valor_transacao, etc.)
            db: Sessão do banco de dados
            
        Returns:
            Dict com pontos calculados e metadados
        """
        try:
            if action not in self.point_rules:
                logger.warning(f"Ação não reconhecida para gamificação: {action}")
                return {'points': 0, 'reason': 'action_not_found'}

            rule = self.point_rules[action]
            base_points = rule['base']
            multiplier = rule['multiplier']
            
            # Buscar usuário
            usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
            if not usuario:
                return {'points': 0, 'reason': 'user_not_found'}
            
            # Calcular multiplicadores dinâmicos
            streak_multiplier = await self._calculate_streak_multiplier(user_id, db)
            time_multiplier = await self._calculate_time_multiplier(context.get('evento_id'), db)
            tier_multiplier = await self._calculate_tier_multiplier(usuario.tipo, db)
            
            # Calcular pontos finais
            total_multiplier = multiplier * streak_multiplier * time_multiplier * tier_multiplier
            final_points = int(base_points * total_multiplier)
            
            # Verificar limite diário
            daily_points = await self._get_daily_points(user_id, action, db)
            if daily_points + final_points > rule['max_daily']:
                final_points = max(0, rule['max_daily'] - daily_points)
            
            # Salvar pontuação
            if final_points > 0:
                await self._save_points(user_id, action, final_points, context, db)
                
                # Verificar conquistas
                achievements = await self._check_achievements(user_id, action, context, db)
                
                # Atualizar ranking
                await self._update_user_ranking(user_id, final_points, db)
                
                # Notificar via WebSocket
                await self._notify_points_earned(user_id, final_points, achievements)
                
                return {
                    'points': final_points,
                    'base_points': base_points,
                    'multipliers': {
                        'streak': streak_multiplier,
                        'time': time_multiplier,
                        'tier': tier_multiplier,
                        'total': total_multiplier
                    },
                    'achievements': achievements,
                    'daily_total': daily_points + final_points,
                    'daily_limit': rule['max_daily']
                }
            
            return {'points': 0, 'reason': 'daily_limit_exceeded'}
            
        except Exception as e:
            logger.error(f"Erro ao calcular pontos para usuário {user_id}: {e}")
            return {'points': 0, 'reason': 'calculation_error', 'error': str(e)}

    async def _calculate_streak_multiplier(self, user_id: str, db: Session) -> float:
        """Calcula multiplicador baseado em sequência de atividades"""
        try:
            # Buscar atividades dos últimos 30 dias
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            # Contar dias consecutivos com atividade
            streak_query = db.query(
                func.date(Pontuacao.created_at).label('data_atividade')
            ).filter(
                and_(
                    Pontuacao.usuario_id == user_id,
                    Pontuacao.created_at >= thirty_days_ago
                )
            ).distinct().order_by(desc('data_atividade'))
            
            dates = [row.data_atividade for row in streak_query.all()]
            
            if not dates:
                return 1.0
            
            # Calcular streak atual
            streak_days = 0
            current_date = datetime.utcnow().date()
            
            for date in dates:
                if date == current_date - timedelta(days=streak_days):
                    streak_days += 1
                else:
                    break
            
            # Multiplicador baseado na streak (máximo 2.0x)
            if streak_days >= 30:
                return 2.0
            elif streak_days >= 15:
                return 1.8
            elif streak_days >= 7:
                return 1.5
            elif streak_days >= 3:
                return 1.2
            else:
                return 1.0
                
        except Exception as e:
            logger.error(f"Erro ao calcular streak multiplier: {e}")
            return 1.0

    async def _calculate_time_multiplier(self, evento_id: str, db: Session) -> float:
        """Calcula multiplicador baseado no horário do evento"""
        try:
            if not evento_id:
                return 1.0
                
            evento = db.query(Evento).filter(Evento.id == evento_id).first()
            if not evento:
                return 1.0
            
            now = datetime.utcnow()
            
            # Multiplicador para check-in antecipado
            if now < evento.data_inicio - timedelta(hours=2):
                return 1.5  # Chegou muito cedo
            elif now < evento.data_inicio:
                return 1.3  # Chegou no horário
            elif now < evento.data_inicio + timedelta(hours=1):
                return 1.0  # Chegou um pouco atrasado
            else:
                return 0.8  # Chegou muito atrasado
                
        except Exception as e:
            logger.error(f"Erro ao calcular time multiplier: {e}")
            return 1.0

    async def _calculate_tier_multiplier(self, tipo_usuario: TipoUsuario, db: Session) -> float:
        """Calcula multiplicador baseado no tipo de usuário"""
        multipliers = {
            TipoUsuario.ADMIN: 1.0,
            TipoUsuario.ORGANIZADOR: 1.2,
            TipoUsuario.OPERADOR: 1.1,
            TipoUsuario.PARTICIPANTE: 1.0
        }
        return multipliers.get(tipo_usuario, 1.0)

    async def _get_daily_points(self, user_id: str, action: str, db: Session) -> int:
        """Obtém pontos já ganhos hoje para uma ação específica"""
        try:
            today = datetime.utcnow().date()
            
            total = db.query(func.sum(Pontuacao.pontos_total)).filter(
                and_(
                    Pontuacao.usuario_id == user_id,
                    func.date(Pontuacao.created_at) == today,
                    Pontuacao.tipo_acao == action
                )
            ).scalar()
            
            return int(total or 0)
            
        except Exception as e:
            logger.error(f"Erro ao buscar pontos diários: {e}")
            return 0

    async def _save_points(self, user_id: str, action: str, points: int, context: Dict, db: Session):
        """Salva pontuação no banco de dados"""
        try:
            pontuacao = Pontuacao(
                usuario_id=user_id,
                evento_id=context.get('evento_id'),
                tipo_acao=action,
                pontos_base=self.point_rules[action]['base'],
                pontos_total=points,
                contexto_acao=context,
                created_at=datetime.utcnow()
            )
            
            db.add(pontuacao)
            db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao salvar pontuação: {e}")
            db.rollback()

    async def _check_achievements(self, user_id: str, action: str, context: Dict, db: Session) -> List[Dict]:
        """Verifica e desbloqueia conquistas"""
        achievements = []
        
        try:
            # First checkin achievement
            if action == 'checkin':
                checkin_count = db.query(func.count(CheckinLog.id)).filter(
                    and_(
                        CheckinLog.participante_id.in_(
                            db.query(Participante.id).filter(Participante.usuario_id == user_id)
                        ),
                        CheckinLog.sucesso == True
                    )
                ).scalar()
                
                if checkin_count == 1:
                    achievements.append(await self._award_achievement(user_id, 'first_checkin', db))
            
            # Early bird achievement
            if action == 'checkin' and context.get('early_checkin'):
                achievements.append(await self._award_achievement(user_id, 'early_bird', db))
            
            # Sales achievements
            if action == 'sale_completed':
                sales_count = db.query(func.count(VendaPDV.id)).filter(
                    VendaPDV.usuario_vendedor_id == user_id
                ).scalar()
                
                if sales_count == 100:
                    achievements.append(await self._award_achievement(user_id, 'sales_champion', db))
            
            return [achievement for achievement in achievements if achievement]
            
        except Exception as e:
            logger.error(f"Erro ao verificar conquistas: {e}")
            return []

    async def _award_achievement(self, user_id: str, achievement_key: str, db: Session) -> Optional[Dict]:
        """Concede uma conquista específica"""
        try:
            # Verificar se já possui a conquista
            existing = db.query(PromoterConquista).filter(
                and_(
                    PromoterConquista.usuario_id == user_id,
                    PromoterConquista.tipo == achievement_key
                )
            ).first()
            
            if existing:
                return None
            
            achievement_data = self.achievement_rules[achievement_key]
            
            conquista = PromoterConquista(
                usuario_id=user_id,
                nome=achievement_data['name'],
                descricao=f"Conquista desbloqueada: {achievement_data['name']}",
                tipo=achievement_key,
                pontos_xp=achievement_data['points'],
                desbloqueada=True,
                data_desbloqueio=datetime.utcnow()
            )
            
            db.add(conquista)
            db.commit()
            
            return {
                'name': achievement_data['name'],
                'icon': achievement_data['icon'],
                'points': achievement_data['points'],
                'description': f"Conquista desbloqueada: {achievement_data['name']}"
            }
            
        except Exception as e:
            logger.error(f"Erro ao conceder conquista: {e}")
            return None

    async def _update_user_ranking(self, user_id: str, points: int, db: Session):
        """Atualiza ranking do usuário"""
        try:
            # Buscar ou criar ranking atual
            current_month = datetime.utcnow().strftime('%Y-%m')
            
            ranking = db.query(RankingGamificacao).filter(
                and_(
                    RankingGamificacao.usuario_id == user_id,
                    RankingGamificacao.mes_referencia == current_month
                )
            ).first()
            
            if not ranking:
                usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
                ranking = RankingGamificacao(
                    usuario_id=user_id,
                    empresa_id=usuario.empresa_id if usuario else None,
                    mes_referencia=current_month,
                    xp_total=0
                )
                db.add(ranking)
            
            # Atualizar pontuação
            ranking.xp_total += points
            ranking.ultima_atualizacao = datetime.utcnow()
            
            # Determinar badge atual baseado nos pontos totais
            total_points = db.query(func.sum(Pontuacao.pontos_total)).filter(
                Pontuacao.usuario_id == user_id
            ).scalar() or 0
            
            for badge_name, badge_data in self.badge_tiers.items():
                if badge_data['min_points'] <= total_points <= badge_data['max_points']:
                    ranking.badge_atual = badge_name
                    break
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar ranking: {e}")
            db.rollback()

    async def _notify_points_earned(self, user_id: str, points: int, achievements: List[Dict]):
        """Envia notificação em tempo real via WebSocket"""
        try:
            notification = {
                'type': 'points_earned',
                'user_id': user_id,
                'points': points,
                'achievements': achievements,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Enviar para o usuário específico
            await websocket_manager.send_personal_message(notification, user_id)
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")

    async def get_user_leaderboard(self, user_id: str, period: str = 'month', limit: int = 100, db: Session) -> List[Dict]:
        """
        Obtém leaderboard para período específico
        
        Args:
            user_id: ID do usuário solicitante
            period: Período (day, week, month, year, all)
            limit: Número máximo de resultados
            db: Sessão do banco
            
        Returns:
            Lista com ranking de usuários
        """
        try:
            # Determinar período de tempo
            now = datetime.utcnow()
            if period == 'day':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == 'month':
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == 'year':
                start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:  # all time
                start_date = datetime(2020, 1, 1)
            
            # Query do ranking
            leaderboard_query = db.query(
                Usuario.id,
                Usuario.nome,
                Usuario.email,
                func.sum(Pontuacao.pontos_total).label('total_points'),
                func.count(Pontuacao.id).label('total_actions'),
                func.max(Pontuacao.created_at).label('last_activity')
            ).outerjoin(
                Pontuacao, and_(
                    Pontuacao.usuario_id == Usuario.id,
                    Pontuacao.created_at >= start_date
                )
            ).group_by(
                Usuario.id, Usuario.nome, Usuario.email
            ).order_by(
                desc('total_points')
            ).limit(limit)
            
            results = leaderboard_query.all()
            
            # Formattar resultados
            leaderboard = []
            for i, result in enumerate(results, 1):
                total_points = int(result.total_points or 0)
                
                # Determinar badge
                badge = 'bronze'
                for badge_name, badge_data in self.badge_tiers.items():
                    if badge_data['min_points'] <= total_points <= badge_data['max_points']:
                        badge = badge_name
                        break
                
                leaderboard.append({
                    'position': i,
                    'user_id': str(result.id),
                    'name': result.nome,
                    'email': result.email,
                    'total_points': total_points,
                    'total_actions': result.total_actions or 0,
                    'badge': badge,
                    'badge_icon': self.badge_tiers[badge]['icon'],
                    'badge_color': self.badge_tiers[badge]['color'],
                    'last_activity': result.last_activity.isoformat() if result.last_activity else None,
                    'is_current_user': str(result.id) == user_id
                })
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Erro ao buscar leaderboard: {e}")
            return []

    async def get_user_profile(self, user_id: str, db: Session) -> Dict[str, Any]:
        """
        Obtém perfil completo de gamificação do usuário
        
        Args:
            user_id: ID do usuário
            db: Sessão do banco
            
        Returns:
            Dict com dados completos do perfil
        """
        try:
            # Dados básicos do usuário
            usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
            if not usuario:
                return {}
            
            # Pontos totais
            total_points = db.query(func.sum(Pontuacao.pontos_total)).filter(
                Pontuacao.usuario_id == user_id
            ).scalar() or 0
            
            # Conquistas
            achievements = db.query(PromoterConquista).filter(
                and_(
                    PromoterConquista.usuario_id == user_id,
                    PromoterConquista.desbloqueada == True
                )
            ).all()
            
            # Ranking atual
            current_month = datetime.utcnow().strftime('%Y-%m')
            ranking = db.query(RankingGamificacao).filter(
                and_(
                    RankingGamificacao.usuario_id == user_id,
                    RankingGamificacao.mes_referencia == current_month
                )
            ).first()
            
            # Estatísticas de atividade
            activity_stats = db.query(
                func.count(Pontuacao.id).label('total_actions'),
                func.avg(Pontuacao.pontos_total).label('avg_points_per_action'),
                func.max(Pontuacao.created_at).label('last_activity')
            ).filter(Pontuacao.usuario_id == user_id).first()
            
            # Determinar badge atual
            current_badge = 'bronze'
            for badge_name, badge_data in self.badge_tiers.items():
                if badge_data['min_points'] <= total_points <= badge_data['max_points']:
                    current_badge = badge_name
                    break
            
            # Próximo badge
            next_badge = None
            points_to_next = 0
            for badge_name, badge_data in self.badge_tiers.items():
                if badge_data['min_points'] > total_points:
                    next_badge = badge_name
                    points_to_next = badge_data['min_points'] - total_points
                    break
            
            return {
                'user_id': str(user_id),
                'name': usuario.nome,
                'email': usuario.email,
                'total_points': int(total_points),
                'monthly_points': ranking.xp_total if ranking else 0,
                'current_badge': {
                    'name': current_badge,
                    'icon': self.badge_tiers[current_badge]['icon'],
                    'color': self.badge_tiers[current_badge]['color'],
                    'min_points': self.badge_tiers[current_badge]['min_points']
                },
                'next_badge': {
                    'name': next_badge,
                    'icon': self.badge_tiers[next_badge]['icon'] if next_badge else None,
                    'color': self.badge_tiers[next_badge]['color'] if next_badge else None,
                    'points_needed': points_to_next
                } if next_badge else None,
                'achievements': [
                    {
                        'name': achievement.nome,
                        'description': achievement.descricao,
                        'type': achievement.tipo,
                        'points': achievement.pontos_xp,
                        'unlocked_at': achievement.data_desbloqueio.isoformat()
                    }
                    for achievement in achievements
                ],
                'activity_stats': {
                    'total_actions': activity_stats.total_actions or 0,
                    'avg_points_per_action': float(activity_stats.avg_points_per_action or 0),
                    'last_activity': activity_stats.last_activity.isoformat() if activity_stats.last_activity else None
                },
                'monthly_ranking': {
                    'position': ranking.posicao_geral if ranking else None,
                    'company_position': ranking.posicao_empresa if ranking else None,
                    'level': ranking.nivel_atual if ranking else 1
                } if ranking else None
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar perfil de gamificação: {e}")
            return {}


# Instância global do engine
gamification_engine = GamificationEngine()