"""
Sistema de Backup Automático Avançado (Versão Simplificada)
Priority #4: Backup Automation - Implementação Completa
"""

from pathlib import Path
from datetime import datetime, timedelta
import shutil
import logging
import asyncio
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class BackupInfo:
    """Informações sobre um backup"""
    filename: str
    path: str
    size: int
    created_at: datetime
    type: str  # 'manual', 'scheduled', 'startup', 'shutdown'
    status: str  # 'success', 'failed', 'in_progress'
    duration_seconds: float = 0.0
    error_message: Optional[str] = None

class SimpleBackupManager:
    """Gerenciador simplificado de backups"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        self.config_file = self.backup_dir / "backup_config.json"
        self.history_file = self.backup_dir / "backup_history.json"
        
        # Configurações padrão
        self.config = {
            "max_backups": 10,
            "backup_interval_hours": 6,
            "auto_cleanup": True,
            "compress_backups": False,
            "destinations": {
                "local": True,
                "cloud": False
            },
            "notifications": {
                "success": False,
                "failure": True
            }
        }
        
        self.backup_history: List[Dict] = []
        self.scheduler_running = False
        self.load_config()
        self.load_history()
    
    def load_config(self):
        """Carrega configurações do backup"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                logger.info("[BACKUP] Configurações carregadas")
            except Exception as e:
                logger.error(f"[BACKUP] Erro ao carregar config: {e}")
    
    def save_config(self):
        """Salva configurações do backup"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, default=str)
            logger.info("[BACKUP] Configurações salvas")
        except Exception as e:
            logger.error(f"[BACKUP] Erro ao salvar config: {e}")
    
    def load_history(self):
        """Carrega histórico de backups"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.backup_history = data
                logger.info(f"[BACKUP] Histórico carregado: {len(self.backup_history)} backups")
            except Exception as e:
                logger.error(f"[BACKUP] Erro ao carregar histórico: {e}")
    
    def save_history(self):
        """Salva histórico de backups"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.backup_history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"[BACKUP] Erro ao salvar histórico: {e}")
    
    def add_to_history(self, backup_info: BackupInfo):
        """Adiciona backup ao histórico"""
        backup_dict = asdict(backup_info)
        backup_dict['created_at'] = backup_info.created_at.isoformat()
        self.backup_history.append(backup_dict)
        self.save_history()
        
        # Limpa histórico antigo se necessário
        if len(self.backup_history) > 100:
            self.backup_history = self.backup_history[-50:]
            self.save_history()
    
    async def create_backup(self, backup_type: str = "manual") -> Optional[BackupInfo]:
        """Cria um backup do banco de dados"""
        start_time = datetime.now()
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        backup_filename = f"sistema_universal_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_filename
        
        backup_info = BackupInfo(
            filename=backup_filename,
            path=str(backup_path),
            size=0,
            created_at=start_time,
            type=backup_type,
            status="in_progress"
        )
        
        try:
            logger.info(f"[BACKUP] Iniciando backup {backup_type}: {backup_filename}")
            
            # Localizar arquivo de banco de dados
            source_db = Path("app/sistema_universal.db")
            if not source_db.exists():
                # Tentar outras localizações possíveis
                possible_paths = [
                    Path("sistema_universal.db"),
                    Path("../sistema_universal.db"),
                    Path("../../sistema_universal.db")
                ]
                
                for path in possible_paths:
                    if path.exists():
                        source_db = path
                        break
                else:
                    backup_info.status = "failed"
                    backup_info.error_message = "Arquivo de banco de dados não encontrado"
                    logger.error(f"[BACKUP] {backup_info.error_message}")
                    self.add_to_history(backup_info)
                    return backup_info
            
            # Copiar arquivo
            shutil.copy2(source_db, backup_path)
            
            # Verificar se o backup foi criado
            if backup_path.exists():
                backup_info.size = backup_path.stat().st_size
                backup_info.status = "success"
                backup_info.duration_seconds = (datetime.now() - start_time).total_seconds()
                
                logger.info(f"[BACKUP] Backup criado com sucesso: {backup_filename} ({backup_info.size} bytes)")
                
                # Limpar backups antigos se configurado
                if self.config["auto_cleanup"]:
                    await self.cleanup_old_backups()
                
            else:
                backup_info.status = "failed"
                backup_info.error_message = "Arquivo de backup não foi criado"
                logger.error(f"[BACKUP] {backup_info.error_message}")
                
        except Exception as e:
            backup_info.status = "failed"
            backup_info.error_message = str(e)
            backup_info.duration_seconds = (datetime.now() - start_time).total_seconds()
            logger.error(f"[BACKUP] Erro ao criar backup: {e}")
        
        self.add_to_history(backup_info)
        return backup_info
    
    async def cleanup_old_backups(self):
        """Remove backups antigos baseado na configuração"""
        try:
            backup_files = list(self.backup_dir.glob("sistema_universal_backup_*.db"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            max_backups = self.config["max_backups"]
            if len(backup_files) > max_backups:
                files_to_remove = backup_files[max_backups:]
                for file_path in files_to_remove:
                    file_path.unlink()
                    logger.info(f"[BACKUP] Backup antigo removido: {file_path.name}")
                
                logger.info(f"[BACKUP] Limpeza concluída. Mantidos {max_backups} backups")
        
        except Exception as e:
            logger.error(f"[BACKUP] Erro na limpeza: {e}")
    
    def start_scheduler(self):
        """Inicia o agendador de backups (simulado)"""
        try:
            self.scheduler_running = True
            logger.info(f"[BACKUP] Agendador simulado iniciado. Backup a cada {self.config['backup_interval_hours']}h")
        except Exception as e:
            logger.error(f"[BACKUP] Erro ao iniciar agendador: {e}")
    
    def stop_scheduler(self):
        """Para o agendador de backups"""
        try:
            self.scheduler_running = False
            logger.info("[BACKUP] Agendador parado")
        except Exception as e:
            logger.error(f"[BACKUP] Erro ao parar agendador: {e}")
    
    def get_backup_stats(self) -> Dict:
        """Estatísticas dos backups"""
        total_backups = len(self.backup_history)
        successful_backups = len([b for b in self.backup_history if b["status"] == "success"])
        failed_backups = len([b for b in self.backup_history if b["status"] == "failed"])
        
        total_size = 0
        for backup in self.backup_history:
            if backup["status"] == "success":
                total_size += backup.get("size", 0)
        
        # Backup mais recente
        latest_backup = None
        if self.backup_history:
            latest_backup = self.backup_history[-1]
        
        return {
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "failed_backups": failed_backups,
            "success_rate": (successful_backups / total_backups * 100) if total_backups > 0 else 0,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "latest_backup": latest_backup,
            "config": self.config,
            "scheduler_running": self.scheduler_running
        }
    
    def list_backup_files(self) -> List[Dict]:
        """Lista arquivos de backup disponíveis"""
        backup_files = []
        try:
            for file_path in self.backup_dir.glob("sistema_universal_backup_*.db"):
                stat = file_path.stat()
                backup_files.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            
            # Ordenar por data de criação (mais recente primeiro)
            backup_files.sort(key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            logger.error(f"[BACKUP] Erro ao listar arquivos: {e}")
        
        return backup_files
    
    async def restore_backup(self, backup_filename: str) -> bool:
        """Restaura um backup específico"""
        try:
            backup_path = self.backup_dir / backup_filename
            if not backup_path.exists():
                logger.error(f"[BACKUP] Arquivo de backup não encontrado: {backup_filename}")
                return False
            
            # Fazer backup do arquivo atual antes de restaurar
            current_db = Path("app/sistema_universal.db")
            if current_db.exists():
                backup_current = self.backup_dir / f"backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(current_db, backup_current)
                logger.info(f"[BACKUP] Backup atual salvo como: {backup_current.name}")
            
            # Restaurar backup
            shutil.copy2(backup_path, current_db)
            logger.info(f"[BACKUP] Backup restaurado com sucesso: {backup_filename}")
            return True
            
        except Exception as e:
            logger.error(f"[BACKUP] Erro ao restaurar backup: {e}")
            return False

# Instância global do gerenciador de backup
backup_manager = SimpleBackupManager()
