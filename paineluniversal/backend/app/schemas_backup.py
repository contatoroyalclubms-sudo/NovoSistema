"""
Schemas Pydantic para validação de dados
Sistema Universal de Gestão de Eventos - FASE 2

Modelos de entrada e saída para APIs RESTful
"""

from pydantic import BaseModel, EmailStr, validator, Field, HttpUrl
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
import uuid
from decimal import Decimal

# Validadores personalizados para documentos brasileiros
try:
    from app.utils.cpf_utils import validar_cpf
    from app.utils.cnpj_utils import validar_cnpj
    VALIDATORS_AVAILABLE = True
except ImportError:
    VALIDATORS_AVAILABLE = False

# ================================
# ENUMS PARA VALIDAÇÃO
# ================================

class StatusEventoEnum(str, Enum):
    PLANEJAMENTO = "planejamento"
    ATIVO = "ativo"
    PAUSADO = "pausado"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"

class TipoEventoEnum(str, Enum):
    FESTA = "festa"
    SHOW = "show"
    CONFERENCIA = "conferencia"
    WORKSHOP = "workshop"
    NETWORKING = "networking"
    CORPORATIVO = "corporativo"
    CASAMENTO = "casamento"
    ANIVERSARIO = "aniversario"
    OUTRO = "outro"

class StatusParticipanteEnum(str, Enum):
    CONFIRMADO = "confirmado"
    PRESENTE = "presente"
    AUSENTE = "ausente"
    CANCELADO = "cancelado"

class TipoPagamentoEnum(str, Enum):
    DINHEIRO = "dinheiro"
    PIX = "pix"
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    TRANSFERENCIA = "transferencia"

class StatusTransacaoEnum(str, Enum):
    PENDENTE = "pendente"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    CANCELADA = "cancelada"
    ESTORNADA = "estornada"

class TipoUsuarioEnum(str, Enum):
    ADMIN = "admin"
    ORGANIZADOR = "organizador"
    OPERADOR = "operador"
    PARTICIPANTE = "participante"

# ================================
# SCHEMAS BASE
# ================================

class BaseSchema(BaseModel):
    """Schema base com configurações padrão"""
    
    class Config:
        orm_mode = True
        use_enum_values = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v)
        }

class TimestampMixin(BaseModel):
    """Mixin para campos de timestamp"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ================================
# SCHEMAS DE USUÁRIO
# ================================

class UsuarioBase(BaseSchema):
    """Schema base para usuário"""
    nome: str = Field(..., min_length=2, max_length=100, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Email único do usuário")
    telefone: Optional[str] = Field(None, pattern=r'^\(\d{2}\) \d{4,5}-\d{4}$', description="Telefone no formato (00) 00000-0000")
    tipo_usuario: TipoUsuarioEnum = Field(TipoUsuarioEnum.PARTICIPANTE, description="Tipo de usuário")
    ativo: bool = Field(True, description="Se o usuário está ativo")
    foto_perfil: Optional[HttpUrl] = Field(None, description="URL da foto de perfil")
    bio: Optional[str] = Field(None, max_length=500, description="Biografia do usuário")
    data_nascimento: Optional[date] = Field(None, description="Data de nascimento")
    cpf: Optional[str] = Field(None, pattern=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', description="CPF no formato 000.000.000-00")

class UsuarioCreate(UsuarioBase):
    """Schema para criação de usuário"""
    senha: str = Field(..., min_length=8, description="Senha (mínimo 8 caracteres)")
    confirmar_senha: str = Field(..., description="Confirmação da senha")
    
    endereco: Optional[Dict[str, Any]] = Field(None, description="Endereço completo")
    configuracoes: Optional[Dict[str, Any]] = Field(None, description="Configurações personalizadas")
    
    @validator('confirmar_senha')
    def senhas_devem_coincidir(cls, v, values):
        if 'senha' in values and v != values['senha']:
            raise ValueError('Senhas não coincidem')
        return v
    
    @validator('cpf')
    def validar_cpf(cls, v):
        if v:
            # Validação básica de CPF (implementar validação completa)
            digits = ''.join(filter(str.isdigit, v))
            if len(digits) != 11:
                raise ValueError('CPF deve ter 11 dígitos')
        return v

class UsuarioUpdate(BaseSchema):
    """Schema para atualização de usuário"""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    telefone: Optional[str] = Field(None, pattern=r'^\(\d{2}\) \d{4,5}-\d{4}$')
    foto_perfil: Optional[HttpUrl] = None
    bio: Optional[str] = Field(None, max_length=500)
    data_nascimento: Optional[date] = None
    endereco: Optional[Dict[str, Any]] = None
    configuracoes: Optional[Dict[str, Any]] = None

class UsuarioResponse(UsuarioBase, TimestampMixin):
    """Schema de resposta com dados do usuário"""
    id: uuid.UUID
    email_verificado: bool
    ultimo_login: Optional[datetime]
    endereco: Optional[Dict[str, Any]]
    configuracoes: Optional[Dict[str, Any]]

class UsuarioLogin(BaseSchema):
    """Schema para login"""
    email: EmailStr
    senha: str
    lembrar_me: bool = Field(False, description="Manter login ativo")

class UsuarioLoginResponse(BaseSchema):
    """Resposta do login"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UsuarioResponse

