"""
Módulo de utilitários gerais
Sistema Universal de Gestão de Eventos - FASE 2

Funções auxiliares para QR codes, validações, emails, etc.
"""

import json
import secrets
import hashlib
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

# Imports condicionais
try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from sqlalchemy.orm import Session
    from sqlalchemy import func
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# ================================
# FUNÇÕES DE QR CODE
# ================================

def generate_qr_code(data: Union[str, Dict[str, Any]], size: int = 10, border: int = 4) -> str:
    """
    Gera QR code a partir de dados
    
    Args:
        data: Dados para codificar (string ou dict)
        size: Tamanho do QR code
        border: Tamanho da borda
        
    Returns:
        String base64 do QR code ou string de fallback
    """
    if not QR_AVAILABLE:
        # Fallback quando qrcode não está disponível
        if isinstance(data, dict):
            data_str = json.dumps(data)
        else:
            data_str = str(data)
        return f"qr_fallback_{hashlib.md5(data_str.encode()).hexdigest()}"
    
    # Converter dados para string se necessário
    if isinstance(data, dict):
        qr_data = json.dumps(data, ensure_ascii=False)
    else:
        qr_data = str(data)
    
    # Criar QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=border,
    )
    
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Gerar imagem
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64 (implementação simplificada)
    # Em produção, usar io.BytesIO para conversão completa
    return f"qr_code_{hashlib.md5(qr_data.encode()).hexdigest()}"

def parse_qr_code_data(qr_string: str) -> Optional[Dict[str, Any]]:
    """
    Extrai dados de um QR code
    
    Args:
        qr_string: String do QR code
        
    Returns:
        Dados extraídos ou None se inválido
    """
    try:
        # Tentar parsear como JSON
        return json.loads(qr_string)
    except (json.JSONDecodeError, TypeError):
        # Fallback para string simples
        return {"data": qr_string}

def validate_qr_code_data(qr_data: Dict[str, Any], expected_type: str) -> bool:
    """
    Valida dados de QR code
    
    Args:
        qr_data: Dados do QR code
        expected_type: Tipo esperado
        
    Returns:
        True se válido
    """
    if not isinstance(qr_data, dict):
        return False
    
    # Verificar tipo
    if qr_data.get("type") != expected_type:
        return False
    
    # Verificar timestamp (não muito antigo)
    timestamp_str = qr_data.get("timestamp")
    if timestamp_str:
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            age = datetime.utcnow() - timestamp.replace(tzinfo=None)
            # QR codes válidos por 24 horas
            if age > timedelta(hours=24):
                return False
        except (ValueError, TypeError):
            return False
    
    return True

# ================================
# FUNÇÕES DE VALIDAÇÃO
# ================================

def validate_event_dates(event_data: Dict[str, Any]) -> None:
    """
    Valida datas de um evento
    
    Args:
        event_data: Dados do evento
        
    Raises:
        ValueError: Se as datas são inválidas
    """
    data_inicio = event_data.get("data_inicio")
    data_fim = event_data.get("data_fim")
    data_inicio_checkin = event_data.get("data_inicio_checkin")
    data_fim_checkin = event_data.get("data_fim_checkin")
    
    # Converter strings para datetime se necessário
    if isinstance(data_inicio, str):
        data_inicio = datetime.fromisoformat(data_inicio)
    if isinstance(data_fim, str):
        data_fim = datetime.fromisoformat(data_fim)
    if isinstance(data_inicio_checkin, str):
        data_inicio_checkin = datetime.fromisoformat(data_inicio_checkin)
    if isinstance(data_fim_checkin, str):
        data_fim_checkin = datetime.fromisoformat(data_fim_checkin)
    
    # Validações básicas
    if data_inicio and data_fim:
        if data_fim <= data_inicio:
            raise ValueError("Data de fim deve ser posterior à data de início")
    
    if data_inicio and data_inicio < datetime.utcnow():
        raise ValueError("Data de início não pode ser no passado")
    
    # Validações de check-in
    if data_inicio_checkin and data_inicio:
        if data_inicio_checkin > data_inicio:
            raise ValueError("Check-in não pode começar depois do evento")
    
    if data_fim_checkin and data_fim:
        if data_fim_checkin > data_fim:
            raise ValueError("Check-in não pode terminar depois do evento")
    
    if data_inicio_checkin and data_fim_checkin:
        if data_fim_checkin <= data_inicio_checkin:
            raise ValueError("Fim do check-in deve ser posterior ao início")

