"""
Modelos de dados para o Sistema Universal de Gestão de Eventos
Desenvolvido para ser escalável, performático e modular
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Numeric, Enum, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

# Enums para tipos de dados estruturados
class StatusUsuario(PyEnum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    PENDENTE = "pendente"
    BLOQUEADO = "bloqueado"

class StatusEvento(PyEnum):
    PLANEJAMENTO = "planejamento"
    ATIVO = "ativo"
    PAUSADO = "pausado"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"

class TipoEvento(PyEnum):
    FESTA = "festa"
    SHOW = "show"
    CONFERENCIA = "conferencia"
    WORKSHOP = "workshop"
    NETWORKING = "networking"
    CORPORATIVO = "corporativo"
    CASAMENTO = "casamento"
    ANIVERSARIO = "aniversario"
    OUTRO = "outro"

class StatusParticipante(PyEnum):
    CONFIRMADO = "confirmado"
    PRESENTE = "presente"
    AUSENTE = "ausente"
    CANCELADO = "cancelado"

class TipoPagamento(PyEnum):
    DINHEIRO = "dinheiro"
    PIX = "pix"
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    TRANSFERENCIA = "transferencia"

class StatusTransacao(PyEnum):
    PENDENTE = "pendente"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    CANCELADA = "cancelada"
    ESTORNADA = "estornada"

class TipoUsuario(PyEnum):
    ADMIN = "admin"
    ORGANIZADOR = "organizador"
    OPERADOR = "operador"
    PARTICIPANTE = "participante"

# ================================
# MODELOS PRINCIPAIS
# ================================

class Usuario(Base):
    """Modelo para usuários do sistema"""
    __tablename__ = "usuarios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefone = Column(String(20), nullable=True)
    senha_hash = Column(String(255), nullable=False)
    tipo_usuario = Column(Enum(TipoUsuario), default=TipoUsuario.PARTICIPANTE)
    ativo = Column(Boolean, default=True)
    foto_perfil = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    data_nascimento = Column(DateTime, nullable=True)
    cpf = Column(String(14), nullable=True, unique=True)
    empresa_id = Column(UUID(as_uuid=True), nullable=True)  # ID da empresa/organização
    endereco = Column(JSON, nullable=True)  # {rua, cidade, cep, estado}
    configuracoes = Column(JSON, nullable=True)  # Preferências do usuário
    ultimo_login = Column(DateTime, nullable=True)
    token_reset_senha = Column(String(255), nullable=True)
    token_verificacao = Column(String(255), nullable=True)
    email_verificado = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    eventos_organizados = relationship("Evento", back_populates="organizador")
    participacoes = relationship("Participante", back_populates="usuario")
    transacoes = relationship("Transacao", back_populates="usuario")
    movimentos_estoque = relationship("MovimentoEstoque", back_populates="usuario")
    vendas_pdv = relationship("VendaPDV", back_populates="vendedor")
    conquistas_promoter = relationship("PromoterConquista", back_populates="usuario")
    ranking_gamificacao = relationship("RankingGamificacao", back_populates="usuario")
    
    # Índices para performance
    __table_args__ = (
        Index('idx_usuario_email', 'email'),
        Index('idx_usuario_tipo', 'tipo_usuario'),
        Index('idx_usuario_ativo', 'ativo'),
    )

class Evento(Base):
    """Modelo principal para eventos"""
    __tablename__ = "eventos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    tipo_evento = Column(Enum(TipoEvento), nullable=False)
    status = Column(Enum(StatusEvento), default=StatusEvento.PLANEJAMENTO)
    
    # Dados temporais
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    data_inicio_checkin = Column(DateTime, nullable=True)
    data_fim_checkin = Column(DateTime, nullable=True)
    
    # Localização
    local_nome = Column(String(200), nullable=False)
    local_endereco = Column(String(500), nullable=False)
    local_coordenadas = Column(JSON, nullable=True)  # {lat, lng}
    capacidade_maxima = Column(Integer, nullable=True)
    
    # Configurações visuais e de branding
    cor_primaria = Column(String(7), default="#0EA5E9")  # Hex color
    cor_secundaria = Column(String(7), default="#64748B")
    logo_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    template_layout = Column(String(50), default="default")
    
    # Configurações funcionais
    permite_checkin_antecipado = Column(Boolean, default=False)
    requer_confirmacao = Column(Boolean, default=True)
    limite_participantes = Column(Integer, nullable=True)
    valor_entrada = Column(Numeric(10, 2), default=0.00)
    moeda = Column(String(3), default="BRL")
    
    # Configurações de gamificação
    sistema_pontuacao_ativo = Column(Boolean, default=False)
    pontos_checkin = Column(Integer, default=10)
    pontos_participacao = Column(Integer, default=5)
    
    # QR Code único do evento
    qr_code_checkin = Column(String(500), nullable=True)
    qr_code_data = Column(JSON, nullable=True)
    
    # Dados organizacionais
    organizador_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    equipe_organizacao = Column(JSON, nullable=True)  # Lista de IDs da equipe
    
    # Configurações de notificação
    webhook_checkin = Column(String(500), nullable=True)
    email_confirmacao_template = Column(Text, nullable=True)
    
    # Metadados
    tags = Column(JSON, nullable=True)  # Lista de tags
    configuracoes_extras = Column(JSON, nullable=True)
    notas_internas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    organizador = relationship("Usuario", back_populates="eventos_organizados")
    participantes = relationship("Participante", back_populates="evento", cascade="all, delete-orphan")
    produtos = relationship("Produto", back_populates="evento", cascade="all, delete-orphan")
    transacoes = relationship("Transacao", back_populates="evento")
    pontuacoes = relationship("Pontuacao", back_populates="evento")
    vendas_pdv = relationship("VendaPDV", back_populates="evento")
    
    # Índices para performance
    __table_args__ = (
        Index('idx_evento_status', 'status'),
        Index('idx_evento_data_inicio', 'data_inicio'),
        Index('idx_evento_organizador', 'organizador_id'),
        Index('idx_evento_tipo', 'tipo_evento'),
    )

class Participante(Base):
    """Modelo para participantes de eventos"""
    __tablename__ = "participantes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id"), nullable=False)
    
    # Status e dados de participação
    status = Column(Enum(StatusParticipante), default=StatusParticipante.CONFIRMADO)
    data_inscricao = Column(DateTime, default=func.now())
    data_checkin = Column(DateTime, nullable=True)
    data_checkout = Column(DateTime, nullable=True)
    
    # QR Code individual
    qr_code_individual = Column(String(500), nullable=True)
    qr_code_data = Column(JSON, nullable=True)
    
    # Dados de pagamento
    valor_pago = Column(Numeric(10, 2), default=0.00)
    forma_pagamento = Column(Enum(TipoPagamento), nullable=True)
    data_pagamento = Column(DateTime, nullable=True)
    comprovante_pagamento = Column(String(500), nullable=True)
    
    # Dados personalizados
    dados_adicionais = Column(JSON, nullable=True)  # Campos customizados do evento
    preferencias_alimentares = Column(String(500), nullable=True)
    necessidades_especiais = Column(String(500), nullable=True)
    
    # Gamificação
    pontos_obtidos = Column(Integer, default=0)
    badges_conquistadas = Column(JSON, nullable=True)  # Lista de badges
    
    # Controle de presença detalhado
    tempo_permanencia = Column(Integer, nullable=True)  # Em minutos
    areas_visitadas = Column(JSON, nullable=True)  # Lista de áreas do evento
    
    # Avaliação do evento
    avaliacao_evento = Column(Integer, nullable=True)  # 1-5 estrelas
    comentario_evento = Column(Text, nullable=True)
    data_avaliacao = Column(DateTime, nullable=True)
    
    # Metadados
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="participacoes")
    evento = relationship("Evento", back_populates="participantes")
    transacoes = relationship("Transacao", back_populates="participante")
    
    # Índices para performance
    __table_args__ = (
        Index('idx_participante_evento', 'evento_id'),
        Index('idx_participante_usuario', 'usuario_id'),
        Index('idx_participante_status', 'status'),
        Index('idx_participante_checkin', 'data_checkin'),
        # Índice único para evitar participação duplicada
        Index('idx_participante_unico', 'usuario_id', 'evento_id', unique=True),
    )

# ================================
# SISTEMA PDV E FINANCEIRO
# ================================

class Produto(Base):
    """Produtos disponíveis no PDV do evento"""
    __tablename__ = "produtos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id"), nullable=False)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.empresa_id"), nullable=False)
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias.id"), nullable=True)
    
    # Dados básicos do produto
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    codigo = Column(String(50), nullable=True, unique=True)  # Código interno
    codigo_barras = Column(String(50), nullable=True, unique=True)
    sku = Column(String(50), nullable=True)
    
    # Preços e custos
    preco_venda = Column(Numeric(10, 2), nullable=False)
    preco_custo = Column(Numeric(10, 2), nullable=True)
    margem_lucro = Column(Numeric(5, 2), nullable=True)  # Percentual
    
    # Controle de estoque
    quantidade_estoque = Column(Integer, default=0)  # Nome padrão do sistema
    estoque_inicial = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=0)
    estoque_maximo = Column(Integer, nullable=True)
    permite_venda_sem_estoque = Column(Boolean, default=False)
    
    # Configurações
    ativo = Column(Boolean, default=True)
    destaque = Column(Boolean, default=False)
    permite_desconto = Column(Boolean, default=True)
    requer_idade_minima = Column(Integer, nullable=True)
    
    # Mídia
    imagem_url = Column(String(500), nullable=True)
    imagens_extras = Column(JSON, nullable=True)  # URLs adicionais
    
    # Metadados
    tags = Column(JSON, nullable=True)
    configuracoes = Column(JSON, nullable=True)
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    evento = relationship("Evento", back_populates="produtos")
    categoria_rel = relationship("Categoria", back_populates="produtos")
    itens_transacao = relationship("ItemTransacao", back_populates="produto")
    movimentos_estoque = relationship("MovimentoEstoque", back_populates="produto")
    itens_venda_pdv = relationship("ItemVendaPDV", back_populates="produto")
    
    # Índices
    __table_args__ = (
        Index('idx_produto_evento', 'evento_id'),
        Index('idx_produto_ativo', 'ativo'),
        Index('idx_produto_categoria', 'categoria_id'),
    )

class Transacao(Base):
    """Transações financeiras do sistema"""
    __tablename__ = "transacoes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    participante_id = Column(UUID(as_uuid=True), ForeignKey("participantes.id"), nullable=True)
    
    # Dados da transação
    numero_transacao = Column(String(50), unique=True, nullable=False)
    tipo_transacao = Column(String(20), nullable=False)  # venda, entrada, desconto, etc
    status = Column(Enum(StatusTransacao), default=StatusTransacao.PENDENTE)
    
    # Valores
    valor_bruto = Column(Numeric(10, 2), nullable=False)
    valor_desconto = Column(Numeric(10, 2), default=0.00)
    valor_taxa = Column(Numeric(10, 2), default=0.00)
    valor_liquido = Column(Numeric(10, 2), nullable=False)
    moeda = Column(String(3), default="BRL")
    
    # Pagamento
    forma_pagamento = Column(Enum(TipoPagamento), nullable=False)
    parcelas = Column(Integer, default=1)
    valor_parcela = Column(Numeric(10, 2), nullable=True)
    
    # Dados do pagamento externo
    gateway_transacao_id = Column(String(100), nullable=True)
    gateway_resposta = Column(JSON, nullable=True)
    comprovante_url = Column(String(500), nullable=True)
    
    # Timestamps
    data_transacao = Column(DateTime, default=func.now())
    data_processamento = Column(DateTime, nullable=True)
    data_confirmacao = Column(DateTime, nullable=True)
    data_cancelamento = Column(DateTime, nullable=True)
    
    # Dados adicionais
    observacoes = Column(Text, nullable=True)
    metadados = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    evento = relationship("Evento", back_populates="transacoes")
    usuario = relationship("Usuario", back_populates="transacoes")
    participante = relationship("Participante", back_populates="transacoes")
    itens = relationship("ItemTransacao", back_populates="transacao", cascade="all, delete-orphan")
    movimentos_estoque = relationship("MovimentoEstoque", back_populates="venda")
    
    # Índices
    __table_args__ = (
        Index('idx_transacao_evento', 'evento_id'),
        Index('idx_transacao_usuario', 'usuario_id'),
        Index('idx_transacao_status', 'status'),
        Index('idx_transacao_data', 'data_transacao'),
        Index('idx_transacao_numero', 'numero_transacao'),
    )

class ItemTransacao(Base):
    """Itens individuais de uma transação"""
    __tablename__ = "itens_transacao"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transacao_id = Column(UUID(as_uuid=True), ForeignKey("transacoes.id"), nullable=False)
    produto_id = Column(UUID(as_uuid=True), ForeignKey("produtos.id"), nullable=False)
    
    # Dados do item
    quantidade = Column(Integer, nullable=False, default=1)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    desconto_unitario = Column(Numeric(10, 2), default=0.00)
    preco_total = Column(Numeric(10, 2), nullable=False)
    
    # Metadados
    observacoes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relacionamentos
    transacao = relationship("Transacao", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_transacao")
    
    # Índices
    __table_args__ = (
        Index('idx_item_transacao', 'transacao_id'),
        Index('idx_item_produto', 'produto_id'),
    )

# ================================
# SISTEMA DE GAMIFICAÇÃO
# ================================

class Pontuacao(Base):
    """Sistema de pontuação e gamificação"""
    __tablename__ = "pontuacoes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id"), nullable=False)
    
    # Pontuação
    pontos_checkin = Column(Integer, default=0)
    pontos_participacao = Column(Integer, default=0)
    pontos_compras = Column(Integer, default=0)
    pontos_bonus = Column(Integer, default=0)
    pontos_total = Column(Integer, default=0)
    
    # Ranking
    posicao_ranking = Column(Integer, nullable=True)
    categoria_ranking = Column(String(20), nullable=True)  # bronze, prata, ouro, etc
    
    # Conquistas
    conquistas_desbloqueadas = Column(JSON, nullable=True)
    data_ultima_conquista = Column(DateTime, nullable=True)
    
    # Metadados
    historico_pontos = Column(JSON, nullable=True)  # Log de pontuações
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    evento = relationship("Evento", back_populates="pontuacoes")
    
    # Índices
    __table_args__ = (
        Index('idx_pontuacao_evento', 'evento_id'),
        Index('idx_pontuacao_usuario', 'usuario_id'),
        Index('idx_pontuacao_total', 'pontos_total'),
        Index('idx_pontuacao_unica', 'usuario_id', 'evento_id', unique=True),
    )

class Conquista(Base):
    """Conquistas disponíveis no sistema"""
    __tablename__ = "conquistas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Dados da conquista
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=False)
    categoria = Column(String(50), nullable=False)  # checkin, compras, social, etc
    dificuldade = Column(String(20), default="normal")  # facil, normal, dificil, lendario
    
    # Critérios
    criterios = Column(JSON, nullable=False)  # Condições para desbloquear
    pontos_recompensa = Column(Integer, default=0)
    
    # Visual
    icone_url = Column(String(500), nullable=True)
    cor = Column(String(7), default="#FFD700")
    
    # Configurações
    ativa = Column(Boolean, default=True)
    global_conquista = Column(Boolean, default=False)  # Disponível em todos os eventos
    
    # Metadados
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# ================================
# SISTEMA DE AUDITORIA E LOGS
# ================================

class LogAuditoria(Base):
    """Log de auditoria para rastreamento de ações"""
    __tablename__ = "logs_auditoria"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Dados da ação
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id"), nullable=True)
    acao = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc
    entidade = Column(String(50), nullable=False)  # usuario, evento, participante, etc
    entidade_id = Column(String(100), nullable=True)
    
    # Detalhes
    descricao = Column(Text, nullable=True)
    dados_anteriores = Column(JSON, nullable=True)
    dados_novos = Column(JSON, nullable=True)
    
    # Contexto técnico
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    dispositivo = Column(String(100), nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=func.now())
    
    # Índices
    __table_args__ = (
        Index('idx_auditoria_usuario', 'usuario_id'),
        Index('idx_auditoria_evento', 'evento_id'),
        Index('idx_auditoria_acao', 'acao'),
        Index('idx_auditoria_timestamp', 'timestamp'),
    )

# ================================
# CONFIGURAÇÕES E METADADOS
# ================================

class ConfiguracaoSistema(Base):
    """Configurações globais do sistema"""
    __tablename__ = "configuracoes_sistema"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chave = Column(String(100), unique=True, nullable=False)
    valor = Column(JSON, nullable=False)
    descricao = Column(Text, nullable=True)
    categoria = Column(String(50), nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Índices
    __table_args__ = (
        Index('idx_config_chave', 'chave'),
        Index('idx_config_categoria', 'categoria'),
    )

# ================================
# VIEWS PARA RELATÓRIOS
# ================================

# ================================
# SISTEMA DE ESTOQUE COMPLEMENTAR
# ================================

class Categoria(Base):
    """Categorias para organização de produtos"""
    __tablename__ = "categorias"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.empresa_id"), nullable=False)
    
    # Dados básicos
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    cor = Column(String(7), default="#007bff")  # Cor hex para UI
    icone = Column(String(50), nullable=True)  # Nome do ícone
    
    # Configurações
    ativa = Column(Boolean, default=True)
    ordem = Column(Integer, default=0)  # Para ordenação customizada
    
    # Metadados
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    produtos = relationship("Produto", back_populates="categoria_rel")
    
    # Índices
    __table_args__ = (
        Index('idx_categoria_empresa', 'empresa_id'),
        Index('idx_categoria_ativa', 'ativa'),
    )

class MovimentoEstoque(Base):
    """Histórico de movimentações de estoque"""
    __tablename__ = "movimentos_estoque"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produto_id = Column(UUID(as_uuid=True), ForeignKey("produtos.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    venda_id = Column(UUID(as_uuid=True), ForeignKey("transacoes.id"), nullable=True)
    
    # Dados do movimento
    tipo_movimento = Column(String(20), nullable=False)  # entrada, saida, ajuste
    quantidade = Column(Integer, nullable=False)
    estoque_anterior = Column(Integer, nullable=False)
    estoque_atual = Column(Integer, nullable=False)
    motivo = Column(String(200), nullable=False)
    
    # Valores (opcionais para movimentos com valor)
    valor_unitario = Column(Numeric(10, 2), nullable=True)
    valor_total = Column(Numeric(10, 2), nullable=True)
    
    # Dados adicionais
    observacoes = Column(Text, nullable=True)
    documento_referencia = Column(String(100), nullable=True)  # NF, pedido, etc
    
    # Timestamp
    criado_em = Column(DateTime, default=func.now())
    
    # Relacionamentos
    produto = relationship("Produto", back_populates="movimentos_estoque")
    usuario = relationship("Usuario", back_populates="movimentos_estoque")
    venda = relationship("Transacao", back_populates="movimentos_estoque")
    
    # Índices
    __table_args__ = (
        Index('idx_movimento_produto', 'produto_id'),
        Index('idx_movimento_usuario', 'usuario_id'),
        Index('idx_movimento_tipo', 'tipo_movimento'),
        Index('idx_movimento_data', 'criado_em'),
    )

class VendaPDV(Base):
    """Vendas realizadas pelo sistema PDV"""
    __tablename__ = "vendas_pdv"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id"), nullable=False)
    usuario_vendedor_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Dados da venda
    numero_venda = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default="PENDENTE")  # PENDENTE, APROVADA, CANCELADA
    
    # Valores
    valor_bruto = Column(Numeric(10, 2), nullable=False)
    valor_desconto = Column(Numeric(10, 2), default=0.00)
    valor_liquido = Column(Numeric(10, 2), nullable=False)
    
    # Pagamento
    forma_pagamento = Column(Enum(TipoPagamento), nullable=False)
    valor_pago = Column(Numeric(10, 2), nullable=False)
    valor_troco = Column(Numeric(10, 2), default=0.00)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    aprovado_em = Column(DateTime, nullable=True)
    
    # Relacionamentos
    evento = relationship("Evento", back_populates="vendas_pdv")
    vendedor = relationship("Usuario", back_populates="vendas_pdv")
    itens = relationship("ItemVendaPDV", back_populates="venda", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_venda_evento', 'evento_id'),
        Index('idx_venda_vendedor', 'usuario_vendedor_id'),
        Index('idx_venda_status', 'status'),
        Index('idx_venda_data', 'criado_em'),
    )

class ItemVendaPDV(Base):
    """Itens de uma venda PDV"""
    __tablename__ = "itens_venda_pdv"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venda_id = Column(UUID(as_uuid=True), ForeignKey("vendas_pdv.id"), nullable=False)
    produto_id = Column(UUID(as_uuid=True), ForeignKey("produtos.id"), nullable=False)
    
    # Dados do item
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    desconto_unitario = Column(Numeric(10, 2), default=0.00)
    preco_total = Column(Numeric(10, 2), nullable=False)
    
    # Relacionamentos
    venda = relationship("VendaPDV", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_venda_pdv")
    
    # Índices
    __table_args__ = (
        Index('idx_item_venda', 'venda_id'),
        Index('idx_item_venda_produto', 'produto_id'),
    )

# ================================
# SISTEMA DE GAMIFICAÇÃO COMPLEMENTAR
# ================================

class PromoterConquista(Base):
    """Conquistas específicas para promoters"""
    __tablename__ = "promoter_conquistas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Dados da conquista
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=False)
    tipo = Column(String(50), nullable=False)  # vendas, participacao, engajamento
    nivel = Column(String(20), default="bronze")  # bronze, prata, ouro, diamante
    
    # Métricas
    meta_valor = Column(Numeric(10, 2), nullable=True)
    meta_quantidade = Column(Integer, nullable=True)
    valor_atual = Column(Numeric(10, 2), default=0)
    quantidade_atual = Column(Integer, default=0)
    progresso_percentual = Column(Numeric(5, 2), default=0)
    
    # Status
    desbloqueada = Column(Boolean, default=False)
    data_desbloqueio = Column(DateTime, nullable=True)
    pontos_xp = Column(Integer, default=0)
    
    # Timestamps
    criado_em = Column(DateTime, default=func.now())
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="conquistas_promoter")
    
    # Índices
    __table_args__ = (
        Index('idx_conquista_usuario', 'usuario_id'),
        Index('idx_conquista_tipo', 'tipo'),
        Index('idx_conquista_nivel', 'nivel'),
    )

class RankingGamificacao(Base):
    """Ranking global de gamificação"""
    __tablename__ = "ranking_gamificacao"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.empresa_id"), nullable=False)
    
    # Pontuação
    xp_total = Column(Integer, default=0)
    vendas_total = Column(Numeric(12, 2), default=0)
    vendas_mes_atual = Column(Numeric(10, 2), default=0)
    vendas_mes_anterior = Column(Numeric(10, 2), default=0)
    
    # Ranking
    posicao_geral = Column(Integer, nullable=True)
    posicao_empresa = Column(Integer, nullable=True)
    badge_atual = Column(String(50), default="novato")
    nivel_atual = Column(Integer, default=1)
    
    # Crescimento
    crescimento_percentual = Column(Numeric(5, 2), default=0)
    streak_vendas = Column(Integer, default=0)  # Dias consecutivos com vendas
    
    # Períodos
    mes_referencia = Column(String(7), nullable=False)  # YYYY-MM
    ultima_atualizacao = Column(DateTime, default=func.now())
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="ranking_gamificacao")
    
    # Índices
    __table_args__ = (
        Index('idx_ranking_usuario', 'usuario_id'),
        Index('idx_ranking_empresa', 'empresa_id'),
        Index('idx_ranking_xp', 'xp_total'),
        Index('idx_ranking_mes', 'mes_referencia'),
        Index('idx_ranking_unico', 'usuario_id', 'mes_referencia', unique=True),
    )

# ================================
# SISTEMA DE PAYMENT LINKS
# ================================

class StatusLink(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    COMPLETED = "completed"

class TipoPagamentoLink(PyEnum):
    SINGLE = "single"        # Pagamento único
    RECURRING = "recurring"   # Recorrente
    FLEXIBLE = "flexible"     # Valor flexível

class StatusPagamentoLink(PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentLink(Base):
    """Links de pagamento dinâmicos"""
    __tablename__ = "payment_links"
    
    id = Column(String(36), primary_key=True)  # UUID string
    user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    url_hash = Column(String(32), unique=True, nullable=False, index=True)
    
    # Dados básicos
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Valores
    amount = Column(Numeric(12, 2), nullable=True)  # None para valor flexível
    min_amount = Column(Numeric(12, 2), nullable=True)
    max_amount = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), default="BRL")
    
    # Configurações
    payment_type = Column(Enum(TipoPagamentoLink), default=TipoPagamentoLink.SINGLE)
    status = Column(Enum(StatusLink), default=StatusLink.ACTIVE)
    expires_at = Column(DateTime, nullable=True)
    max_uses = Column(Integer, nullable=True)
    
    # Personalização
    theme = Column(String(20), default="default")
    custom_css = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    success_url = Column(String(500), nullable=True)
    cancel_url = Column(String(500), nullable=True)
    
    # Split de pagamentos
    enable_split = Column(Boolean, default=False)
    split_recipients = Column(JSON, nullable=True)  # Lista de destinatários
    
    # Configurações avançadas
    collect_customer_info = Column(Boolean, default=True)
    send_receipt = Column(Boolean, default=True)
    allow_installments = Column(Boolean, default=False)
    webhook_url = Column(String(500), nullable=True)
    
    # Estatísticas
    uses_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    total_collected = Column(Numeric(15, 2), default=0)
    
    # Metadados
    link_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("Usuario")
    payment_attempts = relationship("PaymentAttempt", back_populates="payment_link")
    
    # Índices
    __table_args__ = (
        Index('idx_payment_link_user', 'user_id'),
        Index('idx_payment_link_status', 'status'),
        Index('idx_payment_link_type', 'payment_type'),
        Index('idx_payment_link_created', 'created_at'),
        Index('idx_payment_link_expires', 'expires_at'),
        Index('idx_payment_link_hash', 'url_hash'),
    )

class PaymentAttempt(Base):
    """Tentativas de pagamento via links"""
    __tablename__ = "payment_attempts"
    
    id = Column(String(36), primary_key=True)  # UUID string
    link_id = Column(String(36), ForeignKey("payment_links.id"), nullable=False)
    
    # Dados do pagamento
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="BRL")
    
    # Dados do cliente
    customer_name = Column(String(200), nullable=True)
    customer_email = Column(String(255), nullable=True)
    customer_phone = Column(String(20), nullable=True)
    customer_document = Column(String(20), nullable=True)
    
    # Dados do pagamento
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    gateway_response = Column(JSON, nullable=True)
    
    # Status e processamento
    status = Column(Enum(StatusPagamentoLink), default=StatusPagamentoLink.PENDING)
    failure_reason = Column(Text, nullable=True)
    
    # Dados técnicos
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    payment_link = relationship("PaymentLink", back_populates="payment_attempts")
    
    # Índices
    __table_args__ = (
        Index('idx_payment_attempt_link', 'link_id'),
        Index('idx_payment_attempt_status', 'status'),
        Index('idx_payment_attempt_created', 'created_at'),
        Index('idx_payment_attempt_transaction', 'transaction_id'),
        Index('idx_payment_attempt_email', 'customer_email'),
    )

class PaymentLinkAnalytics(Base):
    """Analytics consolidados de links de pagamento"""
    __tablename__ = "payment_link_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    link_id = Column(String(36), ForeignKey("payment_links.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Métricas do dia
    views = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    successful_payments = Column(Integer, default=0)
    failed_payments = Column(Integer, default=0)
    
    # Valores
    total_amount = Column(Numeric(15, 2), default=0)
    average_amount = Column(Numeric(10, 2), default=0)
    
    # Breakdown por método
    payment_methods_breakdown = Column(JSON, nullable=True)
    
    # Geolocalização
    countries = Column(JSON, nullable=True)
    cities = Column(JSON, nullable=True)
    
    # Dispositivos
    devices = Column(JSON, nullable=True)
    browsers = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    payment_link = relationship("PaymentLink")
    
    # Índices
    __table_args__ = (
        Index('idx_analytics_link_date', 'link_id', 'date', unique=True),
        Index('idx_analytics_date', 'date'),
    )

"""
Views SQL que serão criadas para relatórios e dashboards:

1. view_dashboard_evento - Métricas gerais por evento
2. view_ranking_participantes - Ranking de pontuação
3. view_vendas_pdv - Relatórios de vendas
4. view_presenca_tempo_real - Status de presença em tempo real
5. view_financeiro_resumo - Resumo financeiro por evento
6. view_payment_links_summary - Resumo de links de pagamento
7. view_payment_analytics - Analytics de pagamentos consolidados
"""