# ================================
# SCHEMAS DE EVENTO
# ================================

class EventoBase(BaseSchema):
    """Schema base para evento"""
    nome: str = Field(..., min_length=3, max_length=200, description="Nome do evento")
    descricao: Optional[str] = Field(None, max_length=2000, description="Descrição detalhada")
    tipo_evento: TipoEventoEnum = Field(..., description="Tipo do evento")
    status: StatusEventoEnum = Field(StatusEventoEnum.PLANEJAMENTO, description="Status atual")
    
    # Dados temporais
    data_inicio: datetime = Field(..., description="Data e hora de início")
    data_fim: datetime = Field(..., description="Data e hora de fim")
    data_inicio_checkin: Optional[datetime] = Field(None, description="Quando check-in inicia")
    data_fim_checkin: Optional[datetime] = Field(None, description="Quando check-in encerra")
    
    # Localização
    local_nome: str = Field(..., min_length=3, max_length=200, description="Nome do local")
    local_endereco: str = Field(..., min_length=10, max_length=500, description="Endereço completo")
    local_coordenadas: Optional[Dict[str, float]] = Field(None, description="Latitude e longitude")
    capacidade_maxima: Optional[int] = Field(None, ge=1, description="Capacidade máxima")
    
    # Configurações visuais
    cor_primaria: str = Field("#0EA5E9", pattern=r'^#[0-9A-Fa-f]{6}$', description="Cor primária (hex)")
    cor_secundaria: str = Field("#64748B", pattern=r'^#[0-9A-Fa-f]{6}$', description="Cor secundária (hex)")
    logo_url: Optional[HttpUrl] = Field(None, description="URL do logo")
    banner_url: Optional[HttpUrl] = Field(None, description="URL do banner")
    template_layout: str = Field("default", description="Template visual")
    
    # Configurações funcionais
    permite_checkin_antecipado: bool = Field(False, description="Permite check-in antes do horário")
    requer_confirmacao: bool = Field(True, description="Requer confirmação de participação")
    limite_participantes: Optional[int] = Field(None, ge=1, description="Limite de participantes")
    valor_entrada: Decimal = Field(Decimal('0.00'), ge=0, description="Valor da entrada")
    moeda: str = Field("BRL", min_length=3, max_length=3, description="Código da moeda")
    
    # Gamificação
    sistema_pontuacao_ativo: bool = Field(False, description="Sistema de pontuação ativo")
    pontos_checkin: int = Field(10, ge=0, description="Pontos por check-in")
    pontos_participacao: int = Field(5, ge=0, description="Pontos por participação")
    
    @validator('data_fim')
    def data_fim_posterior_inicio(cls, v, values):
        if 'data_inicio' in values and v <= values['data_inicio']:
            raise ValueError('Data de fim deve ser posterior à data de início')
        return v
    
    @validator('local_coordenadas')
    def validar_coordenadas(cls, v):
        if v and ('lat' not in v or 'lng' not in v):
            raise ValueError('Coordenadas devem conter lat e lng')
        if v:
            if not (-90 <= v['lat'] <= 90):
                raise ValueError('Latitude deve estar entre -90 e 90')
            if not (-180 <= v['lng'] <= 180):
                raise ValueError('Longitude deve estar entre -180 e 180')
        return v

class EventoCreate(EventoBase):
    """Schema para criação de evento"""
    equipe_organizacao: Optional[List[uuid.UUID]] = Field(None, description="IDs da equipe organizadora")
    webhook_checkin: Optional[HttpUrl] = Field(None, description="Webhook para check-ins")
    email_confirmacao_template: Optional[str] = Field(None, description="Template de email")
    tags: Optional[List[str]] = Field(None, description="Tags do evento")
    configuracoes_extras: Optional[Dict[str, Any]] = Field(None, description="Configurações extras")
    notas_internas: Optional[str] = Field(None, max_length=1000, description="Notas internas")

class EventoUpdate(BaseSchema):
    """Schema para atualização de evento"""
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    status: Optional[StatusEventoEnum] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    data_inicio_checkin: Optional[datetime] = None
    data_fim_checkin: Optional[datetime] = None
    local_nome: Optional[str] = Field(None, min_length=3, max_length=200)
    local_endereco: Optional[str] = Field(None, min_length=10, max_length=500)
    local_coordenadas: Optional[Dict[str, float]] = None
    capacidade_maxima: Optional[int] = Field(None, ge=1)
    cor_primaria: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    cor_secundaria: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    logo_url: Optional[HttpUrl] = None
    banner_url: Optional[HttpUrl] = None
    permite_checkin_antecipado: Optional[bool] = None
    requer_confirmacao: Optional[bool] = None
    limite_participantes: Optional[int] = Field(None, ge=1)
    valor_entrada: Optional[Decimal] = Field(None, ge=0)
    sistema_pontuacao_ativo: Optional[bool] = None
    pontos_checkin: Optional[int] = Field(None, ge=0)
    pontos_participacao: Optional[int] = Field(None, ge=0)

