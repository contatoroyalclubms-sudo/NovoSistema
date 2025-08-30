"""
Priority #6: QR Code Check-in System
Sistema completo de check-in com QR codes para eventos
"""

import qrcode
import io
import base64
import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from PIL import Image

logger = logging.getLogger(__name__)

@dataclass
class CheckInEvent:
    """Evento para check-in"""
    id: str
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    max_capacity: int
    created_at: datetime
    status: str = "active"  # active, paused, ended
    qr_code_data: Optional[str] = None
    check_ins_count: int = 0

@dataclass
class CheckInRecord:
    """Registro de check-in"""
    id: str
    event_id: str
    user_name: str
    user_email: Optional[str]
    user_phone: Optional[str]
    check_in_time: datetime
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    device_info: Optional[str] = None
    ip_address: Optional[str] = None

@dataclass
class QRCodeConfig:
    """Configuração do QR Code"""
    version: int = 1
    error_correction: str = "M"  # L, M, Q, H
    box_size: int = 10
    border: int = 4
    fill_color: str = "black"
    back_color: str = "white"

class QRCodeCheckInManager:
    """Gerenciador do sistema de check-in com QR codes"""
    
    def __init__(self):
        self.events: Dict[str, CheckInEvent] = {}
        self.check_ins: Dict[str, CheckInRecord] = {}
        self.config = QRCodeConfig()
        self.data_file = Path("qr_checkin_data.json")
        self.load_data()
        
        logger.info("[QR_CHECKIN] QRCodeCheckInManager inicializado")

    def load_data(self):
        """Carrega dados persistidos"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Carregar eventos
                for event_data in data.get('events', []):
                    event_data['start_time'] = datetime.fromisoformat(event_data['start_time'])
                    event_data['end_time'] = datetime.fromisoformat(event_data['end_time'])
                    event_data['created_at'] = datetime.fromisoformat(event_data['created_at'])
                    event = CheckInEvent(**event_data)
                    self.events[event.id] = event
                
                # Carregar check-ins
                for checkin_data in data.get('check_ins', []):
                    checkin_data['check_in_time'] = datetime.fromisoformat(checkin_data['check_in_time'])
                    checkin = CheckInRecord(**checkin_data)
                    self.check_ins[checkin.id] = checkin
                
                logger.info(f"[QR_CHECKIN] Dados carregados: {len(self.events)} eventos, {len(self.check_ins)} check-ins")
        except Exception as e:
            logger.error(f"[QR_CHECKIN] Erro ao carregar dados: {e}")

    def save_data(self):
        """Salva dados no arquivo"""
        try:
            data = {
                'events': [
                    {
                        **asdict(event),
                        'start_time': event.start_time.isoformat(),
                        'end_time': event.end_time.isoformat(),
                        'created_at': event.created_at.isoformat()
                    }
                    for event in self.events.values()
                ],
                'check_ins': [
                    {
                        **asdict(checkin),
                        'check_in_time': checkin.check_in_time.isoformat()
                    }
                    for checkin in self.check_ins.values()
                ]
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("[QR_CHECKIN] Dados salvos com sucesso")
        except Exception as e:
            logger.error(f"[QR_CHECKIN] Erro ao salvar dados: {e}")

    def create_event(self, name: str, description: str, start_time: datetime, 
                    end_time: datetime, location: str, max_capacity: int) -> CheckInEvent:
        """Cria um novo evento"""
        try:
            event_id = str(uuid.uuid4())
            
            event = CheckInEvent(
                id=event_id,
                name=name,
                description=description,
                start_time=start_time,
                end_time=end_time,
                location=location,
                max_capacity=max_capacity,
                created_at=datetime.now()
            )
            
            # Gerar QR code para o evento
            qr_data = self.generate_qr_code_data(event_id)
            event.qr_code_data = qr_data
            
            self.events[event_id] = event
            self.save_data()
            
            logger.info(f"[QR_CHECKIN] Evento criado: {name} (ID: {event_id})")
            return event
            
        except Exception as e:
            logger.error(f"[QR_CHECKIN] Erro ao criar evento: {e}")
            raise

    def generate_qr_code_data(self, event_id: str) -> str:
        """Gera dados do QR code para o evento"""
        qr_data = {
            "type": "event_checkin",
            "event_id": event_id,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }
        return json.dumps(qr_data)

    def generate_qr_code_image(self, event_id: str) -> str:
        """Gera imagem do QR code em base64"""
        try:
            event = self.events.get(event_id)
            if not event:
                raise ValueError(f"Evento não encontrado: {event_id}")
            
            # Configurar QR code
            error_correction_map = {
                "L": qrcode.constants.ERROR_CORRECT_L,
                "M": qrcode.constants.ERROR_CORRECT_M,
                "Q": qrcode.constants.ERROR_CORRECT_Q,
                "H": qrcode.constants.ERROR_CORRECT_H
            }
            
            qr = qrcode.QRCode(
                version=self.config.version,
                error_correction=error_correction_map[self.config.error_correction],
                box_size=self.config.box_size,
                border=self.config.border,
            )
            
            qr.add_data(event.qr_code_data)
            qr.make(fit=True)
            
            # Criar imagem
            qr_image = qr.make_image(
                fill_color=self.config.fill_color,
                back_color=self.config.back_color
            )
            
            # Converter para base64
            img_buffer = io.BytesIO()
            qr_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            logger.info(f"[QR_CHECKIN] QR code gerado para evento: {event_id}")
            return qr_base64
            
        except Exception as e:
            logger.error(f"[QR_CHECKIN] Erro ao gerar QR code: {e}")
            raise

    def process_check_in(self, qr_data: str, user_name: str, user_email: Optional[str] = None,
                        user_phone: Optional[str] = None, location_lat: Optional[float] = None,
                        location_lng: Optional[float] = None, device_info: Optional[str] = None,
                        ip_address: Optional[str] = None) -> Dict:
        """Processa um check-in a partir dos dados do QR code"""
        try:
            # Decodificar dados do QR
            qr_info = json.loads(qr_data)
            event_id = qr_info.get('event_id')
            
            if not event_id:
                return {"success": False, "message": "QR code inválido: evento não especificado"}
            
            event = self.events.get(event_id)
            if not event:
                return {"success": False, "message": "Evento não encontrado"}
            
            # Verificar se evento está ativo
            now = datetime.now()
            if event.status != "active":
                return {"success": False, "message": f"Evento está {event.status}"}
            
            if now < event.start_time:
                return {"success": False, "message": "Evento ainda não começou"}
            
            if now > event.end_time:
                return {"success": False, "message": "Evento já terminou"}
            
            # Verificar capacidade
            if event.check_ins_count >= event.max_capacity:
                return {"success": False, "message": "Evento lotado"}
            
            # Verificar se usuário já fez check-in
            existing_checkin = self.find_user_checkin(event_id, user_email or user_name)
            if existing_checkin:
                return {
                    "success": False, 
                    "message": "Usuário já fez check-in neste evento",
                    "existing_checkin": existing_checkin.check_in_time.isoformat()
                }
            
            # Criar registro de check-in
            checkin_id = str(uuid.uuid4())
            checkin = CheckInRecord(
                id=checkin_id,
                event_id=event_id,
                user_name=user_name,
                user_email=user_email,
                user_phone=user_phone,
                check_in_time=now,
                location_lat=location_lat,
                location_lng=location_lng,
                device_info=device_info,
                ip_address=ip_address
            )
            
            self.check_ins[checkin_id] = checkin
            
            # Atualizar contador do evento
            event.check_ins_count += 1
            
            self.save_data()
            
            logger.info(f"[QR_CHECKIN] Check-in realizado: {user_name} no evento {event.name}")
            
            return {
                "success": True,
                "message": "Check-in realizado com sucesso",
                "checkin_id": checkin_id,
                "event_name": event.name,
                "check_in_time": checkin.check_in_time.isoformat(),
                "attendees_count": event.check_ins_count,
                "capacity": event.max_capacity
            }
            
        except json.JSONDecodeError:
            return {"success": False, "message": "QR code inválido: formato incorreto"}
        except Exception as e:
            logger.error(f"[QR_CHECKIN] Erro no check-in: {e}")
            return {"success": False, "message": f"Erro interno: {str(e)}"}

    def find_user_checkin(self, event_id: str, user_identifier: str) -> Optional[CheckInRecord]:
        """Busca check-in existente do usuário no evento"""
        for checkin in self.check_ins.values():
            if (checkin.event_id == event_id and 
                (checkin.user_email == user_identifier or checkin.user_name == user_identifier)):
                return checkin
        return None

    def get_event_stats(self, event_id: str) -> Dict:
        """Obtém estatísticas do evento"""
        try:
            event = self.events.get(event_id)
            if not event:
                return {"error": "Evento não encontrado"}
            
            event_checkins = [c for c in self.check_ins.values() if c.event_id == event_id]
            
            # Estatísticas por hora
            hourly_stats = {}
            for checkin in event_checkins:
                hour = checkin.check_in_time.strftime("%H:00")
                hourly_stats[hour] = hourly_stats.get(hour, 0) + 1
            
            # Taxa de ocupação
            occupancy_rate = (len(event_checkins) / event.max_capacity) * 100 if event.max_capacity > 0 else 0
            
            return {
                "event_id": event_id,
                "event_name": event.name,
                "total_checkins": len(event_checkins),
                "max_capacity": event.max_capacity,
                "occupancy_rate": round(occupancy_rate, 2),
                "hourly_checkins": hourly_stats,
                "last_checkin": event_checkins[-1].check_in_time.isoformat() if event_checkins else None,
                "event_status": event.status,
                "event_start": event.start_time.isoformat(),
                "event_end": event.end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"[QR_CHECKIN] Erro ao obter estatísticas: {e}")
            return {"error": str(e)}

    def get_all_events(self) -> List[Dict]:
        """Lista todos os eventos"""
        return [
            {
                **asdict(event),
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "created_at": event.created_at.isoformat()
            }
            for event in self.events.values()
        ]

    def get_dashboard_data(self) -> Dict:
        """Dados para dashboard geral"""
        try:
            active_events = [e for e in self.events.values() if e.status == "active"]
            total_checkins = len(self.check_ins)
            
            # Check-ins hoje
            today = datetime.now().date()
            today_checkins = [
                c for c in self.check_ins.values() 
                if c.check_in_time.date() == today
            ]
            
            # Eventos mais populares
            event_popularity = {}
            for checkin in self.check_ins.values():
                event_popularity[checkin.event_id] = event_popularity.get(checkin.event_id, 0) + 1
            
            popular_events = sorted(event_popularity.items(), key=lambda x: x[1], reverse=True)[:5]
            popular_events_data = []
            for event_id, count in popular_events:
                event = self.events.get(event_id)
                if event:
                    popular_events_data.append({
                        "event_name": event.name,
                        "checkins": count,
                        "capacity": event.max_capacity,
                        "occupancy_rate": round((count / event.max_capacity) * 100, 1) if event.max_capacity > 0 else 0
                    })
            
            return {
                "total_events": len(self.events),
                "active_events": len(active_events),
                "total_checkins": total_checkins,
                "today_checkins": len(today_checkins),
                "popular_events": popular_events_data,
                "recent_checkins": [
                    {
                        "user_name": c.user_name,
                        "event_id": c.event_id,
                        "event_name": self.events.get(c.event_id, {}).name if c.event_id in self.events else "Unknown",
                        "check_in_time": c.check_in_time.isoformat()
                    }
                    for c in sorted(self.check_ins.values(), key=lambda x: x.check_in_time, reverse=True)[:10]
                ]
            }
            
        except Exception as e:
            logger.error(f"[QR_CHECKIN] Erro no dashboard: {e}")
            return {"error": str(e)}

# Instância global
qr_checkin_manager = QRCodeCheckInManager()
