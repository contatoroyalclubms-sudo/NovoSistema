"""
Serviço avançado de webhooks para eventos
Sistema Universal de Gestão de Eventos - Sprint 3
"""

import asyncio
import json
import logging
import hmac
import hashlib
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

from app.core.config import settings
from app.models import Evento, Participante, Transacao

logger = logging.getLogger(__name__)

class WebhookService:
    """Serviço avançado de webhooks"""
    
    def __init__(self):
        self.timeout = 30  # Timeout para requisições
        self.max_retries = 3
        self.retry_delays = [1, 5, 15]  # Delays entre tentativas (segundos)
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Gera assinatura HMAC para validação do webhook"""
        if not secret:
            return ""
        
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def _validate_url(self, url: str) -> bool:
        """Valida se a URL é válida e segura"""
        try:
            parsed = urlparse(url)
            
            # Verificar esquema
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Verificar se tem host
            if not parsed.netloc:
                return False
            
            # Verificar se não é localhost/IP privado em produção
            if settings.environment == 'production':
                if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
                    return False
                
                # Verificar IPs privados
                if parsed.hostname and parsed.hostname.startswith(('192.168.', '10.', '172.')):
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def _send_webhook(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia webhook para URL
        
        Returns:
            Dict com resultado do envio
        """
        if not self._validate_url(url):
            return {
                'success': False,
                'error': 'URL inválida ou não permitida'
            }
        
        # Preparar payload
        payload_json = json.dumps(payload, ensure_ascii=False, default=str)
        
        # Preparar headers
        request_headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'EventoWebhook/1.0 ({settings.app_name})',
            'X-Webhook-Timestamp': str(int(datetime.utcnow().timestamp())),
            'X-Webhook-ID': payload.get('id', ''),
        }
        
        # Adicionar headers customizados
        if headers:
            request_headers.update(headers)
        
        # Adicionar assinatura se secret fornecido
        if secret:
            signature = self._generate_signature(payload_json, secret)
            request_headers['X-Webhook-Signature'] = signature
        
        # Tentar enviar com retry
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    async with session.post(
                        url,
                        data=payload_json,
                        headers=request_headers
                    ) as response:
                        response_text = await response.text()
                        
                        if response.status < 400:
                            logger.info(f"Webhook enviado com sucesso para {url}")
                            return {
                                'success': True,
                                'status_code': response.status,
                                'response': response_text[:500],  # Limitar resposta
                                'attempt': attempt + 1
                            }
                        else:
                            last_error = f"HTTP {response.status}: {response_text[:200]}"
                            logger.warning(f"Webhook falhou (tentativa {attempt + 1}): {last_error}")
            
            except asyncio.TimeoutError:
                last_error = "Timeout na requisição"
                logger.warning(f"Webhook timeout (tentativa {attempt + 1}) para {url}")
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"Erro no webhook (tentativa {attempt + 1}) para {url}: {e}")
            
            # Aguardar antes da próxima tentativa
            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delays[attempt])
        
        return {
            'success': False,
            'error': last_error,
            'attempts': self.max_retries
        }
    
    async def send_checkin_webhook(
        self,
        evento: Evento,
        participante: Participante,
        checkin_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Envia webhook de check-in"""
        if not evento.webhook_checkin:
            return None
        
        payload = {
            'id': f"checkin_{participante.id}_{int(datetime.utcnow().timestamp())}",
            'type': 'checkin',
            'timestamp': datetime.utcnow().isoformat(),
            'event': {
                'id': str(evento.id),
                'name': evento.nome,
                'start_date': evento.data_inicio.isoformat() if evento.data_inicio else None,
                'location': evento.local_nome
            },
            'participant': {
                'id': str(participante.id),
                'user_id': str(participante.usuario_id),
                'name': participante.usuario.nome if participante.usuario else None,
                'email': participante.usuario.email if participante.usuario else None,
                'checkin_time': checkin_data.get('checkin_time'),
                'location': checkin_data.get('location'),
                'method': checkin_data.get('method', 'qr_code')
            },
            'points_earned': checkin_data.get('points_earned', 0),
            'badges_unlocked': checkin_data.get('badges_unlocked', [])
        }
        
        result = await self._send_webhook(
            url=evento.webhook_checkin,
            payload=payload,
            headers=evento.webhook_headers,
            secret=evento.webhook_secret
        )
        
        return result
    
    async def send_checkout_webhook(
        self,
        evento: Evento,
        participante: Participante,
        checkout_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Envia webhook de check-out"""
        if not evento.webhook_checkout:
            return None
        
        payload = {
            'id': f"checkout_{participante.id}_{int(datetime.utcnow().timestamp())}",
            'type': 'checkout',
            'timestamp': datetime.utcnow().isoformat(),
            'event': {
                'id': str(evento.id),
                'name': evento.nome
            },
            'participant': {
                'id': str(participante.id),
                'user_id': str(participante.usuario_id),
                'name': participante.usuario.nome if participante.usuario else None,
                'checkout_time': checkout_data.get('checkout_time'),
                'duration_minutes': checkout_data.get('duration_minutes'),
                'rating': checkout_data.get('rating'),
                'feedback': checkout_data.get('feedback')
            }
        }
        
        result = await self._send_webhook(
            url=evento.webhook_checkout,
            payload=payload,
            headers=evento.webhook_headers,
            secret=evento.webhook_secret
        )
        
        return result
    
    async def send_payment_webhook(
        self,
        evento: Evento,
        transacao: Transacao,
        payment_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Envia webhook de pagamento"""
        if not evento.webhook_pagamento:
            return None
        
        payload = {
            'id': f"payment_{transacao.id}_{int(datetime.utcnow().timestamp())}",
            'type': 'payment',
            'timestamp': datetime.utcnow().isoformat(),
            'event': {
                'id': str(evento.id),
                'name': evento.nome
            },
            'transaction': {
                'id': str(transacao.id),
                'number': transacao.numero_transacao,
                'status': transacao.status.value if transacao.status else None,
                'amount': float(transacao.valor_liquido) if transacao.valor_liquido else 0,
                'currency': transacao.moeda or 'BRL',
                'payment_method': transacao.forma_pagamento.value if transacao.forma_pagamento else None,
                'participant_id': str(transacao.participante_id) if transacao.participante_id else None,
                'user_id': str(transacao.usuario_id) if transacao.usuario_id else None,
                'created_at': transacao.data_transacao.isoformat() if transacao.data_transacao else None,
                'processed_at': payment_data.get('processed_at')
            }
        }
        
        result = await self._send_webhook(
            url=evento.webhook_pagamento,
            payload=payload,
            headers=evento.webhook_headers,
            secret=evento.webhook_secret
        )
        
        return result
    
    async def send_cancellation_webhook(
        self,
        evento: Evento,
        cancellation_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Envia webhook de cancelamento"""
        if not evento.webhook_cancelamento:
            return None
        
        payload = {
            'id': f"cancellation_{evento.id}_{int(datetime.utcnow().timestamp())}",
            'type': 'event_cancellation',
            'timestamp': datetime.utcnow().isoformat(),
            'event': {
                'id': str(evento.id),
                'name': evento.nome,
                'start_date': evento.data_inicio.isoformat() if evento.data_inicio else None,
                'location': evento.local_nome,
                'cancelled_at': cancellation_data.get('cancelled_at'),
                'reason': cancellation_data.get('reason'),
                'refund_policy': cancellation_data.get('refund_policy')
            },
            'impact': {
                'total_participants': cancellation_data.get('total_participants', 0),
                'confirmed_participants': cancellation_data.get('confirmed_participants', 0),
                'total_revenue': cancellation_data.get('total_revenue', 0),
                'refund_amount': cancellation_data.get('refund_amount', 0)
            }
        }
        
        result = await self._send_webhook(
            url=evento.webhook_cancelamento,
            payload=payload,
            headers=evento.webhook_headers,
            secret=evento.webhook_secret
        )
        
        return result
    
    async def send_custom_webhook(
        self,
        url: str,
        event_type: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envia webhook customizado"""
        custom_payload = {
            'id': f"custom_{int(datetime.utcnow().timestamp())}",
            'type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': payload
        }
        
        result = await self._send_webhook(
            url=url,
            payload=custom_payload,
            headers=headers,
            secret=secret
        )
        
        return result
    
    async def test_webhook(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """Testa webhook com payload de exemplo"""
        test_payload = {
            'id': f"test_{int(datetime.utcnow().timestamp())}",
            'type': 'webhook_test',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Este é um teste de webhook do Sistema Universal de Eventos',
            'test_data': {
                'webhook_version': '1.0',
                'test_timestamp': datetime.utcnow().isoformat(),
                'environment': settings.environment
            }
        }
        
        result = await self._send_webhook(
            url=url,
            payload=test_payload,
            headers=headers,
            secret=secret
        )
        
        return result
    
    def validate_webhook_signature(
        self,
        payload: str,
        signature: str,
        secret: str
    ) -> bool:
        """Valida assinatura de webhook recebido"""
        if not signature or not secret:
            return False
        
        try:
            # Remover prefixo se presente
            if signature.startswith('sha256='):
                signature = signature[7:]
            
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Erro na validação da assinatura do webhook: {e}")
            return False
    
    async def send_bulk_webhooks(
        self,
        webhooks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Envia múltiplos webhooks em paralelo
        
        Args:
            webhooks: Lista de webhooks para enviar
                     [{'url': str, 'payload': dict, 'headers': dict, 'secret': str}]
        
        Returns:
            Resultados dos envios
        """
        if not webhooks:
            return {'total': 0, 'success': 0, 'failed': 0, 'results': []}
        
        # Criar tasks para envio paralelo
        tasks = []
        for webhook in webhooks:
            task = self._send_webhook(
                url=webhook['url'],
                payload=webhook['payload'],
                headers=webhook.get('headers'),
                secret=webhook.get('secret')
            )
            tasks.append(task)
        
        # Executar em paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Contar sucessos e falhas
        success_count = 0
        failed_count = 0
        processed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'webhook_index': i,
                    'success': False,
                    'error': str(result)
                })
                failed_count += 1
            elif isinstance(result, dict) and result.get('success'):
                processed_results.append(result)
                success_count += 1
            else:
                processed_results.append(result)
                failed_count += 1
        
        return {
            'total': len(webhooks),
            'success': success_count,
            'failed': failed_count,
            'results': processed_results
        }

# Instância global do serviço
webhook_service = WebhookService()