class EventoResponse(EventoBase, TimestampMixin):
    """Schema de resposta com dados do evento"""
    id: uuid.UUID
    organizador_id: uuid.UUID
    qr_code_checkin: Optional[str]
    qr_code_data: Optional[Dict[str, Any]]
    equipe_organizacao: Optional[List[uuid.UUID]]
    tags: Optional[List[str]]
    configuracoes_extras: Optional[Dict[str, Any]]
    notas_internas: Optional[str]
    
    # Estatísticas (calculadas)
    total_participantes: Optional[int] = 0
    total_presentes: Optional[int] = 0
    total_confirmados: Optional[int] = 0
    receita_total: Optional[Decimal] = Decimal('0.00')

# ================================
# SCHEMAS DE PARTICIPANTE
# ================================

class ParticipanteBase(BaseSchema):
    """Schema base para participante"""
    status: StatusParticipanteEnum = Field(StatusParticipanteEnum.CONFIRMADO, description="Status da participação")
    valor_pago: Decimal = Field(Decimal('0.00'), ge=0, description="Valor pago pelo participante")
    forma_pagamento: Optional[TipoPagamentoEnum] = Field(None, description="Forma de pagamento")
    dados_adicionais: Optional[Dict[str, Any]] = Field(None, description="Dados customizados")
    preferencias_alimentares: Optional[str] = Field(None, max_length=500, description="Preferências alimentares")
    necessidades_especiais: Optional[str] = Field(None, max_length=500, description="Necessidades especiais")

class ParticipanteCreate(ParticipanteBase):
    """Schema para criação de participante"""
    usuario_id: uuid.UUID = Field(..., description="ID do usuário")
    evento_id: uuid.UUID = Field(..., description="ID do evento")
    comprovante_pagamento: Optional[HttpUrl] = Field(None, description="URL do comprovante")

class ParticipanteUpdate(BaseSchema):
    """Schema para atualização de participante"""
    status: Optional[StatusParticipanteEnum] = None
    valor_pago: Optional[Decimal] = Field(None, ge=0)
    forma_pagamento: Optional[TipoPagamentoEnum] = None
    dados_adicionais: Optional[Dict[str, Any]] = None
    preferencias_alimentares: Optional[str] = Field(None, max_length=500)
    necessidades_especiais: Optional[str] = Field(None, max_length=500)
    observacoes: Optional[str] = Field(None, max_length=1000)

class ParticipanteResponse(ParticipanteBase, TimestampMixin):
    """Schema de resposta com dados do participante"""
    id: uuid.UUID
    usuario_id: uuid.UUID
    evento_id: uuid.UUID
    data_inscricao: datetime
    data_checkin: Optional[datetime]
    data_checkout: Optional[datetime]
    qr_code_individual: Optional[str]
    qr_code_data: Optional[Dict[str, Any]]
    data_pagamento: Optional[datetime]
    comprovante_pagamento: Optional[str]
    pontos_obtidos: int = 0
    badges_conquistadas: Optional[List[str]]
    tempo_permanencia: Optional[int]
    areas_visitadas: Optional[List[str]]
    avaliacao_evento: Optional[int]
    comentario_evento: Optional[str]
    data_avaliacao: Optional[datetime]
    observacoes: Optional[str]

# ================================
# SCHEMAS DE CHECK-IN
# ================================

class CheckinRequest(BaseSchema):
    """Schema para solicitação de check-in"""
    participante_id: Optional[uuid.UUID] = Field(None, description="ID do participante")
    qr_code: Optional[str] = Field(None, description="QR Code para check-in")
    localizacao: Optional[Dict[str, float]] = Field(None, description="Coordenadas do check-in")
    
    @validator('participante_id', 'qr_code')
    def pelo_menos_um_identificador(cls, v, values, field):
        if field.name == 'qr_code' and not v and not values.get('participante_id'):
            raise ValueError('Deve fornecer participante_id ou qr_code')
        return v

class CheckinResponse(BaseSchema):
    """Resposta do check-in"""
    success: bool
    message: str
    participante_id: uuid.UUID
    evento_id: uuid.UUID
    data_checkin: datetime
    pontos_obtidos: int = 0
    badges_desbloqueadas: Optional[List[str]] = []

class CheckoutRequest(BaseSchema):
    """Schema para check-out"""
    participante_id: uuid.UUID = Field(..., description="ID do participante")
    avaliacao_evento: Optional[int] = Field(None, ge=1, le=5, description="Avaliação de 1 a 5")
    comentario_evento: Optional[str] = Field(None, max_length=1000, description="Comentário sobre o evento")

