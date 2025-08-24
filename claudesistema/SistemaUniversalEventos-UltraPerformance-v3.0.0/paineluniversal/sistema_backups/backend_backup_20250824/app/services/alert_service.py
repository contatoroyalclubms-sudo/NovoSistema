import asyncio
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from ..database import SessionLocal
from ..models import Evento, Lista, Transacao, Usuario, TipoLista
from ..services.whatsapp_service import whatsapp_service
import logging

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.alert_rules = {
            "limite_lista": self.check_limite_lista,
            "aniversarios_vip": self.check_aniversarios_vip,
            "vendas_baixas": self.check_vendas_baixas,
            "evento_proximo": self.check_evento_proximo,
            "conquistas_pendentes": self.check_conquistas_pendentes
        }
    
    async def run_alert_checks(self):
        """Executar todas as verificações de alerta"""
        db = SessionLocal()
        try:
            for rule_name, rule_func in self.alert_rules.items():
                try:
                    await rule_func(db)
                except Exception as e:
                    logger.error(f"Erro na regra {rule_name}: {e}")
        finally:
            db.close()
    
    async def check_limite_lista(self, db: Session):
        """Verificar listas próximas do limite"""
        listas_criticas = db.query(Lista).filter(
            Lista.ativa == True,
            Lista.limite_vendas.isnot(None),
            Lista.vendas_realizadas >= Lista.limite_vendas * 0.9
        ).all()
        
        for lista in listas_criticas:
            percentual = (lista.vendas_realizadas / lista.limite_vendas) * 100
            
            if lista.promoter_id:
                promoter = db.query(Usuario).filter(Usuario.id == lista.promoter_id).first()
                if promoter and promoter.telefone:
                    message = f"""
🚨 *ALERTA - LIMITE DE LISTA*

Lista: {lista.nome}
Vendas: {lista.vendas_realizadas}/{lista.limite_vendas} ({percentual:.1f}%)
Evento: {lista.evento.nome}

Ação necessária: Verificar estratégia de vendas
                    """.strip()
                    
                    await whatsapp_service._send_whatsapp_message(
                        promoter.telefone, message
                    )
    
    async def check_aniversarios_vip(self, db: Session):
        """Verificar aniversariantes VIP nos próximos eventos"""
        hoje = date.today()
        proximos_7_dias = hoje + timedelta(days=7)
        
        eventos_proximos = db.query(Evento).filter(
            func.date(Evento.data_evento).between(hoje, proximos_7_dias)
        ).all()
        
        for evento in eventos_proximos:
            transacoes_vip = db.query(Transacao).join(Lista).filter(
                Transacao.evento_id == evento.id,
                Lista.tipo == TipoLista.VIP,
                Transacao.status == "aprovada"
            ).all()
            
            aniversariantes = []
            for transacao in transacoes_vip:
                if self._is_birthday_week(transacao.cpf_comprador):
                    aniversariantes.append(transacao.nome_comprador)
            
            if aniversariantes:
                admin_users = db.query(Usuario).filter(
                    Usuario.empresa_id == evento.empresa_id,
                    Usuario.tipo == "admin"
                ).all()
                
                for admin in admin_users:
                    if admin.telefone:
                        message = f"""
🎂 *ANIVERSARIANTES VIP*

Evento: {evento.nome}
Data: {evento.data_evento.strftime('%d/%m/%Y')}

Aniversariantes da semana:
{chr(10).join(f"• {nome}" for nome in aniversariantes)}

Considere preparar algo especial! 🎉
                        """.strip()
                        
                        await whatsapp_service._send_whatsapp_message(
                            admin.telefone, message
                        )
    
    async def check_vendas_baixas(self, db: Session):
        """Verificar eventos com vendas baixas"""
        hoje = date.today()
        proximos_30_dias = hoje + timedelta(days=30)
        
        eventos_proximos = db.query(Evento).filter(
            func.date(Evento.data_evento).between(hoje, proximos_30_dias)
        ).all()
        
        for evento in eventos_proximos:
            total_vendas = db.query(func.count(Transacao.id)).filter(
                Transacao.evento_id == evento.id,
                Transacao.status == "aprovada"
            ).scalar() or 0
            
            dias_restantes = (evento.data_evento.date() - hoje).days
            
            if dias_restantes <= 7 and total_vendas < 10:
                promoters = db.query(Usuario).join(
                    Lista, Lista.promoter_id == Usuario.id
                ).filter(Lista.evento_id == evento.id).distinct().all()
                
                for promoter in promoters:
                    if promoter.telefone:
                        message = f"""
📉 *ALERTA - VENDAS BAIXAS*

Evento: {evento.nome}
Data: {evento.data_evento.strftime('%d/%m/%Y')}
Vendas atuais: {total_vendas}
Dias restantes: {dias_restantes}

Ação sugerida: Intensificar divulgação
                        """.strip()
                        
                        await whatsapp_service._send_whatsapp_message(
                            promoter.telefone, message
                        )
    
    async def check_evento_proximo(self, db: Session):
        """Verificar eventos nas próximas 24h"""
        amanha = date.today() + timedelta(days=1)
        
        eventos_amanha = db.query(Evento).filter(
            func.date(Evento.data_evento) == amanha
        ).all()
        
        for evento in eventos_amanha:
            total_vendas = db.query(func.count(Transacao.id)).filter(
                Transacao.evento_id == evento.id,
                Transacao.status == "aprovada"
            ).scalar() or 0
            
            admin_users = db.query(Usuario).filter(
                Usuario.empresa_id == evento.empresa_id,
                Usuario.tipo == "admin"
            ).all()
            
            for admin in admin_users:
                if admin.telefone:
                    message = f"""
⏰ *EVENTO AMANHÃ*

{evento.nome}
📅 {evento.data_evento.strftime('%d/%m/%Y às %H:%M')}
📍 {evento.local}
🎫 {total_vendas} vendas confirmadas

Lembrete: Preparar equipe e materiais
                    """.strip()
                    
                    await whatsapp_service._send_whatsapp_message(
                        admin.telefone, message
                    )
    
    def _is_birthday_week(self, cpf: str) -> bool:
        """Mock para verificação de aniversário (requer API de CPF real)"""
        return cpf.endswith(('01', '15', '30'))
    
    async def check_conquistas_pendentes(self, db: Session):
        """Verificar promoters que podem ter novas conquistas"""
        from ..models import Conquista, PromoterConquista, TipoConquista
        
        promoters_ativos = db.query(Usuario).filter(
            Usuario.tipo == "promoter",
            Usuario.ativo == True
        ).all()
        
        for promoter in promoters_ativos:
            total_vendas = db.query(func.count(Transacao.id)).join(Lista).filter(
                Lista.promoter_id == promoter.id,
                Transacao.status == "aprovada"
            ).scalar() or 0
            
            conquistas_vendas = db.query(Conquista).filter(
                Conquista.tipo == TipoConquista.VENDAS,
                Conquista.criterio_valor <= total_vendas,
                Conquista.ativa == True
            ).all()
            
            for conquista in conquistas_vendas:
                ja_possui = db.query(PromoterConquista).filter(
                    PromoterConquista.promoter_id == promoter.id,
                    PromoterConquista.conquista_id == conquista.id
                ).first()
                
                if not ja_possui and promoter.telefone:
                    message = f"""
🎉 *NOVA CONQUISTA DISPONÍVEL!*

{promoter.nome}, você pode ter desbloqueado:
{conquista.icone} {conquista.nome}

Acesse o sistema para verificar! 🚀
                    """.strip()
                    
                    await whatsapp_service._send_whatsapp_message(
                        promoter.telefone, message
                    )

alert_service = AlertService()
