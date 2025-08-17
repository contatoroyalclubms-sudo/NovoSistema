from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import json
import re
import uuid
import asyncio

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

# Modelos para requests
class EnviarMensagem(BaseModel):
    telefone: str
    mensagem: str
    tipo: str = "texto"  # texto, imagem, documento
    arquivo_url: Optional[str] = None

class CriarCampanha(BaseModel):
    nome: str
    template_id: str
    evento_id: Optional[int] = None
    lista_id: Optional[int] = None
    filtro_status: Optional[str] = None
    agendamento: Optional[datetime] = None
    mensagem_personalizada: Optional[str] = None

class ConfigurarWhatsApp(BaseModel):
    api_token: str
    webhook_url: str
    numero_remetente: str
    ativo: bool = True

# Mock de usuário simples
class MockUsuario:
    def __init__(self):
        self.id = 1
        self.nome = "Admin"
        self.tipo_usuario = "admin"
        self.empresa_id = 1

def get_current_user():
    """Mock function para usuário atual"""
    return MockUsuario()

def verify_admin():
    """Mock function para verificar admin"""
    return MockUsuario()

@router.post("/configurar")
async def configurar_whatsapp(
    config: ConfigurarWhatsApp,
    usuario_atual: MockUsuario = Depends(verify_admin)
):
    """Configurar integração WhatsApp"""
    
    try:
        # Mock da validação - em produção conectar com API real
        if not config.api_token or len(config.api_token) < 10:
            raise HTTPException(
                status_code=400,
                detail="Token da API WhatsApp inválido"
            )
        
        # Mock do teste de conexão
        teste_conexao = True  # Simular sucesso
        
        if not teste_conexao:
            raise HTTPException(
                status_code=400,
                detail="Erro ao conectar com WhatsApp API. Verifique as credenciais."
            )
        
        return {
            "mensagem": "WhatsApp configurado com sucesso",
            "status_conexao": "ativo",
            "numero_verificado": config.numero_remetente
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao configurar WhatsApp: {str(e)}"
        )