# ================================
# SCHEMAS DE PRODUTO E PDV
# ================================

class ProdutoBase(BaseSchema):
    """Schema base para produto"""
    nome: str = Field(..., min_length=2, max_length=100, description="Nome do produto")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição do produto")
    categoria: Optional[str] = Field(None, max_length=50, description="Categoria do produto")
    codigo_barras: Optional[str] = Field(None, description="Código de barras")
    sku: Optional[str] = Field(None, max_length=50, description="SKU do produto")
    preco_venda: Decimal = Field(..., gt=0, description="Preço de venda")
    preco_custo: Optional[Decimal] = Field(None, ge=0, description="Preço de custo")
    estoque_inicial: int = Field(0, ge=0, description="Estoque inicial")
    estoque_minimo: int = Field(0, ge=0, description="Estoque mínimo")
    estoque_maximo: Optional[int] = Field(None, ge=0, description="Estoque máximo")
    ativo: bool = Field(True, description="Produto ativo")
    destaque: bool = Field(False, description="Produto em destaque")
    permite_desconto: bool = Field(True, description="Permite aplicar desconto")
    requer_idade_minima: Optional[int] = Field(None, ge=0, le=100, description="Idade mínima para compra")

class ProdutoCreate(ProdutoBase):
    """Schema para criação de produto"""
    evento_id: uuid.UUID = Field(..., description="ID do evento")
    imagem_url: Optional[HttpUrl] = Field(None, description="URL da imagem principal")
    imagens_extras: Optional[List[HttpUrl]] = Field(None, description="URLs de imagens extras")
    tags: Optional[List[str]] = Field(None, description="Tags do produto")
    configuracoes: Optional[Dict[str, Any]] = Field(None, description="Configurações extras")

class ProdutoUpdate(BaseSchema):
    """Schema para atualização de produto"""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(None, max_length=1000)
    categoria: Optional[str] = Field(None, max_length=50)
    preco_venda: Optional[Decimal] = Field(None, gt=0)
    preco_custo: Optional[Decimal] = Field(None, ge=0)
    estoque_minimo: Optional[int] = Field(None, ge=0)
    estoque_maximo: Optional[int] = Field(None, ge=0)
    ativo: Optional[bool] = None
    destaque: Optional[bool] = None
    permite_desconto: Optional[bool] = None
    requer_idade_minima: Optional[int] = Field(None, ge=0, le=100)

class ProdutoResponse(ProdutoBase, TimestampMixin):
    """Schema de resposta com dados do produto"""
    id: uuid.UUID
    evento_id: uuid.UUID
    estoque_atual: int
    margem_lucro: Optional[Decimal]
    imagem_url: Optional[str]
    imagens_extras: Optional[List[str]]
    tags: Optional[List[str]]
    configuracoes: Optional[Dict[str, Any]]

# ================================
# SCHEMAS DE TRANSAÇÃO
# ================================

class ItemTransacaoCreate(BaseSchema):
    """Schema para item de transação"""
    produto_id: uuid.UUID = Field(..., description="ID do produto")
    quantidade: int = Field(..., gt=0, description="Quantidade do produto")
    desconto_unitario: Decimal = Field(Decimal('0.00'), ge=0, description="Desconto por unidade")
    observacoes: Optional[str] = Field(None, max_length=500, description="Observações do item")

class TransacaoCreate(BaseSchema):
    """Schema para criação de transação"""
    evento_id: uuid.UUID = Field(..., description="ID do evento")
    participante_id: Optional[uuid.UUID] = Field(None, description="ID do participante (opcional)")
    tipo_transacao: str = Field("venda", description="Tipo da transação")
    forma_pagamento: TipoPagamentoEnum = Field(..., description="Forma de pagamento")
    parcelas: int = Field(1, ge=1, le=12, description="Número de parcelas")
    valor_desconto: Decimal = Field(Decimal('0.00'), ge=0, description="Desconto total")
    itens: List[ItemTransacaoCreate] = Field(..., min_items=1, description="Itens da transação")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações da transação")
    metadados: Optional[Dict[str, Any]] = Field(None, description="Metadados extras")

class TransacaoResponse(BaseSchema, TimestampMixin):
    """Schema de resposta com dados da transação"""
    id: uuid.UUID
    numero_transacao: str
    evento_id: uuid.UUID
    usuario_id: Optional[uuid.UUID]
    participante_id: Optional[uuid.UUID]
    tipo_transacao: str
    status: StatusTransacaoEnum
    valor_bruto: Decimal
    valor_desconto: Decimal
    valor_taxa: Decimal
    valor_liquido: Decimal
    moeda: str
    forma_pagamento: TipoPagamentoEnum
    parcelas: int
    valor_parcela: Optional[Decimal]
    data_transacao: datetime
    data_processamento: Optional[datetime]
    data_confirmacao: Optional[datetime]
    observacoes: Optional[str]
    metadados: Optional[Dict[str, Any]]
    itens: List[Dict[str, Any]] = []

