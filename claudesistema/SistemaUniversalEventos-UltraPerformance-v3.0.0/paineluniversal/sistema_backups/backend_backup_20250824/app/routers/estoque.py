from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from decimal import Decimal
import csv
import io

from ..database import get_db
from ..models import (
    Usuario, Evento, Produto, Categoria, MovimentoEstoque, VendaPDV,
    ItemVendaPDV, TipoUsuario
)
from ..schemas import (
    ProdutoCreate, ProdutoUpdate, ProdutoResponse,
    CategoriaCreate, CategoriaResponse, CategoriaUpdate,
    MovimentoEstoqueCreate, MovimentoEstoqueResponse,
    RelatorioEstoque, AlertaEstoque, EstoqueAjusteManual,
    EstoqueEntradaLote, DisponibilidadeEstoque, ProdutoEstoqueUpdate,
    InventarioResponse
)
from ..services import EstoqueService
from ..auth import get_current_active_user

router = APIRouter(prefix="/estoque", tags=["Estoque e Produtos"])

# PRODUTOS

@router.post("/produtos", response_model=ProdutoResponse)
async def criar_produto(
    produto: ProdutoCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Criar novo produto"""
    
    if usuario_atual.tipo.value not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    # Verificar se categoria existe
    if produto.categoria_id:
        categoria = db.query(Categoria).filter(Categoria.id == produto.categoria_id).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        
        if (usuario_atual.tipo.value != "admin" and 
            categoria.empresa_id != usuario_atual.empresa_id):
            raise HTTPException(status_code=403, detail="Categoria não pertence à sua empresa")
    
    # Verificar se evento existe e pertence à empresa
    if produto.evento_id:
        evento = db.query(Evento).filter(Evento.id == produto.evento_id).first()
        if not evento:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        
        if (usuario_atual.tipo.value != "admin" and 
            evento.empresa_id != usuario_atual.empresa_id):
            raise HTTPException(status_code=403, detail="Evento não pertence à sua empresa")
    
    # Verificar se já existe produto com mesmo código
    produto_existente = db.query(Produto).filter(
        Produto.codigo == produto.codigo,
        Produto.empresa_id == usuario_atual.empresa_id
    ).first()
    
    if produto_existente:
        raise HTTPException(
            status_code=400, 
            detail="Já existe um produto com este código"
        )
    
    # Criar produto
    db_produto = Produto(
        **produto.dict(),
        empresa_id=usuario_atual.empresa_id,
        criado_por_id=usuario_atual.id
    )
    
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    
    # Registrar movimento inicial de estoque se quantidade > 0
    if db_produto.quantidade_estoque > 0:
        estoque_service = EstoqueService(db)
        await estoque_service.registrar_movimento(
            produto_id=db_produto.id,
            tipo_movimento="entrada",
            quantidade=db_produto.quantidade_estoque,
            motivo="Estoque inicial",
            usuario_id=usuario_atual.id
        )
    
    return ProdutoResponse(
        id=db_produto.id,
        nome=db_produto.nome,
        descricao=db_produto.descricao,
        codigo=db_produto.codigo,
        preco_venda=float(db_produto.preco_venda),
        preco_custo=float(db_produto.preco_custo or 0),
        quantidade_estoque=db_produto.quantidade_estoque,
        estoque_minimo=db_produto.estoque_minimo,
        categoria_id=db_produto.categoria_id,
        categoria_nome=db_produto.categoria.nome if db_produto.categoria else None,
        evento_id=db_produto.evento_id,
        ativo=db_produto.ativo,
        permite_venda_sem_estoque=db_produto.permite_venda_sem_estoque,
        unidade_medida=db_produto.unidade_medida,
        peso=float(db_produto.peso or 0),
        imagem_url=db_produto.imagem_url,
        tags=db_produto.tags,
        criado_em=db_produto.criado_em,
        atualizado_em=db_produto.atualizado_em
    )

@router.get("/produtos", response_model=List[ProdutoResponse])
async def listar_produtos(
    evento_id: Optional[int] = None,
    categoria_id: Optional[int] = None,
    ativo: Optional[bool] = None,
    busca: Optional[str] = None,
    estoque_baixo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Listar produtos com filtros"""
    
    query = db.query(Produto)
    
    # Filtro de acesso
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Produto.empresa_id == usuario_atual.empresa_id)
    
    # Aplicar filtros
    if evento_id:
        query = query.filter(Produto.evento_id == evento_id)
    
    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)
    
    if ativo is not None:
        query = query.filter(Produto.ativo == ativo)
    
    if busca:
        query = query.filter(
            or_(
                Produto.nome.ilike(f"%{busca}%"),
                Produto.descricao.ilike(f"%{busca}%"),
                Produto.codigo.ilike(f"%{busca}%")
            )
        )
    
    if estoque_baixo:
        query = query.filter(Produto.quantidade_estoque <= Produto.estoque_minimo)
    
    produtos = query.order_by(Produto.nome).offset(skip).limit(limit).all()
    
    return [ProdutoResponse(
        id=p.id,
        nome=p.nome,
        descricao=p.descricao,
        codigo=p.codigo,
        preco_venda=float(p.preco_venda),
        preco_custo=float(p.preco_custo or 0),
        quantidade_estoque=p.quantidade_estoque,
        estoque_minimo=p.estoque_minimo,
        categoria_id=p.categoria_id,
        categoria_nome=p.categoria.nome if p.categoria else None,
        evento_id=p.evento_id,
        ativo=p.ativo,
        permite_venda_sem_estoque=p.permite_venda_sem_estoque,
        unidade_medida=p.unidade_medida,
        peso=float(p.peso or 0),
        imagem_url=p.imagem_url,
        tags=p.tags,
        criado_em=p.criado_em,
        atualizado_em=p.atualizado_em
    ) for p in produtos]

