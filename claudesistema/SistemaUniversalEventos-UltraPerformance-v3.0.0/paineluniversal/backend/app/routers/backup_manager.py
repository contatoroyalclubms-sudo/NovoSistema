"""
Router simples para BackupManager
Backup Automation Priority #4 - Endpoints básicos
"""

from fastapi import APIRouter, HTTPException
from datetime import timedelta
from ..backup_manager import backup_manager

router = APIRouter(prefix="/backup-manager", tags=["Backup Manager"])

@router.get("/health")
async def backup_health():
    """Health check do sistema de backup"""
    try:
        stats = backup_manager.get_backup_stats()
        return {
            "status": "healthy",
            "message": "BackupManager funcionando",
            "scheduler_running": stats["scheduler_running"],
            "total_backups": stats["total_backups"]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/stats")
async def get_stats():
    """Estatísticas dos backups"""
    return backup_manager.get_backup_stats()

@router.post("/create")
async def create_backup():
    """Cria backup manual"""
    try:
        backup_info = await backup_manager.create_backup("manual")
        if backup_info and backup_info.status == "success":
            return {
                "success": True,
                "message": "Backup criado",
                "filename": backup_info.filename,
                "size": backup_info.size
            }
        else:
            return {
                "success": False,
                "message": backup_info.error_message if backup_info else "Erro desconhecido"
            }
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/list")
async def list_backups():
    """Lista arquivos de backup"""
    return backup_manager.list_backup_files()

@router.get("/dashboard")
async def backup_dashboard():
    """Dashboard simples de backup"""
    try:
        stats = backup_manager.get_backup_stats()
        files = backup_manager.list_backup_files()
        
        return {
            "stats": stats,
            "recent_files": files[:5],
            "total_files": len(files)
        }
    except Exception as e:
        return {"error": str(e)}
