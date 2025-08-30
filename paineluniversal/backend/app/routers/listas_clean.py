from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
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

def get_current_user():
    return MockUsuario()

def get_db():
    return None

# Pydantic Models
class ListaCreate(BaseModel):
    nome: str
    tipo: str = "lista"
    preco: float
    limite_vendas: Optional[int] = None
    descricao: Optional[str] = None
    evento_id: int

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
    criado_em: datetime

# Mock data
mock_listas = {}
mock_eventos = {
    1: {"id": 1, "nome": "Evento 1"},
    2: {"id": 2, "nome": "Evento 2"}
}

@router.post("/", response_model=ListaResponse)
async def criar_lista(
    lista: ListaCreate,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Criar nova lista"""
    
    if lista.preco < 0:
        raise HTTPException(status_code=400, detail="Preço não pode ser negativo")
    
    if lista.evento_id not in mock_eventos:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
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
        evento_nome=mock_eventos[nova_lista["evento_id"]]["nome"],
        criado_em=nova_lista["criado_em"]
    )

@router.get("/", response_model=List[ListaResponse])
async def listar_listas(
    evento_id: Optional[int] = None,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Listar listas"""
    
    listas = list(mock_listas.values())
    
    if evento_id:
        listas = [l for l in listas if l["evento_id"] == evento_id]
    
    return [ListaResponse(
        id=l["id"],
        nome=l["nome"],
        tipo=l["tipo"],
        preco=l["preco"],
        limite_vendas=l["limite_vendas"],
        vendas_realizadas=l["vendas_realizadas"],
        ativa=l["ativa"],
        evento_id=l["evento_id"],
        evento_nome=mock_eventos.get(l["evento_id"], {"nome": "Evento Desconhecido"})["nome"],
        criado_em=l["criado_em"]
    ) for l in listas]

@router.get("/{lista_id}", response_model=ListaResponse)
async def obter_lista(
    lista_id: int,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Obter lista por ID"""
    
    if lista_id not in mock_listas:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    lista = mock_listas[lista_id]
    
    return ListaResponse(
        id=lista["id"],
        nome=lista["nome"],
        tipo=lista["tipo"],
        preco=lista["preco"],
        limite_vendas=lista["limite_vendas"],
        vendas_realizadas=lista["vendas_realizadas"],
        ativa=lista["ativa"],
        evento_id=lista["evento_id"],
        evento_nome=mock_eventos.get(lista["evento_id"], {"nome": "Evento Desconhecido"})["nome"],
        criado_em=lista["criado_em"]
    )

@router.delete("/{lista_id}")
async def deletar_lista(
    lista_id: int,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Deletar lista"""
    
    if lista_id not in mock_listas:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    
    del mock_listas[lista_id]
    
    return {"mensagem": "Lista deletada com sucesso"}

@router.post("/validar-cupom")
async def validar_cupom(
    codigo_cupom: str,
    evento_id: int,
    db = Depends(get_db)
):
    """Validar código de cupom"""
    
    # Mock de validação
    return {
        "valido": True,
        "lista_id": 1,
        "nome_lista": "Lista VIP",
        "preco": 150.0,
        "desconto_percentual": 10.0,
        "vendas_restantes": 50
    }
