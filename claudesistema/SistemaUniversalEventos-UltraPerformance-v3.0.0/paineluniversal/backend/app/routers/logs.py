"""
Router para Sistema de Logging Avançado
Priority #5: Logging System - API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..logging_manager import log_manager, LogLevel, LogType

router = APIRouter(prefix="/logs", tags=["Logging System"])

class LogConfigModel(BaseModel):
    log_level: str = "INFO"
    max_file_size_mb: int = 50
    backup_count: int = 5
    retention_days: int = 30
    enable_console: bool = True
    enable_file: bool = True
    enable_json: bool = True
    enable_rotation: bool = True
    enable_compression: bool = True
    enable_alerts: bool = True

class AlertAcknowledgeModel(BaseModel):
    alert_id: str

@router.get("/health")
async def logs_health():
    """Health check do sistema de logging"""
    try:
        stats = log_manager.get_log_stats()
        return {
            "status": "healthy",
            "message": "Sistema de logging funcionando",
            "total_logs": stats["total_logs"],
            "new_alerts": stats["new_alerts"],
            "config": {
                "level": log_manager.config["log_level"],
                "file_enabled": log_manager.config["enable_file"],
                "alerts_enabled": log_manager.config["enable_alerts"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no sistema de logging: {e}")

@router.get("/stats")
async def get_log_stats():
    """Estatísticas detalhadas do sistema de logging"""
    try:
        stats = log_manager.get_log_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {e}")

@router.get("/recent")
async def get_recent_logs(
    limit: int = Query(100, ge=1, le=1000),
    level: Optional[str] = Query(None, regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
):
    """Obtém logs recentes"""
    try:
        logs = log_manager.get_recent_logs(limit=limit, level=level)
        return {
            "success": True,
            "message": f"Encontrados {len(logs)} logs",
            "data": logs,
            "total": len(logs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter logs: {e}")

@router.get("/search")
async def search_logs(
    query: str = Query(..., min_length=1),
    limit: int = Query(100, ge=1, le=1000)
):
    """Busca nos logs por palavra-chave"""
    try:
        logs = log_manager.search_logs(query=query, limit=limit)
        return {
            "success": True,
            "message": f"Encontrados {len(logs)} logs para '{query}'",
            "data": logs,
            "query": query,
            "total": len(logs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {e}")

@router.get("/alerts")
async def get_alerts():
    """Lista todos os alertas"""
    try:
        # Filtrar alertas recentes (últimos 7 dias)
        recent_alerts = []
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for alert in log_manager.alerts:
            alert_date = datetime.fromisoformat(alert["timestamp"])
            if alert_date > cutoff_date:
                recent_alerts.append(alert)
        
        # Ordenar por timestamp (mais recente primeiro)
        recent_alerts.sort(key=lambda x: x["timestamp"], reverse=True)
        
        new_alerts = [a for a in recent_alerts if a["status"] == "new"]
        
        return {
            "success": True,
            "data": {
                "alerts": recent_alerts,
                "new_count": len(new_alerts),
                "total_count": len(recent_alerts)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter alertas: {e}")

@router.post("/alerts/acknowledge")
async def acknowledge_alert(alert_data: AlertAcknowledgeModel):
    """Marca um alerta como reconhecido"""
    try:
        success = log_manager.acknowledge_alert(alert_data.alert_id)
        
        if success:
            return {
                "success": True,
                "message": f"Alerta {alert_data.alert_id} reconhecido"
            }
        else:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reconhecer alerta: {e}")

@router.get("/config")
async def get_log_config():
    """Obtém configurações do sistema de logging"""
    try:
        return {
            "success": True,
            "data": log_manager.config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter configurações: {e}")

@router.put("/config")
async def update_log_config(config: LogConfigModel):
    """Atualiza configurações do sistema de logging"""
    try:
        # Validar nível de log
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config.log_level not in valid_levels:
            raise HTTPException(status_code=400, detail=f"Nível de log inválido. Use: {valid_levels}")
        
        # Atualizar configurações
        log_manager.config.update(config.dict())
        log_manager.save_config()
        
        # Reconfigurar sistema de logging
        log_manager.setup_logging()
        
        return {
            "success": True,
            "message": "Configurações atualizadas com sucesso",
            "data": log_manager.config
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar configurações: {e}")

@router.post("/cleanup")
async def cleanup_old_logs(background_tasks: BackgroundTasks):
    """Remove logs antigos baseado na configuração"""
    try:
        background_tasks.add_task(log_manager.cleanup_old_logs)
        return {
            "success": True,
            "message": "Limpeza de logs antigos iniciada em background"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na limpeza: {e}")

@router.get("/levels")
async def get_log_levels():
    """Lista níveis de log disponíveis"""
    return {
        "success": True,
        "data": {
            "levels": [level.value for level in LogLevel],
            "current": log_manager.config["log_level"],
            "descriptions": {
                "DEBUG": "Informações detalhadas para debugging",
                "INFO": "Informações gerais do sistema",
                "WARNING": "Avisos que não impedem funcionamento",
                "ERROR": "Erros que podem afetar funcionalidade",
                "CRITICAL": "Erros críticos que podem parar sistema"
            }
        }
    }

@router.get("/types")
async def get_log_types():
    """Lista tipos de log disponíveis"""
    return {
        "success": True,
        "data": {
            "types": [log_type.value for log_type in LogType],
            "descriptions": {
                "system": "Logs gerais do sistema",
                "backup": "Logs do sistema de backup",
                "api": "Logs de requisições da API",
                "database": "Logs do banco de dados",
                "performance": "Logs de performance",
                "security": "Logs de segurança",
                "analytics": "Logs do sistema de analytics",
                "whatsapp": "Logs da integração WhatsApp",
                "websocket": "Logs do WebSocket",
                "error": "Logs de erros específicos"
            }
        }
    }

@router.get("/dashboard")
async def logs_dashboard():
    """Dashboard completo do sistema de logging"""
    try:
        stats = log_manager.get_log_stats()
        recent_logs = log_manager.get_recent_logs(limit=50)
        
        # Alertas não reconhecidos
        new_alerts = [a for a in log_manager.alerts if a["status"] == "new"]
        
        # Logs por hora (últimas 24h)
        hourly_stats = {}
        now = datetime.now()
        for i in range(24):
            hour = (now - timedelta(hours=i)).strftime("%H:00")
            hourly_stats[hour] = 0
        
        for log in recent_logs:
            log_time = datetime.fromisoformat(log["timestamp"])
            hour = log_time.strftime("%H:00")
            if hour in hourly_stats:
                hourly_stats[hour] += 1
        
        dashboard_data = {
            "stats": stats,
            "recent_logs": recent_logs[:20],  # Últimos 20 logs
            "new_alerts": new_alerts,
            "hourly_stats": hourly_stats,
            "system_status": {
                "logging_active": True,
                "file_logging": log_manager.config["enable_file"],
                "json_logging": log_manager.config["enable_json"],
                "alerts_enabled": log_manager.config["enable_alerts"],
                "current_level": log_manager.config["log_level"]
            }
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no dashboard: {e}")

@router.post("/test")
async def test_logging():
    """Gera logs de teste para verificar funcionamento"""
    import logging
    
    try:
        logger = logging.getLogger("test_logging")
        
        # Gerar logs de diferentes níveis
        logger.debug("Log de DEBUG - teste funcionamento")
        logger.info("Log de INFO - sistema funcionando normalmente")
        logger.warning("Log de WARNING - atenção necessária")
        logger.error("Log de ERROR - erro de teste")
        
        return {
            "success": True,
            "message": "Logs de teste gerados com sucesso",
            "logs_generated": 4
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar logs de teste: {e}")
