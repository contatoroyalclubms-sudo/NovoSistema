from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import json
from ..database import get_db
from ..models import (
    Produto, Comanda, VendaPDV, ItemVendaPDV, PagamentoPDV, 
    RecargaComanda, MovimentoEstoque, CaixaPDV, Evento,
    StatusProduto, StatusComanda, StatusVendaPDV, TipoPagamentoPDV
)
from ..schemas import (
    ProdutoCreate, Produto as ProdutoSchema, ComandaCreate, Comanda as ComandaSchema,
    VendaPDVCreate, VendaPDV as VendaPDVSchema, RecargaComandaCreate, RecargaComanda as RecargaComandaSchema,
    CaixaPDVCreate, CaixaPDV as CaixaPDVSchema, RelatorioVendasPDV, DashboardPDV
)
from ..auth import obter_usuario_atual, verificar_permissao_admin
from ..websocket import notify_stock_update, notify_new_sale, notify_cash_register_update

router = APIRouter(prefix="/pdv", tags=["PDV"])

@router.post("/produtos", response_model=ProdutoSchema)
async def criar_produto(
    produto: ProdutoCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(verificar_permissao_admin)
):
    """Criar novo produto"""
    
    evento = db.query(Evento).filter(Evento.id == produto.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if evento.empresa_id != usuario_atual.empresa_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if not produto.codigo_interno:
        import uuid
        produto.codigo_interno = f"PROD{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"
    
    db_produto = Produto(
        **produto.model_dump(),
        empresa_id=usuario_atual.empresa_id,
        status=StatusProduto.ATIVO
    )
    
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    
    return db_produto

@router.get("/produtos", response_model=List[ProdutoSchema])
async def listar_produtos(
    evento_id: int,
    categoria: Optional[str] = None,
    status: Optional[str] = None,
    busca: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual = Depends(obter_usuario_atual)
):
    """Listar produtos do evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    query = db.query(Produto).filter(Produto.evento_id == evento_id)
    
    if categoria:
        query = query.filter(Produto.categoria == categoria)
    
    if status:
        query = query.filter(Produto.status == status)
    
    if busca:
        query = query.filter(
            Produto.nome.ilike(f"%{busca}%") |
            Produto.codigo_barras.ilike(f"%{busca}%") |
            Produto.codigo_interno.ilike(f"%{busca}%")
        )
    
    return query.order_by(Produto.nome).all()

@router.get("/produtos/{produto_id}", response_model=ProdutoSchema)
async def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(obter_usuario_atual)
):
    """Obter produto por ID"""
    
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != produto.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return produto

@router.put("/produtos/{produto_id}", response_model=ProdutoSchema)
async def atualizar_produto(
    produto_id: int,
    produto_update: ProdutoCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(verificar_permissao_admin)
):
    """Atualizar produto"""
    
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    if produto.empresa_id != usuario_atual.empresa_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    for field, value in produto_update.model_dump(exclude={'evento_id'}).items():
        if hasattr(produto, field):
            setattr(produto, field, value)
    
    db.commit()
    db.refresh(produto)
    
    return produto

@router.post("/comandas", response_model=ComandaSchema)
async def criar_comanda(
    comanda: ComandaCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(obter_usuario_atual)
):
    """Criar nova comanda"""
    
    evento = db.query(Evento).filter(Evento.id == comanda.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    qr_code = str(uuid.uuid4())[:8].upper()
    
    db_comanda = Comanda(
        **comanda.model_dump(),
        empresa_id=usuario_atual.empresa_id,
        qr_code=qr_code,
        status=StatusComanda.ATIVA
    )
    
    db.add(db_comanda)
    db.commit()
    db.refresh(db_comanda)
    
    return db_comanda

@router.get("/comandas", response_model=List[ComandaSchema])
async def listar_comandas(
    evento_id: int,
    status: Optional[str] = None,
    cpf: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual = Depends(obter_usuario_atual)
):
    """Listar comandas do evento"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    query = db.query(Comanda).filter(Comanda.evento_id == evento_id)
    
    if status:
        query = query.filter(Comanda.status == status)
    
    if cpf:
        query = query.filter(Comanda.cpf_cliente == cpf)
    
    return query.order_by(desc(Comanda.criado_em)).all()

@router.post("/comandas/{comanda_id}/recarga", response_model=RecargaComandaSchema)
async def recarregar_comanda(
    comanda_id: int,
    recarga: RecargaComandaCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(obter_usuario_atual)
):
    """Recarregar saldo da comanda"""
    
    comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
    if not comanda:
        raise HTTPException(status_code=404, detail="Comanda não encontrada")
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != comanda.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if comanda.status != StatusComanda.ATIVA:
        raise HTTPException(status_code=400, detail="Comanda não está ativa")
    
    db_recarga = RecargaComanda(
        comanda_id=comanda_id,
        valor=recarga.valor,
        tipo_pagamento=recarga.tipo_pagamento,
        usuario_id=usuario_atual.id,
        codigo_transacao=str(uuid.uuid4())
    )
    
    comanda.saldo_atual += recarga.valor
    
    db.add(db_recarga)
    db.commit()
    db.refresh(db_recarga)
    
    return db_recarga

@router.post("/vendas", response_model=VendaPDVSchema)
async def processar_venda(
    venda: VendaPDVCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario_atual = Depends(obter_usuario_atual)
):
    """Processar venda no PDV"""
    
    evento = db.query(Evento).filter(Evento.id == venda.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    for item in venda.itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto {item.produto_id} não encontrado")
        
        if produto.controla_estoque and produto.estoque_atual < item.quantidade:
            raise HTTPException(
                status_code=400, 
                detail=f"Estoque insuficiente para {produto.nome}. Disponível: {produto.estoque_atual}"
            )
    
    valor_total = sum(item.quantidade * item.preco_unitario for item in venda.itens)
    valor_desconto = Decimal('0.00')
    
    if venda.cupom_codigo:
        pass
    
    valor_final = valor_total - valor_desconto
    
    valor_pagamentos = sum(pag.valor for pag in venda.pagamentos)
    if valor_pagamentos != valor_final:
        raise HTTPException(
            status_code=400, 
            detail=f"Valor dos pagamentos ({valor_pagamentos}) não confere com valor final ({valor_final})"
        )
    
    numero_venda = f"PDV{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db_venda = VendaPDV(
        numero_venda=numero_venda,
        cpf_cliente=venda.cpf_cliente,
        nome_cliente=venda.nome_cliente,
        valor_total=valor_total,
        valor_desconto=valor_desconto,
        valor_final=valor_final,
        tipo_pagamento=venda.pagamentos[0].tipo_pagamento if venda.pagamentos else TipoPagamentoPDV.DINHEIRO,
        status=StatusVendaPDV.APROVADA,
        comanda_id=venda.comanda_id,
        evento_id=venda.evento_id,
        empresa_id=usuario_atual.empresa_id,
        usuario_vendedor_id=usuario_atual.id,
        cupom_codigo=venda.cupom_codigo,
        observacoes=venda.observacoes
    )
    
    db.add(db_venda)
    db.flush()  # Para obter o ID da venda
    
    for item in venda.itens:
        preco_total = item.quantidade * item.preco_unitario
        
        db_item = ItemVendaPDV(
            venda_id=db_venda.id,
            produto_id=item.produto_id,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario,
            preco_total=preco_total,
            observacoes=item.observacoes
        )
        db.add(db_item)
        
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if produto.controla_estoque:
            estoque_anterior = produto.estoque_atual
            produto.estoque_atual -= item.quantidade
            
            movimento = MovimentoEstoque(
                produto_id=item.produto_id,
                tipo_movimento="saida",
                quantidade=item.quantidade,
                estoque_anterior=estoque_anterior,
                estoque_atual=produto.estoque_atual,
                motivo="Venda PDV",
                venda_id=db_venda.id,
                usuario_id=usuario_atual.id
            )
            db.add(movimento)
    
    for pagamento in venda.pagamentos:
        db_pagamento = PagamentoPDV(
            venda_id=db_venda.id,
            tipo_pagamento=pagamento.tipo_pagamento,
            valor=pagamento.valor,
            promoter_id=pagamento.promoter_id,
            comissao_percentual=pagamento.comissao_percentual or Decimal('0.00'),
            valor_comissao=(pagamento.valor * (pagamento.comissao_percentual or Decimal('0.00')) / 100),
            codigo_transacao=str(uuid.uuid4())
        )
        db.add(db_pagamento)
    
    if venda.comanda_id:
        comanda = db.query(Comanda).filter(Comanda.id == venda.comanda_id).first()
        if comanda and comanda.saldo_atual >= valor_final:
            comanda.saldo_atual -= valor_final
        else:
            raise HTTPException(status_code=400, detail="Saldo insuficiente na comanda")
    
    db.commit()
    db.refresh(db_venda)
    
    await notify_new_sale(venda.evento_id, {
        "numero_venda": db_venda.numero_venda,
        "valor_final": float(db_venda.valor_final),
        "tipo_pagamento": db_venda.pagamentos[0].tipo_pagamento.value if db_venda.pagamentos else "N/A",
        "itens_count": len(venda.itens)
    })
    
    for item in venda.itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if produto:
            await notify_stock_update(
                produto.id, 
                venda.evento_id, 
                produto.estoque_atual,
                produto.nome
            )
    
    background_tasks.add_task(imprimir_comprovante, db_venda.id)
    
    return db_venda

@router.get("/vendas", response_model=List[VendaPDVSchema])
async def listar_vendas(
    evento_id: int,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    status: Optional[str] = None,
    cpf_cliente: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual = Depends(obter_usuario_atual)
):
    """Listar vendas do PDV"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    query = db.query(VendaPDV).filter(VendaPDV.evento_id == evento_id)
    
    if data_inicio:
        query = query.filter(func.date(VendaPDV.criado_em) >= data_inicio)
    
    if data_fim:
        query = query.filter(func.date(VendaPDV.criado_em) <= data_fim)
    
    if status:
        query = query.filter(VendaPDV.status == status)
    
    if cpf_cliente:
        query = query.filter(VendaPDV.cpf_cliente == cpf_cliente)
    
    return query.order_by(desc(VendaPDV.criado_em)).all()

@router.post("/caixa/abrir", response_model=CaixaPDVSchema)
async def abrir_caixa(
    caixa: CaixaPDVCreate,
    db: Session = Depends(get_db),
    usuario_atual = Depends(obter_usuario_atual)
):
    """Abrir caixa PDV"""
    
    evento = db.query(Evento).filter(Evento.id == caixa.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    caixa_aberto = db.query(CaixaPDV).filter(
        and_(
            CaixaPDV.evento_id == caixa.evento_id,
            CaixaPDV.usuario_operador_id == usuario_atual.id,
            CaixaPDV.status == "aberto"
        )
    ).first()
    
    if caixa_aberto:
        raise HTTPException(status_code=400, detail="Já existe um caixa aberto para este operador")
    
    db_caixa = CaixaPDV(
        numero_caixa=caixa.numero_caixa,
        evento_id=caixa.evento_id,
        usuario_operador_id=usuario_atual.id,
        valor_abertura=caixa.valor_abertura,
        status="aberto"
    )
    
    db.add(db_caixa)
    db.commit()
    db.refresh(db_caixa)
    
    return db_caixa

@router.post("/caixa/{caixa_id}/fechar", response_model=CaixaPDVSchema)
async def fechar_caixa(
    caixa_id: int,
    valor_fechamento: Decimal,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario_atual = Depends(obter_usuario_atual)
):
    """Fechar caixa PDV"""
    
    caixa = db.query(CaixaPDV).filter(CaixaPDV.id == caixa_id).first()
    if not caixa:
        raise HTTPException(status_code=404, detail="Caixa não encontrado")
    
    if caixa.usuario_operador_id != usuario_atual.id:
        raise HTTPException(status_code=403, detail="Apenas o operador pode fechar o caixa")
    
    if caixa.status != "aberto":
        raise HTTPException(status_code=400, detail="Caixa já está fechado")
    
    vendas_periodo = db.query(func.sum(VendaPDV.valor_final)).filter(
        and_(
            VendaPDV.evento_id == caixa.evento_id,
            VendaPDV.usuario_vendedor_id == usuario_atual.id,
            VendaPDV.criado_em >= caixa.data_abertura,
            VendaPDV.status == StatusVendaPDV.APROVADA
        )
    ).scalar() or Decimal('0.00')
    
    caixa.valor_vendas = vendas_periodo
    caixa.valor_fechamento = valor_fechamento
    caixa.data_fechamento = datetime.now()
    caixa.observacoes = observacoes
    caixa.status = "fechado"
    
    db.commit()
    db.refresh(caixa)
    
    return caixa

@router.get("/dashboard/{evento_id}", response_model=DashboardPDV)
async def obter_dashboard_pdv(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(obter_usuario_atual)
):
    """Obter dashboard do PDV"""
    
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if (usuario_atual.tipo.value != "admin" and 
        usuario_atual.empresa_id != evento.empresa_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    hoje = date.today()
    
    vendas_hoje = db.query(func.count(VendaPDV.id)).filter(
        and_(
            VendaPDV.evento_id == evento_id,
            func.date(VendaPDV.criado_em) == hoje,
            VendaPDV.status == StatusVendaPDV.APROVADA
        )
    ).scalar() or 0
    
    valor_vendas_hoje = db.query(func.sum(VendaPDV.valor_final)).filter(
        and_(
            VendaPDV.evento_id == evento_id,
            func.date(VendaPDV.criado_em) == hoje,
            VendaPDV.status == StatusVendaPDV.APROVADA
        )
    ).scalar() or Decimal('0.00')
    
    produtos_em_falta = db.query(func.count(Produto.id)).filter(
        and_(
            Produto.evento_id == evento_id,
            Produto.controla_estoque == True,
            Produto.estoque_atual <= Produto.estoque_minimo
        )
    ).scalar() or 0
    
    comandas_ativas = db.query(func.count(Comanda.id)).filter(
        and_(
            Comanda.evento_id == evento_id,
            Comanda.status == StatusComanda.ATIVA
        )
    ).scalar() or 0
    
    caixas_abertos = db.query(func.count(CaixaPDV.id)).filter(
        and_(
            CaixaPDV.evento_id == evento_id,
            CaixaPDV.status == "aberto"
        )
    ).scalar() or 0
    
    return DashboardPDV(
        vendas_hoje=vendas_hoje,
        valor_vendas_hoje=valor_vendas_hoje,
        produtos_em_falta=produtos_em_falta,
        comandas_ativas=comandas_ativas,
        caixas_abertos=caixas_abertos,
        vendas_por_hora=[],  # Implementar conforme necessário
        produtos_mais_vendidos=[],  # Implementar conforme necessário
        alertas=[]  # Implementar conforme necessário
    )

@router.get("/relatorios/x/{caixa_id}")
async def relatorio_x(
    caixa_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(obter_usuario_atual)
):
    """Relatório X - Vendas do caixa sem fechamento"""
    
    caixa = db.query(CaixaPDV).filter(CaixaPDV.id == caixa_id).first()
    if not caixa:
        raise HTTPException(status_code=404, detail="Caixa não encontrado")
    
    if caixa.usuario_operador_id != usuario_atual.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    vendas = db.query(VendaPDV).filter(
        and_(
            VendaPDV.evento_id == caixa.evento_id,
            VendaPDV.usuario_vendedor_id == usuario_atual.id,
            VendaPDV.criado_em >= caixa.data_abertura,
            VendaPDV.status == StatusVendaPDV.APROVADA
        )
    ).all()
    
    totais_pagamento = {}
    total_geral = Decimal('0.00')
    
    for venda in vendas:
        for pagamento in venda.pagamentos:
            forma = pagamento.tipo_pagamento.value
            if forma not in totais_pagamento:
                totais_pagamento[forma] = Decimal('0.00')
            totais_pagamento[forma] += pagamento.valor
            total_geral += pagamento.valor
    
    return {
        "tipo": "relatorio_x",
        "caixa_id": caixa_id,
        "numero_caixa": caixa.numero_caixa,
        "data_abertura": caixa.data_abertura,
        "operador": usuario_atual.nome,
        "total_vendas": len(vendas),
        "valor_total": float(total_geral),
        "totais_por_pagamento": {k: float(v) for k, v in totais_pagamento.items()},
        "vendas": [
            {
                "numero_venda": v.numero_venda,
                "valor": float(v.valor_final),
                "tipo_pagamento": v.pagamentos[0].tipo_pagamento.value if v.pagamentos else "N/A",
                "horario": v.criado_em.isoformat()
            } for v in vendas
        ]
    }

@router.get("/relatorios/z/{caixa_id}")
async def relatorio_z(
    caixa_id: int,
    db: Session = Depends(get_db),
    usuario_atual = Depends(obter_usuario_atual)
):
    """Relatório Z - Fechamento definitivo do caixa"""
    
    caixa = db.query(CaixaPDV).filter(CaixaPDV.id == caixa_id).first()
    if not caixa:
        raise HTTPException(status_code=404, detail="Caixa não encontrado")
    
    if caixa.usuario_operador_id != usuario_atual.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if caixa.status != "fechado":
        raise HTTPException(status_code=400, detail="Caixa deve estar fechado para relatório Z")
    
    relatorio_x_data = await relatorio_x(caixa_id, db, usuario_atual)
    
    relatorio_x_data.update({
        "tipo": "relatorio_z",
        "data_fechamento": caixa.data_fechamento.isoformat() if caixa.data_fechamento else None,
        "valor_abertura": float(caixa.valor_abertura),
        "valor_fechamento": float(caixa.valor_fechamento),
        "diferenca": float(caixa.valor_fechamento - (caixa.valor_abertura + caixa.valor_vendas)),
        "observacoes": caixa.observacoes
    })
    
    return relatorio_x_data

@router.websocket("/ws/{evento_id}")
async def websocket_endpoint(websocket: WebSocket, evento_id: int):
    from ..websocket import manager
    await manager.connect(websocket, evento_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(json.dumps({"type": "ping", "message": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, evento_id)

async def imprimir_comprovante(venda_id: int):
    """Função para imprimir comprovante (background task)"""
    pass
