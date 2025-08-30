from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import aiohttp
import asyncio
import uuid

from ..database import get_db
from ..auth import obter_usuario_atual
from ..models import Usuario, Tablet, TabletLog, ConfiguracaoMeep
from ..schemas import (
    TabletCreate, TabletResponse, TabletUpdate,
    TabletLogResponse, ConfiguracaoMeepResponse,
    TipoTablet, StatusTablet
)

router = APIRouter(prefix="/api/tablets", tags=["tablets"])


@router.post("/", response_model=TabletResponse)
async def criar_tablet(
    tablet_data: TabletCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Criar um novo tablet"""
    
    tablet_existente = db.query(Tablet).filter(
        Tablet.ip == tablet_data.ip,
        Tablet.porta == tablet_data.porta,
        Tablet.empresa_id == usuario_atual.empresa_id
    ).first()
    
    if tablet_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um tablet com este IP e porta"
        )
    
    novo_tablet = Tablet(
        id=str(uuid.uuid4()),
        nome=tablet_data.nome,
        ip=tablet_data.ip,
        porta=tablet_data.porta,
        tipo=tablet_data.tipo,
        empresa_id=usuario_atual.empresa_id
    )
    
    db.add(novo_tablet)
    db.commit()
    db.refresh(novo_tablet)
    
    log = TabletLog(
        id=str(uuid.uuid4()),
        tablet_id=novo_tablet.id,
        evento="criacao",
        detalhes=f"Tablet {novo_tablet.nome} criado por {usuario_atual.nome}"
    )
    db.add(log)
    db.commit()
    
    return novo_tablet

@router.get("/", response_model=List[TabletResponse])
async def listar_tablets(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar todos os tablets da empresa"""
    tablets = db.query(Tablet).filter(
        Tablet.empresa_id == usuario_atual.empresa_id
    ).all()
    
    return tablets

@router.get("/{tablet_id}", response_model=TabletResponse)
async def obter_tablet(
    tablet_id: str,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter detalhes de um tablet específico"""
    tablet = db.query(Tablet).filter(
        Tablet.id == tablet_id,
        Tablet.empresa_id == usuario_atual.empresa_id
    ).first()
    
    if not tablet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablet não encontrado"
        )
    
    return tablet

@router.put("/{tablet_id}", response_model=TabletResponse)
async def atualizar_tablet(
    tablet_id: str,
    tablet_data: TabletUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Atualizar dados de um tablet"""
    tablet = db.query(Tablet).filter(
        Tablet.id == tablet_id,
        Tablet.empresa_id == usuario_atual.empresa_id
    ).first()
    
    if not tablet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablet não encontrado"
        )
    
    for field, value in tablet_data.dict(exclude_unset=True).items():
        setattr(tablet, field, value)
    
    tablet.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(tablet)
    
    log = TabletLog(
        id=str(uuid.uuid4()),
        tablet_id=tablet.id,
        evento="atualizacao",
        detalhes=f"Tablet {tablet.nome} atualizado por {usuario_atual.nome}"
    )
    db.add(log)
    db.commit()
    
    return tablet

@router.delete("/{tablet_id}")
async def deletar_tablet(
    tablet_id: str,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Deletar um tablet"""
    tablet = db.query(Tablet).filter(
        Tablet.id == tablet_id,
        Tablet.empresa_id == usuario_atual.empresa_id
    ).first()
    
    if not tablet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablet não encontrado"
        )
    
    log = TabletLog(
        id=str(uuid.uuid4()),
        tablet_id=tablet.id,
        evento="exclusao",
        detalhes=f"Tablet {tablet.nome} excluído por {usuario_atual.nome}"
    )
    db.add(log)
    
    db.delete(tablet)
    db.commit()
    
    return {"message": "Tablet excluído com sucesso"}


@router.post("/integrate")
async def integrar_tablet(
    integration_data: dict,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Integrar tablet com sistema MEEP"""
    
    tablet_info = integration_data.get("tablet", {})
    tablet_id = tablet_info.get("id")
    
    if not tablet_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID do tablet é obrigatório"
        )
    
    tablet = db.query(Tablet).filter(
        Tablet.id == tablet_id,
        Tablet.empresa_id == usuario_atual.empresa_id
    ).first()
    
    if not tablet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablet não encontrado"
        )
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://{tablet.ip}:{tablet.porta}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    tablet.status = "conectado"
                    tablet.ultima_conexao = datetime.utcnow()
                    
                    log = TabletLog(
                        id=str(uuid.uuid4()),
                        tablet_id=tablet.id,
                        evento="integracao",
                        detalhes=f"Tablet {tablet.nome} integrado com sucesso"
                    )
                    db.add(log)
                    db.commit()
                    db.refresh(tablet)
                    
                    return {
                        "success": True,
                        "message": "Tablet integrado com sucesso",
                        "tablet": tablet
                    }
                else:
                    tablet.status = "desconectado"
                    db.commit()
                    
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Tablet não responde"
                    )
            
    except aiohttp.ClientError as e:
        tablet.status = "desconectado"
        db.commit()
        
        log = TabletLog(
            id=str(uuid.uuid4()),
            tablet_id=tablet.id,
            evento="erro",
            detalhes=f"Erro na integração do tablet {tablet.nome}: {str(e)}"
        )
        db.add(log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao conectar com tablet: {str(e)}"
        )