# ================================
# SCHEMAS DE RELATÓRIOS
# ================================

class RelatorioEventoResponse(BaseSchema):
    """Relatório completo do evento"""
    evento: EventoResponse
    participantes: Dict[str, int]  # status -> quantidade
    financeiro: Dict[str, Decimal]  # receitas, custos, etc
    produtos_vendidos: List[Dict[str, Any]]
    checkins_por_hora: List[Dict[str, int]]
    ranking_participantes: List[Dict[str, Any]]
    data_geracao: datetime

class DashboardResponse(BaseSchema):
    """Dashboard em tempo real"""
    eventos_ativos: int
    total_participantes: int
    total_presentes: int
    receita_hoje: Decimal
    receita_total: Decimal
    eventos_recentes: List[EventoResponse]
    checkins_recentes: List[Dict[str, Any]]
    vendas_recentes: List[Dict[str, Any]]
    timestamp: datetime

# ================================
# SCHEMAS DE SISTEMA
# ================================

class HealthResponse(BaseSchema):
    """Resposta do health check"""
    status: str
    timestamp: datetime
    version: str
    phase: str
    environment: str
    database: str
    cache: str
    websocket: str
    uptime_seconds: float

class ErrorResponse(BaseSchema):
    """Schema padrão para erros"""
    error: str
    status_code: int
    timestamp: datetime
    path: str
    details: Optional[Dict[str, Any]] = None

# ================================
# SCHEMAS DE WEBSOCKET
# ================================

class WebSocketMessage(BaseSchema):
    """Mensagem WebSocket padrão"""
    type: str = Field(..., description="Tipo da mensagem")
    data: Optional[Dict[str, Any]] = Field(None, description="Dados da mensagem")
    evento_id: Optional[uuid.UUID] = Field(None, description="ID do evento relacionado")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da mensagem")

class WebSocketResponse(BaseSchema):
    """Resposta WebSocket padrão"""
    type: str
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ================================
# SCHEMAS DE ESTOQUE
# ================================

class CategoriaBase(BaseModel):
    """Schema base para categoria"""
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = None
    cor: str = Field(default="#007bff", pattern=r"^#[0-9A-Fa-f]{6}$")
    icone: Optional[str] = None
    ativa: bool = True
    ordem: int = 0

class CategoriaCreate(CategoriaBase):
    """Schema para criação de categoria"""
    pass

