"""
Router de Eventos - CRUD completo de eventos
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, File, UploadFile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, desc, asc, func, select
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
import logging
import os
from pathlib import Path
import uuid

from app.database import get_db
from app.models import Evento, Usuario, Empresa, StatusEvento, TipoUsuario, ComentarioEvento
from app.schemas import (
    Evento as EventoSchema, EventoCreate, EventoUpdate,
    FiltroEventos, PaginatedResponse, ResponseSuccess
)
from app.services.openai_service import OpenAIService
from app.dependencies import get_current_user, get_openai_service
from app.auth import (
    get_current_active_user, get_current_admin_user, 
    verificar_acesso_evento, log_user_action
)
from app.websocket import event_notifier
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# =============================================================================
# ENDPOINTS DE LISTAGEM E BUSCA
# =============================================================================

@router.get("/", response_model=PaginatedResponse, summary="Listar eventos")
async def list_eventos(
    request: Request,
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    status: Optional[StatusEvento] = Query(None, description="Filtrar por status"),
    data_inicio: Optional[date] = Query(None, description="Data início mínima"),
    data_fim: Optional[date] = Query(None, description="Data fim máxima"),
    empresa_id: Optional[int] = Query(None, description="Filtrar por empresa"),
    only_active: bool = Query(False, description="Apenas eventos ativos"),
    order_by: str = Query("data_inicio", description="Campo para ordenação"),
    order_dir: str = Query("desc", description="Direção da ordenação (asc/desc)"),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lista eventos com filtros e paginação
    
    Filtros disponíveis:
    - **nome**: Busca por nome (like)
    - **status**: Status do evento
    - **data_inicio/data_fim**: Filtros por data
    - **empresa_id**: Filtrar por empresa (admin only)
    - **only_active**: Apenas eventos ativos
    """
    try:
        # Query base
        query = db.query(Evento).options(
            joinedload(Evento.empresa),
            joinedload(Evento.usuario_criador)
        )
        
        # Filtro por empresa (usuários só veem eventos da própria empresa)
        if current_user.tipo != TipoUsuario.ADMIN:
            query = query.filter(Evento.empresa_id == current_user.empresa_id)
        elif empresa_id:
            query = query.filter(Evento.empresa_id == empresa_id)
        
        # Aplicar filtros
        if nome:
            query = query.filter(Evento.nome.ilike(f"%{nome}%"))
        
        if status:
            query = query.filter(Evento.status == status)
        
        if only_active:
            query = query.filter(Evento.status == StatusEvento.ATIVO)
        
        if data_inicio:
            query = query.filter(Evento.data_inicio >= data_inicio)
        
        if data_fim:
            query = query.filter(Evento.data_fim <= data_fim)
        
        # Ordenação
        order_column = getattr(Evento, order_by, Evento.data_inicio)
        if order_dir.lower() == "asc":
            query = query.order_by(asc(order_column))
        else:
            query = query.order_by(desc(order_column))
        
        # Contagem total
        total = query.count()
        
        # Paginação
        offset = (page - 1) * size
        eventos = query.offset(offset).limit(size).all()
        
        # Calcular metadados da paginação
        pages = (total + size - 1) // size
        has_next = page < pages
        has_prev = page > 1
        
        return PaginatedResponse(
            items=[EventoSchema.from_orm(evento) for evento in eventos],
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar eventos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.get("/my-events", response_model=List[EventoSchema], summary="Meus eventos")
async def get_my_events(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retorna eventos criados pelo usuário atual
    """
    try:
        eventos = db.query(Evento).filter(
            Evento.usuario_criador_id == current_user.id
        ).order_by(desc(Evento.criado_em)).all()
        
        return [EventoSchema.from_orm(evento) for evento in eventos]
        
    except Exception as e:
        logger.error(f"Erro ao buscar eventos do usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.get("/upcoming", response_model=List[EventoSchema], summary="Próximos eventos")
async def get_upcoming_events(
    limit: int = Query(10, ge=1, le=50, description="Número máximo de eventos"),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retorna próximos eventos da empresa do usuário
    """
    try:
        now = datetime.utcnow()
        
        eventos = db.query(Evento).filter(
            and_(
                Evento.empresa_id == current_user.empresa_id,
                Evento.data_inicio >= now,
                Evento.status == StatusEvento.ATIVO
            )
        ).order_by(asc(Evento.data_inicio)).limit(limit).all()
        
        return [EventoSchema.from_orm(evento) for evento in eventos]
        
    except Exception as e:
        logger.error(f"Erro ao buscar próximos eventos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

# =============================================================================
# ENDPOINTS DE CRUD
# =============================================================================

@router.get("/{evento_id}", response_model=EventoSchema, summary="Obter evento por ID")
async def get_evento(
    evento_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retorna dados detalhados de um evento específico
    """
    try:
        evento = db.query(Evento).options(
            joinedload(Evento.empresa),
            joinedload(Evento.usuario_criador)
        ).filter(Evento.id == evento_id).first()
        
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        # Verificar acesso
        if not verificar_acesso_evento(current_user, evento.empresa_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este evento"
            )
        
        return EventoSchema.from_orm(evento)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar evento {evento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.post("/", response_model=EventoSchema, summary="Criar novo evento")
async def create_evento(
    evento_data: EventoCreate,
    request: Request,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo evento
    
    Campos obrigatórios:
    - **nome**: Nome do evento
    - **local**: Local do evento
    - **data_inicio**: Data e hora de início
    - **data_fim**: Data e hora de fim
    """
    try:
        # Verificar permissões para criar eventos
        if current_user.tipo not in [TipoUsuario.ADMIN, TipoUsuario.ORGANIZADOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores e organizadores podem criar eventos"
            )
        
        # Validações de negócio
        if evento_data.data_fim <= evento_data.data_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data de fim deve ser posterior à data de início"
            )
        
        if evento_data.data_inicio <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data de início deve ser futura"
            )
        
        # Verificar se há conflito de local (opcional)
        conflito = db.query(Evento).filter(
            and_(
                Evento.local == evento_data.local,
                Evento.empresa_id == current_user.empresa_id,
                Evento.status.in_([StatusEvento.ATIVO, StatusEvento.RASCUNHO]),
                or_(
                    and_(
                        Evento.data_inicio <= evento_data.data_inicio,
                        Evento.data_fim >= evento_data.data_inicio
                    ),
                    and_(
                        Evento.data_inicio <= evento_data.data_fim,
                        Evento.data_fim >= evento_data.data_fim
                    )
                )
            )
        ).first()
        
        if conflito:
            logger.warning(f"Conflito de local detectado para evento no local {evento_data.local}")
            # Não bloquear, apenas avisar no log
        
        # Criar evento
        db_evento = Evento(
            **evento_data.dict(),
            empresa_id=current_user.empresa_id,
            usuario_criador_id=current_user.id,
            status=StatusEvento.RASCUNHO
        )
        
        db.add(db_evento)
        db.commit()
        db.refresh(db_evento)
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=current_user,
            action="CREATE_EVENTO",
            table_name="eventos",
            record_id=db_evento.id,
            new_data=evento_data.dict(),
            request=request,
            details=f"Criação do evento {db_evento.nome}"
        )
        
        logger.info(f"Evento criado por {current_user.email}: {db_evento.nome}")
        
        return EventoSchema.from_orm(db_evento)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar evento: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.put("/{evento_id}", response_model=EventoSchema, summary="Atualizar evento")
async def update_evento(
    evento_id: int,
    evento_update: EventoUpdate,
    request: Request,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza dados de um evento existente
    """
    try:
        # Buscar evento
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        # Verificar acesso
        if not verificar_acesso_evento(current_user, evento.empresa_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este evento"
            )
        
        # Verificar permissões para editar
        if current_user.tipo not in [TipoUsuario.ADMIN] and evento.usuario_criador_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o criador do evento ou administradores podem editá-lo"
            )
        
        # Dados anteriores para auditoria
        old_data = {
            "nome": evento.nome,
            "descricao": evento.descricao,
            "local": evento.local,
            "data_inicio": evento.data_inicio.isoformat() if evento.data_inicio else None,
            "data_fim": evento.data_fim.isoformat() if evento.data_fim else None,
            "status": evento.status.value if evento.status else None
        }
        
        # Aplicar atualizações
        update_data = evento_update.dict(exclude_unset=True)
        
        # Validações se data está sendo alterada
        if "data_inicio" in update_data or "data_fim" in update_data:
            new_data_inicio = update_data.get("data_inicio", evento.data_inicio)
            new_data_fim = update_data.get("data_fim", evento.data_fim)
            
            if new_data_fim <= new_data_inicio:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Data de fim deve ser posterior à data de início"
                )
        
        # Aplicar mudanças
        for field, value in update_data.items():
            setattr(evento, field, value)
        
        db.commit()
        db.refresh(evento)
        
        # Notificar mudança de status via WebSocket
        if "status" in update_data:
            await event_notifier.notify_evento_status_change(
                evento_id=evento.id,
                old_status=old_data["status"],
                new_status=update_data["status"]
            )
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=current_user,
            action="UPDATE_EVENTO",
            table_name="eventos",
            record_id=evento.id,
            old_data=old_data,
            new_data=update_data,
            request=request,
            details=f"Atualização do evento {evento.nome}"
        )
        
        logger.info(f"Evento atualizado por {current_user.email}: {evento.nome}")
        
        return EventoSchema.from_orm(evento)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar evento {evento_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.delete("/{evento_id}", response_model=ResponseSuccess, summary="Excluir evento")
async def delete_evento(
    evento_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Exclui um evento (soft delete - muda status para CANCELADO)
    """
    try:
        # Buscar evento
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        # Verificar acesso
        if not verificar_acesso_evento(current_user, evento.empresa_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este evento"
            )
        
        # Verificar permissões para excluir
        if current_user.tipo != TipoUsuario.ADMIN and evento.usuario_criador_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o criador do evento ou administradores podem excluí-lo"
            )
        
        # Verificar se evento pode ser excluído
        if evento.status == StatusEvento.FINALIZADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível excluir evento já finalizado"
            )
        
        # Verificar se há transações ou check-ins
        from app.models import Transacao, Checkin
        
        transacoes_count = db.query(func.count(Transacao.id)).filter(
            Transacao.evento_id == evento_id
        ).scalar()
        
        checkins_count = db.query(func.count(Checkin.id)).filter(
            Checkin.evento_id == evento_id
        ).scalar()
        
        if transacoes_count > 0 or checkins_count > 0:
            # Soft delete - apenas cancelar evento
            old_status = evento.status
            evento.status = StatusEvento.CANCELADO
            db.commit()
            
            # Notificar cancelamento
            await event_notifier.notify_evento_status_change(
                evento_id=evento.id,
                old_status=old_status.value,
                new_status=StatusEvento.CANCELADO.value
            )
            
            message = "Evento cancelado (há transações/check-ins vinculados)"
        else:
            # Hard delete - excluir completamente
            db.delete(evento)
            db.commit()
            message = "Evento excluído permanentemente"
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=current_user,
            action="DELETE_EVENTO",
            table_name="eventos",
            record_id=evento_id,
            old_data={"nome": evento.nome, "status": old_status.value if 'old_status' in locals() else evento.status.value},
            request=request,
            details=f"Exclusão do evento {evento.nome}"
        )
        
        logger.info(f"Evento excluído por {current_user.email}: {evento.nome}")
        
        return ResponseSuccess(message=message)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir evento {evento_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

# =============================================================================
# ENDPOINTS DE UPLOAD E MÍDIA
# =============================================================================

@router.post("/{evento_id}/upload-image", response_model=ResponseSuccess, summary="Upload de imagem do evento")
async def upload_evento_image(
    evento_id: int,
    file: UploadFile = File(...),
    image_type: str = Query("imagem", description="Tipo da imagem (imagem/banner)"),
    request: Request = None,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Faz upload de imagem para o evento
    
    - **image_type**: 'imagem' ou 'banner'
    - **file**: Arquivo de imagem (JPG, PNG, WebP)
    """
    try:
        # Buscar evento
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        # Verificar acesso
        if not verificar_acesso_evento(current_user, evento.empresa_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este evento"
            )
        
        # Validar tipo de arquivo
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de arquivo não suportado. Use JPG, PNG ou WebP"
            )
        
        # Validar tamanho do arquivo
        if file.size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Arquivo muito grande. Máximo: {settings.max_file_size}MB"
            )
        
        # Gerar nome único para arquivo
        file_extension = file.filename.split(".")[-1].lower()
        unique_filename = f"evento_{evento_id}_{image_type}_{uuid.uuid4()}.{file_extension}"
        
        # Criar diretório se não existir
        upload_dir = Path(settings.upload_dir) / "eventos"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Salvar arquivo
        file_path = upload_dir / unique_filename
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Gerar URL do arquivo
        file_url = f"/uploads/eventos/{unique_filename}"
        
        # Atualizar evento
        if image_type == "banner":
            evento.banner_url = file_url
        else:
            evento.imagem_url = file_url
        
        db.commit()
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=current_user,
            action="UPLOAD_EVENTO_IMAGE",
            table_name="eventos",
            record_id=evento.id,
            new_data={"image_type": image_type, "file_url": file_url},
            request=request,
            details=f"Upload de {image_type} para evento {evento.nome}"
        )
        
        logger.info(f"Imagem uploaded para evento {evento_id} por {current_user.email}")
        
        return ResponseSuccess(
            message="Imagem enviada com sucesso",
            data={"file_url": file_url}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload de imagem para evento {evento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

# =============================================================================
# ENDPOINTS DE ESTATÍSTICAS
# =============================================================================

@router.get("/{evento_id}/stats", summary="Estatísticas do evento")
async def get_evento_stats(
    evento_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas detalhadas do evento
    """
    try:
        # Buscar evento
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        # Verificar acesso
        if not verificar_acesso_evento(current_user, evento.empresa_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este evento"
            )
        
        # Buscar estatísticas
        from app.models import Lista, Convidado, Transacao, Checkin, VendaPDV
        
        # Estatísticas de listas
        total_listas = db.query(func.count(Lista.id)).filter(Lista.evento_id == evento_id).scalar()
        total_convidados = db.query(func.count(Convidado.id)).filter(Convidado.evento_id == evento_id).scalar()
        total_presentes = db.query(func.count(Checkin.id)).filter(Checkin.evento_id == evento_id).scalar()
        
        # Estatísticas financeiras
        receita_listas = db.query(func.coalesce(func.sum(Transacao.valor), 0)).filter(
            and_(Transacao.evento_id == evento_id, Transacao.status == "aprovada")
        ).scalar()
        
        receita_pdv = db.query(func.coalesce(func.sum(VendaPDV.total_final), 0)).filter(
            and_(VendaPDV.evento_id == evento_id, VendaPDV.status == "finalizada")
        ).scalar()
        
        # Taxa de presença
        taxa_presenca = (total_presentes / total_convidados * 100) if total_convidados > 0 else 0
        
        # Capacidade ocupada
        capacidade_ocupada = (total_presentes / evento.capacidade_maxima * 100) if evento.capacidade_maxima else 0
        
        return {
            "evento_id": evento_id,
            "nome_evento": evento.nome,
            "status": evento.status.value,
            "listas": {
                "total_listas": total_listas,
                "total_convidados": total_convidados,
                "total_presentes": total_presentes,
                "taxa_presenca": round(taxa_presenca, 2)
            },
            "financeiro": {
                "receita_listas": float(receita_listas),
                "receita_pdv": float(receita_pdv),
                "receita_total": float(receita_listas + receita_pdv)
            },
            "capacidade": {
                "capacidade_maxima": evento.capacidade_maxima,
                "ocupacao_atual": total_presentes,
                "capacidade_ocupada": round(capacidade_ocupada, 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas do evento {evento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


# ============== AI-POWERED ENDPOINTS ==============

@router.post("/{evento_id}/ai/generate-description")
async def generate_event_description(
    evento_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Gera descrição automática para evento usando IA
    """
    try:
        # Verificar se o evento existe
        evento = await db.get(Evento, evento_id)
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        # Verificar permissões (apenas admin ou criador do evento)
        if not (current_user.is_admin or evento.criado_por == current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para modificar este evento"
            )
        
        # Gerar descrição usando IA
        description = await openai_service.generate_event_description(
            titulo=evento.titulo,
            categoria=evento.categoria,
            data_inicio=evento.data_inicio,
            data_fim=evento.data_fim,
            local=evento.local
        )
        
        return {
            "success": True,
            "description": description,
            "evento_id": evento_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar descrição do evento {evento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar descrição com IA"
        )


@router.post("/{evento_id}/ai/generate-marketing")
async def generate_marketing_copy(
    evento_id: UUID,
    platform: str = Query(..., description="Plataforma (facebook, instagram, linkedin, twitter)"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Gera copy de marketing para evento usando IA
    """
    try:
        # Verificar se o evento existe
        evento = await db.get(Evento, evento_id)
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        # Verificar permissões (apenas admin ou criador do evento)
        if not (current_user.is_admin or evento.criado_por == current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para modificar este evento"
            )
        
        # Validar plataforma
        valid_platforms = ["facebook", "instagram", "linkedin", "twitter"]
        if platform.lower() not in valid_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plataforma deve ser uma de: {', '.join(valid_platforms)}"
            )
        
        # Gerar copy de marketing usando IA
        marketing_copy = await openai_service.generate_marketing_copy(
            titulo=evento.titulo,
            descricao=evento.descricao,
            categoria=evento.categoria,
            data_inicio=evento.data_inicio,
            local=evento.local,
            platform=platform.lower()
        )
        
        return {
            "success": True,
            "marketing_copy": marketing_copy,
            "platform": platform.lower(),
            "evento_id": evento_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar copy de marketing do evento {evento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar copy de marketing com IA"
        )


@router.post("/{evento_id}/ai/analyze-feedback")
async def analyze_event_feedback(
    evento_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Analisa feedback do evento usando IA
    """
    try:
        # Verificar se o evento existe
        evento = await db.get(Evento, evento_id)
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        # Verificar permissões (apenas admin ou criador do evento)
        if not (current_user.is_admin or evento.criado_por == current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para analisar este evento"
            )
        
        # Buscar comentários/feedback do evento
        query = select(ComentarioEvento).where(ComentarioEvento.evento_id == evento_id)
        result = await db.execute(query)
        comentarios = result.scalars().all()
        
        if not comentarios:
            return {
                "success": False,
                "message": "Não há feedback suficiente para análise",
                "evento_id": evento_id
            }
        
        # Preparar textos dos comentários
        feedback_texts = [comentario.comentario for comentario in comentarios]
        
        # Analisar feedback usando IA
        analysis = await openai_service.analyze_event_feedback(feedback_texts)
        
        return {
            "success": True,
            "analysis": analysis,
            "feedback_count": len(comentarios),
            "evento_id": evento_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao analisar feedback do evento {evento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao analisar feedback com IA"
        )


@router.post("/ai/generate-event-ideas")
async def generate_event_ideas(
    categoria: str = Query(..., description="Categoria do evento"),
    target_audience: str = Query(..., description="Público-alvo"),
    budget_range: str = Query(..., description="Faixa de orçamento (baixo, medio, alto)"),
    current_user=Depends(get_current_user),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Gera ideias de eventos usando IA
    """
    try:
        # Verificar permissões (apenas admin pode gerar ideias)
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem gerar ideias de eventos"
            )
        
        # Validar faixa de orçamento
        valid_budgets = ["baixo", "medio", "alto"]
        if budget_range.lower() not in valid_budgets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Faixa de orçamento deve ser uma de: {', '.join(valid_budgets)}"
            )
        
        # Gerar ideias usando IA
        ideas = await openai_service.generate_event_ideas(
            categoria=categoria,
            target_audience=target_audience,
            budget_range=budget_range.lower()
        )
        
        return {
            "success": True,
            "ideas": ideas,
            "categoria": categoria,
            "target_audience": target_audience,
            "budget_range": budget_range.lower()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar ideias de eventos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar ideias com IA"
        )


@router.get("/system/status")
async def get_system_status():
    """
    Endpoint para verificar status do sistema e serviços
    """
    try:
        status_info = {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "eventos_router": "ok",
                "database": "ok",
                "openai": "pending"
            },
            "version": "2.0.0",
            "features": [
                "eventos_crud",
                "ai_integration",
                "estoque_management",
                "gamification",
                "pdv_system"
            ]
        }
        
        # Testar serviço OpenAI
        try:
            from app.services.openai_service import OpenAIService
            openai_service = OpenAIService()
            status_info["services"]["openai"] = "ok"
        except Exception as e:
            status_info["services"]["openai"] = f"error: {str(e)}"
        
        return status_info
        
    except Exception as e:
        logger.error(f"Erro ao verificar status do sistema: {e}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