@router.get("/produtos/{produto_id}", response_model=ProdutoResponse)
async def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Obter produto específico"""
    
    query = db.query(Produto).filter(Produto.id == produto_id)
    
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Produto.empresa_id == usuario_atual.empresa_id)
    
    produto = query.first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    return ProdutoResponse(
        id=produto.id,
        nome=produto.nome,
        descricao=produto.descricao,
        codigo=produto.codigo,
        preco_venda=float(produto.preco_venda),
        preco_custo=float(produto.preco_custo or 0),
        quantidade_estoque=produto.quantidade_estoque,
        estoque_minimo=produto.estoque_minimo,
        categoria_id=produto.categoria_id,
        categoria_nome=produto.categoria.nome if produto.categoria else None,
        evento_id=produto.evento_id,
        ativo=produto.ativo,
        permite_venda_sem_estoque=produto.permite_venda_sem_estoque,
        unidade_medida=produto.unidade_medida,
        peso=float(produto.peso or 0),
        imagem_url=produto.imagem_url,
        tags=produto.tags,
        criado_em=produto.criado_em,
        atualizado_em=produto.atualizado_em
    )

@router.put("/produtos/{produto_id}", response_model=ProdutoResponse)
async def atualizar_produto(
    produto_id: int,
    produto_update: ProdutoUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Atualizar produto"""
    
    if usuario_atual.tipo.value not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    query = db.query(Produto).filter(Produto.id == produto_id)
    
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Produto.empresa_id == usuario_atual.empresa_id)
    
    produto = query.first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Atualizar campos
    for field, value in produto_update.dict(exclude_unset=True).items():
        if field != "quantidade_estoque":  # Estoque é alterado por movimentações
            setattr(produto, field, value)
    
    produto.atualizado_em = datetime.now()
    
    db.commit()
    db.refresh(produto)
    
    return ProdutoResponse(
        id=produto.id,
        nome=produto.nome,
        descricao=produto.descricao,
        codigo=produto.codigo,
        preco_venda=float(produto.preco_venda),
        preco_custo=float(produto.preco_custo or 0),
        quantidade_estoque=produto.quantidade_estoque,
        estoque_minimo=produto.estoque_minimo,
        categoria_id=produto.categoria_id,
        categoria_nome=produto.categoria.nome if produto.categoria else None,
        evento_id=produto.evento_id,
        ativo=produto.ativo,
        permite_venda_sem_estoque=produto.permite_venda_sem_estoque,
        unidade_medida=produto.unidade_medida,
        peso=float(produto.peso or 0),
        imagem_url=produto.imagem_url,
        tags=produto.tags,
        criado_em=produto.criado_em,
        atualizado_em=produto.atualizado_em
    )

# CATEGORIAS