class CategoriaUpdate(BaseModel):
    """Schema para atualização de categoria"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = None
    cor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icone: Optional[str] = None
    ativa: Optional[bool] = None
    ordem: Optional[int] = None

class CategoriaResponse(CategoriaBase):
    """Schema de resposta para categoria"""
    id: str
    empresa_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProdutoEstoqueUpdate(BaseModel):
    """Schema para atualização de estoque de produto"""
    quantidade_estoque: int = Field(..., ge=0)
    estoque_minimo: int = Field(..., ge=0)
    estoque_maximo: Optional[int] = Field(None, ge=0)
    permite_venda_sem_estoque: bool = False

class MovimentoEstoqueBase(BaseModel):
    """Schema base para movimento de estoque"""
    produto_id: str
    tipo_movimento: str = Field(..., pattern=r"^(entrada|saida|ajuste)$")
    quantidade: int = Field(..., gt=0)
    motivo: str = Field(..., min_length=1, max_length=200)
    venda_id: Optional[str] = None  # UUID da venda associada
    observacoes: Optional[str] = None
    documento_referencia: Optional[str] = None

class MovimentoEstoqueCreate(MovimentoEstoqueBase):
    """Schema para criação de movimento de estoque"""
    pass

class MovimentoEstoqueResponse(MovimentoEstoqueBase):
    """Schema de resposta para movimento de estoque"""
    id: str
    usuario_id: str
    venda_id: Optional[str] = None
    estoque_anterior: int
    estoque_atual: int
    valor_unitario: Optional[Decimal] = None
    valor_total: Optional[Decimal] = None
    criado_em: datetime
    
    class Config:
        from_attributes = True

class AlertaEstoque(BaseModel):
    """Schema para alertas de estoque"""
    produto_id: str
    produto_nome: str
    produto_codigo: Optional[str] = None
    quantidade_atual: int
    estoque_minimo: int
    categoria: Optional[str] = None
    evento_nome: Optional[str] = None
    tipo_alerta: str  # "baixo", "zerado", "negativo"
    prioridade: str  # "baixa", "media", "alta", "critica"
    
class RelatorioEstoque(BaseModel):
    """Schema para relatório de estoque"""
    # Valores totais
    valor_total_estoque: float
    valor_potencial_venda: float
    margem_potencial: float
    total_produtos: int
    
    # Alertas
    produtos_estoque_baixo: int
    produtos_sem_estoque: int
    
    # Movimentações do período
    entradas_periodo: int
    saidas_periodo: int
    saldo_periodo: int
    
    # Dados detalhados
    movimentacoes_por_dia: Dict[str, Dict[str, int]]
    top_produtos_vendidos: List[Dict[str, Any]]
    produtos_por_categoria: Dict[str, Dict[str, int]]
    
    # Metadados
    periodo_inicio: date
    periodo_fim: date
    gerado_em: datetime

class VendaPDVCreate(BaseModel):
    """Schema para criação de venda PDV"""
    evento_id: str
    itens: List[Dict[str, Any]]  # [{"produto_id": str, "quantidade": int, "preco_unitario": float}]
    forma_pagamento: TipoPagamentoEnum
    valor_pago: Decimal = Field(..., ge=0)
    observacoes: Optional[str] = None

class VendaPDVResponse(BaseModel):
    """Schema de resposta para venda PDV"""
    id: str
    evento_id: str
    usuario_vendedor_id: str
    numero_venda: str
    status: str
    valor_bruto: Decimal
    valor_desconto: Decimal
    valor_liquido: Decimal
    forma_pagamento: str
    valor_pago: Decimal
    valor_troco: Decimal
    criado_em: datetime
    aprovado_em: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ItemVendaPDVResponse(BaseModel):
    """Schema de resposta para item de venda PDV"""
    id: str
    venda_id: str
    produto_id: str
    quantidade: int
    preco_unitario: Decimal
    desconto_unitario: Decimal
    preco_total: Decimal
    
    class Config:
        from_attributes = True

class EstoqueAjusteManual(BaseModel):
    """Schema para ajuste manual de estoque"""
    produto_id: str
    quantidade_nova: int = Field(..., ge=0)
    motivo: str = Field(..., min_length=1, max_length=200)
    observacoes: Optional[str] = None

class EstoqueEntradaLote(BaseModel):
    """Schema para entrada de estoque em lote"""
    entradas: List[Dict[str, Any]]  # [{"produto_id": str, "quantidade": int, "motivo": str}]

class DisponibilidadeEstoque(BaseModel):
    """Schema para verificação de disponibilidade"""
    disponivel: bool
    mensagens: List[str]
    itens_verificados: int
    itens_indisponiveis: int

# ================================
# SCHEMAS DE GAMIFICAÇÃO
# ================================

class PromoterConquistaCreate(BaseModel):
    """Schema para criação de conquista de promoter"""
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: str = Field(..., min_length=1)
    tipo: str = Field(..., pattern=r"^(vendas|participacao|engajamento)$")
    nivel: str = Field(default="bronze", pattern=r"^(bronze|prata|ouro|diamante)$")
    meta_valor: Optional[Decimal] = None
    meta_quantidade: Optional[int] = None

class PromoterConquistaResponse(BaseModel):
    """Schema de resposta para conquista de promoter"""
    id: str
    usuario_id: str
    nome: str
    descricao: str
    tipo: str
    nivel: str
    meta_valor: Optional[Decimal] = None
    meta_quantidade: Optional[int] = None
    valor_atual: Decimal
    quantidade_atual: int
    progresso_percentual: Decimal
    desbloqueada: bool
    data_desbloqueio: Optional[datetime] = None
    pontos_xp: int
    criado_em: datetime
    atualizado_em: datetime
    
    class Config:
        from_attributes = True

class RankingGamificacaoResponse(BaseModel):
    """Schema de resposta para ranking de gamificação"""
    id: str
    usuario_id: str
    empresa_id: str
    xp_total: int
    vendas_total: Decimal
    vendas_mes_atual: Decimal
    vendas_mes_anterior: Decimal
    posicao_geral: Optional[int] = None
    posicao_empresa: Optional[int] = None
    badge_atual: str
    nivel_atual: int
    crescimento_percentual: Decimal
    streak_vendas: int
    mes_referencia: str
    ultima_atualizacao: datetime
    
    class Config:
        from_attributes = True

class InventarioResponse(BaseModel):
    """Schema de resposta para inventário completo"""
    total_produtos: int
    total_categorias: int
    valor_total_estoque: float
    produtos_estoque_baixo: int
    produtos_sem_estoque: int
    produtos_recentes: List[Dict[str, Any]]
    categorias_populares: List[Dict[str, Any]]
    movimentacoes_recentes: List[MovimentoEstoqueResponse]
    alertas: List[AlertaEstoque]
    
    class Config:
        from_attributes = True

class DashboardGamificacao(BaseModel):
    """Schema para dashboard de gamificação"""
    usuario_ranking: RankingGamificacaoResponse
    conquistas_recentes: List[PromoterConquistaResponse]
    estatisticas_mes: Dict[str, Any]
    top_performers: List[Dict[str, Any]]
    badges_disponiveis: List[str]
    proximo_nivel: Dict[str, Any]

class MetricasGamificacao(BaseModel):
    """Schema para métricas de gamificação"""
    total_xp: int
    vendas_mes: Decimal
    crescimento: Decimal
    posicao_ranking: int
    conquistas_desbloqueadas: int
    badge_atual: str
    nivel: int
    progresso_proximo_nivel: float


# ===== SCHEMAS FINANCEIROS ADICIONAIS =====

class MovimentacaoFinanceiraResponse(BaseModel):
    id: int
    tipo: str
    valor: float
    descricao: str
    categoria: str
    evento_id: Optional[int]
    status: str
    data_movimentacao: datetime
    criado_em: datetime

class ResumoFinanceiro(BaseModel):
    receita_bruta: float
    receita_liquida: float
    receita_ingressos: float
    receita_pdv: float
    comissoes_total: float
    entradas_extras: float
    saidas_operacionais: float
    receita_por_metodo: Dict[str, float]
    crescimento_receita: float
    margem_liquida: float
    periodo_inicio: date
    periodo_fim: date
    calculado_em: datetime

class FluxoCaixa(BaseModel):
    fluxo_dados: List[Dict[str, Any]]
    projecoes: List[Dict[str, Any]]
    saldo_atual: float
    periodo_consultado: str
    data_inicio: date
    data_fim: date
    gerado_em: datetime

class ComissoesPromoters(BaseModel):
    comissoes: List[Dict[str, Any]]
    total_comissoes: float
    total_vendas: float
    total_promoters: int
    periodo_inicio: Optional[date]
    periodo_fim: Optional[date]
    gerado_em: datetime

class ConciliacaoPagamentos(BaseModel):
    data_conciliacao: date
    evento_id: Optional[int]
    vendas_por_metodo: Dict[str, Dict[str, Any]]
    total_transacoes: int
    total_valor: float
    divergencias: List[str]
    status_conciliacao: str
    realizada_em: datetime

class CaixaPDVResponse(BaseModel):
    id: int
    numero_caixa: str
    evento_id: int
    operador_nome: str
    valor_abertura: float
    valor_vendas: float
    valor_sangrias: float
    valor_fechamento: float
    status: str
    data_abertura: datetime
    data_fechamento: Optional[datetime]
    observacoes: Optional[str]

# ===== SCHEMAS DE GAMIFICAÇÃO AVANÇADA =====

class ConquistaResponse(BaseModel):
    id: int
    nome: str
    descricao: str
    categoria: str
    badge_nivel: str
    icone: str
    pontos_necessarios: int
    recompensa_creditos: int
    ativa: bool
    criado_em: datetime

class RankingPromoterResponse(BaseModel):
    promoter_id: int
    nome_promoter: str
    avatar_url: Optional[str]
    badge_principal: str
    badge_icone: str
    nivel_experiencia: int
    pontos_xp: int
    total_vendas: int
    receita_gerada: float
    ticket_medio: float
    eventos_trabalhados: int
    taxa_presenca: float
    taxa_conversao: float
    crescimento_mensal: float
    posicao_atual: int
    posicao_anterior: Optional[int]
    streak_vendas: int
    ultima_venda: Optional[datetime]

class BadgeResponse(BaseModel):
    nome: str
    descricao: str
    icone: str
    cor: str

class MetricasGamificacaoAvancadas(BaseModel):
    promoter_id: int
    vendas_total: int
    receita_total: float
    eventos_trabalhados: int
    conquistas_obtidas: int
    nivel_atual: int
    pontos_xp: int
    xp_proximo_nivel: int
    ticket_medio: float
    periodo_consultado: str
    data_inicio: datetime
    data_fim: datetime

# ===== SCHEMAS DE RELATÓRIOS =====

class RelatorioVendas(BaseModel):
    total_vendas: int
    receita_total: float
    ticket_medio: float
    taxa_conversao: float
    vendas_por_dia: Dict[str, Dict[str, float]]
    vendas_por_promoter: Dict[str, Dict[str, float]]
    vendas_por_lista: Dict[str, Dict[str, float]]
    vendas_por_pagamento: Dict[str, Dict[str, float]]
    periodo_inicio: Optional[date]
    periodo_fim: Optional[date]
    gerado_em: datetime

class RelatorioCheckins(BaseModel):
    total_checkins: int
    total_vendas: int
    taxa_presenca: float
    tempo_medio_checkin: int
    pico_checkins: int
    hora_pico: Optional[int]
    checkins_por_hora: Dict[int, int]
    checkins_por_metodo: Dict[str, int]
    fila_espera: int
    periodo_inicio: Optional[date]
    periodo_fim: Optional[date]
    gerado_em: datetime

class RelatorioFinanceiro(BaseModel):
    receita_ingressos: float
    receita_pdv: float
    receita_bruta: float
    comissoes_promoters: float
    receita_liquida: float
    custos_operacionais: float
    lucro_estimado: float
    margem_lucro: float
    receita_por_pagamento: Dict[str, float]
    periodo_inicio: Optional[date]
    periodo_fim: Optional[date]
    gerado_em: datetime

class RelatorioPromoters(BaseModel):
    total_promoters: int
    promoters_ativos: int
    receita_total: float
    vendas_total: int
    taxa_presenca_media: float
    performance_promoters: List[Dict[str, Any]]
    periodo_inicio: Optional[date]
    periodo_fim: Optional[date]
    gerado_em: datetime

class FiltrosRelatorio(BaseModel):
    evento_id: Optional[int] = None
    promoter_id: Optional[int] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    tipo_lista: Optional[str] = None
    metodo_pagamento: Optional[str] = None
    incluir_pdv: bool = True
    incluir_comissoes: bool = True
    incluir_ranking: bool = True


# ===== SCHEMAS DE VALIDAÇÃO DE DOCUMENTOS =====

class DocumentoCPF(BaseModel):
    """Schema para validação de CPF"""
    cpf: str = Field(..., description="CPF do usuário")
    
    @validator('cpf')
    def validar_cpf_format(cls, v):
        if not VALIDATORS_AVAILABLE:
            return v
        
        if not validar_cpf(v):
            raise ValueError('CPF inválido')
        return v

class DocumentoCNPJ(BaseModel):
    """Schema para validação de CNPJ"""
    cnpj: str = Field(..., description="CNPJ da empresa")
    
    @validator('cnpj')
    def validar_cnpj_format(cls, v):
        if not VALIDATORS_AVAILABLE:
            return v
            
        if not validar_cnpj(v):
            raise ValueError('CNPJ inválido')
        return v

class ValidacaoDocumento(BaseModel):
    """Schema para resposta de validação de documentos"""
    documento: str
    tipo: str  # cpf ou cnpj
    valido: bool
    formatado: str
    erro: Optional[str] = None
    informacoes: Optional[Dict[str, Any]] = None

class PessoaFisica(DocumentoCPF):
    """Schema base para pessoa física"""
    nome: str = Field(..., min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    data_nascimento: Optional[date] = None

class PessoaJuridica(DocumentoCNPJ):
    """Schema base para pessoa jurídica"""
    razao_social: str = Field(..., min_length=2, max_length=200)
    nome_fantasia: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    inscricao_municipal: Optional[str] = None

class EnderecoCompleto(BaseModel):
    """Schema para endereço completo"""
    cep: str = Field(..., pattern=r'^\d{5}-?\d{3}$')
    logradouro: str = Field(..., min_length=5, max_length=200)
    numero: str = Field(..., max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: str = Field(..., min_length=2, max_length=100)
    cidade: str = Field(..., min_length=2, max_length=100)
    estado: str = Field(..., min_length=2, max_length=2)
    pais: str = Field(default="Brasil", max_length=50)

class ContratanteEvento(BaseModel):
    """Schema para contratante de evento (pessoa física ou jurídica)"""
    tipo_pessoa: str = Field(..., pattern=r'^(fisica|juridica)$')
    
    # Dados pessoa física
    nome: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    
    # Dados pessoa jurídica  
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    
    # Dados comuns
    email: EmailStr
    telefone: str
    endereco: EnderecoCompleto
    
    @validator('cpf')
    def validar_cpf_se_pessoa_fisica(cls, v, values):
        if values.get('tipo_pessoa') == 'fisica' and v:
            if VALIDATORS_AVAILABLE and not validar_cpf(v):
                raise ValueError('CPF inválido')
        return v
    
    @validator('cnpj') 
    def validar_cnpj_se_pessoa_juridica(cls, v, values):
        if values.get('tipo_pessoa') == 'juridica' and v:
            if VALIDATORS_AVAILABLE and not validar_cnpj(v):
                raise ValueError('CNPJ inválido')
        return v
    
    @validator('nome')
    def validar_nome_pessoa_fisica(cls, v, values):
        if values.get('tipo_pessoa') == 'fisica' and not v:
            raise ValueError('Nome é obrigatório para pessoa física')
        return v
    
    @validator('razao_social')
    def validar_razao_social_pessoa_juridica(cls, v, values):
        if values.get('tipo_pessoa') == 'juridica' and not v:
            raise ValueError('Razão social é obrigatória para pessoa jurídica')
        return v

# ===== SCHEMAS DE USUÁRIO COM VALIDAÇÃO APRIMORADA =====

class UsuarioComDocumento(BaseModel):
    """Schema de usuário com validação de documento"""
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    telefone: Optional[str] = None
    tipo_usuario: str = Field(default="cliente")
    
    @validator('cpf')
    def validar_cpf_usuario(cls, v):
        if v and VALIDATORS_AVAILABLE and not validar_cpf(v):
            raise ValueError('CPF inválido')
        return v
    
    @validator('cnpj')
    def validar_cnpj_usuario(cls, v):
        if v and VALIDATORS_AVAILABLE and not validar_cnpj(v):
            raise ValueError('CNPJ inválido')
        return v
    
    @validator('telefone')
    def validar_telefone(cls, v):
        if v:
            # Remove caracteres não numéricos
            telefone_limpo = ''.join(filter(str.isdigit, v))
            if len(telefone_limpo) not in [10, 11]:
                raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        return v
