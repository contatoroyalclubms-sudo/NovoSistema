"""
Router para Sistema de Backup e Recuperação
Endpoints para gerenciar backups automáticos e manuais
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from ..services.backup import BackupService, TipoBackup, StatusBackup
from ..schemas.responses import Response

router = APIRouter(prefix="/backup", tags=["Backup e Recuperação"])

# Instância global do serviço
backup_service = BackupService()

@router.on_event("startup")
async def startup_backup():
    """Inicia serviço de backup automaticamente"""
    await backup_service.iniciar_servico()

@router.on_event("shutdown")
async def shutdown_backup():
    """Para serviço de backup"""
    await backup_service.parar_servico()

@router.get("/dashboard", summary="Dashboard de Backup")
async def obter_dashboard_backup():
    """
    Retorna dashboard principal com estatísticas de backup.
    
    Inclui:
    - Resumo geral dos backups
    - Configurações ativas
    - Próximos backups agendados
    - Backups em progresso
    """
    try:
        estatisticas = backup_service.obter_estatisticas_backup()
        
        return Response(
            success=True,
            message="Dashboard de backup obtido com sucesso",
            data=estatisticas
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dashboard: {str(e)}")

@router.get("/configuracoes", summary="Configurações de Backup")
async def obter_configuracoes():
    """
    Retorna todas as configurações de backup.
    """
    try:
        configuracoes = backup_service.obter_configuracoes()
        
        return Response(
            success=True,
            message="Configurações obtidas com sucesso",
            data={
                "total": len(configuracoes),
                "configuracoes": configuracoes
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter configurações: {str(e)}")

@router.post("/configuracoes", summary="Criar Configuração de Backup")
async def criar_configuracao(configuracao: Dict[str, Any]):
    """
    Cria nova configuração de backup.
    
    Corpo da requisição:
    ```json
    {
        "nome": "Backup Custom",
        "tipo": "incremental",
        "origem": "./dados",
        "destino": "./backups/custom",
        "frequencia_horas": 12,
        "retenção_dias": 7,
        "compressao": true,
        "criptografia": false,
        "ativo": true
    }
    ```
    """
    try:
        # Validações básicas
        campos_obrigatorios = ["nome", "tipo", "origem", "destino", "frequencia_horas", "retenção_dias"]
        for campo in campos_obrigatorios:
            if campo not in configuracao:
                raise HTTPException(status_code=400, detail=f"Campo obrigatório: {campo}")
        
        # Valida tipo de backup
        if configuracao["tipo"] not in [tipo.value for tipo in TipoBackup]:
            raise HTTPException(status_code=400, detail="Tipo de backup inválido")
        
        config_id = backup_service.criar_configuracao(configuracao)
        
        return Response(
            success=True,
            message="Configuração criada com sucesso",
            data={"config_id": config_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar configuração: {str(e)}")

@router.put("/configuracoes/{config_id}", summary="Atualizar Configuração")
async def atualizar_configuracao(config_id: str, updates: Dict[str, Any]):
    """
    Atualiza configuração de backup existente.
    
    Parâmetros:
    - config_id: ID da configuração
    """
    try:
        sucesso = backup_service.atualizar_configuracao(config_id, updates)
        
        if not sucesso:
            raise HTTPException(status_code=404, detail="Configuração não encontrada")
        
        return Response(
            success=True,
            message="Configuração atualizada com sucesso",
            data={"config_id": config_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar configuração: {str(e)}")

@router.delete("/configuracoes/{config_id}", summary="Remover Configuração")
async def remover_configuracao(config_id: str):
    """
    Remove configuração de backup.
    
    Parâmetros:
    - config_id: ID da configuração
    """
    try:
        sucesso = backup_service.remover_configuracao(config_id)
        
        if not sucesso:
            raise HTTPException(status_code=404, detail="Configuração não encontrada ou backup em progresso")
        
        return Response(
            success=True,
            message="Configuração removida com sucesso",
            data={"config_id": config_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover configuração: {str(e)}")

@router.get("/historico", summary="Histórico de Backups")
async def obter_historico_backups(
    limite: int = Query(50, ge=1, le=500, description="Limite de registros"),
    config_id: Optional[str] = Query(None, description="Filtrar por configuração"),
    status: Optional[StatusBackup] = Query(None, description="Filtrar por status")
):
    """
    Retorna histórico de backups executados.
    
    Parâmetros:
    - limite: Número máximo de registros (1-500)
    - config_id: Filtrar por configuração específica
    - status: Filtrar por status do backup
    """
    try:
        historico = backup_service.obter_historico_backups(limite)
        
        # Aplica filtros se especificados
        if config_id:
            historico = [h for h in historico if h["config_id"] == config_id]
        
        if status:
            historico = [h for h in historico if h["status"] == status]
        
        return Response(
            success=True,
            message="Histórico obtido com sucesso",
            data={
                "total": len(historico),
                "historico": historico
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter histórico: {str(e)}")

@router.post("/executar/{config_id}", summary="Executar Backup Manual")
async def executar_backup_manual(config_id: str, background_tasks: BackgroundTasks):
    """
    Executa backup manual de uma configuração.
    
    Parâmetros:
    - config_id: ID da configuração de backup
    """
    try:
        # Executa backup em background
        background_tasks.add_task(backup_service.executar_backup_manual, config_id)
        
        return Response(
            success=True,
            message="Backup manual iniciado",
            data={
                "config_id": config_id,
                "iniciado_em": datetime.now().isoformat(),
                "status": "em_progresso"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao executar backup: {str(e)}")

@router.post("/restaurar/{backup_id}", summary="Restaurar Backup")
async def restaurar_backup(backup_id: str, destino: Dict[str, str]):
    """
    Restaura um backup específico.
    
    Parâmetros:
    - backup_id: ID do backup a ser restaurado
    
    Corpo da requisição:
    ```json
    {
        "destino": "/path/para/restauracao"
    }
    ```
    """
    try:
        if "destino" not in destino:
            raise HTTPException(status_code=400, detail="Campo 'destino' é obrigatório")
        
        resultado = await backup_service.restaurar_backup(backup_id, destino["destino"])
        
        return Response(
            success=True,
            message="Backup restaurado com sucesso",
            data=resultado
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao restaurar backup: {str(e)}")

@router.get("/validar/{backup_id}", summary="Validar Integridade do Backup")
async def validar_integridade(backup_id: str):
    """
    Valida integridade de um backup específico.
    
    Parâmetros:
    - backup_id: ID do backup a ser validado
    """
    try:
        resultado = backup_service.validar_integridade_backup(backup_id)
        
        return Response(
            success=True,
            message="Validação de integridade concluída",
            data=resultado
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao validar backup: {str(e)}")

@router.get("/tipos", summary="Tipos de Backup Disponíveis")
async def obter_tipos_backup():
    """
    Retorna os tipos de backup disponíveis.
    """
    try:
        tipos = [
            {
                "valor": tipo.value,
                "nome": tipo.value.replace("_", " ").title(),
                "descricao": {
                    "completo": "Backup completo de todos os dados",
                    "incremental": "Backup apenas dos dados alterados desde o último backup",
                    "diferencial": "Backup dos dados alterados desde o último backup completo",
                    "configuracao": "Backup das configurações do sistema",
                    "banco_dados": "Backup específico do banco de dados",
                    "arquivos": "Backup de arquivos e documentos"
                }.get(tipo.value, "Tipo de backup")
            }
            for tipo in TipoBackup
        ]
        
        return Response(
            success=True,
            message="Tipos de backup obtidos com sucesso",
            data={"tipos": tipos}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter tipos: {str(e)}")

@router.get("/status", summary="Status do Serviço de Backup")
async def obter_status_servico():
    """
    Retorna status atual do serviço de backup.
    """
    try:
        estatisticas = backup_service.obter_estatisticas_backup()
        
        status_servico = {
            "servico_ativo": backup_service._executando,
            "configuracoes_ativas": estatisticas["configuracoes_ativas"],
            "backups_em_progresso": estatisticas["backups_em_progresso"],
            "ultimo_backup": None,
            "proximo_backup": None
        }
        
        # Obtém informações do último e próximo backup
        historico = backup_service.obter_historico_backups(1)
        if historico:
            status_servico["ultimo_backup"] = {
                "config_nome": historico[0]["config_nome"],
                "data": historico[0]["fim"] or historico[0]["inicio"],
                "status": historico[0]["status"]
            }
        
        if estatisticas["proximos_backups"]:
            proximo = estatisticas["proximos_backups"][0]
            status_servico["proximo_backup"] = {
                "config_nome": proximo["config_nome"],
                "data": proximo["proximo_backup"],
                "tempo_restante_horas": proximo["tempo_restante_horas"]
            }
        
        return Response(
            success=True,
            message="Status do serviço obtido com sucesso",
            data=status_servico
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

@router.post("/servico/reiniciar", summary="Reiniciar Serviço de Backup")
async def reiniciar_servico():
    """
    Reinicia o serviço de backup automático.
    """
    try:
        await backup_service.parar_servico()
        await asyncio.sleep(1)
        await backup_service.iniciar_servico()
        
        return Response(
            success=True,
            message="Serviço de backup reiniciado com sucesso",
            data={"reiniciado_em": datetime.now().isoformat()}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reiniciar serviço: {str(e)}")

@router.get("/relatorio/resumo", summary="Relatório Resumido")
async def obter_relatorio_resumo():
    """
    Retorna relatório resumido de backup.
    """
    try:
        estatisticas = backup_service.obter_estatisticas_backup()
        configuracoes = backup_service.obter_configuracoes()
        historico_recente = backup_service.obter_historico_backups(10)
        
        relatorio = {
            "resumo_geral": estatisticas["resumo"],
            "saude_backup": {
                "status": "saudável" if estatisticas["resumo"]["taxa_sucesso"] >= 90 else "atenção",
                "configuracoes_ativas": len([c for c in configuracoes if c["ativo"]]),
                "configuracoes_inativas": len([c for c in configuracoes if not c["ativo"]]),
                "espaco_utilizado_gb": estatisticas["resumo"]["tamanho_total_gb"]
            },
            "atividade_recente": {
                "backups_ultima_semana": estatisticas["resumo"]["backups_esta_semana"],
                "backups_recentes": historico_recente[:5],
                "tipos_backup_ativo": list(set([c["tipo"] for c in configuracoes if c["ativo"]]))
            },
            "alertas": [],
            "recomendacoes": []
        }
        
        # Adiciona alertas baseado na análise
        if estatisticas["resumo"]["taxa_sucesso"] < 80:
            relatorio["alertas"].append("Taxa de sucesso dos backups está baixa")
        
        if estatisticas["backups_em_progresso"] > 3:
            relatorio["alertas"].append("Muitos backups em progresso simultaneamente")
        
        # Adiciona recomendações
        if estatisticas["resumo"]["tamanho_total_gb"] > 100:
            relatorio["recomendacoes"].append("Considere revisar política de retenção")
        
        if not estatisticas["proximos_backups"]:
            relatorio["recomendacoes"].append("Configure backups automáticos")
        
        return Response(
            success=True,
            message="Relatório gerado com sucesso",
            data=relatorio
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")