@router.post("/categorias", response_model=CategoriaResponse)
async def criar_categoria(
    categoria: CategoriaCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Criar nova categoria"""
    
    if usuario_atual.tipo.value not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    # Verificar se já existe categoria com mesmo nome
    categoria_existente = db.query(Categoria).filter(
        Categoria.nome == categoria.nome,
        Categoria.empresa_id == usuario_atual.empresa_id
    ).first()
    
    if categoria_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe uma categoria com este nome"
        )
    
    db_categoria = Categoria(
        **categoria.dict(),
        empresa_id=usuario_atual.empresa_id
    )
    
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    
    return CategoriaResponse(
        id=db_categoria.id,
        nome=db_categoria.nome,
        descricao=db_categoria.descricao,
        cor=db_categoria.cor,
        icone=db_categoria.icone,
        ativa=db_categoria.ativa,
        criado_em=db_categoria.criado_em
    )

@router.get("/categorias", response_model=List[CategoriaResponse])
async def listar_categorias(
    ativa: Optional[bool] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Listar categorias"""
    
    query = db.query(Categoria)
    
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Categoria.empresa_id == usuario_atual.empresa_id)
    
    if ativa is not None:
        query = query.filter(Categoria.ativa == ativa)
    
    categorias = query.order_by(Categoria.nome).all()
    
    return [CategoriaResponse(
        id=c.id,
        nome=c.nome,
        descricao=c.descricao,
        cor=c.cor,
        icone=c.icone,
        ativa=c.ativa,
        criado_em=c.criado_em
    ) for c in categorias]

# MOVIMENTAÇÕES DE ESTOQUE

@router.post("/movimentacoes", response_model=MovimentoEstoqueResponse)
async def criar_movimento_estoque(
    movimento: MovimentoEstoqueCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Registrar movimentação de estoque"""
    
    if usuario_atual.tipo.value not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    estoque_service = EstoqueService(db)
    
    try:
        movimento_criado = await estoque_service.registrar_movimento(
            produto_id=movimento.produto_id,
            tipo_movimento=movimento.tipo_movimento,
            quantidade=movimento.quantidade,
            motivo=movimento.motivo,
            usuario_id=usuario_atual.id,
            venda_id=movimento.venda_id
        )
        
        return MovimentoEstoqueResponse(
            id=movimento_criado.id,
            produto_id=movimento_criado.produto_id,
            produto_nome=movimento_criado.produto.nome,
            tipo_movimento=movimento_criado.tipo_movimento,
            quantidade=movimento_criado.quantidade,
            estoque_anterior=movimento_criado.estoque_anterior,
            estoque_atual=movimento_criado.estoque_atual,
            motivo=movimento_criado.motivo,
            venda_id=movimento_criado.venda_id,
            usuario_id=movimento_criado.usuario_id,
            usuario_nome=movimento_criado.usuario.nome,
            criado_em=movimento_criado.criado_em
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/movimentacoes", response_model=List[MovimentoEstoqueResponse])
async def listar_movimentos_estoque(
    produto_id: Optional[int] = None,
    tipo_movimento: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Listar movimentações de estoque"""
    
    query = db.query(MovimentoEstoque).join(Produto)
    
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Produto.empresa_id == usuario_atual.empresa_id)
    
    if produto_id:
        query = query.filter(MovimentoEstoque.produto_id == produto_id)
    
    if tipo_movimento:
        query = query.filter(MovimentoEstoque.tipo_movimento == tipo_movimento)
    
    if data_inicio:
        query = query.filter(func.date(MovimentoEstoque.criado_em) >= data_inicio)
    
    if data_fim:
        query = query.filter(func.date(MovimentoEstoque.criado_em) <= data_fim)
    
    movimentos = query.order_by(desc(MovimentoEstoque.criado_em)).offset(skip).limit(limit).all()
    
    return [MovimentoEstoqueResponse(
        id=m.id,
        produto_id=m.produto_id,
        produto_nome=m.produto.nome,
        tipo_movimento=m.tipo_movimento,
        quantidade=m.quantidade,
        estoque_anterior=m.estoque_anterior,
        estoque_atual=m.estoque_atual,
        motivo=m.motivo,
        venda_id=m.venda_id,
        usuario_id=m.usuario_id,
        usuario_nome=m.usuario.nome,
        criado_em=m.criado_em
    ) for m in movimentos]

# RELATÓRIOS E ALERTAS

