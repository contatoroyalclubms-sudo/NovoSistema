"""
Router para Sistema de QR Code Check-in
Priority #6: QR Code Check-in System - API Endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from ..qr_checkin_manager import qr_checkin_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/qr-checkin", tags=["QR Check-in System"])

class EventCreateModel(BaseModel):
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    max_capacity: int

class CheckInModel(BaseModel):
    qr_data: str
    user_name: str
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    device_info: Optional[str] = None

@router.get("/health")
async def qr_checkin_health():
    """Health check do sistema de QR check-in"""
    try:
        events_count = len(qr_checkin_manager.events)
        checkins_count = len(qr_checkin_manager.check_ins)
        active_events = len([e for e in qr_checkin_manager.events.values() if e.status == "active"])
        
        return {
            "status": "healthy",
            "message": "Sistema de QR check-in funcionando",
            "total_events": events_count,
            "active_events": active_events,
            "total_checkins": checkins_count
        }
    except Exception as e:
        logger.error(f"[QR_CHECKIN] Erro no health check: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no sistema: {e}")

@router.post("/events")
async def create_event(event_data: EventCreateModel):
    """Cria um novo evento para check-in"""
    try:
        # Validações
        if event_data.start_time >= event_data.end_time:
            raise HTTPException(status_code=400, detail="Data de início deve ser anterior à data de fim")
        
        if event_data.max_capacity <= 0:
            raise HTTPException(status_code=400, detail="Capacidade máxima deve ser maior que zero")
        
        event = qr_checkin_manager.create_event(
            name=event_data.name,
            description=event_data.description,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            location=event_data.location,
            max_capacity=event_data.max_capacity
        )
        
        return {
            "success": True,
            "message": "Evento criado com sucesso",
            "event": {
                "id": event.id,
                "name": event.name,
                "description": event.description,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "location": event.location,
                "max_capacity": event.max_capacity,
                "status": event.status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[QR_CHECKIN] Erro ao criar evento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/events")
async def list_events():
    """Lista todos os eventos"""
    try:
        events = qr_checkin_manager.get_all_events()
        return {
            "success": True,
            "data": events,
            "total": len(events)
        }
    except Exception as e:
        logger.error(f"[QR_CHECKIN] Erro ao listar eventos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/events/{event_id}")
async def get_event(event_id: str):
    """Obtém detalhes de um evento específico"""
    try:
        event = qr_checkin_manager.events.get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        
        return {
            "success": True,
            "data": {
                "id": event.id,
                "name": event.name,
                "description": event.description,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "location": event.location,
                "max_capacity": event.max_capacity,
                "status": event.status,
                "check_ins_count": event.check_ins_count,
                "created_at": event.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[QR_CHECKIN] Erro ao obter evento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/events/{event_id}/qr-code")
async def get_event_qr_code(event_id: str):
    """Gera e retorna o QR code do evento"""
    try:
        event = qr_checkin_manager.events.get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        
        qr_image_base64 = qr_checkin_manager.generate_qr_code_image(event_id)
        
        return {
            "success": True,
            "data": {
                "event_id": event_id,
                "event_name": event.name,
                "qr_code_image": f"data:image/png;base64,{qr_image_base64}",
                "qr_code_data": event.qr_code_data
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[QR_CHECKIN] Erro ao gerar QR code: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.post("/checkin")
async def process_checkin(checkin_data: CheckInModel, request: Request):
    """Processa um check-in via QR code"""
    try:
        # Capturar IP do usuário
        client_ip = request.client.host if request.client else None
        
        result = qr_checkin_manager.process_check_in(
            qr_data=checkin_data.qr_data,
            user_name=checkin_data.user_name,
            user_email=checkin_data.user_email,
            user_phone=checkin_data.user_phone,
            location_lat=checkin_data.location_lat,
            location_lng=checkin_data.location_lng,
            device_info=checkin_data.device_info,
            ip_address=client_ip
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "data": {
                    "checkin_id": result["checkin_id"],
                    "event_name": result["event_name"],
                    "check_in_time": result["check_in_time"],
                    "attendees_count": result["attendees_count"],
                    "capacity": result["capacity"]
                }
            }
        else:
            return {
                "success": False,
                "message": result["message"],
                "data": result.get("existing_checkin")
            }
            
    except Exception as e:
        logger.error(f"[QR_CHECKIN] Erro no check-in: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/events/{event_id}/stats")
async def get_event_stats(event_id: str):
    """Obtém estatísticas detalhadas do evento"""
    try:
        stats = qr_checkin_manager.get_event_stats(event_id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return {
            "success": True,
            "data": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[QR_CHECKIN] Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/events/{event_id}/attendees")
async def get_event_attendees(event_id: str):
    """Lista participantes do evento"""
    try:
        event = qr_checkin_manager.events.get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        
        attendees = [
            {
                "id": checkin.id,
                "user_name": checkin.user_name,
                "user_email": checkin.user_email,
                "user_phone": checkin.user_phone,
                "check_in_time": checkin.check_in_time.isoformat(),
                "location_lat": checkin.location_lat,
                "location_lng": checkin.location_lng
            }
            for checkin in qr_checkin_manager.check_ins.values()
            if checkin.event_id == event_id
        ]
        
        # Ordenar por hora de check-in
        attendees.sort(key=lambda x: x["check_in_time"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "event_name": event.name,
                "total_attendees": len(attendees),
                "max_capacity": event.max_capacity,
                "attendees": attendees
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[QR_CHECKIN] Erro ao listar participantes: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.put("/events/{event_id}/status")
async def update_event_status(event_id: str, status: str):
    """Atualiza status do evento (active, paused, ended)"""
    try:
        valid_statuses = ["active", "paused", "ended"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Status inválido. Use: {valid_statuses}")
        
        event = qr_checkin_manager.events.get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        
        old_status = event.status
        event.status = status
        qr_checkin_manager.save_data()
        
        return {
            "success": True,
            "message": f"Status do evento alterado de '{old_status}' para '{status}'",
            "data": {
                "event_id": event_id,
                "old_status": old_status,
                "new_status": status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[QR_CHECKIN] Erro ao atualizar status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/dashboard")
async def get_dashboard():
    """Dashboard geral do sistema de check-in"""
    try:
        dashboard_data = qr_checkin_manager.get_dashboard_data()
        
        if "error" in dashboard_data:
            raise HTTPException(status_code=500, detail=dashboard_data["error"])
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[QR_CHECKIN] Erro no dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """Remove um evento (apenas se não houver check-ins)"""
    try:
        event = qr_checkin_manager.events.get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        
        # Verificar se há check-ins
        event_checkins = [c for c in qr_checkin_manager.check_ins.values() if c.event_id == event_id]
        if event_checkins:
            raise HTTPException(
                status_code=400, 
                detail=f"Não é possível remover evento com {len(event_checkins)} check-ins"
            )
        
        del qr_checkin_manager.events[event_id]
        qr_checkin_manager.save_data()
        
        return {
            "success": True,
            "message": f"Evento '{event.name}' removido com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[QR_CHECKIN] Erro ao remover evento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/validate-qr")
async def validate_qr_code(qr_data: str):
    """Valida um QR code sem fazer check-in"""
    try:
        import json
        
        # Decodificar dados do QR
        qr_info = json.loads(qr_data)
        event_id = qr_info.get('event_id')
        
        if not event_id:
            return {"valid": False, "message": "QR code inválido: evento não especificado"}
        
        event = qr_checkin_manager.events.get(event_id)
        if not event:
            return {"valid": False, "message": "Evento não encontrado"}
        
        now = datetime.now()
        if event.status != "active":
            return {"valid": False, "message": f"Evento está {event.status}"}
        
        if now < event.start_time:
            return {"valid": False, "message": "Evento ainda não começou"}
        
        if now > event.end_time:
            return {"valid": False, "message": "Evento já terminou"}
        
        if event.check_ins_count >= event.max_capacity:
            return {"valid": False, "message": "Evento lotado"}
        
        return {
            "valid": True,
            "message": "QR code válido",
            "event": {
                "id": event.id,
                "name": event.name,
                "location": event.location,
                "available_spots": event.max_capacity - event.check_ins_count,
                "max_capacity": event.max_capacity
            }
        }
        
    except json.JSONDecodeError:
        return {"valid": False, "message": "QR code inválido: formato incorreto"}
    except Exception as e:
        logger.error(f"[QR_CHECKIN] Erro na validação: {e}")
        return {"valid": False, "message": f"Erro interno: {str(e)}"}
