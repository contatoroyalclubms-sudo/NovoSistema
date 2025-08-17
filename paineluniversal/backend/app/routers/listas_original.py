from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from ..database import get_db
from ..models import (
    Usuario, Evento, Lista, Transacao, TipoLista, TipoUsuario,
    PromoterEvento, Cupom
)
from ..schemas import (
    ListaCreate, ListaUpdate, ListaResponse, ListaDetalhada,
    ConvidadoLista, RelatorioLista
)
from ..auth import obter_usuario_atual
from ..utils.cpf_validator import validar_cpf, formatar_cpf

router = APIRouter(prefix="/listas", tags=["Listas"])

@router.post("/", response_model=ListaResponse)
async def criar_lista(
    lista: ListaCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Criar nova lista"""
    
    # Verificar se evento existe e usuário tem acesso
    evento = db.query(Evento).filter(Evento.id == lista.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Verificar permissões
    if usuario_atual.tipo.value not in ["admin", "promoter"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    if (usuario_atual.tipo.value != "admin" and 
        evento.empresa_id != usuario_atual.empresa_id):
        raise HTTPException(status_code=403, detail="Evento não pertence à sua empresa")
    
    # Se for promoter, verificar se está associado ao evento
    if usuario_atual.tipo.value == "promoter":
        associacao = db.query(PromoterEvento).filter(
            PromoterEvento.promoter_id == usuario_atual.id,
            PromoterEvento.evento_id == lista.evento_id
        ).first()
        
        if not associacao:
            raise HTTPException(
                status_code=403, 
                detail="Promoter não está associado a este evento"
            )
    
    # Validações
    if lista.preco < 0:
        raise HTTPException(status_code=400, detail="Preço não pode ser negativo")
    
    if lista.limite_vendas and lista.limite_vendas < 1:
        raise HTTPException(status_code=400, detail="Limite de vendas deve ser maior que zero")
    
    # Verificar se já existe lista com mesmo nome para o evento
    lista_existente = db.query(Lista).filter(
        Lista.evento_id == lista.evento_id,
        Lista.nome == lista.nome
    ).first()
    
    if lista_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe uma lista com este nome para este evento"
        )
    
    # Gerar código cupom único se for tipo cupom
    codigo_cupom = None
    if lista.tipo == TipoLista.CUPOM and not lista.codigo_cupom:
        import uuid
        codigo_cupom = f"CUP{str(uuid.uuid4())[:8].upper()}"
    elif lista.codigo_cupom:
        # Verificar se código não existe
        cupom_existente = db.query(Lista).filter(
            Lista.evento_id == lista.evento_id,
            Lista.codigo_cupom == lista.codigo_cupom
        ).first()
        
        if cupom_existente:
            raise HTTPException(
                status_code=400,
                detail="Código de cupom já existe para este evento"
            )
        codigo_cupom = lista.codigo_cupom
    
    # Criar lista
    db_lista = Lista(
        nome=lista.nome,
        tipo=lista.tipo,
        preco=lista.preco,
        limite_vendas=lista.limite_vendas,
        descricao=lista.descricao,
        codigo_cupom=codigo_cupom,
        desconto_percentual=lista.desconto_percentual,
        evento_id=lista.evento_id,
        promoter_id=usuario_atual.id if usuario_atual.tipo.value == "promoter" else lista.promoter_id
    )
    
    db.add(db_lista)
    db.commit()
    db.refresh(db_lista)
    
    return ListaResponse(
        id=db_lista.id,
        nome=db_lista.nome,
        tipo=db_lista.tipo.value,
        preco=float(db_lista.preco),
        limite_vendas=db_lista.limite_vendas,
        vendas_realizadas=db_lista.vendas_realizadas,
        ativa=db_lista.ativa,
        evento_id=db_lista.evento_id,
        evento_nome=evento.nome,
        promoter_id=db_lista.promoter_id,
        promoter_nome=db_lista.promoter.nome if db_lista.promoter else None,
        descricao=db_lista.descricao,
        codigo_cupom=db_lista.codigo_cupom,
        desconto_percentual=float(db_lista.desconto_percentual or 0),
        criado_em=db_lista.criado_em
    )

@router.get("/", response_model=List[ListaResponse])
async def listar_listas(
    evento_id: Optional[int] = None,
    tipo: Optional[str] = None,
    ativa: Optional[bool] = None,
    promoter_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar listas com filtros"""
    
    query = db.query(Lista).join(Evento)
    
    # Filtro de acesso
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    # Se for promoter, mostrar apenas suas listas
    if usuario_atual.tipo.value == "promoter":
        query = query.filter(Lista.promoter_id == usuario_atual.id)
    
    # Aplicar filtros
    if evento_id:
        query = query.filter(Lista.evento_id == evento_id)
    
    if tipo:
        query = query.filter(Lista.tipo == tipo)
    
    if ativa is not None:
        query = query.filter(Lista.ativa == ativa)
    
    if promoter_id:
        query = query.filter(Lista.promoter_id == promoter_id)
    
    listas = query.order_by(desc(Lista.criado_em)).offset(skip).limit(limit).all()
    
    return [ListaResponse(
        id=l.id,
        nome=l.nome,
        tipo=l.tipo.value,
        preco=float(l.preco),
        limite_vendas=l.limite_vendas,
        vendas_realizadas=l.vendas_realizadas,
        ativa=l.ativa,
        evento_id=l.evento_id,
        evento_nome=l.evento.nome,
        promoter_id=l.promoter_id,
        promoter_nome=l.promoter.nome if l.promoter else None,
        descricao=l.descricao,
        codigo_cupom=l.codigo_cupom,
        desconto_percentual=float(l.desconto_percentual or 0),
        criado_em=l.criado_em
    ) for l in listas]

@router.get("/{lista_id}", response_model=ListaDetalhada)
async def obter_lista(
    lista_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter detalhes de uma lista"""
    
    query = db.query(Lista).join(Evento)
    
    # Filtro de acesso
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    # Se for promoter, verificar se é sua lista
    if usuario_atual.tipo.value == "promoter":
        query = query.filter(Lista.promoter_id == usuario_atual.id)
    
    lista = query.filter(Lista.id == lista_id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    # Estatísticas da lista
    vendas_lista = db.query(Transacao).filter(
        Transacao.lista_id == lista_id,
        Transacao.status == "aprovada"
    ).all()
    
    receita_total = sum(venda.valor for venda in vendas_lista)
    
    # Vendas por dia (últimos 30 dias)
    trinta_dias_atras = datetime.now() - timedelta(days=30)
    vendas_por_dia = db.query(
        func.date(Transacao.criado_em).label('data'),
        func.count(Transacao.id).label('quantidade'),
        func.sum(Transacao.valor).label('receita')
    ).filter(
        Transacao.lista_id == lista_id,
        Transacao.status == "aprovada",
        Transacao.criado_em >= trinta_dias_atras
    ).group_by(
        func.date(Transacao.criado_em)
    ).all()
    
    vendas_diarias = {
        str(v.data): {
            "quantidade": v.quantidade,
            "receita": float(v.receita)
        }
        for v in vendas_por_dia
    }
    
    # Top compradores
    top_compradores = db.query(
        Transacao.cpf_comprador,
        Transacao.nome_comprador,
        func.count(Transacao.id).label('total_compras'),
        func.sum(Transacao.valor).label('valor_total')
    ).filter(
        Transacao.lista_id == lista_id,
        Transacao.status == "aprovada"
    ).group_by(
        Transacao.cpf_comprador, Transacao.nome_comprador
    ).order_by(
        desc('total_compras')
    ).limit(10).all()
    
    compradores = [
        {
            "cpf": c.cpf_comprador,
            "nome": c.nome_comprador,
            "total_compras": c.total_compras,
            "valor_total": float(c.valor_total)
        }
        for c in top_compradores
    ]
    
    return ListaDetalhada(
        id=lista.id,
        nome=lista.nome,
        tipo=lista.tipo.value,
        preco=float(lista.preco),
        limite_vendas=lista.limite_vendas,
        vendas_realizadas=lista.vendas_realizadas,
        ativa=lista.ativa,
        evento_id=lista.evento_id,
        evento_nome=lista.evento.nome,
        promoter_id=lista.promoter_id,
        promoter_nome=lista.promoter.nome if lista.promoter else None,
        descricao=lista.descricao,
        codigo_cupom=lista.codigo_cupom,
        desconto_percentual=float(lista.desconto_percentual or 0),
        criado_em=lista.criado_em,
        receita_total=float(receita_total),
        ticket_medio=float(receita_total / len(vendas_lista)) if vendas_lista else 0,
        vendas_por_dia=vendas_diarias,
        top_compradores=compradores,
        disponivel_venda=lista.ativa and (
            not lista.limite_vendas or lista.vendas_realizadas < lista.limite_vendas
        )
    )

@router.put("/{lista_id}", response_model=ListaResponse)
async def atualizar_lista(
    lista_id: int,
    lista_update: ListaUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar lista"""
    
    query = db.query(Lista).join(Evento)
    
    # Filtro de acesso
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    # Se for promoter, verificar se é sua lista
    if usuario_atual.tipo.value == "promoter":
        query = query.filter(Lista.promoter_id == usuario_atual.id)
    
    lista = query.filter(Lista.id == lista_id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    # Validações
    if lista_update.preco is not None and lista_update.preco < 0:
        raise HTTPException(status_code=400, detail="Preço não pode ser negativo")
    
    if (lista_update.limite_vendas is not None and 
        lista_update.limite_vendas < lista.vendas_realizadas):
        raise HTTPException(
            status_code=400,
            detail=f"Limite não pode ser menor que vendas já realizadas ({lista.vendas_realizadas})"
        )
    
    # Verificar código cupom se fornecido
    if lista_update.codigo_cupom:
        cupom_existente = db.query(Lista).filter(
            Lista.evento_id == lista.evento_id,
            Lista.codigo_cupom == lista_update.codigo_cupom,
            Lista.id != lista_id
        ).first()
        
        if cupom_existente:
            raise HTTPException(
                status_code=400,
                detail="Código de cupom já existe para este evento"
            )
    
    # Atualizar campos
    for field, value in lista_update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(lista, field, value)
    
    db.commit()
    db.refresh(lista)
    
    return ListaResponse(
        id=lista.id,
        nome=lista.nome,
        tipo=lista.tipo.value,
        preco=float(lista.preco),
        limite_vendas=lista.limite_vendas,
        vendas_realizadas=lista.vendas_realizadas,
        ativa=lista.ativa,
        evento_id=lista.evento_id,
        evento_nome=lista.evento.nome,
        promoter_id=lista.promoter_id,
        promoter_nome=lista.promoter.nome if lista.promoter else None,
        descricao=lista.descricao,
        codigo_cupom=lista.codigo_cupom,
        desconto_percentual=float(lista.desconto_percentual or 0),
        criado_em=lista.criado_em
    )

@router.post("/{lista_id}/toggle-ativa")
async def toggle_ativa_lista(
    lista_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Ativar/desativar lista"""
    
    query = db.query(Lista).join(Evento)
    
    # Filtro de acesso
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    # Se for promoter, verificar se é sua lista
    if usuario_atual.tipo.value == "promoter":
        query = query.filter(Lista.promoter_id == usuario_atual.id)
    
    lista = query.filter(Lista.id == lista_id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    lista.ativa = not lista.ativa
    db.commit()
    
    status_texto = "ativada" if lista.ativa else "desativada"
    return {"mensagem": f"Lista {status_texto} com sucesso"}

@router.get("/{lista_id}/convidados", response_model=List[ConvidadoLista])
async def listar_convidados_lista(
    lista_id: int,
    skip: int = 0,
    limit: int = 100,
    busca: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar convidados/compradores de uma lista"""
    
    # Verificar acesso à lista
    query_lista = db.query(Lista).join(Evento)
    
    if usuario_atual.tipo.value != "admin":
        query_lista = query_lista.filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    if usuario_atual.tipo.value == "promoter":
        query_lista = query_lista.filter(Lista.promoter_id == usuario_atual.id)
    
    lista = query_lista.filter(Lista.id == lista_id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    # Buscar compradores da lista
    query = db.query(Transacao).filter(
        Transacao.lista_id == lista_id,
        Transacao.status == "aprovada"
    )
    
    if busca:
        query = query.filter(
            or_(
                Transacao.nome_comprador.ilike(f"%{busca}%"),
                Transacao.cpf_comprador.ilike(f"%{busca}%"),
                Transacao.email_comprador.ilike(f"%{busca}%")
            )
        )
    
    transacoes = query.order_by(desc(Transacao.criado_em)).offset(skip).limit(limit).all()
    
    return [ConvidadoLista(
        cpf=t.cpf_comprador,
        nome=t.nome_comprador,
        email=t.email_comprador,
        telefone=t.telefone_comprador,
        valor_pago=float(t.valor),
        data_compra=t.criado_em,
        metodo_pagamento=t.metodo_pagamento,
        codigo_transacao=t.codigo_transacao,
        status="presente" if any(c.cpf == t.cpf_comprador for c in lista.evento.checkins) else "ausente"
    ) for t in transacoes]

@router.post("/{lista_id}/duplicar", response_model=ListaResponse)
async def duplicar_lista(
    lista_id: int,
    novo_nome: str,
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Duplicar lista para outro evento ou mesmo evento"""
    
    # Verificar acesso à lista original
    query_lista = db.query(Lista).join(Evento)
    
    if usuario_atual.tipo.value != "admin":
        query_lista = query_lista.filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    if usuario_atual.tipo.value == "promoter":
        query_lista = query_lista.filter(Lista.promoter_id == usuario_atual.id)
    
    lista_original = query_lista.filter(Lista.id == lista_id).first()
    if not lista_original:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    # Definir evento destino
    evento_destino_id = evento_id or lista_original.evento_id
    
    # Verificar acesso ao evento destino
    evento_destino = db.query(Evento).filter(Evento.id == evento_destino_id).first()
    if not evento_destino:
        raise HTTPException(status_code=404, detail="Evento destino não encontrado")
    
    if (usuario_atual.tipo.value != "admin" and 
        evento_destino.empresa_id != usuario_atual.empresa_id):
        raise HTTPException(status_code=403, detail="Evento destino não pertence à sua empresa")
    
    # Verificar se nome já existe no evento destino
    lista_existente = db.query(Lista).filter(
        Lista.evento_id == evento_destino_id,
        Lista.nome == novo_nome
    ).first()
    
    if lista_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe uma lista com este nome no evento destino"
        )
    
    # Criar nova lista
    nova_lista = Lista(
        nome=novo_nome,
        tipo=lista_original.tipo,
        preco=lista_original.preco,
        limite_vendas=lista_original.limite_vendas,
        descricao=f"Duplicada de: {lista_original.nome}",
        desconto_percentual=lista_original.desconto_percentual,
        evento_id=evento_destino_id,
        promoter_id=lista_original.promoter_id
    )
    
    # Gerar novo código cupom se necessário
    if lista_original.codigo_cupom:
        import uuid
        nova_lista.codigo_cupom = f"CUP{str(uuid.uuid4())[:8].upper()}"
    
    db.add(nova_lista)
    db.commit()
    db.refresh(nova_lista)
    
    return ListaResponse(
        id=nova_lista.id,
        nome=nova_lista.nome,
        tipo=nova_lista.tipo.value,
        preco=float(nova_lista.preco),
        limite_vendas=nova_lista.limite_vendas,
        vendas_realizadas=nova_lista.vendas_realizadas,
        ativa=nova_lista.ativa,
        evento_id=nova_lista.evento_id,
        evento_nome=evento_destino.nome,
        promoter_id=nova_lista.promoter_id,
        promoter_nome=nova_lista.promoter.nome if nova_lista.promoter else None,
        descricao=nova_lista.descricao,
        codigo_cupom=nova_lista.codigo_cupom,
        desconto_percentual=float(nova_lista.desconto_percentual or 0),
        criado_em=nova_lista.criado_em
    )

@router.get("/{lista_id}/relatorio", response_model=RelatorioLista)
async def gerar_relatorio_lista(
    lista_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Gerar relatório completo da lista"""
    
    # Verificar acesso
    query_lista = db.query(Lista).join(Evento)
    
    if usuario_atual.tipo.value != "admin":
        query_lista = query_lista.filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    if usuario_atual.tipo.value == "promoter":
        query_lista = query_lista.filter(Lista.promoter_id == usuario_atual.id)
    
    lista = query_lista.filter(Lista.id == lista_id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    # Vendas da lista
    vendas = db.query(Transacao).filter(
        Transacao.lista_id == lista_id,
        Transacao.status == "aprovada"
    ).all()
    
    total_vendas = len(vendas)
    receita_total = sum(venda.valor for venda in vendas)
    
    # Métodos de pagamento
    vendas_por_metodo = {}
    for venda in vendas:
        metodo = venda.metodo_pagamento
        if metodo not in vendas_por_metodo:
            vendas_por_metodo[metodo] = {"quantidade": 0, "valor": 0}
        vendas_por_metodo[metodo]["quantidade"] += 1
        vendas_por_metodo[metodo]["valor"] += float(venda.valor)
    
    # Taxa de conversão (se tiver cupom)
    taxa_conversao = 0
    if lista.codigo_cupom:
        # Calcular baseado em tentativas vs sucessos
        # Por simplicidade, usar vendas realizadas vs limite
        if lista.limite_vendas:
            taxa_conversao = (total_vendas / lista.limite_vendas) * 100
    
    # Performance vs outras listas do evento
    outras_listas = db.query(Lista).filter(
        Lista.evento_id == lista.evento_id,
        Lista.id != lista_id
    ).all()
    
    ranking_evento = []
    for l in [lista] + outras_listas:
        vendas_lista = db.query(func.count(Transacao.id)).filter(
            Transacao.lista_id == l.id,
            Transacao.status == "aprovada"
        ).scalar() or 0
        
        receita_lista = db.query(func.sum(Transacao.valor)).filter(
            Transacao.lista_id == l.id,
            Transacao.status == "aprovada"
        ).scalar() or 0
        
        ranking_evento.append({
            "lista_id": l.id,
            "nome": l.nome,
            "vendas": vendas_lista,
            "receita": float(receita_lista)
        })
    
    ranking_evento.sort(key=lambda x: x["vendas"], reverse=True)
    
    # Encontrar posição da lista atual
    posicao_ranking = next(
        (i + 1 for i, item in enumerate(ranking_evento) if item["lista_id"] == lista_id),
        0
    )
    
    return RelatorioLista(
        lista_id=lista.id,
        nome_lista=lista.nome,
        evento_nome=lista.evento.nome,
        promoter_nome=lista.promoter.nome if lista.promoter else "N/A",
        total_vendas=total_vendas,
        receita_total=float(receita_total),
        ticket_medio=float(receita_total / total_vendas) if total_vendas > 0 else 0,
        limite_vendas=lista.limite_vendas,
        disponibilidade=lista.limite_vendas - total_vendas if lista.limite_vendas else None,
        taxa_ocupacao=round((total_vendas / lista.limite_vendas * 100) if lista.limite_vendas else 0, 2),
        vendas_por_metodo=vendas_por_metodo,
        taxa_conversao=round(taxa_conversao, 2),
        posicao_ranking=posicao_ranking,
        total_listas_evento=len(ranking_evento),
        gerado_em=datetime.now()
    )

@router.post("/validar-cupom")
async def validar_cupom(
    codigo_cupom: str,
    evento_id: int,
    db: Session = Depends(get_db)
):
    """Validar código de cupom"""
    
    # Buscar lista com o código
    lista = db.query(Lista).filter(
        Lista.codigo_cupom == codigo_cupom.upper(),
        Lista.evento_id == evento_id,
        Lista.ativa == True
    ).first()
    
    if not lista:
        raise HTTPException(status_code=404, detail="Cupom não encontrado ou inativo")
    
    # Verificar se ainda tem vendas disponíveis
    if lista.limite_vendas and lista.vendas_realizadas >= lista.limite_vendas:
        raise HTTPException(status_code=400, detail="Cupom esgotado")
    
    return {
        "valido": True,
        "lista_id": lista.id,
        "nome_lista": lista.nome,
        "preco": float(lista.preco),
        "desconto_percentual": float(lista.desconto_percentual or 0),
        "vendas_restantes": (lista.limite_vendas - lista.vendas_realizadas) if lista.limite_vendas else None
    }

@router.get("/cupons/{evento_id}")
async def listar_cupons_evento(
    evento_id: int,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar cupons de um evento"""
    
    # Verificar acesso ao evento
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if (usuario_atual.tipo.value != "admin" and 
        evento.empresa_id != usuario_atual.empresa_id):
        raise HTTPException(status_code=403, detail="Evento não pertence à sua empresa")
    
    query = db.query(Lista).filter(
        Lista.evento_id == evento_id,
        Lista.codigo_cupom.isnot(None)
    )
    
    if ativo is not None:
        query = query.filter(Lista.ativa == ativo)
    
    cupons = query.all()
    
    return [
        {
            "lista_id": c.id,
            "nome": c.nome,
            "codigo_cupom": c.codigo_cupom,
            "preco": float(c.preco),
            "desconto_percentual": float(c.desconto_percentual or 0),
            "limite_vendas": c.limite_vendas,
            "vendas_realizadas": c.vendas_realizadas,
            "ativo": c.ativa,
            "vendas_restantes": (c.limite_vendas - c.vendas_realizadas) if c.limite_vendas else None
        }
        for c in cupons
    ]
