"""
Schemas simplificados para inicialização rápida
Sistema Universal de Gestão de Eventos - FASE 2
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


# Base Schema
class BaseSchema(BaseModel):
    """Schema base com configurações comuns"""
    
    class Config:
        from_attributes = True
        validate_by_name = True


# Enums
class TipoUsuarioEnum(str, Enum):
    ADMIN = "ADMIN"
    ORGANIZADOR = "ORGANIZADOR"
    PROMOTER = "PROMOTER"
    PARTICIPANTE = "PARTICIPANTE"


class StatusEventoEnum(str, Enum):
    RASCUNHO = "RASCUNHO"
    ATIVO = "ATIVO"
    CANCELADO = "CANCELADO"
    FINALIZADO = "FINALIZADO"


# Schemas de Usuário
class UsuarioBase(BaseSchema):
    """Base para dados do usuário"""
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(...)
    telefone: Optional[str] = None
    tipo_usuario: TipoUsuarioEnum = TipoUsuarioEnum.PARTICIPANTE
    ativo: bool = True


class UsuarioCreate(UsuarioBase):
    """Schema para criação de usuário"""
    senha: str = Field(..., min_length=6)


class UsuarioUpdate(BaseSchema):
    """Schema para atualização de usuário"""
    nome: Optional[str] = None
    telefone: Optional[str] = None
    ativo: Optional[bool] = None


class Usuario(UsuarioBase):
    """Schema completo do usuário"""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Schemas de Autenticação
class LoginRequest(BaseSchema):
    """Request de login"""
    email: EmailStr
    senha: str


class Token(BaseSchema):
    """Response de token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Usuario


class RefreshTokenRequest(BaseSchema):
    """Request de refresh token"""
    refresh_token: str


# Schemas de Evento
class EventoBase(BaseSchema):
    """Base para dados do evento"""
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = None
    data_inicio: datetime
    data_fim: datetime
    local_nome: str = Field(..., max_length=200)
    local_endereco: str = Field(..., max_length=500)


class EventoCreate(EventoBase):
    """Schema para criação de evento"""
    pass


class EventoUpdate(BaseSchema):
    """Schema para atualização de evento"""
    nome: Optional[str] = None
    descricao: Optional[str] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None


class Evento(EventoBase):
    """Schema completo do evento"""
    id: str
    organizador_id: str
    status: StatusEventoEnum
    created_at: Optional[datetime] = None


# Response padrão
class ResponseSuccess(BaseSchema):
    """Response de sucesso padrão"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


# Schema de erro
class ResponseError(BaseSchema):
    """Response de erro padrão"""
    success: bool = False
    message: str
    detail: Optional[str] = None


# Schema para health check
class HealthCheck(BaseSchema):
    """Schema para health check"""
    status: str = "healthy"
    timestamp: datetime
    version: str = "2.0.0"