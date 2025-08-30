"""
Router PDV (Ponto de Venda) - Sistema completo de vendas
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc, or_
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
import logging

from app.database import get_db
from app.models import (
    Produto, Venda, ItemVenda, Usuario, Evento, EstoqueProduto,
    StatusVenda, TipoUsuario, MovimentacaoEstoque, TipoMovimentacao
)
from app.schemas import (
    Produto as ProdutoSchema, ProdutoCreate, ProdutoUpdate,
    Venda as VendaSchema, VendaCreate, ItemVendaCreate,
    EstoqueProduto as EstoqueSchema, MovimentacaoEstoque as MovimentacaoSchema,
    PaginatedResponse, ResponseSuccess, DashboardPDV
)
from app.auth import (
    get_current_active_user, get_current_operador_user,
    verificar_acesso_evento, log_user_action
)
from app.websocket import event_notifier
from app.utils.image_uploader import upload_image, delete_image

logger = logging.getLogger(__name__)
router = APIRouter()

# =============================================================================
# ENDPOINTS DE PRODUTOS
# =============================================================================

@router.post("/produtos", response_model=ProdutoSchema, summary="Criar produto")
async def create_produto(
    produto_data: ProdutoCreate,
    request: Request,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo produto
    
    - **nome**: Nome do produto
    - **descricao**: Descrição detalhada
    - **preco**: Preço unitário
    - **categoria**: Categoria do produto
    - **codigo_barras**: Código de barras (opcional)
    - **ativo**: Se o produto está ativo para venda
    """
    try:
        # Verificar permissões
        if current_user.tipo not in [TipoUsuario.ADMIN, TipoUsuario.ORGANIZADOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores e organizadores podem criar produtos"
            )
        
        # Verificar se código de barras já existe
        if produto_data.codigo_barras:
            produto_existente = db.query(Produto).filter(
                and_(
                    Produto.codigo_barras == produto_data.codigo_barras,
                    Produto.empresa_id == current_user.empresa_id
                )
            ).first()
            
            if produto_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código de barras já cadastrado"
                )
        
        # Criar produto
        db_produto = Produto(
            nome=produto_data.nome,
            descricao=produto_data.descricao,
            preco=produto_data.preco,
            categoria=produto_data.categoria,
            codigo_barras=produto_data.codigo_barras,
            ativo=produto_data.ativo,
            empresa_id=current_user.empresa_id,
            criado_por_id=current_user.id
        )
        
        db.add(db_produto)
        db.commit()
        db.refresh(db_produto)
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=current_user,
            action="CREATE_PRODUTO",
            table_name="produtos",
            record_id=db_produto.id,
            new_data={
                "nome": produto_data.nome,
                "preco": float(produto_data.preco),
                "categoria": produto_data.categoria
            },
            request=request,
            details=f"Criação do produto {produto_data.nome}"
        )
        
        logger.info(f"Produto criado por {current_user.email}: {produto_data.nome}")
        
        return ProdutoSchema.from_orm(db_produto)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar produto: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.get("/produtos", response_model=PaginatedResponse, summary="Listar produtos")
