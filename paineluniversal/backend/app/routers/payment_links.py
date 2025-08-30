"""
Router para Sistema de Links de Pagamento Dinâmicos
Sistema Universal de Gestão de Eventos - Sprint 2

Funcionalidades:
- Criação de links de pagamento personalizáveis
- Pagamento único ou recorrente
- Múltiplas formas de pagamento
- Customização visual
- Analytics em tempo real
- Integração com split de pagamentos
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum
import uuid
import qrcode
import io
import base64

# Imports do sistema
from app.core.security import get_current_user
from app.core.database import get_db
from app.services.payment_links_service import PaymentLinksService
from app.services.qr_code_generator import QRCodeGenerator

router = APIRouter(prefix="/payment-links", tags=["Payment Links"])

# Enums
class LinkStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    COMPLETED = "completed"

class PaymentType(str, Enum):
    SINGLE = "single"        # Pagamento único
    RECURRING = "recurring"   # Recorrente
    FLEXIBLE = "flexible"     # Valor flexível

class LinkTheme(str, Enum):
    DEFAULT = "default"
    DARK = "dark"
    COLORFUL = "colorful"
    MINIMAL = "minimal"
    CUSTOM = "custom"

# Schemas
class PaymentLinkCreate(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0)  # None para valor flexível
    min_amount: Optional[Decimal] = Field(None, gt=0)
    max_amount: Optional[Decimal] = Field(None, gt=0)
    currency: str = Field(default="BRL")
    payment_type: PaymentType = PaymentType.SINGLE
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = Field(None, gt=0)
    
    # Personalização
    theme: LinkTheme = LinkTheme.DEFAULT
    custom_css: Optional[str] = None
    logo_url: Optional[HttpUrl] = None
    success_url: Optional[HttpUrl] = None
    cancel_url: Optional[HttpUrl] = None
    
    # Split de pagamentos
    enable_split: bool = Field(default=False)
    split_recipients: Optional[List[Dict[str, Any]]] = None
    
    # Configurações
    collect_customer_info: bool = Field(default=True)
    send_receipt: bool = Field(default=True)
    allow_installments: bool = Field(default=False)
    webhook_url: Optional[HttpUrl] = None
    
    metadata: Optional[Dict[str, Any]] = None

    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        min_amount = values.get('min_amount')
        if min_amount and v and v <= min_amount:
            raise ValueError('max_amount deve ser maior que min_amount')
        return v

class PaymentLinkResponse(BaseModel):
    link_id: str
    url: str
    qr_code: str  # Base64 encoded
    short_url: str
    title: str
    amount: Optional[Decimal]
    status: LinkStatus
    payment_type: PaymentType
    uses_count: int
    max_uses: Optional[int]
    total_collected: Decimal
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class PaymentAttempt(BaseModel):
    attempt_id: str
    link_id: str
    amount: Decimal
    customer_email: Optional[str]
    customer_name: Optional[str]
    status: str  # pending, completed, failed, cancelled
    payment_method: Optional[str]
    transaction_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

class LinkAnalytics(BaseModel):
    link_id: str
    total_views: int
    total_attempts: int
    successful_payments: int
    total_collected: Decimal
    conversion_rate: float
    avg_amount: Decimal
    payment_methods_breakdown: Dict[str, int]
    daily_stats: List[Dict[str, Any]]

# Serviços
def get_payment_links_service(db = Depends(get_db)) -> PaymentLinksService:
    return PaymentLinksService(db)

def get_qr_generator() -> QRCodeGenerator:
    return QRCodeGenerator()

# ================================
# CRIAÇÃO E GESTÃO DE LINKS
# ================================

@router.post("/create", response_model=PaymentLinkResponse)
async def create_payment_link(
    link_data: PaymentLinkCreate,
    current_user = Depends(get_current_user),
    service: PaymentLinksService = Depends(get_payment_links_service),
    qr_generator: QRCodeGenerator = Depends(get_qr_generator)
):
    """
    Criar novo link de pagamento dinâmico
    """
    try:
        # Validações específicas
        if link_data.payment_type == PaymentType.SINGLE and not link_data.amount:
            raise ValueError("Pagamento único deve ter valor definido")
        
        if link_data.enable_split and not link_data.split_recipients:
            raise ValueError("Split habilitado mas sem destinatários definidos")
        
        # Criar link
        link_id = str(uuid.uuid4())
        
        payment_link = await service.create_payment_link(
            link_id=link_id,
            user_id=current_user.id,
            link_data=link_data
        )
        
        # Gerar URL e QR Code
        base_url = "https://pay.novosistema.com"  # Configurável
        link_url = f"{base_url}/p/{link_id}"
        
        qr_code_b64 = await qr_generator.generate_qr_code(
            data=link_url,
            size=300,
            border=4
        )
        
        # Short URL (implementar serviço de encurtamento)
        short_url = f"https://pay.app/{link_id[:8]}"
        
        return PaymentLinkResponse(
            link_id=link_id,
            url=link_url,
            qr_code=qr_code_b64,
            short_url=short_url,
            title=link_data.title,
            amount=link_data.amount,
            status=LinkStatus.ACTIVE,
            payment_type=link_data.payment_type,
            uses_count=0,
            max_uses=link_data.max_uses,
            total_collected=Decimal('0.00'),
            expires_at=link_data.expires_at,
            created_at=payment_link["created_at"],
            updated_at=payment_link["updated_at"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao criar link de pagamento")

@router.get("/list")
async def list_payment_links(
    status: Optional[LinkStatus] = Query(None),
    payment_type: Optional[PaymentType] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    service: PaymentLinksService = Depends(get_payment_links_service)
):
    """
    Listar links de pagamento do usuário
    """
    try:
        links = await service.get_user_payment_links(
            user_id=current_user.id,
            status=status,
            payment_type=payment_type,
            limit=limit,
            offset=offset
        )
        
        return {
            "links": links["items"],
            "total_count": links["total_count"],
            "summary": links["summary"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao listar links")

@router.get("/{link_id}", response_model=PaymentLinkResponse)
async def get_payment_link(
    link_id: str,
    current_user = Depends(get_current_user),
    service: PaymentLinksService = Depends(get_payment_links_service)
):
    """
    Obter detalhes de um link específico
    """
    try:
        link = await service.get_payment_link_by_id(
            link_id=link_id,
            user_id=current_user.id
        )
        
        if not link:
            raise HTTPException(status_code=404, detail="Link não encontrado")
        
        return PaymentLinkResponse(**link)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao consultar link")

@router.put("/{link_id}")
async def update_payment_link(
    link_id: str,
    updates: Dict[str, Any],
    current_user = Depends(get_current_user),
    service: PaymentLinksService = Depends(get_payment_links_service)
):
    """
    Atualizar link de pagamento existente
    """
    try:
        updated_link = await service.update_payment_link(
            link_id=link_id,
            user_id=current_user.id,
            updates=updates
        )
        
        return {"message": "Link atualizado com sucesso", "link": updated_link}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao atualizar link")

@router.delete("/{link_id}")
async def delete_payment_link(
    link_id: str,
    current_user = Depends(get_current_user),
    service: PaymentLinksService = Depends(get_payment_links_service)
):
    """
    Desativar/excluir link de pagamento
    """
    try:
        await service.deactivate_payment_link(
            link_id=link_id,
            user_id=current_user.id
        )
        
        return {"message": "Link desativado com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao desativar link")

# ================================
# PÁGINA PÚBLICA DE PAGAMENTO
# ================================

@router.get("/p/{link_id}", response_class=HTMLResponse)
async def payment_page(
    link_id: str,
    request: Request,
    service: PaymentLinksService = Depends(get_payment_links_service)
):
    """
    Página pública de pagamento (sem autenticação)
    """
    try:
        # Buscar link público
        link = await service.get_public_payment_link(link_id)
        
        if not link:
            return HTMLResponse(
                content=generate_error_page("Link de pagamento não encontrado"),
                status_code=404
            )
        
        # Verificar se está ativo e não expirado
        if link["status"] != LinkStatus.ACTIVE:
            return HTMLResponse(
                content=generate_error_page("Link de pagamento inativo"),
                status_code=400
            )
        
        if link["expires_at"] and datetime.utcnow() > link["expires_at"]:
            return HTMLResponse(
                content=generate_error_page("Link de pagamento expirado"),
                status_code=400
            )
        
        # Incrementar contador de visualizações
        await service.increment_link_views(link_id)
        
        # Gerar página de pagamento
        payment_html = generate_payment_page(link, request)
        
        return HTMLResponse(content=payment_html)
        
    except Exception as e:
        return HTMLResponse(
            content=generate_error_page("Erro interno do servidor"),
            status_code=500
        )

@router.post("/p/{link_id}/process")
async def process_payment(
    link_id: str,
    payment_data: Dict[str, Any],
    service: PaymentLinksService = Depends(get_payment_links_service)
):
    """
    Processar pagamento via link público
    """
    try:
        result = await service.process_link_payment(
            link_id=link_id,
            payment_data=payment_data
        )
        
        return {
            "status": "success",
            "payment_id": result["payment_id"],
            "redirect_url": result.get("redirect_url"),
            "message": "Pagamento processado com sucesso"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao processar pagamento")

# ================================
# ANALYTICS E RELATÓRIOS
# ================================

@router.get("/{link_id}/analytics", response_model=LinkAnalytics)
async def get_link_analytics(
    link_id: str,
    period_days: int = Query(default=30, ge=1, le=365),
    current_user = Depends(get_current_user),
    service: PaymentLinksService = Depends(get_payment_links_service)
):
    """
    Analytics detalhado de um link de pagamento
    """
    try:
        analytics = await service.get_link_analytics(
            link_id=link_id,
            user_id=current_user.id,
            period_days=period_days
        )
        
        return LinkAnalytics(**analytics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao gerar analytics")

@router.get("/{link_id}/payments")
async def get_link_payments(
    link_id: str,
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    service: PaymentLinksService = Depends(get_payment_links_service)
):
    """
    Listar pagamentos de um link específico
    """
    try:
        payments = await service.get_link_payments(
            link_id=link_id,
            user_id=current_user.id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        return {
            "payments": payments["items"],
            "total_count": payments["total_count"],
            "summary": payments["summary"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao consultar pagamentos")

# ================================
# FUNÇÕES AUXILIARES
# ================================

def generate_payment_page(link: Dict[str, Any], request: Request) -> str:
    """
    Gerar página HTML de pagamento personalizada
    """
    theme_css = get_theme_css(link.get("theme", "default"))
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{link['title']} - Pagamento</title>
        <style>{theme_css}</style>
        {link.get('custom_css', '')}
    </head>
    <body>
        <div class="payment-container">
            <div class="payment-card">
                {f'<img src="{link["logo_url"]}" alt="Logo" class="logo">' if link.get("logo_url") else ''}
                
                <h1 class="title">{link['title']}</h1>
                
                {f'<p class="description">{link["description"]}</p>' if link.get("description") else ''}
                
                <div class="amount-section">
                    {format_amount_section(link)}
                </div>
                
                <form id="payment-form" class="payment-form">
                    {generate_form_fields(link)}
                    
                    <button type="submit" class="pay-button">
                        Pagar {format_currency(link.get('amount', 0)) if link.get('amount') else ''}
                    </button>
                </form>
                
                <div class="security-info">
                    🔒 Pagamento 100% seguro
                </div>
            </div>
        </div>
        
        <script>{generate_payment_script(link)}</script>
    </body>
    </html>
    """
    
    return html_template