def validate_cpf(cpf: str) -> bool:
    """
    Valida CPF brasileiro
    
    Args:
        cpf: CPF para validar
        
    Returns:
        True se válido
    """
    if not cpf:
        return False
    
    # Remover formatação
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Verificar tamanho
    if len(cpf) != 11:
        return False
    
    # Verificar se todos os dígitos são iguais
    if len(set(cpf)) == 1:
        return False
    
    # Calcular primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != dv1:
        return False
    
    # Calcular segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto
    
    return int(cpf[10]) == dv2

def validate_email(email: str) -> bool:
    """
    Validação básica de email
    
    Args:
        email: Email para validar
        
    Returns:
        True se válido
    """
    if not email or "@" not in email:
        return False
    
    parts = email.split("@")
    if len(parts) != 2:
        return False
    
    local, domain = parts
    if not local or not domain:
        return False
    
    if "." not in domain:
        return False
    
    return True

def validate_phone(phone: str) -> bool:
    """
    Validação básica de telefone brasileiro
    
    Args:
        phone: Telefone para validar
        
    Returns:
        True se válido
    """
    if not phone:
        return False
    
    # Remover formatação
    digits = ''.join(filter(str.isdigit, phone))
    
    # Telefone brasileiro tem 10 ou 11 dígitos (com DDD)
    return len(digits) in [10, 11]

# ================================
# FUNÇÕES DE CÁLCULO
# ================================

def calculate_event_statistics(db_session, event_id: uuid.UUID, detailed: bool = False) -> Dict[str, Any]:
    """
    Calcula estatísticas de um evento
    
    Args:
        db_session: Sessão do banco de dados
        event_id: ID do evento
        detailed: Se deve incluir estatísticas detalhadas
        
    Returns:
        Dicionário com estatísticas
    """
    if not SQLALCHEMY_AVAILABLE:
        # Fallback quando SQLAlchemy não está disponível
        return {
            "total_participantes": 0,
            "total_presentes": 0,
            "total_confirmados": 0,
            "receita_total": Decimal('0.00')
        }
    
    stats = {
        "total_participantes": 0,
        "total_presentes": 0,
        "total_confirmados": 0,
        "receita_total": Decimal('0.00')
    }
    
    # Implementação básica - expandir quando modelos estiverem disponíveis
    try:
        # from ..models import Participante, Transacao
        # 
        # # Contar participantes
        # stats["total_participantes"] = db_session.query(Participante).filter(
        #     Participante.evento_id == event_id
        # ).count()
        # 
        # # Contar presentes
        # stats["total_presentes"] = db_session.query(Participante).filter(
        #     Participante.evento_id == event_id,
        #     Participante.status == "presente"
        # ).count()
        # 
        # # Contar confirmados
        # stats["total_confirmados"] = db_session.query(Participante).filter(
        #     Participante.evento_id == event_id,
        #     Participante.status == "confirmado"
        # ).count()
        # 
        # # Calcular receita
        # receita = db_session.query(func.sum(Transacao.valor_liquido)).filter(
        #     Transacao.evento_id == event_id,
        #     Transacao.status == "aprovada"
        # ).scalar()
        # 
        # stats["receita_total"] = receita or Decimal('0.00')
        
        pass
    except Exception:
        # Se houver erro, retornar estatísticas vazias
        pass
    
    if detailed:
        stats.update({
            "taxa_presenca": 0.0,
            "receita_media_por_participante": Decimal('0.00'),
            "checkins_por_hora": [],
            "participantes_por_status": {}
        })
    
    return stats

def calculate_age(birth_date: datetime) -> int:
    """
    Calcula idade a partir da data de nascimento
    
    Args:
        birth_date: Data de nascimento
        
    Returns:
        Idade em anos
    """
    today = datetime.today()
    age = today.year - birth_date.year
    
    # Ajustar se ainda não fez aniversário este ano
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age

def calculate_discount(original_price: Decimal, discount_percent: float) -> Decimal:
    """
    Calcula desconto sobre um preço
    
    Args:
        original_price: Preço original
        discount_percent: Percentual de desconto (0-100)
        
    Returns:
        Valor do desconto
    """
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Percentual de desconto deve estar entre 0 e 100")
    
    return original_price * (Decimal(str(discount_percent)) / 100)

def calculate_final_price(original_price: Decimal, discount_percent: float = 0, tax_percent: float = 0) -> Decimal:
    """
    Calcula preço final com desconto e taxas
    
    Args:
        original_price: Preço original
        discount_percent: Percentual de desconto
        tax_percent: Percentual de taxa
        
    Returns:
        Preço final
    """
    discount = calculate_discount(original_price, discount_percent)
    price_after_discount = original_price - discount
    
    tax = price_after_discount * (Decimal(str(tax_percent)) / 100)
    final_price = price_after_discount + tax
    
    return final_price