@router.post("/enviar-mensagem")
async def enviar_mensagem_individual(
    dados: EnviarMensagem,
    background_tasks: BackgroundTasks,
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Enviar mensagem individual via WhatsApp"""
    
    if usuario_atual.tipo_usuario not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    # Validar e formatar telefone
    telefone = validar_telefone(dados.telefone)
    if not telefone:
        raise HTTPException(status_code=400, detail="Número de telefone inválido")
    
    try:
        # Adicionar tarefa em background
        background_tasks.add_task(
            enviar_mensagem_background,
            telefone,
            dados.mensagem,
            dados.tipo,
            dados.arquivo_url,
            usuario_atual.id
        )
        
        return {
            "mensagem": "Mensagem enviada para fila de processamento",
            "telefone": telefone,
            "tipo": dados.tipo
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar mensagem: {str(e)}"
        )

@router.post("/campanhas", response_model=Dict[str, Any])
async def criar_campanha(
    campanha: CriarCampanha,
    background_tasks: BackgroundTasks,
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Criar campanha de mensagens WhatsApp"""
    
    if usuario_atual.tipo_usuario not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    try:
        # Mock de destinatários para teste
        destinatarios = obter_destinatarios_mock()
        
        if not destinatarios:
            raise HTTPException(
                status_code=400,
                detail="Nenhum destinatário encontrado com os filtros especificados"
            )
        
        # Criar ID da campanha
        campanha_id = str(uuid.uuid4())
        
        if campanha.agendamento and campanha.agendamento > datetime.now():
            # Agendar campanha
            background_tasks.add_task(
                agendar_campanha,
                campanha_id,
                campanha.dict(),
                destinatarios,
                usuario_atual.id
            )
            
            status_campanha = "agendada"
        else:
            # Executar imediatamente
            background_tasks.add_task(
                executar_campanha,
                campanha_id,
                campanha.dict(),
                destinatarios,
                usuario_atual.id
            )
            
            status_campanha = "em_execucao"
        
        return {
            "campanha_id": campanha_id,
            "nome": campanha.nome,
            "total_destinatarios": len(destinatarios),
            "status": status_campanha,
            "agendamento": campanha.agendamento,
            "criado_em": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar campanha: {str(e)}"
        )

@router.get("/templates")
async def listar_templates(
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Listar templates de mensagem disponíveis"""
    
    templates = [
        {
            "id": "boas_vindas",
            "nome": "Boas-vindas",
            "descricao": "Mensagem de boas-vindas após compra",
            "variaveis": ["nome", "evento_nome", "data_evento"],
            "template": "Olá {nome}! Sua compra para o evento {evento_nome} foi confirmada. Data: {data_evento}. Aguardamos você!"
        },
        {
            "id": "lembrete_evento",
            "nome": "Lembrete do Evento",
            "descricao": "Lembrete enviado próximo ao evento",
            "variaveis": ["nome", "evento_nome", "data_evento", "local"],
            "template": "Oi {nome}! Lembrete: {evento_nome} acontece em {data_evento} no {local}. Não esqueça!"
        },
        {
            "id": "checkin_disponivel",
            "nome": "Check-in Disponível",
            "descricao": "Notificação de que check-in está aberto",
            "variaveis": ["nome", "evento_nome", "qr_code_url"],
            "template": "🎉 {nome}, o check-in para {evento_nome} já está aberto! Use este QR Code: {qr_code_url}"
        },
        {
            "id": "promocao",
            "nome": "Promoção",
            "descricao": "Mensagem promocional para novos eventos",
            "variaveis": ["nome", "evento_nome", "desconto", "link_compra"],
            "template": "Oi {nome}! Nova promoção: {desconto}% de desconto para {evento_nome}! Compre: {link_compra}"
        },
        {
            "id": "agradecimento",
            "nome": "Agradecimento",
            "descricao": "Mensagem de agradecimento pós-evento",
            "variaveis": ["nome", "evento_nome"],
            "template": "Obrigado por participar do {evento_nome}, {nome}! Esperamos você nos próximos eventos! 🎉"
        }
    ]
    
    return templates

@router.post("/enviar-template")
async def enviar_template_personalizado(
    template_id: str,
    evento_id: Optional[int] = None,
    lista_id: Optional[int] = None,
    telefones: Optional[List[str]] = None,
    variaveis_extras: Optional[Dict[str, str]] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Enviar template personalizado para destinatários específicos"""
    
    if usuario_atual.tipo_usuario not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    # Buscar template
    templates = await listar_templates(usuario_atual)
    template = next((t for t in templates if t["id"] == template_id), None)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    # Determinar destinatários
    if telefones:
        destinatarios = [{"telefone": t, "nome": "Cliente"} for t in telefones]
    else:
        destinatarios = obter_destinatarios_mock()
    
    if not destinatarios:
        raise HTTPException(status_code=400, detail="Nenhum destinatário encontrado")
    
    # Mock de dados do evento
    evento_dados = {
        "evento_nome": "Evento Teste",
        "data_evento": "25/12/2024",
        "local": "São Paulo - SP"
    }
    
    # Executar envio
    background_tasks.add_task(
        enviar_template_background,
        template,
        destinatarios,
        evento_dados,
        variaveis_extras or {},
        usuario_atual.id
    )
    
    return {
        "mensagem": "Template adicionado à fila de envio",
        "template": template["nome"],
        "total_destinatarios": len(destinatarios)
    }

@router.get("/historico")
async def obter_historico_mensagens(
    limite: int = 50,
    telefone: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    status: Optional[str] = None,
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Obter histórico de mensagens enviadas"""
    
    # Mock de histórico para demonstração
    historico = [
        {
            "id": 1,
            "telefone": "+5567999999999",
            "mensagem": "Obrigado por sua compra!",
            "tipo": "texto",
            "status": "entregue",
            "enviado_em": datetime.now() - timedelta(hours=2),
            "entregue_em": datetime.now() - timedelta(hours=2, minutes=1),
            "usuario_envio": usuario_atual.nome
        },
        {
            "id": 2,
            "telefone": "+5567888888888",
            "mensagem": "Lembrete: Seu evento é hoje!",
            "tipo": "texto",
            "status": "lida",
            "enviado_em": datetime.now() - timedelta(hours=1),
            "entregue_em": datetime.now() - timedelta(hours=1, minutes=2),
            "usuario_envio": usuario_atual.nome
        }
    ]
    
    # Aplicar filtros se necessário
    if telefone:
        historico = [h for h in historico if telefone in h["telefone"]]
    
    if status:
        historico = [h for h in historico if h["status"] == status]
    
    return {
        "total": len(historico),
        "mensagens": historico[:limite]
    }

@router.get("/relatorio")
async def gerar_relatorio_whatsapp(
    evento_id: Optional[int] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    usuario_atual: MockUsuario = Depends(get_current_user)
):
    """Gerar relatório de performance do WhatsApp"""
    
    if not data_inicio:
        data_inicio = datetime.now() - timedelta(days=30)
    if not data_fim:
        data_fim = datetime.now()
    
    # Mock de relatório para demonstração
    relatorio = {
        "periodo": {
            "inicio": data_inicio,
            "fim": data_fim
        },
        "estatisticas": {
            "total_mensagens_enviadas": 1250,
            "mensagens_entregues": 1180,
            "mensagens_lidas": 950,
            "mensagens_falharam": 70,
            "taxa_entrega": 94.4,
            "taxa_leitura": 80.5
        },
        "campanhas": [
            {
                "nome": "Lembrete Evento XYZ",
                "data_envio": datetime.now() - timedelta(days=5),
                "destinatarios": 500,
                "entregues": 485,
                "lidas": 420,
                "cliques": 45
            }
        ],
        "mensagens_por_dia": {
            (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"): 
            {"enviadas": 50 + i * 5, "entregues": 45 + i * 4}
            for i in range(7)
        },
        "tipos_mensagem": {
            "texto": 1000,
            "imagem": 200,
            "documento": 50
        },
        "principais_horarios": {
            "09:00": 120,
            "14:00": 180,
            "19:00": 200,
            "21:00": 150
        }
    }
    
    return relatorio

@router.post("/webhook")
async def webhook_whatsapp(
    dados: Dict[str, Any]
):
    """Webhook para receber status das mensagens"""
    
    try:
        # Log do webhook
        print(f"Webhook WhatsApp recebido: {dados}")
        
        # Processar status de entrega
        if "status" in dados:
            status = dados["status"]
            message_id = dados.get("message_id")
            
            # Em produção, atualizar status no banco
            print(f"Atualizando status da mensagem {message_id}: {status}")
            
            # Mock de notificação WebSocket
            print(f"Notificação WebSocket enviada: whatsapp_status")
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"Erro no webhook WhatsApp: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/configuracao")
async def obter_configuracao(
    usuario_atual: MockUsuario = Depends(verify_admin)
):
    """Obter configuração atual do WhatsApp"""
    
    # Mock de configuração
    config = {
        "configurado": True,
        "numero_remetente": "+5567999999999",
        "webhook_configurado": True,
        "status_conexao": "ativo",
        "ultimo_teste": datetime.now() - timedelta(hours=1),
        "limite_mensal": 10000,
        "mensagens_enviadas_mes": 1250,
        "creditos_restantes": 8750
    }
    
    return config

@router.post("/testar-conexao")
async def testar_conexao_whatsapp(
    telefone_teste: str,
    usuario_atual: MockUsuario = Depends(verify_admin)
):
    """Testar conexão com WhatsApp enviando mensagem de teste"""
    
    telefone = validar_telefone(telefone_teste)
    if not telefone:
        raise HTTPException(status_code=400, detail="Número de telefone inválido")
    
    try:
        mensagem_teste = f"🔧 Teste de conexão WhatsApp realizado em {datetime.now().strftime('%d/%m/%Y %H:%M')} pelo sistema de eventos."
        
        # Mock do envio
        print(f"Enviando mensagem de teste para {telefone}: {mensagem_teste}")
        
        # Simular delay da API
        await asyncio.sleep(1)
        
        return {
            "sucesso": True,
            "mensagem": "Mensagem de teste enviada com sucesso",
            "telefone": telefone,
            "message_id": f"test_{uuid.uuid4().hex[:8]}"
        }
        
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e),
            "telefone": telefone
        }

# Funções auxiliares

def validar_telefone(telefone: str) -> Optional[str]:
    """Validar e formatar número de telefone"""
    
    # Remover caracteres não numéricos
    telefone_limpo = re.sub(r'\D', '', telefone)
    
    # Verificar se tem pelo menos 10 dígitos
    if len(telefone_limpo) < 10:
        return None
    
    # Adicionar código do país se não tiver
    if not telefone_limpo.startswith('55'):
        telefone_limpo = '55' + telefone_limpo
    
    # Formatação final
    return f"+{telefone_limpo}"

def obter_destinatarios_mock() -> List[Dict[str, str]]:
    """Mock de destinatários para teste"""
    
    return [
        {
            "telefone": "+5567999999999",
            "nome": "João Silva",
            "email": "joao@email.com",
            "cpf": "12345678901"
        },
        {
            "telefone": "+5567888888888",
            "nome": "Maria Santos",
            "email": "maria@email.com",
            "cpf": "98765432109"
        }
    ]

async def enviar_mensagem_background(
    telefone: str,
    mensagem: str,
    tipo: str,
    arquivo_url: Optional[str],
    usuario_id: int
):
    """Enviar mensagem em background"""
    
    try:
        print(f"Enviando mensagem para {telefone}: {mensagem}")
        
        # Simular delay da API
        await asyncio.sleep(1)
        
        print(f"Mensagem enviada com sucesso para {telefone}")
        
    except Exception as e:
        print(f"Erro ao enviar mensagem para {telefone}: {e}")

async def executar_campanha(
    campanha_id: str,
    dados_campanha: Dict[str, Any],
    destinatarios: List[Dict[str, str]],
    usuario_id: int
):
    """Executar campanha de mensagens"""
    
    try:
        print(f"Iniciando campanha {campanha_id} para {len(destinatarios)} destinatários")
        
        for destinatario in destinatarios:
            await enviar_mensagem_background(
                destinatario["telefone"],
                dados_campanha.get("mensagem_personalizada", "Mensagem da campanha"),
                "texto",
                None,
                usuario_id
            )
            
            # Delay entre envios
            await asyncio.sleep(0.5)
        
        print(f"Campanha {campanha_id} concluída")
        
    except Exception as e:
        print(f"Erro na campanha {campanha_id}: {e}")

async def agendar_campanha(
    campanha_id: str,
    dados_campanha: Dict[str, Any],
    destinatarios: List[Dict[str, str]],
    usuario_id: int
):
    """Agendar execução de campanha"""
    
    print(f"Campanha {campanha_id} agendada para {dados_campanha.get('agendamento')}")
    # Em produção, implementar sistema de agendamento real

async def enviar_template_background(
    template: Dict[str, Any],
    destinatarios: List[Dict[str, str]],
    evento_dados: Dict[str, str],
    variaveis_extras: Dict[str, str],
    usuario_id: int
):
    """Enviar template em background"""
    
    try:
        template_texto = template["template"]
        
        for destinatario in destinatarios:
            # Substituir variáveis no template
            mensagem = template_texto.format(
                nome=destinatario["nome"],
                **evento_dados,
                **variaveis_extras
            )
            
            await enviar_mensagem_background(
                destinatario["telefone"],
                mensagem,
                "texto",
                None,
                usuario_id
            )
            
            # Delay entre envios
            await asyncio.sleep(0.3)
            
    except Exception as e:
        print(f"Erro ao enviar template: {e}")