def get_theme_css(theme: str) -> str:
    """
    Retornar CSS para o tema especificado
    """
    themes = {
        "default": """
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .payment-container { max-width: 400px; margin: 0 auto; }
            .payment-card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .title { color: #1f2937; margin-bottom: 10px; }
            .description { color: #6b7280; margin-bottom: 20px; }
            .pay-button { width: 100%; background: #3b82f6; color: white; border: none; padding: 12px; border-radius: 8px; font-size: 16px; cursor: pointer; }
            .pay-button:hover { background: #2563eb; }
        """,
        "dark": """
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #111827; color: white; }
            .payment-container { max-width: 400px; margin: 0 auto; }
            .payment-card { background: #1f2937; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            .title { color: white; margin-bottom: 10px; }
            .description { color: #9ca3af; margin-bottom: 20px; }
            .pay-button { width: 100%; background: #10b981; color: white; border: none; padding: 12px; border-radius: 8px; font-size: 16px; cursor: pointer; }
        """
    }
    
    return themes.get(theme, themes["default"])

def format_amount_section(link: Dict[str, Any]) -> str:
    """
    Formatar seção de valor baseado no tipo de pagamento
    """
    if link["payment_type"] == "flexible":
        return f"""
        <div class="flexible-amount">
            <label>Valor do pagamento:</label>
            <input type="number" name="amount" min="{link.get('min_amount', 0)}" 
                   max="{link.get('max_amount', 999999)}" step="0.01" required>
        </div>
        """
    else:
        return f'<div class="fixed-amount">{format_currency(link["amount"])}</div>'

