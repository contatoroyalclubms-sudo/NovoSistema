"""
Sistema de Logging Avançado
Priority #5: Logging System - Implementação Completa
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
import traceback
import threading
import gzip
import shutil

class LogLevel(str, Enum):
    """Níveis de log disponíveis"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogType(str, Enum):
    """Tipos de log do sistema"""
    SYSTEM = "system"
    BACKUP = "backup"
    API = "api"
    DATABASE = "database"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ANALYTICS = "analytics"
    WHATSAPP = "whatsapp"
    WEBSOCKET = "websocket"
    ERROR = "error"

class LogEntry:
    """Entrada de log estruturada"""
    def __init__(
        self,
        level: LogLevel,
        message: str,
        log_type: LogType = LogType.SYSTEM,
        module: str = "",
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        extra_data: Optional[Dict] = None
    ):
        self.timestamp = datetime.now()
        self.level = level
        self.message = message
        self.log_type = log_type
        self.module = module
        self.user_id = user_id
        self.request_id = request_id
        self.extra_data = extra_data or {}
        
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "log_type": self.log_type,
            "module": self.module,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "extra_data": self.extra_data
        }
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)

class EncodingSafeFormatter(logging.Formatter):
    """Formatter que remove emojis e garante encoding seguro"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mapping de emojis para texto
        self.emoji_map = {
            '🎯': '[TARGET]',
            '📊': '[CHART]',
            '💾': '[SAVE]',
            '⚡': '[FAST]',
            '📚': '[DOCS]',
            '🚀': '[ROCKET]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '🔄': '[REFRESH]',
            '🎉': '[PARTY]',
            '💪': '[STRONG]',
            '🌟': '[STAR]',
            '🔧': '[TOOL]',
            '📱': '[MOBILE]',
            '💡': '[IDEA]',
            '🌍': '[WORLD]',
            '💼': '[WORK]',
            '📈': '[UP]',
            '🛑': '[STOP]',
            '⏰': '[CLOCK]',
            '🔒': '[LOCK]',
            '🔐': '[SECURE]',
            '🌐': '[WEB]',
            '🔗': '[LINK]',
            '🎪': '[EVENT]',
            '👥': '[USERS]',
            '📅': '[CALENDAR]',
            '🏪': '[SHOP]',
            '📦': '[BOX]',
            '🤖': '[BOT]',
            '🟢': '[GREEN]',
            '🔴': '[RED]',
            '🟡': '[YELLOW]'
        }
    
    def clean_emoji(self, text: str) -> str:
        """Remove ou substitui emojis por texto seguro"""
        try:
            # Substituir emojis conhecidos
            for emoji, replacement in self.emoji_map.items():
                text = text.replace(emoji, replacement)
            
            # Remover outros caracteres unicode problemáticos
            text = text.encode('ascii', errors='ignore').decode('ascii')
            return text
        except Exception:
            # Fallback: remover todos os caracteres não-ASCII
            return ''.join(char for char in text if ord(char) < 128)
    
    def format(self, record):
        """Formatar log removendo emojis"""
        # Limpar mensagem
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self.clean_emoji(record.msg)
        
        # Limpar argumentos
        if hasattr(record, 'args') and record.args:
            clean_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    clean_args.append(self.clean_emoji(arg))
                else:
                    clean_args.append(arg)
            record.args = tuple(clean_args)
        
        return super().format(record)

class AdvancedLogManager:
    """Gerenciador avançado de logs"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.config_file = self.log_dir / "logging_config.json"
        self.alerts_file = self.log_dir / "alerts.json"
        
        # Configurações padrão
        self.config = {
            "log_level": "INFO",
            "max_file_size_mb": 50,
            "backup_count": 5,
            "retention_days": 30,
            "enable_console": True,
            "enable_file": True,
            "enable_json": True,
            "enable_rotation": True,
            "enable_compression": True,
            "enable_alerts": True,
            "alert_levels": ["ERROR", "CRITICAL"],
            "max_log_entries_memory": 1000
        }
        
        self.recent_logs: List[LogEntry] = []
        self.alerts: List[Dict] = []
        self.loggers: Dict[str, logging.Logger] = {}
        
        self.load_config()
        self.setup_logging()
    
    def load_config(self):
        """Carrega configurações de logging"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                print(f"Erro ao carregar config de logging: {e}")
    
    def save_config(self):
        """Salva configurações de logging"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar config de logging: {e}")
    
    def setup_logging(self):
        """Configura sistema de logging"""
        # Configurar logging root
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Nível de log
        log_level = getattr(logging, self.config["log_level"])
        root_logger.setLevel(log_level)
        
        # Formato safe para encoding
        safe_formatter = EncodingSafeFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para console (se habilitado)
        if self.config["enable_console"]:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(safe_formatter)
            console_handler.setLevel(log_level)
            root_logger.addHandler(console_handler)
        
        # Handler para arquivo principal (se habilitado)
        if self.config["enable_file"]:
            main_log_file = self.log_dir / "sistema_universal.log"
            
            if self.config["enable_rotation"]:
                # Handler com rotação
                file_handler = logging.handlers.RotatingFileHandler(
                    main_log_file,
                    maxBytes=self.config["max_file_size_mb"] * 1024 * 1024,
                    backupCount=self.config["backup_count"],
                    encoding='utf-8'
                )
            else:
                # Handler simples
                file_handler = logging.FileHandler(
                    main_log_file,
                    encoding='utf-8'
                )
            
            file_handler.setFormatter(safe_formatter)
            file_handler.setLevel(log_level)
            root_logger.addHandler(file_handler)
        
        # Handler para logs JSON estruturados (se habilitado)
        if self.config["enable_json"]:
            json_log_file = self.log_dir / "sistema_universal.jsonl"
            json_handler = logging.FileHandler(json_log_file, encoding='utf-8')
            json_handler.setFormatter(logging.Formatter('%(message)s'))
            json_handler.setLevel(log_level)
            
            # Interceptar logs para JSON
            json_handler.addFilter(self.json_filter)
            root_logger.addHandler(json_handler)
    
    def json_filter(self, record):
        """Filtro para converter logs em JSON"""
        try:
            log_entry = LogEntry(
                level=LogLevel(record.levelname),
                message=record.getMessage(),
                log_type=LogType.SYSTEM,
                module=record.name
            )
            
            # Substituir mensagem original por JSON
            record.msg = log_entry.to_json()
            record.args = ()
            
            # Adicionar à memória
            self.add_to_memory(log_entry)
            
            # Verificar alertas
            if record.levelname in self.config["alert_levels"]:
                self.create_alert(log_entry)
            
            return True
        except Exception:
            return True
    
    def add_to_memory(self, log_entry: LogEntry):
        """Adiciona log à memória recente"""
        self.recent_logs.append(log_entry)
        
        # Manter apenas os logs mais recentes
        max_entries = self.config["max_log_entries_memory"]
        if len(self.recent_logs) > max_entries:
            self.recent_logs = self.recent_logs[-max_entries:]
    
    def create_alert(self, log_entry: LogEntry):
        """Cria alerta para log crítico"""
        if not self.config["enable_alerts"]:
            return
        
        alert = {
            "id": f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": log_entry.timestamp.isoformat(),
            "level": log_entry.level,
            "message": log_entry.message,
            "log_type": log_entry.log_type,
            "module": log_entry.module,
            "status": "new",
            "acknowledged": False
        }
        
        self.alerts.append(alert)
        
        # Salvar alertas
        try:
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(self.alerts, f, indent=2, ensure_ascii=False, default=str)
        except Exception:
            pass
    
    def get_recent_logs(self, limit: int = 100, level: Optional[str] = None) -> List[Dict]:
        """Obtém logs recentes"""
        logs = self.recent_logs[-limit:]
        
        if level:
            logs = [log for log in logs if log.level == level]
        
        return [log.to_dict() for log in logs]
    
    def get_log_stats(self) -> Dict:
        """Estatísticas dos logs"""
        total_logs = len(self.recent_logs)
        
        # Contar por nível
        level_counts = {}
        for log in self.recent_logs:
            level = log.level
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Contar por tipo
        type_counts = {}
        for log in self.recent_logs:
            log_type = log.log_type
            type_counts[log_type] = type_counts.get(log_type, 0) + 1
        
        # Alertas
        new_alerts = len([a for a in self.alerts if a["status"] == "new"])
        total_alerts = len(self.alerts)
        
        return {
            "total_logs": total_logs,
            "level_counts": level_counts,
            "type_counts": type_counts,
            "new_alerts": new_alerts,
            "total_alerts": total_alerts,
            "config": self.config
        }
    
    def cleanup_old_logs(self):
        """Limpeza de logs antigos"""
        try:
            retention_days = self.config["retention_days"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Limpar logs em memória
            self.recent_logs = [
                log for log in self.recent_logs 
                if log.timestamp > cutoff_date
            ]
            
            # Limpar arquivos de log antigos
            log_files = list(self.log_dir.glob("*.log*"))
            for log_file in log_files:
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    if self.config["enable_compression"]:
                        # Comprimir antes de remover
                        compressed_file = log_file.with_suffix(log_file.suffix + '.gz')
                        with open(log_file, 'rb') as f_in:
                            with gzip.open(compressed_file, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        log_file.unlink()
                    else:
                        log_file.unlink()
                        
        except Exception as e:
            logging.error(f"Erro na limpeza de logs: {e}")
    
    def search_logs(self, query: str, limit: int = 100) -> List[Dict]:
        """Busca nos logs"""
        matching_logs = []
        query_lower = query.lower()
        
        for log in self.recent_logs[-limit:]:
            if (query_lower in log.message.lower() or 
                query_lower in log.module.lower() or
                query_lower in str(log.extra_data).lower()):
                matching_logs.append(log.to_dict())
        
        return matching_logs
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Marca alerta como reconhecido"""
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                alert["status"] = "acknowledged"
                return True
        return False

# Instância global do gerenciador de logs
log_manager = AdvancedLogManager()

# Logger personalizado para o sistema
def get_logger(name: str) -> logging.Logger:
    """Obtém logger configurado para o sistema"""
    return logging.getLogger(name)