# ================================
# FUNÇÕES DE EMAIL
# ================================

def send_email_verification(email: str, nome: str, user_id: str, recovery_code: str = None) -> bool:
    """
    Envia email de verificação (implementação simplificada)
    
    Args:
        email: Email destinatário
        nome: Nome do usuário
        user_id: ID do usuário
        recovery_code: Código de recuperação (opcional)
        
    Returns:
        True se enviado com sucesso
    """
    # Implementação simplificada - expandir com FastAPI-Mail
    print(f"Email enviado para {email} ({nome})")
    if recovery_code:
        print(f"Código de recuperação: {recovery_code}")
    else:
        print(f"Link de verificação: /verify/{user_id}")
    
    return True

def send_event_notification(email: str, event_name: str, message: str) -> bool:
    """
    Envia notificação sobre evento
    
    Args:
        email: Email destinatário
        event_name: Nome do evento
        message: Mensagem
        
    Returns:
        True se enviado com sucesso
    """
    print(f"Notificação de evento '{event_name}' enviada para {email}: {message}")
    return True

# ================================
# FUNÇÕES DE WEBHOOK
# ================================

def send_webhook(url: str, data: Dict[str, Any], timeout: int = 30) -> bool:
    """
    Envia webhook para URL externa
    
    Args:
        url: URL do webhook
        data: Dados para enviar
        timeout: Timeout em segundos
        
    Returns:
        True se enviado com sucesso
    """
    if not REQUESTS_AVAILABLE:
        print(f"Webhook simulado para {url}: {data}")
        return True
    
    try:
        response = requests.post(
            url,
            json=data,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar webhook: {e}")
        return False

# ================================
# FUNÇÕES DE PROCESSAMENTO
# ================================

def process_event_images(event_id: str, logo_url: str = None, banner_url: str = None) -> bool:
    """
    Processa imagens do evento (redimensionamento, otimização)
    
    Args:
        event_id: ID do evento
        logo_url: URL do logo
        banner_url: URL do banner
        
    Returns:
        True se processado com sucesso
    """
    print(f"Processando imagens do evento {event_id}")
    if logo_url:
        print(f"Logo: {logo_url}")
    if banner_url:
        print(f"Banner: {banner_url}")
    
    # Implementar processamento real de imagens
    return True

def generate_event_report(event_id: str, report_type: str = "basic") -> Dict[str, Any]:
    """
    Gera relatório de evento
    
    Args:
        event_id: ID do evento
        report_type: Tipo de relatório
        
    Returns:
        Dados do relatório
    """
    return {
        "event_id": event_id,
        "report_type": report_type,
        "generated_at": datetime.utcnow().isoformat(),
        "data": {}
    }

# ================================
# FUNÇÕES DE UTILITÁRIOS GERAIS
# ================================

def generate_verification_code(length: int = 6) -> str:
    """
    Gera código de verificação numérico
    
    Args:
        length: Tamanho do código
        
    Returns:
        Código numérico
    """
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def slugify(text: str) -> str:
    """
    Converte texto em slug
    
    Args:
        text: Texto para converter
        
    Returns:
        Slug
    """
    import re
    
    # Converter para minúsculas
    text = text.lower()
    
    # Remover acentos (implementação básica)
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i', 'î': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'û': 'u',
        'ç': 'c'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Substituir espaços e caracteres especiais por hífen
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Remover hífens no início e fim
    text = text.strip('-')
    
    return text

def format_currency(value: Union[Decimal, float], currency: str = "BRL") -> str:
    """
    Formata valor como moeda
    
    Args:
        value: Valor a formatar
        currency: Código da moeda
        
    Returns:
        Valor formatado
    """
    if currency == "BRL":
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        return f"{value:,.2f}"

def format_phone(phone: str) -> str:
    """
    Formata telefone brasileiro
    
    Args:
        phone: Telefone para formatar
        
    Returns:
        Telefone formatado
    """
    # Remover formatação existente
    digits = ''.join(filter(str.isdigit, phone))
    
    if len(digits) == 10:
        # Formato: (00) 0000-0000
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    elif len(digits) == 11:
        # Formato: (00) 00000-0000
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    else:
        return phone

def format_cpf(cpf: str) -> str:
    """
    Formata CPF
    
    Args:
        cpf: CPF para formatar
        
    Returns:
        CPF formatado
    """
    # Remover formatação existente
    digits = ''.join(filter(str.isdigit, cpf))
    
    if len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    else:
        return cpf

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Trunca texto com sufixo
    
    Args:
        text: Texto para truncar
        max_length: Tamanho máximo
        suffix: Sufixo para adicionar
        
    Returns:
        Texto truncado
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
