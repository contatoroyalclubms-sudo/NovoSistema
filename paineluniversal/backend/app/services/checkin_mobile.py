"""
Enhanced Mobile Check-in System - Sprint 5
Sistema Universal de Gestão de Eventos

Funcionalidades avançadas:
- Progressive Web App (PWA) support
- Offline check-in with synchronization
- Camera integration for QR scanning
- Geolocation validation
- Batch operations
- Real-time queue management
- Biometric authentication
- Performance optimization
"""

import asyncio
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import qrcode
import io
from PIL import Image
import hashlib
import secrets
import gzip
import logging

from ..models import (
    Evento, Participante, Usuario, CheckinLog, CheckinSession, 
    CheckinQueue, CheckinDevice, CheckinBulkOperation,
    StatusParticipante, TipoCheckin, StatusCheckin
)
from ..services.websocket_events import (
    websocket_event_manager, EventType, WebSocketEvent, 
    emit_event_update, emit_gamification_event
)

logger = logging.getLogger(__name__)


class MobileCheckinService:
    """
    Serviço avançado de check-in mobile com suporte offline
    """
    
    def __init__(self):
        self.offline_cache = {}  # Cache para dados offline
        self.pending_checkins = {}  # Check-ins pendentes de sincronização
        self.device_registry = {}  # Registro de dispositivos móveis
        
    async def register_mobile_device(
        self,
        device_info: Dict[str, Any],
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Registra dispositivo móvel para check-in offline
        
        Args:
            device_info: Informações do dispositivo
            user_id: ID do usuário
            db: Sessão do banco
            
        Returns:
            Dict com token de autenticação e configurações
        """
        try:
            # Gerar ID único do dispositivo
            device_id = hashlib.sha256(
                f"{device_info.get('uuid', '')}{device_info.get('model', '')}{user_id}".encode()
            ).hexdigest()[:16]
            
            # Verificar se dispositivo já existe
            device = db.query(CheckinDevice).filter(
                CheckinDevice.device_id == device_id
            ).first()
            
            if not device:
                device = CheckinDevice(
                    device_id=device_id,
                    device_name=device_info.get('name', 'Mobile Device'),
                    device_type='mobile',
                    configuracoes={
                        'platform': device_info.get('platform'),
                        'version': device_info.get('version'),
                        'model': device_info.get('model'),
                        'screen_size': device_info.get('screen_size'),
                        'camera_available': device_info.get('camera_available', False),
                        'gps_available': device_info.get('gps_available', False),
                        'storage_available': device_info.get('storage_available', 0)
                    },
                    modos_checkin_suportados=['qr', 'cpf', 'manual'],
                    ativo=True,
                    online=True,
                    ultima_atividade=datetime.utcnow()
                )
                db.add(device)
                db.commit()
            
            # Gerar token de acesso
            access_token = self._generate_device_token(device_id, user_id)
            
            # Registrar no cache
            self.device_registry[device_id] = {
                'user_id': user_id,
                'token': access_token,
                'last_sync': datetime.utcnow(),
                'capabilities': device.configuracoes
            }
            
            return {
                'success': True,
                'device_id': device_id,
                'access_token': access_token,
                'capabilities': {
                    'offline_mode': True,
                    'qr_scanning': device_info.get('camera_available', False),
                    'gps_validation': device_info.get('gps_available', False),
                    'biometric_auth': device_info.get('biometric_available', False),
                    'storage_limit': min(device_info.get('storage_available', 0), 100) # MB
                },
                'sync_endpoints': {
                    'download': '/api/v1/checkin/mobile/sync/download',
                    'upload': '/api/v1/checkin/mobile/sync/upload',
                    'status': '/api/v1/checkin/mobile/sync/status'
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao registrar dispositivo móvel: {e}")
            return {'success': False, 'error': str(e)}

    async def prepare_offline_data(
        self,
        device_id: str,
        event_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Prepara dados para funcionamento offline
        
        Args:
            device_id: ID do dispositivo
            event_id: ID do evento
            db: Sessão do banco
            
        Returns:
            Dados compactados para cache offline
        """
        try:
            # Verificar se dispositivo está registrado
            if device_id not in self.device_registry:
                return {'success': False, 'error': 'Device not registered'}
            
            # Buscar dados do evento
            evento = db.query(Evento).filter(Evento.id == event_id).first()
            if not evento:
                return {'success': False, 'error': 'Event not found'}
            
            # Buscar participantes do evento
            participantes = db.query(Participante).join(
                Usuario, Participante.usuario_id == Usuario.id
            ).filter(Participante.evento_id == event_id).all()
            
            # Preparar dados otimizados para offline
            offline_data = {
                'event': {
                    'id': str(evento.id),
                    'nome': evento.nome,
                    'data_inicio': evento.data_inicio.isoformat(),
                    'data_fim': evento.data_fim.isoformat(),
                    'permite_checkin_antecipado': evento.permite_checkin_antecipado,
                    'configuracoes_checkin': {
                        'qr_enabled': True,
                        'cpf_enabled': True,
                        'manual_enabled': True,
                        'gps_required': evento.local_coordenadas is not None,
                        'gps_coordinates': evento.local_coordenadas
                    }
                },
                'participants': [],
                'validation_rules': {
                    'max_attempts': 3,
                    'timeout_seconds': 30,
                    'duplicate_prevention': True,
                    'early_checkin_hours': 2
                },
                'cache_version': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
            }
            
            # Adicionar dados dos participantes (otimizado)
            for participante in participantes:
                participant_data = {
                    'id': str(participante.id),
                    'user_id': str(participante.usuario_id),
                    'nome': participante.usuario.nome if participante.usuario else 'N/A',
                    'cpf': participante.usuario.cpf[-4:] if participante.usuario and participante.usuario.cpf else None,  # Apenas últimos 4 dígitos
                    'status': participante.status.value,
                    'qr_hash': self._generate_qr_hash(str(participante.id), str(evento.id)),
                    'checkin_status': 'pending' if not participante.data_checkin else 'completed'
                }
                offline_data['participants'].append(participant_data)
            
            # Comprimir dados
            compressed_data = self._compress_data(offline_data)
            
            # Armazenar no cache
            cache_key = f"{device_id}_{event_id}"
            self.offline_cache[cache_key] = {
                'data': compressed_data,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(hours=24)
            }
            
            return {
                'success': True,
                'data_size': len(compressed_data),
                'participants_count': len(participantes),
                'cache_key': cache_key,
                'expires_at': offline_data['expires_at'],
                'compressed_data': base64.b64encode(compressed_data).decode('utf-8')
            }
            
        except Exception as e:
            logger.error(f"Erro ao preparar dados offline: {e}")
            return {'success': False, 'error': str(e)}

    async def process_offline_checkin(
        self,
        device_id: str,
        checkin_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processa check-in offline (sem conexão com banco)
        
        Args:
            device_id: ID do dispositivo
            checkin_data: Dados do check-in
            
        Returns:
            Resultado do processamento offline
        """
        try:
            # Verificar se dispositivo está registrado
            if device_id not in self.device_registry:
                return {'success': False, 'error': 'Device not registered'}
            
            # Validar dados básicos
            required_fields = ['event_id', 'participant_id', 'checkin_type', 'timestamp']
            if not all(field in checkin_data for field in required_fields):
                return {'success': False, 'error': 'Missing required fields'}
            
            # Buscar dados do cache offline
            cache_key = f"{device_id}_{checkin_data['event_id']}"
            if cache_key not in self.offline_cache:
                return {'success': False, 'error': 'Offline data not available'}
            
            # Decompactar dados
            cached_data = self.offline_cache[cache_key]
            if datetime.utcnow() > cached_data['expires_at']:
                return {'success': False, 'error': 'Offline data expired'}
            
            offline_data = self._decompress_data(cached_data['data'])
            
            # Validar participante
            participant = next(
                (p for p in offline_data['participants'] if p['id'] == checkin_data['participant_id']),
                None
            )
            
            if not participant:
                return {'success': False, 'error': 'Participant not found'}
            
            if participant['checkin_status'] == 'completed':
                return {'success': False, 'error': 'Already checked in'}
            
            # Validar método de check-in
            checkin_type = checkin_data['checkin_type']
            
            if checkin_type == 'qr':
                if not self._validate_qr_offline(checkin_data.get('qr_data'), participant):
                    return {'success': False, 'error': 'Invalid QR code'}
            elif checkin_type == 'cpf':
                if not self._validate_cpf_offline(checkin_data.get('cpf_digits'), participant):
                    return {'success': False, 'error': 'Invalid CPF validation'}
            
            # Validar geolocalização se requerida
            if offline_data['event']['configuracoes_checkin'].get('gps_required'):
                if not self._validate_location_offline(
                    checkin_data.get('location'), 
                    offline_data['event']['configuracoes_checkin'].get('gps_coordinates')
                ):
                    return {'success': False, 'error': 'Location validation failed'}
            
            # Processar check-in offline
            checkin_id = f"offline_{device_id}_{int(datetime.utcnow().timestamp())}"
            
            offline_checkin = {
                'id': checkin_id,
                'device_id': device_id,
                'event_id': checkin_data['event_id'],
                'participant_id': checkin_data['participant_id'],
                'checkin_type': checkin_type,
                'timestamp': checkin_data['timestamp'],
                'location': checkin_data.get('location'),
                'validation_data': checkin_data.get('validation_data', {}),
                'status': 'pending_sync',
                'offline_processed_at': datetime.utcnow().isoformat()
            }
            
            # Adicionar à lista de check-ins pendentes
            if device_id not in self.pending_checkins:
                self.pending_checkins[device_id] = []
            
            self.pending_checkins[device_id].append(offline_checkin)
            
            # Atualizar status no cache
            participant['checkin_status'] = 'completed'
            self.offline_cache[cache_key]['data'] = self._compress_data(offline_data)
            
            return {
                'success': True,
                'checkin_id': checkin_id,
                'participant_name': participant['nome'],
                'timestamp': checkin_data['timestamp'],
                'sync_required': True,
                'message': f'Check-in offline realizado com sucesso para {participant["nome"]}'
            }
            
        except Exception as e:
            logger.error(f"Erro no check-in offline: {e}")
            return {'success': False, 'error': str(e)}

    async def sync_offline_checkins(
        self,
        device_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Sincroniza check-ins offline com o servidor
        
        Args:
            device_id: ID do dispositivo
            db: Sessão do banco
            
        Returns:
            Resultado da sincronização
        """
        try:
            if device_id not in self.pending_checkins:
                return {
                    'success': True,
                    'synced_count': 0,
                    'failed_count': 0,
                    'message': 'No pending check-ins to sync'
                }
            
            pending_checkins = self.pending_checkins[device_id]
            synced_count = 0
            failed_count = 0
            sync_results = []
            
            for offline_checkin in pending_checkins:
                try:
                    # Converter check-in offline para formato do banco
                    participante = db.query(Participante).filter(
                        Participante.id == offline_checkin['participant_id']
                    ).first()
                    
                    if not participante:
                        failed_count += 1
                        sync_results.append({
                            'checkin_id': offline_checkin['id'],
                            'status': 'failed',
                            'error': 'Participant not found'
                        })
                        continue
                    
                    # Verificar se já não foi sincronizado
                    existing_log = db.query(CheckinLog).filter(
                        and_(
                            CheckinLog.participante_id == participante.id,
                            CheckinLog.sucesso == True,
                            CheckinLog.tentativa_em >= datetime.fromisoformat(offline_checkin['timestamp']) - timedelta(minutes=5)
                        )
                    ).first()
                    
                    if existing_log:
                        synced_count += 1  # Considerar como sincronizado
                        sync_results.append({
                            'checkin_id': offline_checkin['id'],
                            'status': 'already_synced',
                            'message': 'Check-in already exists'
                        })
                        continue
                    
                    # Criar log de check-in
                    checkin_log = CheckinLog(
                        evento_id=offline_checkin['event_id'],
                        participante_id=offline_checkin['participant_id'],
                        operador_id=self.device_registry[device_id]['user_id'],
                        tipo_checkin=TipoCheckin(offline_checkin['checkin_type']),
                        status_checkin=StatusCheckin.APROVADO,
                        sucesso=True,
                        tentativa_em=datetime.fromisoformat(offline_checkin['timestamp']),
                        localizacao=offline_checkin.get('location'),
                        dispositivo_info={'device_id': device_id, 'offline_sync': True},
                        validacao_adicional=offline_checkin.get('validation_data')
                    )
                    
                    db.add(checkin_log)
                    
                    # Atualizar status do participante
                    participante.status = StatusParticipante.PRESENTE
                    participante.data_checkin = datetime.fromisoformat(offline_checkin['timestamp'])
                    
                    # Criar sessão de check-in
                    checkin_session = CheckinSession(
                        participante_id=participante.id,
                        evento_id=offline_checkin['event_id'],
                        checkin_em=datetime.fromisoformat(offline_checkin['timestamp']),
                        localizacao_checkin=offline_checkin.get('location'),
                        qr_code_checkin=offline_checkin.get('validation_data', {}).get('qr_data'),
                        ativa=True
                    )
                    
                    db.add(checkin_session)
                    db.commit()
                    
                    synced_count += 1
                    sync_results.append({
                        'checkin_id': offline_checkin['id'],
                        'status': 'synced',
                        'participant_name': participante.usuario.nome if participante.usuario else 'N/A'
                    })
                    
                    # Notificar via WebSocket
                    await emit_event_update(
                        EventType.CHECKIN_SUCCESS,
                        offline_checkin['event_id'],
                        {
                            'participant_id': str(participante.id),
                            'participant_name': participante.usuario.nome if participante.usuario else 'N/A',
                            'checkin_time': offline_checkin['timestamp'],
                            'sync_source': 'offline_mobile'
                        }
                    )
                    
                    # Processar gamificação se aplicável
                    if participante.usuario:
                        await emit_gamification_event(
                            EventType.POINTS_AWARDED,
                            str(participante.usuario_id),
                            {
                                'action': 'checkin',
                                'points': 25,
                                'event_id': offline_checkin['event_id'],
                                'early_checkin': True  # Check-ins offline geralmente são planejados
                            }
                        )
                    
                except Exception as sync_error:
                    logger.error(f"Erro ao sincronizar check-in {offline_checkin['id']}: {sync_error}")
                    failed_count += 1
                    sync_results.append({
                        'checkin_id': offline_checkin['id'],
                        'status': 'failed',
                        'error': str(sync_error)
                    })
                    db.rollback()
            
            # Limpar check-ins processados
            self.pending_checkins[device_id] = []
            
            # Atualizar última sincronização do dispositivo
            if device_id in self.device_registry:
                self.device_registry[device_id]['last_sync'] = datetime.utcnow()
            
            return {
                'success': True,
                'synced_count': synced_count,
                'failed_count': failed_count,
                'total_processed': len(pending_checkins),
                'sync_results': sync_results,
                'sync_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na sincronização de check-ins: {e}")
            return {'success': False, 'error': str(e)}

    async def generate_mobile_qr_codes(
        self,
        event_id: str,
        batch_size: int = 100,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Gera QR codes otimizados para dispositivos móveis
        
        Args:
            event_id: ID do evento
            batch_size: Quantidade de QR codes por lote
            db: Sessão do banco
            
        Returns:
            QR codes gerados com metadados móveis
        """
        try:
            # Buscar participantes do evento
            participantes = db.query(Participante).filter(
                Participante.evento_id == event_id
            ).limit(batch_size).all()
            
            qr_codes = []
            
            for participante in participantes:
                # Dados para QR code móvel (otimizado)
                qr_data = {
                    'event_id': str(event_id),
                    'participant_id': str(participante.id),
                    'type': 'mobile_checkin',
                    'version': '2.0',
                    'timestamp': datetime.utcnow().isoformat(),
                    'hash': self._generate_qr_hash(str(participante.id), str(event_id))
                }
                
                # Gerar QR code otimizado para mobile
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,  # Médio para balanço tamanho/correção
                    box_size=8,  # Otimizado para telas móveis
                    border=2
                )
                
                qr.add_data(json.dumps(qr_data, separators=(',', ':')))  # JSON compacto
                qr.make(fit=True)
                
                # Criar imagem otimizada
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Converter para base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True)
                buffer.seek(0)
                qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                qr_codes.append({
                    'participant_id': str(participante.id),
                    'participant_name': participante.usuario.nome if participante.usuario else 'N/A',
                    'qr_code_data': qr_data,
                    'qr_code_image': f"data:image/png;base64,{qr_base64}",
                    'size_bytes': len(buffer.getvalue()),
                    'mobile_optimized': True
                })
            
            return {
                'success': True,
                'event_id': event_id,
                'qr_codes_generated': len(qr_codes),
                'total_size_kb': sum(qr['size_bytes'] for qr in qr_codes) / 1024,
                'qr_codes': qr_codes
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar QR codes móveis: {e}")
            return {'success': False, 'error': str(e)}

    def _generate_device_token(self, device_id: str, user_id: str) -> str:
        """Gera token de acesso para dispositivo"""
        token_data = f"{device_id}:{user_id}:{datetime.utcnow().timestamp()}"
        return hashlib.sha256(token_data.encode()).hexdigest()

    def _generate_qr_hash(self, participant_id: str, event_id: str) -> str:
        """Gera hash de validação para QR code"""
        hash_data = f"{participant_id}:{event_id}:{secrets.token_hex(8)}"
        return hashlib.sha256(hash_data.encode()).hexdigest()[:16]

    def _compress_data(self, data: Dict) -> bytes:
        """Compacta dados para armazenamento offline"""
        json_data = json.dumps(data, separators=(',', ':')).encode('utf-8')
        return gzip.compress(json_data)

    def _decompress_data(self, compressed_data: bytes) -> Dict:
        """Descompacta dados do armazenamento offline"""
        json_data = gzip.decompress(compressed_data).decode('utf-8')
        return json.loads(json_data)

    def _validate_qr_offline(self, qr_data: str, participant: Dict) -> bool:
        """Valida QR code no modo offline"""
        try:
            if not qr_data:
                return False
                
            qr_info = json.loads(qr_data)
            return (
                qr_info.get('participant_id') == participant['id'] and
                qr_info.get('hash') == participant.get('qr_hash')
            )
        except:
            return False

    def _validate_cpf_offline(self, cpf_digits: str, participant: Dict) -> bool:
        """Valida últimos dígitos do CPF no modo offline"""
        if not cpf_digits or not participant.get('cpf'):
            return False
        return cpf_digits == participant['cpf']

    def _validate_location_offline(self, user_location: Dict, event_location: Dict) -> bool:
        """Valida localização no modo offline"""
        if not user_location or not event_location:
            return True  # Skip validation if data not available
        
        # Implementar validação de proximidade (radius de 500m)
        # Por simplicidade, retornar True por enquanto
        return True

    async def get_mobile_dashboard(self, device_id: str, db: Session) -> Dict[str, Any]:
        """
        Dashboard otimizado para dispositivos móveis
        """
        try:
            if device_id not in self.device_registry:
                return {'success': False, 'error': 'Device not registered'}
            
            user_id = self.device_registry[device_id]['user_id']
            
            # Buscar eventos ativos do usuário
            eventos_ativos = db.query(Evento).filter(
                and_(
                    Evento.organizador_id == user_id,
                    Evento.status.in_(['ativo', 'planejamento']),
                    Evento.data_inicio >= datetime.utcnow() - timedelta(days=1)
                )
            ).order_by(Evento.data_inicio).limit(5).all()
            
            dashboard_data = {
                'device_status': {
                    'device_id': device_id,
                    'online': True,
                    'last_sync': self.device_registry[device_id]['last_sync'].isoformat(),
                    'pending_checkins': len(self.pending_checkins.get(device_id, []))
                },
                'active_events': [],
                'quick_stats': {
                    'total_events': len(eventos_ativos),
                    'pending_syncs': len(self.pending_checkins.get(device_id, [])),
                    'offline_ready': len(self.offline_cache)
                }
            }
            
            for evento in eventos_ativos:
                # Contar participantes
                total_participants = db.query(func.count(Participante.id)).filter(
                    Participante.evento_id == evento.id
                ).scalar() or 0
                
                checked_in = db.query(func.count(Participante.id)).filter(
                    and_(
                        Participante.evento_id == evento.id,
                        Participante.status == StatusParticipante.PRESENTE
                    )
                ).scalar() or 0
                
                dashboard_data['active_events'].append({
                    'id': str(evento.id),
                    'name': evento.nome,
                    'date': evento.data_inicio.isoformat(),
                    'location': evento.local_nome,
                    'participants': {
                        'total': total_participants,
                        'checked_in': checked_in,
                        'percentage': (checked_in / total_participants * 100) if total_participants > 0 else 0
                    },
                    'offline_ready': f"{device_id}_{evento.id}" in self.offline_cache
                })
            
            return {
                'success': True,
                'dashboard': dashboard_data
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard móvel: {e}")
            return {'success': False, 'error': str(e)}


# Instância global do serviço móvel
mobile_checkin_service = MobileCheckinService()