@router.get("/relatorio", response_model=RelatorioEstoque)
async def gerar_relatorio_estoque(
    evento_id: Optional[int] = None,
    categoria_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Gerar relatório completo de estoque"""
    
    estoque_service = EstoqueService(db)
    
    return await estoque_service.gerar_relatorio_estoque(
        usuario_atual=usuario_atual,
        evento_id=evento_id,
        categoria_id=categoria_id,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

@router.get("/alertas", response_model=List[AlertaEstoque])
async def obter_alertas_estoque(
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Obter alertas de estoque baixo"""
    
    query = db.query(Produto).filter(
        Produto.ativo == True,
        or_(
            Produto.quantidade_estoque <= Produto.estoque_minimo,
            Produto.quantidade_estoque == 0
        )
    )
    
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Produto.empresa_id == usuario_atual.empresa_id)
    
    if evento_id:
        query = query.filter(Produto.evento_id == evento_id)
    
    produtos_alerta = query.all()
    
    alertas = []
    for produto in produtos_alerta:
        if produto.quantidade_estoque == 0:
            tipo_alerta = "sem_estoque"
            severidade = "alta"
            mensagem = f"Produto {produto.nome} está sem estoque"
        else:
            tipo_alerta = "estoque_baixo"
            severidade = "media"
            mensagem = f"Produto {produto.nome} com estoque baixo ({produto.quantidade_estoque} unidades)"
        
        alertas.append(AlertaEstoque(
            produto_id=produto.id,
            produto_nome=produto.nome,
            produto_codigo=produto.codigo,
            quantidade_atual=produto.quantidade_estoque,
            estoque_minimo=produto.estoque_minimo,
            tipo_alerta=tipo_alerta,
            severidade=severidade,
            mensagem=mensagem,
            gerado_em=datetime.now()
        ))
    
    return alertas

