from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/listas", tags=["Listas"])

# Mock Models
class MockUsuario:
    def __init__(self):
        self.id = 1
        self.nome = "Admin Mock"
        self.tipo_usuario = "admin"
        self.empresa_id = 1

class MockEvento:
    def __init__(self, id: int):
        self.id = id
        self.nome = f"Evento {id}"
        self.empresa_id = 1

def get_current_user():
    return MockUsuario()

def get_db():
    return None

# Pydantic Models
class ListaCreate(BaseModel):
    nome: str
    tipo: str = "lista"  # lista, cupom, promocional
    preco: float
    limite_vendas: Optional[int] = None
    descricao: Optional[str] = None
    codigo_cupom: Optional[str] = None
    desconto_percentual: Optional[float] = 0.0
    evento_id: int
    promoter_id: Optional[int] = None

class ListaUpdate(BaseModel):
    nome: Optional[str] = None
    preco: Optional[float] = None
    limite_vendas: Optional[int] = None
    descricao: Optional[str] = None
    codigo_cupom: Optional[str] = None
    desconto_percentual: Optional[float] = None
    ativa: Optional[bool] = None

class ListaResponse(BaseModel):
    id: int
    nome: str
    tipo: str
    preco: float
    limite_vendas: Optional[int]
    vendas_realizadas: int
    ativa: bool
    evento_id: int
    evento_nome: str
    promoter_id: Optional[int]
    promoter_nome: Optional[str]
    descricao: Optional[str]
    codigo_cupom: Optional[str]
    desconto_percentual: float
    criado_em: datetime

class ListaDetalhada(ListaResponse):
    receita_total: float
    ticket_medio: float
    vendas_por_dia: Dict[str, Dict[str, Any]]
    top_compradores: List[Dict[str, Any]]
    disponivel_venda: bool

class ConvidadoLista(BaseModel):
    cpf: str
    nome: str
    email: str
    telefone: Optional[str]
    valor_pago: float
    data_compra: datetime
    metodo_pagamento: str
    codigo_transacao: str
    status: str

class RelatorioLista(BaseModel):
    lista_id: int
    nome_lista: str
    evento_nome: str
    promoter_nome: str
    total_vendas: int
    receita_total: float
    ticket_medio: float
    limite_vendas: Optional[int]
    disponibilidade: Optional[int]
    taxa_ocupacao: float
    vendas_por_metodo: Dict[str, Dict[str, Any]]
    taxa_conversao: float
    posicao_ranking: int
    total_listas_evento: int
    gerado_em: datetime

# Mock data
mock_listas = {}
mock_vendas = {}
mock_eventos = {
    1: MockEvento(1),
    2: MockEvento(2)
}