async def list_produtos(
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    search: Optional[str] = Query(None, description="Buscar por nome ou código"),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lista produtos com filtros e paginação
    """
    try:
        # Query base
        query = db.query(Produto).filter(Produto.empresa_id == current_user.empresa_id)
        
        # Aplicar filtros
        if categoria:
            query = query.filter(Produto.categoria == categoria)
        
        if ativo is not None:
            query = query.filter(Produto.ativo == ativo)
        
        if search:
            query = query.filter(
                or_(
                    Produto.nome.ilike(f"%{search}%"),
                    Produto.codigo_barras.ilike(f"%{search}%")
                )
            )
        
        # Ordenação
        query = query.order_by(Produto.nome)
        
        # Contagem total
        total = query.count()
        
        # Paginação
        offset = (page - 1) * size
        produtos = query.offset(offset).limit(size).all()
        
        # Calcular metadados da paginação
        pages = (total + size - 1) // size
        has_next = page < pages
        has_prev = page > 1
        
        return PaginatedResponse(
            items=[ProdutoSchema.from_orm(produto) for produto in produtos],
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.get("/produtos/{produto_id}", response_model=ProdutoSchema, summary="Obter produto")
async def get_produto(
    produto_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes de um produto específico
    """
    try:
        produto = db.query(Produto).filter(
            and_(
                Produto.id == produto_id,
                Produto.empresa_id == current_user.empresa_id
            )
        ).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        return ProdutoSchema.from_orm(produto)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar produto {produto_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.put("/produtos/{produto_id}", response_model=ProdutoSchema, summary="Atualizar produto")
async def update_produto(
    produto_id: int,
    produto_data: ProdutoUpdate,
    request: Request,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza um produto existente
    """
    try:
        # Verificar permissões
        if current_user.tipo not in [TipoUsuario.ADMIN, TipoUsuario.ORGANIZADOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores e organizadores podem atualizar produtos"
            )
        
        # Buscar produto
        produto = db.query(Produto).filter(
            and_(
                Produto.id == produto_id,
                Produto.empresa_id == current_user.empresa_id
            )
        ).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Dados originais para auditoria
        old_data = {
            "nome": produto.nome,
            "preco": float(produto.preco),
            "categoria": produto.categoria,
            "ativo": produto.ativo
        }
        
        # Atualizar campos
        update_data = produto_data.dict(exclude_unset=True)
        
        # Verificar código de barras duplicado
        if "codigo_barras" in update_data and update_data["codigo_barras"]:
            produto_existente = db.query(Produto).filter(
                and_(
                    Produto.codigo_barras == update_data["codigo_barras"],
                    Produto.empresa_id == current_user.empresa_id,
                    Produto.id != produto_id
                )
            ).first()
            
            if produto_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código de barras já cadastrado"
                )
        
        for field, value in update_data.items():
            setattr(produto, field, value)
        
        produto.atualizado_em = datetime.utcnow()
        
        db.commit()
        db.refresh(produto)
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=current_user,
            action="UPDATE_PRODUTO",
            table_name="produtos",
            record_id=produto.id,
            old_data=old_data,
            new_data=update_data,
            request=request,
            details=f"Atualização do produto {produto.nome}"
        )
        
        logger.info(f"Produto atualizado por {current_user.email}: {produto.nome}")
        
        return ProdutoSchema.from_orm(produto)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar produto {produto_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

# =============================================================================
# ENDPOINTS DE ESTOQUE
# =============================================================================

@router.get("/estoque/evento/{evento_id}", response_model=List[EstoqueSchema], summary="Estoque por evento")
async def get_estoque_evento(
    evento_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtém estoque de produtos para um evento
    """
    try:
        # Verificar acesso ao evento
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        if not verificar_acesso_evento(current_user, evento.empresa_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este evento"
            )
        
        # Buscar estoque
        estoque = db.query(EstoqueProduto).options(
            joinedload(EstoqueProduto.produto)
        ).filter(
            EstoqueProduto.evento_id == evento_id
        ).all()
        
        return [EstoqueSchema.from_orm(item) for item in estoque]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar estoque do evento {evento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.post("/estoque/evento/{evento_id}/produto/{produto_id}", response_model=EstoqueSchema, summary="Adicionar ao estoque")
async def add_produto_estoque(
    evento_id: int,
    produto_id: int,
    quantidade: int = Query(..., ge=1, description="Quantidade a adicionar"),
    request: Request,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Adiciona produto ao estoque de um evento
    """
    try:
        # Verificar permissões
        if current_user.tipo not in [TipoUsuario.ADMIN, TipoUsuario.ORGANIZADOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores e organizadores podem gerenciar estoque"
            )
        
        # Verificar evento e produto
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        produto = db.query(Produto).filter(
            and_(
                Produto.id == produto_id,
                Produto.empresa_id == current_user.empresa_id
            )
        ).first()
        
        if not evento or not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento ou produto não encontrado"
            )
        
        if not verificar_acesso_evento(current_user, evento.empresa_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este evento"
            )
        
        # Buscar ou criar item de estoque
        estoque = db.query(EstoqueProduto).filter(
            and_(
                EstoqueProduto.evento_id == evento_id,
                EstoqueProduto.produto_id == produto_id
            )
        ).first()
        
        if estoque:
            # Atualizar quantidade
            quantidade_anterior = estoque.quantidade_disponivel
            estoque.quantidade_disponivel += quantidade
            estoque.atualizado_em = datetime.utcnow()
        else:
            # Criar novo item
            quantidade_anterior = 0
            estoque = EstoqueProduto(
                evento_id=evento_id,
                produto_id=produto_id,
                quantidade_disponivel=quantidade
            )
            db.add(estoque)
        
        db.commit()
        db.refresh(estoque)
        
        # Registrar movimentação
        movimentacao = MovimentacaoEstoque(
            estoque_id=estoque.id,
            tipo=TipoMovimentacao.ENTRADA,
            quantidade=quantidade,
            motivo=f"Adição manual ao estoque",
            usuario_id=current_user.id
        )
        db.add(movimentacao)
        db.commit()
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=current_user,
            action="ADD_ESTOQUE",
            table_name="estoque_produtos",
            record_id=estoque.id,
            new_data={
                "evento_id": evento_id,
                "produto_id": produto_id,
                "quantidade_anterior": quantidade_anterior,
                "quantidade_adicionada": quantidade,
                "quantidade_atual": estoque.quantidade_disponivel
            },
            request=request,
            details=f"Adição de {quantidade} unidades do produto {produto.nome} ao estoque"
        )
        
        logger.info(f"Estoque atualizado por {current_user.email}: +{quantidade} {produto.nome}")
        
        return EstoqueSchema.from_orm(estoque)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar produto ao estoque: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

# =============================================================================
# ENDPOINTS DE VENDAS
# =============================================================================

@router.post("/vendas", response_model=VendaSchema, summary="Realizar venda")
async def create_venda(
    venda_data: VendaCreate,
    request: Request,
    current_user: Usuario = Depends(get_current_operador_user),
    db: Session = Depends(get_db)
):
    """
    Realiza uma nova venda
    
    - **evento_id**: ID do evento
    - **itens**: Lista de itens da venda
    - **desconto**: Desconto aplicado (opcional)
    - **observacoes**: Observações da venda (opcional)
    """
    try:
        # Verificar evento
        evento = db.query(Evento).filter(Evento.id == venda_data.evento_id).first()
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        if not verificar_acesso_evento(current_user, evento.empresa_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este evento"
            )
        
        # Validar itens e calcular total
        total_venda = Decimal('0.00')
        itens_validados = []
        
        for item_data in venda_data.itens:
            # Buscar produto
            produto = db.query(Produto).filter(
                and_(
                    Produto.id == item_data.produto_id,
                    Produto.empresa_id == current_user.empresa_id,
                    Produto.ativo == True
                )
            ).first()
            
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Produto ID {item_data.produto_id} não encontrado ou inativo"
                )
            
            # Verificar estoque
            estoque = db.query(EstoqueProduto).filter(
                and_(
                    EstoqueProduto.evento_id == venda_data.evento_id,
                    EstoqueProduto.produto_id == item_data.produto_id
                )
            ).first()
            
            if not estoque or estoque.quantidade_disponivel < item_data.quantidade:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente para o produto {produto.nome}"
                )
            
            # Calcular valor do item
            valor_unitario = produto.preco
            valor_total_item = valor_unitario * item_data.quantidade
            total_venda += valor_total_item
            
            itens_validados.append({
                "produto": produto,
                "estoque": estoque,
                "quantidade": item_data.quantidade,
                "valor_unitario": valor_unitario,
                "valor_total": valor_total_item
            })
        
        # Aplicar desconto
        if venda_data.desconto:
            total_venda -= venda_data.desconto
            if total_venda < 0:
                total_venda = Decimal('0.00')
        
        # Criar venda
        db_venda = Venda(
            evento_id=venda_data.evento_id,
            usuario_id=current_user.id,
            valor_total=total_venda,
            desconto=venda_data.desconto or Decimal('0.00'),
            status=StatusVenda.CONCLUIDA,
            observacoes=venda_data.observacoes
        )
        
        db.add(db_venda)
        db.flush()  # Para obter o ID da venda
        
        # Criar itens da venda e atualizar estoque
        for item_validado in itens_validados:
            # Criar item da venda
            item_venda = ItemVenda(
                venda_id=db_venda.id,
                produto_id=item_validado["produto"].id,
                quantidade=item_validado["quantidade"],
                valor_unitario=item_validado["valor_unitario"],
                valor_total=item_validado["valor_total"]
            )
            db.add(item_venda)
            
            # Atualizar estoque
            estoque = item_validado["estoque"]
            estoque.quantidade_disponivel -= item_validado["quantidade"]
            
            # Registrar movimentação de estoque
            movimentacao = MovimentacaoEstoque(
                estoque_id=estoque.id,
                tipo=TipoMovimentacao.SAIDA,
                quantidade=item_validado["quantidade"],
                motivo=f"Venda #{db_venda.id}",
                usuario_id=current_user.id,
                venda_id=db_venda.id
            )
            db.add(movimentacao)
        
        db.commit()
        db.refresh(db_venda)
        
        # Notificar via WebSocket
        await event_notifier.notify_new_sale(
            evento_id=evento.id,
            sale_data={
                "id": db_venda.id,
                "valor_total": float(db_venda.valor_total),
                "itens_count": len(itens_validados),
                "usuario": current_user.nome,
                "timestamp": db_venda.criado_em.isoformat()
            }
        )
        
        # Log de auditoria
        log_user_action(
            db=db,
            user=current_user,
            action="CREATE_VENDA",
            table_name="vendas",
            record_id=db_venda.id,
            new_data={
                "evento_id": venda_data.evento_id,
                "valor_total": float(total_venda),
                "itens_count": len(itens_validados)
            },
            request=request,
            details=f"Venda realizada no evento {evento.nome}"
        )
        
        logger.info(f"Venda realizada por {current_user.email}: R$ {total_venda} no evento {evento.nome}")
        
        return VendaSchema.from_orm(db_venda)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao realizar venda: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

@router.get("/vendas/evento/{evento_id}", response_model=PaginatedResponse, summary="Vendas por evento")
async def get_vendas_evento(
    evento_id: int,
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    data_inicio: Optional[date] = Query(None, description="Data início"),
    data_fim: Optional[date] = Query(None, description="Data fim"),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lista vendas de um evento com filtros e paginação
    """
    try:
        # Verificar evento
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        if not verificar_acesso_evento(current_user, evento.empresa_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este evento"
            )
        
        # Query base
        query = db.query(Venda).options(
            joinedload(Venda.usuario),
            joinedload(Venda.itens).joinedload(ItemVenda.produto)
        ).filter(Venda.evento_id == evento_id)
        
        # Aplicar filtros de data
        if data_inicio:
            query = query.filter(func.date(Venda.criado_em) >= data_inicio)
        
        if data_fim:
            query = query.filter(func.date(Venda.criado_em) <= data_fim)
        
        # Ordenação por data mais recente
        query = query.order_by(desc(Venda.criado_em))
        
        # Contagem total
        total = query.count()
        
        # Paginação
        offset = (page - 1) * size
        vendas = query.offset(offset).limit(size).all()
        
        # Calcular metadados da paginação
        pages = (total + size - 1) // size
        has_next = page < pages
        has_prev = page > 1
        
        return PaginatedResponse(
            items=[VendaSchema.from_orm(venda) for venda in vendas],
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar vendas do evento {evento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )

# =============================================================================
# DASHBOARD PDV
# =============================================================================

@router.get("/dashboard/evento/{evento_id}", summary="Dashboard PDV")
async def get_dashboard_pdv(
    evento_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard completo do PDV para um evento
    """
    try:
        # Verificar evento
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        if not verificar_acesso_evento(current_user, evento.empresa_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este evento"
            )
        
        # Estatísticas de vendas
        vendas_hoje = db.query(func.count(Venda.id), func.sum(Venda.valor_total)).filter(
            and_(
                Venda.evento_id == evento_id,
                func.date(Venda.criado_em) == date.today()
            )
        ).first()
        
        total_vendas = db.query(func.count(Venda.id), func.sum(Venda.valor_total)).filter(
            Venda.evento_id == evento_id
        ).first()
        
        # Produtos mais vendidos
        produtos_top = db.query(
            Produto.nome,
            func.sum(ItemVenda.quantidade).label('total_vendido'),
            func.sum(ItemVenda.valor_total).label('receita')
        ).join(ItemVenda).join(Venda).filter(
            Venda.evento_id == evento_id
        ).group_by(Produto.id, Produto.nome).order_by(
            desc(func.sum(ItemVenda.quantidade))
        ).limit(5).all()
        
        # Vendas por hora (hoje)
        vendas_por_hora = db.query(
            func.extract('hour', Venda.criado_em).label('hora'),
            func.count(Venda.id).label('vendas'),
            func.sum(Venda.valor_total).label('receita')
        ).filter(
            and_(
                Venda.evento_id == evento_id,
                func.date(Venda.criado_em) == date.today()
            )
        ).group_by(func.extract('hour', Venda.criado_em)).all()
        
        # Produtos com estoque baixo
        estoque_baixo = db.query(EstoqueProduto).options(
            joinedload(EstoqueProduto.produto)
        ).filter(
            and_(
                EstoqueProduto.evento_id == evento_id,
                EstoqueProduto.quantidade_disponivel <= 5
            )
        ).all()
        
        return {
            "evento_id": evento_id,
            "nome_evento": evento.nome,
            "resumo_vendas": {
                "vendas_hoje": vendas_hoje[0] or 0,
                "receita_hoje": float(vendas_hoje[1] or 0),
                "total_vendas": total_vendas[0] or 0,
                "receita_total": float(total_vendas[1] or 0)
            },
            "produtos_top": [
                {
                    "nome": nome,
                    "total_vendido": int(total_vendido),
                    "receita": float(receita)
                }
                for nome, total_vendido, receita in produtos_top
            ],
            "vendas_por_hora": [
                {
                    "hora": int(hora),
                    "vendas": int(vendas),
                    "receita": float(receita)
                }
                for hora, vendas, receita in vendas_por_hora
            ],
            "estoque_baixo": [
                {
                    "produto_id": item.produto_id,
                    "nome": item.produto.nome,
                    "quantidade_disponivel": item.quantidade_disponivel
                }
                for item in estoque_baixo
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard PDV do evento {evento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )