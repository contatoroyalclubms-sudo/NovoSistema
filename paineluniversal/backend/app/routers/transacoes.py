from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from decimal import Decimal
import uuid
import json

from ..database import get_db
from ..models import (
    Usuario, Evento, Lista, Transacao, StatusTransacao, TipoUsuario,
    PromoterEvento, Empresa
)
from ..schemas import (
    TransacaoCreate, TransacaoUpdate, TransacaoResponse, TransacaoDetalhada,
    ProcessarPagamento, EstornarTransacao, RelatorioTransacoes
)
from ..auth import obter_usuario_atual
from ..utils.cpf_validator import validar_cpf, formatar_cpf
from ..services.whatsapp_service import WhatsAppService
from ..websocket import manager

router = APIRouter(prefix="/transacoes", tags=["Transações"])

@router.post("/", response_model=TransacaoResponse)
async def criar_transacao(
    transacao: TransacaoCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Criar nova transação de venda"""
    
    # Validar CPF
    if not validar_cpf(transacao.cpf_comprador):
        raise HTTPException(status_code=400, detail="CPF inválido")
    
    # Verificar se lista existe
    lista = db.query(Lista).filter(Lista.id == transacao.lista_id).first()
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    # Verificar se lista está ativa
    if not lista.ativa:
        raise HTTPException(status_code=400, detail="Lista não está ativa para vendas")
    
    # Verificar acesso ao evento
    evento = lista.evento
    if (usuario_atual.tipo.value != "admin" and 
        evento.empresa_id != usuario_atual.empresa_id):
        raise HTTPException(status_code=403, detail="Evento não pertence à sua empresa")
    
    # Verificar limite de vendas
    if lista.limite_vendas and lista.vendas_realizadas >= lista.limite_vendas:
        raise HTTPException(status_code=400, detail="Lista esgotada")
    
    # Verificar se CPF já comprou desta lista
    transacao_existente = db.query(Transacao).filter(
        Transacao.cpf_comprador == formatar_cpf(transacao.cpf_comprador),
        Transacao.lista_id == transacao.lista_id,
        Transacao.status.in_(["aprovada", "pendente"])
    ).first()
    
    if transacao_existente:
        raise HTTPException(
            status_code=400,
            detail="CPF já possui transação para esta lista"
        )
    
    # Gerar código de transação único
    codigo_transacao = f"TXN{str(uuid.uuid4())[:8].upper()}"
    
    # Calcular valor com desconto se aplicável
    valor_original = lista.preco
    valor_desconto = Decimal(0)
    valor_final = valor_original
    
    if lista.desconto_percentual and lista.desconto_percentual > 0:
        valor_desconto = valor_original * (lista.desconto_percentual / 100)
        valor_final = valor_original - valor_desconto
    
    # Determinar promoter se for o caso
    promoter_id = None
    if usuario_atual.tipo.value == "promoter":
        promoter_id = usuario_atual.id
    elif transacao.promoter_id:
        # Verificar se promoter está associado ao evento
        associacao = db.query(PromoterEvento).filter(
            PromoterEvento.promoter_id == transacao.promoter_id,
            PromoterEvento.evento_id == evento.id
        ).first()
        
        if associacao:
            promoter_id = transacao.promoter_id
    
    # Criar transação
    db_transacao = Transacao(
        codigo_transacao=codigo_transacao,
        cpf_comprador=formatar_cpf(transacao.cpf_comprador),
        nome_comprador=transacao.nome_comprador,
        email_comprador=transacao.email_comprador,
        telefone_comprador=transacao.telefone_comprador,
        valor=valor_final,
        valor_original=valor_original,
        valor_desconto=valor_desconto,
        metodo_pagamento=transacao.metodo_pagamento,
        status=StatusTransacao.PENDENTE,
        lista_id=transacao.lista_id,
        evento_id=evento.id,
        promoter_id=promoter_id,
        observacoes=transacao.observacoes
    )
    
    db.add(db_transacao)
    db.commit()
    db.refresh(db_transacao)
    
    # Adicionar tarefa para notificação
    if db_transacao.telefone_comprador:
        background_tasks.add_task(
            enviar_notificacao_transacao,
            db_transacao.id,
            "criada"
        )
    
    # Notificar via WebSocket
    await manager.broadcast(evento.id, {
        "tipo": "nova_transacao",
        "transacao_id": db_transacao.id,
        "evento_id": evento.id,
        "valor": float(valor_final),
        "promoter": usuario_atual.nome if promoter_id else None
    })
    
    return TransacaoResponse(
        id=db_transacao.id,
        codigo_transacao=db_transacao.codigo_transacao,
        cpf_comprador=db_transacao.cpf_comprador,
        nome_comprador=db_transacao.nome_comprador,
        email_comprador=db_transacao.email_comprador,
        telefone_comprador=db_transacao.telefone_comprador,
        valor=float(db_transacao.valor),
        valor_original=float(db_transacao.valor_original),
        valor_desconto=float(db_transacao.valor_desconto),
        metodo_pagamento=db_transacao.metodo_pagamento,
        status=db_transacao.status.value,
        lista_id=db_transacao.lista_id,
        lista_nome=lista.nome,
        evento_id=db_transacao.evento_id,
        evento_nome=evento.nome,
        promoter_id=db_transacao.promoter_id,
        promoter_nome=db_transacao.promoter.nome if db_transacao.promoter else None,
        observacoes=db_transacao.observacoes,
        criado_em=db_transacao.criado_em,
        atualizado_em=db_transacao.atualizado_em
    )

@router.get("/", response_model=List[TransacaoResponse])
async def listar_transacoes(
    evento_id: Optional[int] = None,
    lista_id: Optional[int] = None,
    promoter_id: Optional[int] = None,
    status: Optional[str] = None,
    metodo_pagamento: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    busca_cpf: Optional[str] = None,
    busca_nome: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar transações com filtros"""
    
    query = db.query(Transacao).join(Evento)
    
    # Filtro de acesso
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    # Se for promoter, mostrar apenas suas transações
    if usuario_atual.tipo.value == "promoter":
        query = query.filter(Transacao.promoter_id == usuario_atual.id)
    
    # Aplicar filtros
    if evento_id:
        query = query.filter(Transacao.evento_id == evento_id)
    
    if lista_id:
        query = query.filter(Transacao.lista_id == lista_id)
    
    if promoter_id:
        query = query.filter(Transacao.promoter_id == promoter_id)
    
    if status:
        query = query.filter(Transacao.status == status)
    
    if metodo_pagamento:
        query = query.filter(Transacao.metodo_pagamento == metodo_pagamento)
    
    if data_inicio:
        query = query.filter(func.date(Transacao.criado_em) >= data_inicio)
    
    if data_fim:
        query = query.filter(func.date(Transacao.criado_em) <= data_fim)
    
    if busca_cpf:
        cpf_formatado = formatar_cpf(busca_cpf)
        query = query.filter(Transacao.cpf_comprador.ilike(f"%{cpf_formatado}%"))
    
    if busca_nome:
        query = query.filter(Transacao.nome_comprador.ilike(f"%{busca_nome}%"))
    
    transacoes = query.order_by(desc(Transacao.criado_em)).offset(skip).limit(limit).all()
    
    return [TransacaoResponse(
        id=t.id,
        codigo_transacao=t.codigo_transacao,
        cpf_comprador=t.cpf_comprador,
        nome_comprador=t.nome_comprador,
        email_comprador=t.email_comprador,
        telefone_comprador=t.telefone_comprador,
        valor=float(t.valor),
        valor_original=float(t.valor_original),
        valor_desconto=float(t.valor_desconto),
        metodo_pagamento=t.metodo_pagamento,
        status=t.status.value,
        lista_id=t.lista_id,
        lista_nome=t.lista.nome,
        evento_id=t.evento_id,
        evento_nome=t.evento.nome,
        promoter_id=t.promoter_id,
        promoter_nome=t.promoter.nome if t.promoter else None,
        observacoes=t.observacoes,
        criado_em=t.criado_em,
        atualizado_em=t.atualizado_em
    ) for t in transacoes]

@router.get("/{transacao_id}", response_model=TransacaoDetalhada)
async def obter_transacao(
    transacao_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter detalhes de uma transação"""
    
    query = db.query(Transacao).join(Evento)
    
    # Filtro de acesso
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    if usuario_atual.tipo.value == "promoter":
        query = query.filter(Transacao.promoter_id == usuario_atual.id)
    
    transacao = query.filter(Transacao.id == transacao_id).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    # Verificar se há check-in
    from ..models import Checkin
    checkin = db.query(Checkin).filter(
        Checkin.cpf == transacao.cpf_comprador,
        Checkin.evento_id == transacao.evento_id
    ).first()
    
    # Calcular comissão se houver promoter
    comissao_valor = Decimal(0)
    comissao_percentual = Decimal(0)
    
    if transacao.promoter_id:
        promoter_evento = db.query(PromoterEvento).filter(
            PromoterEvento.promoter_id == transacao.promoter_id,
            PromoterEvento.evento_id == transacao.evento_id
        ).first()
        
        if promoter_evento and promoter_evento.comissao_percentual:
            comissao_percentual = promoter_evento.comissao_percentual
            comissao_valor = transacao.valor * (comissao_percentual / 100)
    
    return TransacaoDetalhada(
        id=transacao.id,
        codigo_transacao=transacao.codigo_transacao,
        cpf_comprador=transacao.cpf_comprador,
        nome_comprador=transacao.nome_comprador,
        email_comprador=transacao.email_comprador,
        telefone_comprador=transacao.telefone_comprador,
        valor=float(transacao.valor),
        valor_original=float(transacao.valor_original),
        valor_desconto=float(transacao.valor_desconto),
        metodo_pagamento=transacao.metodo_pagamento,
        status=transacao.status.value,
        lista_id=transacao.lista_id,
        lista_nome=transacao.lista.nome,
        evento_id=transacao.evento_id,
        evento_nome=transacao.evento.nome,
        promoter_id=transacao.promoter_id,
        promoter_nome=transacao.promoter.nome if transacao.promoter else None,
        observacoes=transacao.observacoes,
        criado_em=transacao.criado_em,
        atualizado_em=transacao.atualizado_em,
        checkin_realizado=checkin is not None,
        checkin_em=checkin.checkin_em if checkin else None,
        comissao_percentual=float(comissao_percentual),
        comissao_valor=float(comissao_valor),
        empresa_nome=transacao.evento.empresa.nome
    )

@router.post("/{transacao_id}/processar-pagamento")
async def processar_pagamento(
    transacao_id: int,
    dados_pagamento: ProcessarPagamento,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Processar pagamento de uma transação"""
    
    transacao = db.query(Transacao).filter(Transacao.id == transacao_id).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    # Verificar acesso
    evento = transacao.evento
    if (usuario_atual.tipo.value != "admin" and 
        evento.empresa_id != usuario_atual.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Verificar se transação pode ser processada
    if transacao.status != StatusTransacao.PENDENTE:
        raise HTTPException(
            status_code=400,
            detail=f"Transação não pode ser processada. Status atual: {transacao.status.value}"
        )
    
    try:
        # Simular processamento do pagamento
        # Em produção, aqui seria integrado com gateway de pagamento
        
        if dados_pagamento.aprovar:
            # Aprovar transação
            transacao.status = StatusTransacao.APROVADA
            transacao.codigo_autorizacao = dados_pagamento.codigo_autorizacao
            transacao.observacoes_pagamento = dados_pagamento.observacoes
            
            # Incrementar vendas da lista
            lista = transacao.lista
            lista.vendas_realizadas += 1
            
            # Notificar sucesso
            background_tasks.add_task(
                enviar_notificacao_transacao,
                transacao_id,
                "aprovada"
            )
            
            # WebSocket
            await manager.broadcast(evento.id, {
                "tipo": "pagamento_aprovado",
                "transacao_id": transacao_id,
                "evento_id": evento.id,
                "valor": float(transacao.valor)
            })
            
            mensagem = "Pagamento aprovado com sucesso"
            
        else:
            # Rejeitar transação
            transacao.status = StatusTransacao.REJEITADA
            transacao.observacoes_pagamento = dados_pagamento.observacoes or "Pagamento rejeitado"
            
            # Notificar rejeição
            background_tasks.add_task(
                enviar_notificacao_transacao,
                transacao_id,
                "rejeitada"
            )
            
            mensagem = "Pagamento rejeitado"
        
        transacao.atualizado_em = datetime.now()
        db.commit()
        
        return {
            "mensagem": mensagem,
            "status": transacao.status.value,
            "codigo_autorizacao": transacao.codigo_autorizacao
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar pagamento: {str(e)}"
        )

@router.post("/{transacao_id}/estornar")
async def estornar_transacao(
    transacao_id: int,
    dados_estorno: EstornarTransacao,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Estornar uma transação aprovada"""
    
    # Verificar permissão
    if usuario_atual.tipo.value not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    transacao = db.query(Transacao).filter(Transacao.id == transacao_id).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    # Verificar acesso
    evento = transacao.evento
    if (usuario_atual.tipo.value != "admin" and 
        evento.empresa_id != usuario_atual.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Verificar se pode ser estornada
    if transacao.status != StatusTransacao.APROVADA:
        raise HTTPException(
            status_code=400,
            detail="Apenas transações aprovadas podem ser estornadas"
        )
    
    # Verificar se não há check-in
    from ..models import Checkin
    checkin = db.query(Checkin).filter(
        Checkin.cpf == transacao.cpf_comprador,
        Checkin.evento_id == transacao.evento_id
    ).first()
    
    if checkin and not dados_estorno.forcar_estorno:
        raise HTTPException(
            status_code=400,
            detail="Não é possível estornar: cliente já fez check-in. Use 'forcar_estorno' se necessário."
        )
    
    try:
        # Estornar transação
        transacao.status = StatusTransacao.ESTORNADA
        transacao.observacoes_estorno = dados_estorno.motivo
        transacao.estornado_por_id = usuario_atual.id
        transacao.atualizado_em = datetime.now()
        
        # Decrementar vendas da lista
        lista = transacao.lista
        if lista.vendas_realizadas > 0:
            lista.vendas_realizadas -= 1
        
        # Se houver check-in, remover
        if checkin and dados_estorno.forcar_estorno:
            db.delete(checkin)
        
        db.commit()
        
        # Notificar estorno
        background_tasks.add_task(
            enviar_notificacao_transacao,
            transacao_id,
            "estornada"
        )
        
        # WebSocket
        await manager.broadcast(evento.id, {
            "tipo": "transacao_estornada",
            "transacao_id": transacao_id,
            "evento_id": evento.id
        })
        
        return {
            "mensagem": "Transação estornada com sucesso",
            "checkin_removido": checkin is not None and dados_estorno.forcar_estorno
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao estornar transação: {str(e)}"
        )

@router.get("/relatorio/vendas", response_model=RelatorioTransacoes)
async def gerar_relatorio_vendas(
    evento_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    promoter_id: Optional[int] = None,
    metodo_pagamento: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Gerar relatório de vendas/transações"""
    
    # Definir período se não especificado
    if not data_inicio:
        data_inicio = date.today().replace(day=1)  # Início do mês
    if not data_fim:
        data_fim = date.today()
    
    # Query base
    query = db.query(Transacao).join(Evento).filter(
        Transacao.status == StatusTransacao.APROVADA,
        func.date(Transacao.criado_em) >= data_inicio,
        func.date(Transacao.criado_em) <= data_fim
    )
    
    # Filtros de acesso
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    if usuario_atual.tipo.value == "promoter":
        query = query.filter(Transacao.promoter_id == usuario_atual.id)
    
    # Aplicar filtros
    if evento_id:
        query = query.filter(Transacao.evento_id == evento_id)
    
    if promoter_id:
        query = query.filter(Transacao.promoter_id == promoter_id)
    
    if metodo_pagamento:
        query = query.filter(Transacao.metodo_pagamento == metodo_pagamento)
    
    transacoes = query.all()
    
    # Calcular métricas
    total_transacoes = len(transacoes)
    receita_total = sum(t.valor for t in transacoes)
    ticket_medio = receita_total / total_transacoes if total_transacoes > 0 else 0
    
    # Vendas por método de pagamento
    vendas_por_metodo = {}
    for transacao in transacoes:
        metodo = transacao.metodo_pagamento
        if metodo not in vendas_por_metodo:
            vendas_por_metodo[metodo] = {"quantidade": 0, "valor": 0}
        vendas_por_metodo[metodo]["quantidade"] += 1
        vendas_por_metodo[metodo]["valor"] += float(transacao.valor)
    
    # Vendas por promoter
    vendas_por_promoter = {}
    for transacao in transacoes:
        if transacao.promoter_id:
            promoter_nome = transacao.promoter.nome
            if promoter_nome not in vendas_por_promoter:
                vendas_por_promoter[promoter_nome] = {"quantidade": 0, "valor": 0}
            vendas_por_promoter[promoter_nome]["quantidade"] += 1
            vendas_por_promoter[promoter_nome]["valor"] += float(transacao.valor)
    
    # Vendas por dia
    vendas_por_dia = {}
    for transacao in transacoes:
        dia = transacao.criado_em.date().isoformat()
        if dia not in vendas_por_dia:
            vendas_por_dia[dia] = {"quantidade": 0, "valor": 0}
        vendas_por_dia[dia]["quantidade"] += 1
        vendas_por_dia[dia]["valor"] += float(transacao.valor)
    
    # Comparação com período anterior
    periodo_anterior_inicio = data_inicio - (data_fim - data_inicio)
    periodo_anterior_fim = data_inicio - timedelta(days=1)
    
    vendas_periodo_anterior = query.filter(
        func.date(Transacao.criado_em) >= periodo_anterior_inicio,
        func.date(Transacao.criado_em) <= periodo_anterior_fim
    ).count()
    
    crescimento = 0
    if vendas_periodo_anterior > 0:
        crescimento = ((total_transacoes - vendas_periodo_anterior) / vendas_periodo_anterior) * 100
    
    return RelatorioTransacoes(
        total_transacoes=total_transacoes,
        receita_total=float(receita_total),
        ticket_medio=float(ticket_medio),
        crescimento_periodo=round(crescimento, 2),
        vendas_por_metodo=vendas_por_metodo,
        vendas_por_promoter=vendas_por_promoter,
        vendas_por_dia=vendas_por_dia,
        periodo_inicio=data_inicio,
        periodo_fim=data_fim,
        gerado_em=datetime.now()
    )

@router.get("/validar-cpf/{cpf}")
async def validar_cpf_compra(
    cpf: str,
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Validar se CPF pode fazer compra no evento"""
    
    if not validar_cpf(cpf):
        raise HTTPException(status_code=400, detail="CPF inválido")
    
    cpf_formatado = formatar_cpf(cpf)
    
    # Buscar transações existentes do CPF no evento
    transacoes_cpf = db.query(Transacao).filter(
        Transacao.cpf_comprador == cpf_formatado,
        Transacao.evento_id == evento_id,
        Transacao.status.in_([StatusTransacao.APROVADA, StatusTransacao.PENDENTE])
    ).all()
    
    # Buscar última transação para dados do comprador
    ultima_transacao = db.query(Transacao).filter(
        Transacao.cpf_comprador == cpf_formatado,
        Transacao.status == StatusTransacao.APROVADA
    ).order_by(desc(Transacao.criado_em)).first()
    
    dados_comprador = {}
    if ultima_transacao:
        dados_comprador = {
            "nome": ultima_transacao.nome_comprador,
            "email": ultima_transacao.email_comprador,
            "telefone": ultima_transacao.telefone_comprador
        }
    
    return {
        "cpf_valido": True,
        "pode_comprar": len(transacoes_cpf) == 0,
        "transacoes_existentes": len(transacoes_cpf),
        "listas_compradas": [t.lista.nome for t in transacoes_cpf],
        "dados_comprador": dados_comprador,
        "historico_compras": len(db.query(Transacao).filter(
            Transacao.cpf_comprador == cpf_formatado,
            Transacao.status == StatusTransacao.APROVADA
        ).all())
    }

@router.get("/estatisticas/tempo-real")
async def obter_estatisticas_tempo_real(
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter estatísticas de vendas em tempo real"""
    
    agora = datetime.now()
    uma_hora_atras = agora - timedelta(hours=1)
    hoje = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    
    query_base = db.query(Transacao).join(Evento).filter(
        Transacao.status == StatusTransacao.APROVADA
    )
    
    # Filtros de acesso
    if usuario_atual.tipo.value != "admin":
        query_base = query_base.filter(Evento.empresa_id == usuario_atual.empresa_id)
    
    if usuario_atual.tipo.value == "promoter":
        query_base = query_base.filter(Transacao.promoter_id == usuario_atual.id)
    
    if evento_id:
        query_base = query_base.filter(Transacao.evento_id == evento_id)
    
    # Métricas
    vendas_ultima_hora = query_base.filter(
        Transacao.criado_em >= uma_hora_atras
    ).count()
    
    vendas_hoje = query_base.filter(
        Transacao.criado_em >= hoje
    ).count()
    
    receita_hoje = query_base.filter(
        Transacao.criado_em >= hoje
    ).with_entities(func.sum(Transacao.valor)).scalar() or 0
    
    transacoes_pendentes = db.query(Transacao).join(Evento).filter(
        Transacao.status == StatusTransacao.PENDENTE
    )
    
    if usuario_atual.tipo.value != "admin":
        transacoes_pendentes = transacoes_pendentes.filter(
            Evento.empresa_id == usuario_atual.empresa_id
        )
    
    if evento_id:
        transacoes_pendentes = transacoes_pendentes.filter(
            Transacao.evento_id == evento_id
        )
    
    pendentes = transacoes_pendentes.count()
    
    return {
        "vendas_ultima_hora": vendas_ultima_hora,
        "vendas_hoje": vendas_hoje,
        "receita_hoje": float(receita_hoje),
        "transacoes_pendentes": pendentes,
        "timestamp": agora.isoformat()
    }

# Função auxiliar para notificações
async def enviar_notificacao_transacao(transacao_id: int, tipo: str):
    """Enviar notificação sobre transação"""
    try:
        # Implementar envio de notificação via WhatsApp/SMS/Email
        # Por enquanto apenas log
        print(f"Notificação {tipo} enviada para transação {transacao_id}")
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")

@router.post("/reenviar-comprovante/{transacao_id}")
async def reenviar_comprovante(
    transacao_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Reenviar comprovante de compra"""
    
    transacao = db.query(Transacao).filter(Transacao.id == transacao_id).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    # Verificar acesso
    if (usuario_atual.tipo.value != "admin" and 
        transacao.evento.empresa_id != usuario_atual.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if transacao.status != StatusTransacao.APROVADA:
        raise HTTPException(
            status_code=400,
            detail="Apenas transações aprovadas podem ter comprovante reenviado"
        )
    
    # Adicionar tarefa para reenvio
    background_tasks.add_task(
        enviar_notificacao_transacao,
        transacao_id,
        "reenvio_comprovante"
    )
    
    return {"mensagem": "Comprovante será reenviado"}
