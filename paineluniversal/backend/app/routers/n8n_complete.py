from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import json
import asyncio
import uuid

router = APIRouter(prefix="/n8n", tags=["N8N Automação"])

# Mock Models
class MockUsuario:
    def __init__(self):
        self.id = 1
        self.nome = "Admin Mock"
        self.tipo_usuario = "admin"
        self.empresa_id = 1

def get_current_user():
    return MockUsuario()

def verify_admin():
    return MockUsuario()

def get_db():
    return None

# Modelos para requests
class ConfigurarN8N(BaseModel):
    base_url: str
    api_key: str
    webhook_secret: Optional[str] = None
    ativo: bool = True

class CriarTrigger(BaseModel):
    nome: str
    evento_tipo: str
    webhook_url: str
    filtros: Optional[Dict[str, Any]] = None
    ativo: bool = True

class ExecutarWorkflow(BaseModel):
    workflow_id: str
    dados: Dict[str, Any]
    prioridade: int = 1

# Configuração global N8N
N8N_CONFIG = {
    "base_url": None,
    "api_key": None,
    "webhook_secret": None,
    "ativo": False
}

# Mock data storage
mock_triggers = {}
mock_execucoes = {}

@router.post("/configurar")
async def configurar_n8n(
    config: ConfigurarN8N,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(verify_admin)
):
    """Configurar integração com N8N"""
    
    try:
        # Mock do teste de conexão
        teste_conexao = True
        
        if not teste_conexao:
            raise HTTPException(
                status_code=400,
                detail="Erro ao conectar com N8N. Verifique URL e API Key."
            )
        
        # Salvar configuração
        N8N_CONFIG.update({
            "base_url": config.base_url.rstrip('/'),
            "api_key": config.api_key,
            "webhook_secret": config.webhook_secret,
            "ativo": config.ativo
        })
        
        return {
            "mensagem": "N8N configurado com sucesso",
            "status_conexao": "ativo",
            "base_url": config.base_url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao configurar N8N: {str(e)}"
        )

@router.get("/workflows")
async def listar_workflows(
    ativo: Optional[bool] = None,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Listar workflows disponíveis no N8N"""
    
    if not N8N_CONFIG["ativo"]:
        raise HTTPException(
            status_code=400,
            detail="N8N não está configurado ou ativo"
        )
    
    # Mock de workflows
    workflows = [
        {
            "id": "workflow_1",
            "name": "Enviar Email Nova Transação",
            "active": True,
            "createdAt": "2024-01-15T10:00:00Z",
            "updatedAt": "2024-01-20T14:30:00Z",
            "tags": ["vendas", "email"]
        },
        {
            "id": "workflow_2",
            "name": "WhatsApp Check-in",
            "active": True,
            "createdAt": "2024-01-10T09:00:00Z",
            "updatedAt": "2024-01-18T16:45:00Z",
            "tags": ["checkin", "whatsapp"]
        },
        {
            "id": "workflow_3",
            "name": "Backup Dados Evento",
            "active": False,
            "createdAt": "2024-01-05T08:00:00Z",
            "updatedAt": "2024-01-12T11:20:00Z",
            "tags": ["backup", "dados"]
        }
    ]
    
    if ativo is not None:
        workflows = [w for w in workflows if w.get("active") == ativo]
    
    return {
        "total": len(workflows),
        "workflows": [
            {
                "id": w["id"],
                "nome": w["name"],
                "ativo": w.get("active", False),
                "criado_em": w.get("createdAt"),
                "atualizado_em": w.get("updatedAt"),
                "tags": w.get("tags", [])
            }
            for w in workflows
        ]
    }

@router.post("/executar-workflow")
async def executar_workflow(
    dados: ExecutarWorkflow,
    background_tasks: BackgroundTasks,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Executar workflow específico no N8N"""
    
    if usuario_atual.tipo_usuario not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    if not N8N_CONFIG["ativo"]:
        raise HTTPException(
            status_code=400,
            detail="N8N não está configurado ou ativo"
        )
    
    contexto_execucao = {
        "usuario_id": usuario_atual.id,
        "usuario_nome": usuario_atual.nome,
        "empresa_id": usuario_atual.empresa_id,
        "timestamp": datetime.now().isoformat(),
        **dados.dados
    }
    
    background_tasks.add_task(
        executar_workflow_background,
        dados.workflow_id,
        contexto_execucao,
        dados.prioridade
    )
    
    return {
        "mensagem": "Workflow adicionado à fila de execução",
        "workflow_id": dados.workflow_id,
        "prioridade": dados.prioridade
    }

@router.post("/triggers")
async def criar_trigger(
    trigger: CriarTrigger,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(verify_admin)
):
    """Criar novo trigger para automação"""
    
    # Validar tipo de evento
    eventos_validos = [
        "transacao_criada",
        "transacao_aprovada", 
        "transacao_rejeitada",
        "transacao_estornada",
        "checkin_realizado",
        "evento_criado",
        "lista_criada",
        "cupom_usado"
    ]
    
    if trigger.evento_tipo not in eventos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de evento inválido. Use: {', '.join(eventos_validos)}"
        )
    
    trigger_id = f"trigger_{uuid.uuid4().hex[:8]}"
    
    novo_trigger = {
        "id": trigger_id,
        "nome": trigger.nome,
        "evento_tipo": trigger.evento_tipo,
        "webhook_url": trigger.webhook_url,
        "filtros": trigger.filtros or {},
        "ativo": trigger.ativo,
        "execucoes": 0,
        "ultima_execucao": None,
        "criado_em": datetime.now()
    }
    
    mock_triggers[trigger_id] = novo_trigger
    
    return {
        "trigger_id": trigger_id,
        "nome": trigger.nome,
        "evento_tipo": trigger.evento_tipo,
        "webhook_url": trigger.webhook_url,
        "ativo": trigger.ativo,
        "criado_em": datetime.now()
    }