@router.post("/", response_model=ListaResponse)
async def criar_lista(
    lista: ListaCreate,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Criar nova lista"""
    
    # Validações básicas
    if lista.preco < 0:
        raise HTTPException(status_code=400, detail="Preço não pode ser negativo")
    
    if lista.limite_vendas and lista.limite_vendas < 1:
        raise HTTPException(status_code=400, detail="Limite de vendas deve ser maior que zero")
    
    # Verificar se evento existe
    if lista.evento_id not in mock_eventos:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Verificar se já existe lista com mesmo nome
    for l in mock_listas.values():
        if l["evento_id"] == lista.evento_id and l["nome"] == lista.nome:
            raise HTTPException(
                status_code=400,
                detail="Já existe uma lista com este nome para este evento"
            )
    
    # Gerar código cupom se necessário
    codigo_cupom = None
    if lista.tipo == "cupom" and not lista.codigo_cupom:
        codigo_cupom = f"CUP{str(uuid.uuid4())[:8].upper()}"
    elif lista.codigo_cupom:
        codigo_cupom = lista.codigo_cupom.upper()
    
    # Criar lista
    lista_id = len(mock_listas) + 1
    nova_lista = {
        "id": lista_id,
        "nome": lista.nome,
        "tipo": lista.tipo,
        "preco": lista.preco,
        "limite_vendas": lista.limite_vendas,
        "vendas_realizadas": 0,
        "ativa": True,
        "evento_id": lista.evento_id,
        "promoter_id": lista.promoter_id or usuario_atual.id,
        "descricao": lista.descricao,
        "codigo_cupom": codigo_cupom,
        "desconto_percentual": lista.desconto_percentual or 0.0,
        "criado_em": datetime.now()
    }
    
    mock_listas[lista_id] = nova_lista
    
    return ListaResponse(
        id=nova_lista["id"],
        nome=nova_lista["nome"],
        tipo=nova_lista["tipo"],
        preco=nova_lista["preco"],
        limite_vendas=nova_lista["limite_vendas"],
        vendas_realizadas=nova_lista["vendas_realizadas"],
        ativa=nova_lista["ativa"],
        evento_id=nova_lista["evento_id"],
        evento_nome=mock_eventos[nova_lista["evento_id"]].nome,
        promoter_id=nova_lista["promoter_id"],
        promoter_nome=usuario_atual.nome,
        descricao=nova_lista["descricao"],
        codigo_cupom=nova_lista["codigo_cupom"],
        desconto_percentual=nova_lista["desconto_percentual"],
        criado_em=nova_lista["criado_em"]
    )

@router.get("/", response_model=List[ListaResponse])
async def listar_listas(
    evento_id: Optional[int] = None,
    tipo: Optional[str] = None,
    ativa: Optional[bool] = None,
    promoter_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Listar listas com filtros"""
    
    listas = list(mock_listas.values())
    
    # Aplicar filtros
    if evento_id:
        listas = [l for l in listas if l["evento_id"] == evento_id]
    
    if tipo:
        listas = [l for l in listas if l["tipo"] == tipo]
    
    if ativa is not None:
        listas = [l for l in listas if l["ativa"] == ativa]
    
    if promoter_id:
        listas = [l for l in listas if l["promoter_id"] == promoter_id]
    
    # Paginação
    listas = listas[skip:skip + limit]
    
    return [ListaResponse(
        id=l["id"],
        nome=l["nome"],
        tipo=l["tipo"],
        preco=l["preco"],
        limite_vendas=l["limite_vendas"],
        vendas_realizadas=l["vendas_realizadas"],
        ativa=l["ativa"],
        evento_id=l["evento_id"],
        evento_nome=mock_eventos.get(l["evento_id"], MockEvento(l["evento_id"])).nome,
        promoter_id=l["promoter_id"],
        promoter_nome=usuario_atual.nome,
        descricao=l["descricao"],
        codigo_cupom=l["codigo_cupom"],
        desconto_percentual=l["desconto_percentual"],
        criado_em=l["criado_em"]
    ) for l in listas]

@router.get("/{lista_id}", response_model=ListaDetalhada)
async def obter_lista(
    lista_id: int,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Obter detalhes de uma lista"""
    
    if lista_id not in mock_listas:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    lista = mock_listas[lista_id]
    
    # Mock de vendas
    vendas_lista = mock_vendas.get(lista_id, [])
    receita_total = sum(v["valor"] for v in vendas_lista)
    
    # Mock de dados para demonstração
    vendas_por_dia = {
        (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"): {
            "quantidade": max(0, 10 - i),
            "receita": max(0, 500 - i * 50)
        }
        for i in range(7)
    }
    
    top_compradores = [
        {
            "cpf": "12345678901",
            "nome": "João Silva",
            "total_compras": 3,
            "valor_total": 450.0
        },
        {
            "cpf": "98765432109",
            "nome": "Maria Santos",
            "total_compras": 2,
            "valor_total": 300.0
        }
    ]
    
    return ListaDetalhada(
        id=lista["id"],
        nome=lista["nome"],
        tipo=lista["tipo"],
        preco=lista["preco"],
        limite_vendas=lista["limite_vendas"],
        vendas_realizadas=lista["vendas_realizadas"],
        ativa=lista["ativa"],
        evento_id=lista["evento_id"],
        evento_nome=mock_eventos.get(lista["evento_id"], MockEvento(lista["evento_id"])).nome,
        promoter_id=lista["promoter_id"],
        promoter_nome=usuario_atual.nome,
        descricao=lista["descricao"],
        codigo_cupom=lista["codigo_cupom"],
        desconto_percentual=lista["desconto_percentual"],
        criado_em=lista["criado_em"],
        receita_total=receita_total,
        ticket_medio=receita_total / len(vendas_lista) if vendas_lista else 0,
        vendas_por_dia=vendas_por_dia,
        top_compradores=top_compradores,
        disponivel_venda=lista["ativa"] and (
            not lista["limite_vendas"] or lista["vendas_realizadas"] < lista["limite_vendas"]
        )
    )

@router.put("/{lista_id}", response_model=ListaResponse)
async def atualizar_lista(
    lista_id: int,
    lista_update: ListaUpdate,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Atualizar lista"""
    
    if lista_id not in mock_listas:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    lista = mock_listas[lista_id]
    
    # Validações
    if lista_update.preco is not None and lista_update.preco < 0:
        raise HTTPException(status_code=400, detail="Preço não pode ser negativo")
    
    if (lista_update.limite_vendas is not None and 
        lista_update.limite_vendas < lista["vendas_realizadas"]):
        raise HTTPException(
            status_code=400,
            detail=f"Limite não pode ser menor que vendas já realizadas ({lista['vendas_realizadas']})"
        )
    
    # Atualizar campos
    for field, value in lista_update.dict(exclude_unset=True).items():
        if value is not None:
            lista[field] = value
    
    return ListaResponse(
        id=lista["id"],
        nome=lista["nome"],
        tipo=lista["tipo"],
        preco=lista["preco"],
        limite_vendas=lista["limite_vendas"],
        vendas_realizadas=lista["vendas_realizadas"],
        ativa=lista["ativa"],
        evento_id=lista["evento_id"],
        evento_nome=mock_eventos.get(lista["evento_id"], MockEvento(lista["evento_id"])).nome,
        promoter_id=lista["promoter_id"],
        promoter_nome=usuario_atual.nome,
        descricao=lista["descricao"],
        codigo_cupom=lista["codigo_cupom"],
        desconto_percentual=lista["desconto_percentual"],
        criado_em=lista["criado_em"]
    )

@router.post("/{lista_id}/toggle-ativa")
async def toggle_ativa_lista(
    lista_id: int,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Ativar/desativar lista"""
    
    if lista_id not in mock_listas:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    lista = mock_listas[lista_id]
    lista["ativa"] = not lista["ativa"]
    
    status_texto = "ativada" if lista["ativa"] else "desativada"
    return {"mensagem": f"Lista {status_texto} com sucesso"}

@router.get("/{lista_id}/convidados", response_model=List[ConvidadoLista])
async def listar_convidados_lista(
    lista_id: int,
    skip: int = 0,
    limit: int = 100,
    busca: Optional[str] = None,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Listar convidados/compradores de uma lista"""
    
    if lista_id not in mock_listas:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    # Mock de convidados
    convidados = [
        ConvidadoLista(
            cpf="12345678901",
            nome="João Silva",
            email="joao@email.com",
            telefone="67999999999",
            valor_pago=150.0,
            data_compra=datetime.now() - timedelta(days=2),
            metodo_pagamento="PIX",
            codigo_transacao="TXN001",
            status="presente"
        ),
        ConvidadoLista(
            cpf="98765432109",
            nome="Maria Santos",
            email="maria@email.com",
            telefone="67888888888",
            valor_pago=150.0,
            data_compra=datetime.now() - timedelta(days=1),
            metodo_pagamento="Cartão",
            codigo_transacao="TXN002",
            status="ausente"
        )
    ]
    
    # Aplicar filtro de busca se necessário
    if busca:
        convidados = [
            c for c in convidados 
            if busca.lower() in c.nome.lower() or busca in c.cpf or busca.lower() in c.email.lower()
        ]
    
    return convidados[skip:skip + limit]

@router.post("/{lista_id}/duplicar", response_model=ListaResponse)
async def duplicar_lista(
    lista_id: int,
    novo_nome: str,
    evento_id: Optional[int] = None,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Duplicar lista para outro evento ou mesmo evento"""
    
    if lista_id not in mock_listas:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    lista_original = mock_listas[lista_id]
    evento_destino_id = evento_id or lista_original["evento_id"]
    
    # Verificar se evento destino existe
    if evento_destino_id not in mock_eventos:
        raise HTTPException(status_code=404, detail="Evento destino não encontrado")
    
    # Verificar se nome já existe no evento destino
    for l in mock_listas.values():
        if l["evento_id"] == evento_destino_id and l["nome"] == novo_nome:
            raise HTTPException(
                status_code=400,
                detail="Já existe uma lista com este nome no evento destino"
            )
    
    # Criar nova lista
    nova_lista_id = max(mock_listas.keys()) + 1 if mock_listas else 1
    nova_lista = {
        "id": nova_lista_id,
        "nome": novo_nome,
        "tipo": lista_original["tipo"],
        "preco": lista_original["preco"],
        "limite_vendas": lista_original["limite_vendas"],
        "vendas_realizadas": 0,
        "ativa": True,
        "evento_id": evento_destino_id,
        "promoter_id": lista_original["promoter_id"],
        "descricao": f"Duplicada de: {lista_original['nome']}",
        "codigo_cupom": f"CUP{str(uuid.uuid4())[:8].upper()}" if lista_original["codigo_cupom"] else None,
        "desconto_percentual": lista_original["desconto_percentual"],
        "criado_em": datetime.now()
    }
    
    mock_listas[nova_lista_id] = nova_lista
    
    return ListaResponse(
        id=nova_lista["id"],
        nome=nova_lista["nome"],
        tipo=nova_lista["tipo"],
        preco=nova_lista["preco"],
        limite_vendas=nova_lista["limite_vendas"],
        vendas_realizadas=nova_lista["vendas_realizadas"],
        ativa=nova_lista["ativa"],
        evento_id=nova_lista["evento_id"],
        evento_nome=mock_eventos[nova_lista["evento_id"]].nome,
        promoter_id=nova_lista["promoter_id"],
        promoter_nome=usuario_atual.nome,
        descricao=nova_lista["descricao"],
        codigo_cupom=nova_lista["codigo_cupom"],
        desconto_percentual=nova_lista["desconto_percentual"],
        criado_em=nova_lista["criado_em"]
    )

@router.get("/{lista_id}/relatorio", response_model=RelatorioLista)
async def gerar_relatorio_lista(
    lista_id: int,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Gerar relatório completo da lista"""
    
    if lista_id not in mock_listas:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    lista = mock_listas[lista_id]
    
    # Mock de dados para demonstração
    vendas_por_metodo = {
        "PIX": {"quantidade": 15, "valor": 2250.0},
        "Cartão": {"quantidade": 10, "valor": 1500.0},
        "Dinheiro": {"quantidade": 5, "valor": 750.0}
    }
    
    return RelatorioLista(
        lista_id=lista["id"],
        nome_lista=lista["nome"],
        evento_nome=mock_eventos[lista["evento_id"]].nome,
        promoter_nome=usuario_atual.nome,
        total_vendas=30,
        receita_total=4500.0,
        ticket_medio=150.0,
        limite_vendas=lista["limite_vendas"],
        disponibilidade=lista["limite_vendas"] - 30 if lista["limite_vendas"] else None,
        taxa_ocupacao=60.0 if lista["limite_vendas"] else 0,
        vendas_por_metodo=vendas_por_metodo,
        taxa_conversao=75.0,
        posicao_ranking=1,
        total_listas_evento=3,
        gerado_em=datetime.now()
    )

@router.post("/validar-cupom")
async def validar_cupom(
    codigo_cupom: str,
    evento_id: int,
    db = Depends(get_db)
):
    """Validar código de cupom"""
    
    # Buscar cupom
    cupom_encontrado = None
    for lista in mock_listas.values():
        if (lista["codigo_cupom"] == codigo_cupom.upper() and 
            lista["evento_id"] == evento_id and 
            lista["ativa"]):
            cupom_encontrado = lista
            break
    
    if not cupom_encontrado:
        raise HTTPException(status_code=404, detail="Cupom não encontrado ou inativo")
    
    # Verificar se ainda tem vendas disponíveis
    if (cupom_encontrado["limite_vendas"] and 
        cupom_encontrado["vendas_realizadas"] >= cupom_encontrado["limite_vendas"]):
        raise HTTPException(status_code=400, detail="Cupom esgotado")
    
    return {
        "valido": True,
        "lista_id": cupom_encontrado["id"],
        "nome_lista": cupom_encontrado["nome"],
        "preco": cupom_encontrado["preco"],
        "desconto_percentual": cupom_encontrado["desconto_percentual"],
        "vendas_restantes": (
            cupom_encontrado["limite_vendas"] - cupom_encontrado["vendas_realizadas"]
        ) if cupom_encontrado["limite_vendas"] else None
    }

@router.get("/cupons/{evento_id}")
async def listar_cupons_evento(
    evento_id: int,
    ativo: Optional[bool] = None,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Listar cupons de um evento"""
    
    if evento_id not in mock_eventos:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    cupons = [
        l for l in mock_listas.values() 
        if l["evento_id"] == evento_id and l["codigo_cupom"] is not None
    ]
    
    if ativo is not None:
        cupons = [c for c in cupons if c["ativa"] == ativo]
    
    return [
        {
            "lista_id": c["id"],
            "nome": c["nome"],
            "codigo_cupom": c["codigo_cupom"],
            "preco": c["preco"],
            "desconto_percentual": c["desconto_percentual"],
            "limite_vendas": c["limite_vendas"],
            "vendas_realizadas": c["vendas_realizadas"],
            "ativo": c["ativa"],
            "vendas_restantes": (
                c["limite_vendas"] - c["vendas_realizadas"]
            ) if c["limite_vendas"] else None
        }
        for c in cupons
    ]

# Endpoint adicional para simular uma compra
@router.post("/{lista_id}/simular-compra")
async def simular_compra(
    lista_id: int,
    cpf_comprador: str,
    nome_comprador: str,
    quantidade: int = 1,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Simular uma compra para teste"""
    
    if lista_id not in mock_listas:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    lista = mock_listas[lista_id]
    
    # Verificar disponibilidade
    if not lista["ativa"]:
        raise HTTPException(status_code=400, detail="Lista não está ativa")
    
    if (lista["limite_vendas"] and 
        lista["vendas_realizadas"] + quantidade > lista["limite_vendas"]):
        raise HTTPException(status_code=400, detail="Limite de vendas excedido")
    
    # Simular venda
    lista["vendas_realizadas"] += quantidade
    
    # Adicionar à lista de vendas
    if lista_id not in mock_vendas:
        mock_vendas[lista_id] = []
    
    mock_vendas[lista_id].append({
        "cpf": cpf_comprador,
        "nome": nome_comprador,
        "valor": lista["preco"] * quantidade,
        "data": datetime.now(),
        "quantidade": quantidade
    })
    
    return {
        "mensagem": "Compra simulada com sucesso",
        "valor_total": lista["preco"] * quantidade,
        "vendas_restantes": (
            lista["limite_vendas"] - lista["vendas_realizadas"]
        ) if lista["limite_vendas"] else None
    }