def generate_form_fields(link: Dict[str, Any]) -> str:
    """
    Gerar campos do formulário baseado nas configurações
    """
    fields = ""
    
    if link.get("collect_customer_info", True):
        fields += """
        <div class="customer-info">
            <input type="text" name="customer_name" placeholder="Nome completo" required>
            <input type="email" name="customer_email" placeholder="Email" required>
        </div>
        """
    
    fields += """
    <div class="payment-methods">
        <label><input type="radio" name="payment_method" value="pix" checked> PIX</label>
        <label><input type="radio" name="payment_method" value="card"> Cartão</label>
    </div>
    """
    
    return fields

def generate_payment_script(link: Dict[str, Any]) -> str:
    """
    Gerar JavaScript para processar pagamento
    """
    return f"""
    document.getElementById('payment-form').addEventListener('submit', async function(e) {{
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const paymentData = Object.fromEntries(formData);
        
        try {{
            const response = await fetch('/api/v1/payment-links/p/{link['link_id']}/process', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(paymentData)
            }});
            
            const result = await response.json();
            
            if (result.status === 'success') {{
                window.location.href = result.redirect_url || '/success';
            }} else {{
                alert('Erro no pagamento: ' + result.message);
            }}
        }} catch (error) {{
            alert('Erro ao processar pagamento');
        }}
    }});
    """

def generate_error_page(message: str) -> str:
    """
    Gerar página de erro personalizada
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Erro - Pagamento</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: sans-serif; text-align: center; padding: 50px; }}
            .error {{ color: #dc2626; }}
        </style>
    </head>
    <body>
        <h1 class="error">Erro no Pagamento</h1>
        <p>{message}</p>
        <a href="/">Voltar ao início</a>
    </body>
    </html>
    """

def format_currency(amount: Decimal) -> str:
    """
    Formatar valor em moeda brasileira
    """
    return f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")