@router.post("/{tablet_id}/sync-config")
async def sincronizar_configuracao(
    tablet_id: str,
    config_data: dict,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Sincronizar configuração com tablet"""
    
    tablet = db.query(Tablet).filter(
        Tablet.id == tablet_id,
        Tablet.empresa_id == usuario_atual.empresa_id
    ).first()
    
    if not tablet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablet não encontrado"
        )
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{tablet.ip}:{tablet.porta}/api/sync-config",
                json=config_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    tablet.ultima_conexao = datetime.utcnow()
                    
                    log = TabletLog(
                        id=str(uuid.uuid4()),
                        tablet_id=tablet.id,
                        evento="sincronizacao",
                        detalhes=f"Configuração sincronizada com tablet {tablet.nome}"
                    )
                    db.add(log)
                    db.commit()
                    
                    return {
                        "success": True,
                        "message": "Configuração sincronizada com sucesso"
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Erro na sincronização"
                    )
            
    except aiohttp.ClientError as e:
        log = TabletLog(
            id=str(uuid.uuid4()),
            tablet_id=tablet.id,
            evento="erro",
            detalhes=f"Erro na sincronização do tablet {tablet.nome}: {str(e)}"
        )
        db.add(log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao sincronizar com tablet: {str(e)}"
        )

@router.get("/{tablet_id}/status")
async def verificar_status_tablet(
    tablet_id: str,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Verificar status de conexão do tablet"""
    
    tablet = db.query(Tablet).filter(
        Tablet.id == tablet_id,
        Tablet.empresa_id == usuario_atual.empresa_id
    ).first()
    
    if not tablet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablet não encontrado"
        )
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://{tablet.ip}:{tablet.porta}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    tablet.status = "conectado"
                    tablet.ultima_conexao = datetime.utcnow()
                    status_online = True
                else:
                    tablet.status = "desconectado"
                    status_online = False
            
    except aiohttp.ClientError:
        tablet.status = "desconectado"
        status_online = False
    
    db.commit()
    
    return {
        "tablet_id": tablet.id,
        "nome": tablet.nome,
        "ip": tablet.ip,
        "porta": tablet.porta,
        "status": tablet.status,
        "online": status_online,
        "ultima_conexao": tablet.ultima_conexao
    }


@router.get("/{tablet_id}/logs", response_model=List[TabletLogResponse])
async def obter_logs_tablet(
    tablet_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obter logs de um tablet"""
    
    tablet = db.query(Tablet).filter(
        Tablet.id == tablet_id,
        Tablet.empresa_id == usuario_atual.empresa_id
    ).first()
    
    if not tablet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablet não encontrado"
        )
    
    logs = db.query(TabletLog).filter(
        TabletLog.tablet_id == tablet_id
    ).order_by(TabletLog.timestamp.desc()).limit(limit).all()
    
    return logs

@router.get("/configuracoes-meep", response_model=List[ConfiguracaoMeepResponse])
async def listar_configuracoes_meep(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Listar configurações MEEP da empresa"""
    
    configs = db.query(ConfiguracaoMeep).all()
    
    return configs