@router.get("/triggers")
async def listar_triggers(
    evento_tipo: Optional[str] = None,
    ativo: Optional[bool] = None,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Listar triggers configurados"""
    
    triggers_base = [
        {
            "id": "trigger_demo_1",
            "nome": "Notificar Nova Transação",
            "evento_tipo": "transacao_criada",
            "webhook_url": "https://app.n8n.io/webhook/nova-transacao",
            "filtros": {},
            "ativo": True,
            "execucoes": 150,
            "ultima_execucao": datetime.now() - timedelta(minutes=5),
            "criado_em": datetime.now() - timedelta(days=10)
        },
        {
            "id": "trigger_demo_2", 
            "nome": "Enviar Email Check-in",
            "evento_tipo": "checkin_realizado",
            "webhook_url": "https://app.n8n.io/webhook/checkin-email",
            "filtros": {},
            "ativo": True,
            "execucoes": 85,
            "ultima_execucao": datetime.now() - timedelta(hours=1),
            "criado_em": datetime.now() - timedelta(days=5)
        }
    ]
    
    triggers = triggers_base + list(mock_triggers.values())
    
    if evento_tipo:
        triggers = [t for t in triggers if t["evento_tipo"] == evento_tipo]
    
    if ativo is not None:
        triggers = [t for t in triggers if t["ativo"] == ativo]
    
    return {"total": len(triggers), "triggers": triggers}

@router.post("/webhook/{evento_tipo}")
async def processar_webhook_evento(
    evento_tipo: str,
    dados_evento: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Processar evento e disparar webhooks configurados"""
    
    try:
        triggers_ativos = [
            t for t in mock_triggers.values()
            if t["evento_tipo"] == evento_tipo and t["ativo"]
        ]
        
        if evento_tipo == "transacao_criada":
            triggers_ativos.append({
                "id": "trigger_demo_1",
                "webhook_url": "https://app.n8n.io/webhook/teste",
                "filtros": {}
            })
        
        for trigger in triggers_ativos:
            if aplicar_filtros(dados_evento, trigger.get("filtros", {})):
                background_tasks.add_task(
                    executar_webhook_background,
                    trigger["webhook_url"],
                    {
                        "evento_tipo": evento_tipo,
                        "dados": dados_evento,
                        "timestamp": datetime.now().isoformat(),
                        "trigger_id": trigger["id"]
                    }
                )
                
                if trigger["id"] in mock_triggers:
                    mock_triggers[trigger["id"]]["execucoes"] += 1
                    mock_triggers[trigger["id"]]["ultima_execucao"] = datetime.now()
        
        return {"mensagem": "Evento processado", "triggers_executados": len(triggers_ativos)}
        
    except Exception as e:
        return {"erro": str(e)}

@router.post("/notificar/{evento_tipo}")
async def notificar_evento(
    evento_tipo: str,
    dados: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Notificar N8N sobre evento específico"""
    
    eventos_permitidos = [
        "transacao_criada", "transacao_aprovada", "checkin_realizado",
        "evento_criado", "lista_criada", "cupom_usado"
    ]
    
    if evento_tipo not in eventos_permitidos:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de evento não permitido: {evento_tipo}"
        )
    
    dados_completos = {
        "evento_tipo": evento_tipo,
        "dados": dados,
        "usuario_id": usuario_atual.id,
        "usuario_nome": usuario_atual.nome,
        "empresa_id": usuario_atual.empresa_id,
        "timestamp": datetime.now().isoformat()
    }
    
    background_tasks.add_task(
        processar_webhook_evento,
        evento_tipo,
        dados_completos,
        BackgroundTasks(),
        None
    )
    
    return {
        "mensagem": f"Evento '{evento_tipo}' notificado para N8N",
        "dados_enviados": dados_completos
    }

@router.get("/execucoes")
async def obter_execucoes_workflows(
    workflow_id: Optional[str] = None,
    status: Optional[str] = None,
    limite: int = 50,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Obter histórico de execuções de workflows"""
    
    if not N8N_CONFIG["ativo"]:
        raise HTTPException(
            status_code=400,
            detail="N8N não está configurado"
        )
    
    execucoes = [
        {
            "id": "exec_1",
            "workflowId": "workflow_1",
            "finished": True,
            "startedAt": "2024-01-20T10:00:00Z",
            "stoppedAt": "2024-01-20T10:00:15Z",
            "error": None
        },
        {
            "id": "exec_2",
            "workflowId": "workflow_2",
            "finished": True,
            "startedAt": "2024-01-20T09:30:00Z",
            "stoppedAt": "2024-01-20T09:30:08Z",
            "error": None
        },
        {
            "id": "exec_3",
            "workflowId": "workflow_1",
            "finished": False,
            "startedAt": "2024-01-20T09:00:00Z",
            "stoppedAt": "2024-01-20T09:00:05Z",
            "error": "Connection timeout"
        }
    ]
    
    if workflow_id:
        execucoes = [e for e in execucoes if e["workflowId"] == workflow_id]
    
    if status:
        if status == "sucesso":
            execucoes = [e for e in execucoes if e["finished"] and not e["error"]]
        elif status == "falha":
            execucoes = [e for e in execucoes if not e["finished"] or e["error"]]
    
    execucoes = execucoes[:limite]
    
    return {
        "total": len(execucoes),
        "execucoes": [
            {
                "id": e["id"],
                "workflow_id": e.get("workflowId"),
                "status": "sucesso" if e.get("finished") and not e.get("error") else "falha",
                "inicio": e.get("startedAt"),
                "fim": e.get("stoppedAt"),
                "duracao": 12.5,  # Mock
                "erro": e.get("error")
            }
            for e in execucoes
        ]
    }

@router.get("/status")
async def obter_status_n8n(
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Obter status da integração N8N"""
    
    if not N8N_CONFIG["ativo"]:
        return {
            "configurado": False,
            "ativo": False,
            "base_url": None,
            "conexao": "não configurado",
            "ultimo_teste": datetime.now()
        }
    
    return {
        "configurado": True,
        "ativo": True,
        "base_url": N8N_CONFIG["base_url"],
        "conexao": "ok",
        "ultimo_teste": datetime.now(),
        "workflows_ativos": 5,
        "execucoes_hoje": 23,
        "execucoes_sucesso": 21,
        "execucoes_erro": 2
    }

@router.post("/testar-webhook")
async def testar_webhook(
    webhook_url: str,
    dados_teste: Optional[Dict[str, Any]] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(verify_admin)
):
    """Testar webhook específico"""
    
    dados_padrao = {
        "evento_tipo": "teste",
        "dados": dados_teste or {"mensagem": "Teste de webhook"},
        "usuario": usuario_atual.nome,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        background_tasks.add_task(
            executar_webhook_background,
            webhook_url,
            dados_padrao
        )
        
        return {
            "mensagem": "Teste de webhook iniciado",
            "webhook_url": webhook_url,
            "dados_enviados": dados_padrao
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao testar webhook: {str(e)}"
        )

@router.get("/templates")
async def listar_templates_automacao(
    categoria: Optional[str] = None,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Listar templates de automação disponíveis"""
    
    templates = [
        {
            "id": "email_nova_transacao",
            "nome": "Email Nova Transação",
            "descricao": "Enviar email quando nova transação é criada",
            "categoria": "vendas",
            "trigger": "transacao_criada",
            "acoes": ["enviar_email", "salvar_log"],
            "variaveis": ["nome_comprador", "valor", "evento_nome"]
        },
        {
            "id": "whatsapp_checkin",
            "nome": "WhatsApp Check-in",
            "descricao": "Enviar mensagem WhatsApp após check-in",
            "categoria": "checkin",
            "trigger": "checkin_realizado",
            "acoes": ["enviar_whatsapp"],
            "variaveis": ["nome", "evento_nome", "local"]
        },
        {
            "id": "slack_vendas_diarias",
            "nome": "Relatório Slack Vendas",
            "descricao": "Enviar relatório diário de vendas para Slack",
            "categoria": "relatorios",
            "trigger": "agendado_diario",
            "acoes": ["gerar_relatorio", "enviar_slack"],
            "variaveis": ["data", "total_vendas", "receita"]
        }
    ]
    
    if categoria:
        templates = [t for t in templates if t["categoria"] == categoria]
    
    return {
        "total": len(templates),
        "templates": templates,
        "categorias": list(set(t["categoria"] for t in templates))
    }

@router.get("/estatisticas")
async def obter_estatisticas_n8n(
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Obter estatísticas gerais do N8N"""
    
    if not N8N_CONFIG["ativo"]:
        raise HTTPException(
            status_code=400,
            detail="N8N não está configurado"
        )
    
    return {
        "workflows_ativos": 5,
        "workflows_total": 8,
        "triggers_ativos": len([t for t in mock_triggers.values() if t["ativo"]]) + 2,
        "triggers_total": len(mock_triggers) + 2,
        "execucoes_hoje": 23,
        "execucoes_sucesso": 21,
        "execucoes_erro": 2,
        "taxa_sucesso": 91.3,
        "ultima_execucao": datetime.now() - timedelta(minutes=5),
        "tempo_medio_execucao": 12.5,
        "eventos_processados_hoje": 45
    }

@router.delete("/triggers/{trigger_id}")
async def deletar_trigger(
    trigger_id: str,
    db = Depends(get_db),
    usuario_atual: MockUsuario = Depends(verify_admin)
):
    """Deletar trigger"""
    
    if trigger_id not in mock_triggers:
        raise HTTPException(status_code=404, detail="Trigger não encontrado")
    
    del mock_triggers[trigger_id]
    
    return {"mensagem": f"Trigger {trigger_id} deletado com sucesso"}

# Funções auxiliares

def aplicar_filtros(dados: Dict[str, Any], filtros: Dict[str, Any]) -> bool:
    """Aplicar filtros para verificar se deve executar trigger"""
    
    if not filtros:
        return True
    
    for campo, valor in filtros.items():
        if campo in dados and dados[campo] != valor:
            return False
    
    return True

async def executar_workflow_background(
    workflow_id: str,
    dados: Dict[str, Any],
    prioridade: int
):
    """Executar workflow em background"""
    
    try:
        if not N8N_CONFIG["ativo"]:
            print(f"N8N inativo, não executando workflow {workflow_id}")
            return
        
        print(f"Executando workflow {workflow_id} com dados: {dados}")
        await asyncio.sleep(1)  # Simular processamento
        print(f"Workflow {workflow_id} executado com sucesso")
        
        execucao_id = f"exec_{uuid.uuid4().hex[:8]}"
        mock_execucoes[execucao_id] = {
            "id": execucao_id,
            "workflow_id": workflow_id,
            "dados": dados,
            "status": "sucesso",
            "inicio": datetime.now(),
            "fim": datetime.now() + timedelta(seconds=12),
            "prioridade": prioridade
        }
                    
    except Exception as e:
        print(f"Erro ao executar workflow {workflow_id}: {e}")

async def executar_webhook_background(webhook_url: str, dados: Dict[str, Any]):
    """Executar webhook em background"""
    
    try:
        print(f"Executando webhook: {webhook_url}")
        print(f"Dados: {json.dumps(dados, indent=2, default=str)}")
        
        await asyncio.sleep(0.5)  # Simular delay de rede
        
        print(f"Webhook executado com sucesso: {webhook_url}")
                    
    except Exception as e:
        print(f"Erro ao executar webhook {webhook_url}: {e}")