@router.get("/inventario", response_model=InventarioResponse)
async def realizar_inventario(
    evento_id: Optional[int] = None,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Realizar inventário completo"""
    
    query = db.query(Produto).filter(Produto.ativo == True)
    
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Produto.empresa_id == usuario_atual.empresa_id)
    
    if evento_id:
        query = query.filter(Produto.evento_id == evento_id)
    
    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)
    
    produtos = query.all()
    
    # Calcular totais
    total_produtos = len(produtos)
    valor_total_estoque = sum(
        produto.quantidade_estoque * produto.preco_custo 
        for produto in produtos 
        if produto.preco_custo
    )
    
    produtos_sem_estoque = len([p for p in produtos if p.quantidade_estoque == 0])
    produtos_estoque_baixo = len([p for p in produtos if 0 < p.quantidade_estoque <= p.estoque_minimo])
    
    # Itens do inventário
    itens_inventario = []
    for produto in produtos:
        valor_total_item = produto.quantidade_estoque * (produto.preco_custo or 0)
        
        itens_inventario.append({
            "produto_id": produto.id,
            "nome": produto.nome,
            "codigo": produto.codigo,
            "categoria": produto.categoria.nome if produto.categoria else None,
            "quantidade_estoque": produto.quantidade_estoque,
            "estoque_minimo": produto.estoque_minimo,
            "preco_custo": float(produto.preco_custo or 0),
            "preco_venda": float(produto.preco_venda),
            "valor_total_item": float(valor_total_item),
            "status": "normal" if produto.quantidade_estoque > produto.estoque_minimo 
                     else "baixo" if produto.quantidade_estoque > 0 
                     else "sem_estoque"
        })
    
    return InventarioResponse(
        total_produtos=total_produtos,
        valor_total_estoque=float(valor_total_estoque),
        produtos_sem_estoque=produtos_sem_estoque,
        produtos_estoque_baixo=produtos_estoque_baixo,
        itens_inventario=itens_inventario,
        data_inventario=datetime.now(),
        evento_id=evento_id,
        categoria_id=categoria_id
    )

# IMPORTAÇÃO/EXPORTAÇÃO

@router.post("/importar-produtos")
async def importar_produtos_csv(
    arquivo: UploadFile = File(...),
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Importar produtos de arquivo CSV"""
    
    if usuario_atual.tipo.value not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    if not arquivo.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")
    
    try:
        # Ler conteúdo do arquivo
        conteudo = await arquivo.read()
        csv_data = io.StringIO(conteudo.decode('utf-8'))
        reader = csv.DictReader(csv_data)
        
        produtos_criados = []
        erros = []
        
        for linha_num, linha in enumerate(reader, 1):
            try:
                # Validar campos obrigatórios
                campos_obrigatorios = ['nome', 'codigo', 'preco_venda']
                for campo in campos_obrigatorios:
                    if not linha.get(campo):
                        raise ValueError(f"Campo obrigatório '{campo}' não informado")
                
                # Verificar se produto já existe
                produto_existente = db.query(Produto).filter(
                    Produto.codigo == linha['codigo'],
                    Produto.empresa_id == usuario_atual.empresa_id
                ).first()
                
                if produto_existente:
                    erros.append(f"Linha {linha_num}: Produto com código {linha['codigo']} já existe")
                    continue
                
                # Buscar categoria se informada
                categoria_id = None
                if linha.get('categoria'):
                    categoria = db.query(Categoria).filter(
                        Categoria.nome == linha['categoria'],
                        Categoria.empresa_id == usuario_atual.empresa_id
                    ).first()
                    if categoria:
                        categoria_id = categoria.id
                
                # Criar produto
                produto = Produto(
                    nome=linha['nome'],
                    descricao=linha.get('descricao', ''),
                    codigo=linha['codigo'],
                    preco_venda=Decimal(linha['preco_venda']),
                    preco_custo=Decimal(linha.get('preco_custo', 0)),
                    quantidade_estoque=int(linha.get('quantidade_estoque', 0)),
                    estoque_minimo=int(linha.get('estoque_minimo', 5)),
                    categoria_id=categoria_id,
                    evento_id=evento_id,
                    empresa_id=usuario_atual.empresa_id,
                    criado_por_id=usuario_atual.id,
                    unidade_medida=linha.get('unidade_medida', 'unidade'),
                    ativo=linha.get('ativo', 'true').lower() == 'true'
                )
                
                db.add(produto)
                produtos_criados.append(produto.nome)
                
            except Exception as e:
                erros.append(f"Linha {linha_num}: {str(e)}")
        
        if produtos_criados:
            db.commit()
        
        return {
            "produtos_criados": len(produtos_criados),
            "produtos_com_erro": len(erros),
            "lista_criados": produtos_criados,
            "erros": erros
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar arquivo: {str(e)}")

@router.get("/exportar-estoque")
async def exportar_estoque_csv(
    evento_id: Optional[int] = None,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Exportar estoque em formato CSV"""
    
    query = db.query(Produto)
    
    if usuario_atual.tipo.value != "admin":
        query = query.filter(Produto.empresa_id == usuario_atual.empresa_id)
    
    if evento_id:
        query = query.filter(Produto.evento_id == evento_id)
    
    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)
    
    produtos = query.all()
    
    # Criar CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow([
        'ID', 'Nome', 'Código', 'Descrição', 'Categoria',
        'Preço Venda', 'Preço Custo', 'Quantidade Estoque',
        'Estoque Mínimo', 'Unidade Medida', 'Ativo'
    ])
    
    # Dados
    for produto in produtos:
        writer.writerow([
            produto.id,
            produto.nome,
            produto.codigo,
            produto.descricao or '',
            produto.categoria.nome if produto.categoria else '',
            float(produto.preco_venda),
            float(produto.preco_custo or 0),
            produto.quantidade_estoque,
            produto.estoque_minimo,
            produto.unidade_medida,
            produto.ativo
        ])
    
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=estoque_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )

@router.post("/ajustar-estoque/{produto_id}")
async def ajustar_estoque_produto(
    produto_id: int,
    quantidade_nova: int,
    motivo: str,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_active_user)
):
    """Ajustar estoque de um produto específico"""
    
    if usuario_atual.tipo.value not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    if (usuario_atual.tipo.value != "admin" and 
        produto.empresa_id != usuario_atual.empresa_id):
        raise HTTPException(status_code=403, detail="Produto não pertence à sua empresa")
    
    quantidade_anterior = produto.quantidade_estoque
    diferenca = quantidade_nova - quantidade_anterior
    
    if diferenca == 0:
        raise HTTPException(status_code=400, detail="Nova quantidade é igual à atual")
    
    estoque_service = EstoqueService(db)
    
    try:
        # Registrar movimento de ajuste
        await estoque_service.registrar_movimento(
            produto_id=produto_id,
            tipo_movimento="ajuste",
            quantidade=abs(diferenca),
            motivo=f"Ajuste manual: {motivo}",
            usuario_id=usuario_atual.id
        )
        
        return {
            "produto_id": produto_id,
            "quantidade_anterior": quantidade_anterior,
            "quantidade_nova": quantidade_nova,
            "diferenca": diferenca,
            "tipo_ajuste": "entrada" if diferenca > 0 else "saida",
            "motivo": motivo,
            "ajustado_em": datetime.now()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
