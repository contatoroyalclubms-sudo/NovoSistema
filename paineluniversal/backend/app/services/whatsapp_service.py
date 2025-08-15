import asyncio
import json
import logging
import qrcode
import io
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Evento, Usuario, Transacao, Checkin, Lista
from ..auth import validar_cpf_basico
import aiohttp
import websockets

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.session_data = {}
        self.qr_code = None
        self.is_connected = False
        self.webhook_url = None
        self.n8n_webhook_url = None
        
    async def initialize_session(self) -> Dict[str, Any]:
        """Inicializa sessão do WhatsApp e retorna QR Code"""
        try:
            self.qr_code = self._generate_mock_qr()
            
            return {
                "status": "qr_ready",
                "qr_code": self.qr_code,
                "message": "Escaneie o QR Code com seu WhatsApp"
            }
        except Exception as e:
            logger.error(f"Erro ao inicializar sessão WhatsApp: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_mock_qr(self) -> str:
        """Gera QR Code mock para demonstração"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://wa.me/qr/mock-session-" + str(datetime.now().timestamp()))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    async def send_invite(self, phone: str, evento_id: int, lista_id: int, db: Session) -> Dict[str, Any]:
        """Envia convite via WhatsApp"""
        try:
            evento = db.query(Evento).filter(Evento.id == evento_id).first()
            lista = db.query(Lista).filter(Lista.id == lista_id).first()
            
            if not evento or not lista:
                return {"status": "error", "message": "Evento ou lista não encontrados"}
            
            message = self._format_invite_message(evento, lista)
            
            result = await self._send_whatsapp_message(phone, message)
            
            return {
                "status": "sent",
                "phone": phone,
                "evento": evento.nome,
                "lista": lista.nome,
                "message": "Convite enviado com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar convite: {e}")
            return {"status": "error", "message": str(e)}
    
    def _format_invite_message(self, evento: Evento, lista: Lista) -> str:
        """Formata mensagem de convite"""
        data_formatada = evento.data_evento.strftime("%d/%m/%Y às %H:%M")
        
        message = f"""
🎉 *CONVITE ESPECIAL* 🎉

Você está convidado(a) para:
*{evento.nome}*

📅 Data: {data_formatada}
📍 Local: {evento.local}
🎫 Lista: {lista.nome}
💰 Valor: R$ {lista.preco}

Para confirmar presença, responda com:
*CONFIRMAR [SEU CPF]*

Exemplo: CONFIRMAR 123.456.789-10

Limite de idade: {evento.limite_idade}+ anos
        """.strip()
        
        return message
    
    async def _send_whatsapp_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Envia mensagem via WhatsApp (mock)"""
        await asyncio.sleep(0.5)  # Simula delay de envio
        
        return {
            "messageId": f"msg_{datetime.now().timestamp()}",
            "status": "sent",
            "phone": phone
        }
    
    async def process_incoming_message(self, phone: str, message: str, db: Session) -> Dict[str, Any]:
        """Processa mensagens recebidas via WhatsApp"""
        try:
            message = message.strip().upper()
            
            if message.startswith("CONFIRMAR"):
                return await self._process_confirmation(phone, message, db)
            
            elif message.startswith("CHECKIN"):
                return await self._process_checkin(phone, message, db)
            
            else:
                return await self._send_help_message(phone)
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _process_confirmation(self, phone: str, message: str, db: Session) -> Dict[str, Any]:
        """Processa confirmação de presença"""
        try:
            parts = message.split()
            if len(parts) < 2:
                return await self._send_error_message(phone, "Formato inválido. Use: CONFIRMAR [SEU CPF]")
            
            cpf = parts[1].replace(".", "").replace("-", "")
            
            if not validar_cpf_basico(cpf):
                return await self._send_error_message(phone, "CPF inválido. Verifique e tente novamente.")
            
            cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
            
            transacoes = db.query(Transacao).filter(
                Transacao.cpf_comprador == cpf_formatado,
                Transacao.status == "pendente"
            ).all()
            
            if not transacoes:
                return await self._send_error_message(phone, "Nenhum convite pendente encontrado para este CPF.")
            
            for transacao in transacoes:
                transacao.status = "confirmado"
                transacao.telefone_comprador = phone
            
            db.commit()
            
            response_msg = f"""
✅ *PRESENÇA CONFIRMADA!*

CPF: {cpf_formatado}
Eventos confirmados: {len(transacoes)}

Para fazer check-in no evento, responda:
*CHECKIN [CPF] [3 PRIMEIROS DÍGITOS]*

Exemplo: CHECKIN {cpf_formatado} {cpf[:3]}
            """.strip()
            
            await self._send_whatsapp_message(phone, response_msg)
            
            await self.notify_n8n("confirmacao_presenca", {
                "cpf": cpf_formatado,
                "phone": phone,
                "eventos_confirmados": len(transacoes)
            })
            
            return {
                "status": "confirmed",
                "cpf": cpf_formatado,
                "eventos_confirmados": len(transacoes)
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar confirmação: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _process_checkin(self, phone: str, message: str, db: Session) -> Dict[str, Any]:
        """Processa check-in via WhatsApp"""
        try:
            parts = message.split()
            if len(parts) < 3:
                return await self._send_error_message(phone, "Formato inválido. Use: CHECKIN [CPF] [3 DÍGITOS]")
            
            cpf = parts[1].replace(".", "").replace("-", "")
            validacao = parts[2]
            
            if not validar_cpf_basico(cpf):
                return await self._send_error_message(phone, "CPF inválido.")
            
            if len(validacao) != 3 or not validacao.isdigit():
                return await self._send_error_message(phone, "Validação deve ter exatamente 3 dígitos.")
            
            if cpf[:3] != validacao:
                return await self._send_error_message(phone, "Dígitos de validação incorretos.")
            
            cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
            
            hoje = datetime.now().date()
            transacoes = db.query(Transacao).join(Evento).filter(
                Transacao.cpf_comprador == cpf_formatado,
                Transacao.status == "confirmado",
                Evento.data_evento.cast(db.Date) == hoje
            ).all()
            
            if not transacoes:
                return await self._send_error_message(phone, "Nenhum evento confirmado para hoje.")
            
            checkin_existente = db.query(Checkin).filter(
                Checkin.cpf == cpf_formatado,
                Checkin.evento_id.in_([t.evento_id for t in transacoes])
            ).first()
            
            if checkin_existente:
                return await self._send_error_message(phone, "Check-in já realizado para este evento.")
            
            checkins_realizados = []
            for transacao in transacoes:
                checkin = Checkin(
                    cpf=cpf_formatado,
                    nome=transacao.nome_comprador,
                    evento_id=transacao.evento_id,
                    transacao_id=transacao.id,
                    metodo_checkin="whatsapp",
                    validacao_cpf=validacao,
                    checkin_em=datetime.now()
                )
                db.add(checkin)
                checkins_realizados.append(transacao.evento.nome)
            
            db.commit()
            
            response_msg = f"""
✅ *CHECK-IN REALIZADO!*

CPF: {cpf_formatado}
Nome: {transacoes[0].nome_comprador}
Eventos: {', '.join(checkins_realizados)}
Horário: {datetime.now().strftime('%H:%M')}

Bem-vindo(a) ao evento! 🎉
            """.strip()
            
            await self._send_whatsapp_message(phone, response_msg)
            
            await self.notify_n8n("checkin_realizado", {
                "cpf": cpf_formatado,
                "phone": phone,
                "eventos": checkins_realizados
            })
            
            return {
                "status": "checkin_success",
                "cpf": cpf_formatado,
                "eventos": checkins_realizados
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar check-in: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _send_help_message(self, phone: str) -> Dict[str, Any]:
        """Envia mensagem de ajuda"""
        help_msg = """
🤖 *SISTEMA DE EVENTOS*

Comandos disponíveis:

*CONFIRMAR [CPF]*
Confirma sua presença no evento

*CHECKIN [CPF] [3 DÍGITOS]*
Realiza check-in no evento

Exemplo:
CONFIRMAR 123.456.789-10
CHECKIN 123.456.789-10 123

Precisa de ajuda? Entre em contato com a organização.
        """.strip()
        
        await self._send_whatsapp_message(phone, help_msg)
        return {"status": "help_sent"}
    
    async def _send_error_message(self, phone: str, error: str) -> Dict[str, Any]:
        """Envia mensagem de erro"""
        error_msg = f"❌ *ERRO*\n\n{error}\n\nDigite qualquer mensagem para ver os comandos disponíveis."
        await self._send_whatsapp_message(phone, error_msg)
        return {"status": "error_sent", "message": error}
    
    async def send_bulk_invites(self, evento_id: int, lista_id: int, phones: List[str], db: Session) -> Dict[str, Any]:
        """Envia convites em massa"""
        try:
            results = []
            for phone in phones:
                result = await self.send_invite(phone, evento_id, lista_id, db)
                results.append({"phone": phone, "result": result})
                await asyncio.sleep(1)  # Delay entre envios
            
            success_count = sum(1 for r in results if r["result"]["status"] == "sent")
            
            return {
                "status": "completed",
                "total": len(phones),
                "success": success_count,
                "failed": len(phones) - success_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Erro no envio em massa: {e}")
            return {"status": "error", "message": str(e)}
    
    async def set_n8n_webhook(self, webhook_url: str):
        """Configurar webhook N8N para automações"""
        self.n8n_webhook_url = webhook_url
        
    async def notify_n8n(self, event_type: str, data: Dict[str, Any]):
        """Notificar N8N sobre eventos do WhatsApp"""
        if not self.n8n_webhook_url:
            return
            
        payload = {
            "source": "whatsapp",
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.n8n_webhook_url, json=payload) as response:
                    logger.info(f"N8N notificado: {event_type} - Status: {response.status}")
        except Exception as e:
            logger.error(f"Erro ao notificar N8N: {e}")

    async def get_session_status(self) -> Dict[str, Any]:
        """Retorna status da sessão WhatsApp"""
        return {
            "connected": self.is_connected,
            "qr_code": self.qr_code,
            "session_data": bool(self.session_data)
        }

whatsapp_service = WhatsAppService()
