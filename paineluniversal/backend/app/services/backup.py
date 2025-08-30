"""
Sistema de Backup e Recuperação Automática
Gerencia backups incrementais e recuperação de dados
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import os
import shutil
import gzip
import uuid
from dataclasses import dataclass
from pathlib import Path
import hashlib

class TipoBackup(str, Enum):
    """Tipos de backup disponíveis"""
    COMPLETO = "completo"
    INCREMENTAL = "incremental"
    DIFERENCIAL = "diferencial"
    CONFIGURACAO = "configuracao"
    BANCO_DADOS = "banco_dados"
    ARQUIVOS = "arquivos"

class StatusBackup(str, Enum):
    """Status de um backup"""
    PENDENTE = "pendente"
    EM_PROGRESSO = "em_progresso"
    CONCLUIDO = "concluido"
    FALHOU = "falhou"
    CORROMPIDO = "corrompido"

@dataclass
class ConfigBackup:
    """Configuração de backup"""
    id: str
    nome: str
    tipo: TipoBackup
    origem: str
    destino: str
    frequencia_horas: int
    retenção_dias: int
    compressao: bool = True
    criptografia: bool = False
    ativo: bool = True

@dataclass
class RegistroBackup:
    """Registro de um backup executado"""
    id: str
    config_id: str
    tipo: TipoBackup
    inicio: datetime
    fim: Optional[datetime]
    status: StatusBackup
    tamanho_bytes: int
    arquivos_total: int
    erro: Optional[str]
    checksum: Optional[str]
    caminho_arquivo: Optional[str]

class BackupService:
    """Service para backup e recuperação automática"""
    
    def __init__(self, diretorio_backup: str = "./backups"):
        self.diretorio_backup = Path(diretorio_backup)
        self.diretorio_backup.mkdir(exist_ok=True)
        
        self.configuracoes = {}
        self.historico_backups = []
        self.backup_em_progresso = {}
        self._executando = False
        
        # Inicializa configurações padrão
        self._inicializar_configuracoes_padrao()
    
    def _inicializar_configuracoes_padrao(self):
        """Inicializa configurações padrão de backup"""
        configuracoes_padrao = [
            ConfigBackup(
                id="config_sistema",
                nome="Configurações do Sistema",
                tipo=TipoBackup.CONFIGURACAO,
                origem="./config",
                destino=str(self.diretorio_backup / "configuracoes"),
                frequencia_horas=24,
                retenção_dias=30,
                compressao=True
            ),
            ConfigBackup(
                id="banco_dados_diario",
                nome="Backup Diário do Banco",
                tipo=TipoBackup.BANCO_DADOS,
                origem="./database",
                destino=str(self.diretorio_backup / "database"),
                frequencia_horas=24,
                retenção_dias=7,
                compressao=True,
                criptografia=True
            ),
            ConfigBackup(
                id="arquivos_usuarios",
                nome="Arquivos de Usuários",
                tipo=TipoBackup.INCREMENTAL,
                origem="./uploads",
                destino=str(self.diretorio_backup / "uploads"),
                frequencia_horas=6,
                retenção_dias=14,
                compressao=True
            ),
            ConfigBackup(
                id="logs_sistema",
                nome="Logs do Sistema",
                tipo=TipoBackup.DIFERENCIAL,
                origem="./logs",
                destino=str(self.diretorio_backup / "logs"),
                frequencia_horas=12,
                retenção_dias=30,
                compressao=True
            )
        ]
        
        for config in configuracoes_padrao:
            self.configuracoes[config.id] = config
    
    async def iniciar_servico(self):
        """Inicia o serviço de backup automático"""
        if self._executando:
            return
        
        self._executando = True
        asyncio.create_task(self._loop_backup_automatico())
        print("✅ Serviço de backup iniciado")
    
    async def parar_servico(self):
        """Para o serviço de backup automático"""
        self._executando = False
        print("🔄 Serviço de backup parado")
    
    async def _loop_backup_automatico(self):
        """Loop principal do backup automático"""
        while self._executando:
            try:
                await self._verificar_backups_pendentes()
                await self._limpar_backups_antigos()
                
                # Verifica a cada hora
                await asyncio.sleep(3600)
                
            except Exception as e:
                print(f"Erro no loop de backup: {e}")
                await asyncio.sleep(3600)
    
    async def _verificar_backups_pendentes(self):
        """Verifica e executa backups pendentes"""
        agora = datetime.now()
        
        for config in self.configuracoes.values():
            if not config.ativo:
                continue
            
            # Verifica se é hora de fazer backup
            ultimo_backup = self._obter_ultimo_backup(config.id)
            if ultimo_backup:
                proximo_backup = ultimo_backup.inicio + timedelta(hours=config.frequencia_horas)
                if agora < proximo_backup:
                    continue
            
            # Executa backup se não houver outro em progresso
            if config.id not in self.backup_em_progresso:
                await self._executar_backup(config.id)
    
    def _obter_ultimo_backup(self, config_id: str) -> Optional[RegistroBackup]:
        """Obtém o último backup de uma configuração"""
        backups_config = [
            b for b in self.historico_backups 
            if b.config_id == config_id and b.status == StatusBackup.CONCLUIDO
        ]
        return max(backups_config, key=lambda x: x.inicio) if backups_config else None
    
    async def _executar_backup(self, config_id: str) -> RegistroBackup:
        """Executa um backup"""
        if config_id not in self.configuracoes:
            raise ValueError(f"Configuração {config_id} não encontrada")
        
        config = self.configuracoes[config_id]
        registro = RegistroBackup(
            id=str(uuid.uuid4()),
            config_id=config_id,
            tipo=config.tipo,
            inicio=datetime.now(),
            fim=None,
            status=StatusBackup.EM_PROGRESSO,
            tamanho_bytes=0,
            arquivos_total=0,
            erro=None,
            checksum=None,
            caminho_arquivo=None
        )
        
        self.backup_em_progresso[config_id] = registro
        self.historico_backups.append(registro)
        
        try:
            # Simula execução de backup
            await self._simular_backup(config, registro)
            
            registro.status = StatusBackup.CONCLUIDO
            registro.fim = datetime.now()
            
            print(f"✅ Backup concluído: {config.nome}")
            
        except Exception as e:
            registro.status = StatusBackup.FALHOU
            registro.erro = str(e)
            registro.fim = datetime.now()
            
            print(f"❌ Falha no backup {config.nome}: {e}")
        
        finally:
            if config_id in self.backup_em_progresso:
                del self.backup_em_progresso[config_id]
        
        return registro
    
    async def _simular_backup(self, config: ConfigBackup, registro: RegistroBackup):
        """Simula execução de backup (substitua pela implementação real)"""
        # Simula tempo de processamento
        await asyncio.sleep(2)
        
        # Simula dados do backup
        registro.tamanho_bytes = 1024 * 1024 * 50  # 50MB
        registro.arquivos_total = 150
        registro.checksum = hashlib.md5(f"{config.id}_{registro.id}".encode()).hexdigest()
        
        # Simula criação do arquivo de backup
        timestamp = registro.inicio.strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"{config.nome.replace(' ', '_')}_{timestamp}.backup"
        if config.compressao:
            nome_arquivo += ".gz"
        
        caminho_destino = Path(config.destino)
        caminho_destino.mkdir(parents=True, exist_ok=True)
        
        registro.caminho_arquivo = str(caminho_destino / nome_arquivo)
        
        # Simula criação do arquivo
        with open(registro.caminho_arquivo, 'w') as f:
            f.write(f"Backup simulado - {config.nome} - {registro.inicio}")
    
    async def _limpar_backups_antigos(self):
        """Remove backups antigos baseado na política de retenção"""
        agora = datetime.now()
        
        for config in self.configuracoes.values():
            data_limite = agora - timedelta(days=config.retenção_dias)
            
            backups_antigos = [
                b for b in self.historico_backups
                if (b.config_id == config.id and 
                    b.inicio < data_limite and 
                    b.status == StatusBackup.CONCLUIDO)
            ]
            
            for backup in backups_antigos:
                try:
                    # Remove arquivo físico
                    if backup.caminho_arquivo and os.path.exists(backup.caminho_arquivo):
                        os.remove(backup.caminho_arquivo)
                    
                    # Remove do histórico
                    self.historico_backups.remove(backup)
                    
                except Exception as e:
                    print(f"Erro ao remover backup antigo {backup.id}: {e}")
    
    def obter_configuracoes(self) -> List[Dict[str, Any]]:
        """Retorna todas as configurações de backup"""
        return [
            {
                "id": config.id,
                "nome": config.nome,
                "tipo": config.tipo,
                "origem": config.origem,
                "destino": config.destino,
                "frequencia_horas": config.frequencia_horas,
                "retenção_dias": config.retenção_dias,
                "compressao": config.compressao,
                "criptografia": config.criptografia,
                "ativo": config.ativo
            }
            for config in self.configuracoes.values()
        ]
    
    def obter_historico_backups(self, limite: int = 100) -> List[Dict[str, Any]]:
        """Retorna histórico de backups"""
        backups_recentes = sorted(
            self.historico_backups,
            key=lambda x: x.inicio,
            reverse=True
        )[:limite]
        
        return [
            {
                "id": backup.id,
                "config_id": backup.config_id,
                "config_nome": self.configuracoes.get(backup.config_id, {}).nome,
                "tipo": backup.tipo,
                "inicio": backup.inicio.isoformat(),
                "fim": backup.fim.isoformat() if backup.fim else None,
                "status": backup.status,
                "tamanho_mb": round(backup.tamanho_bytes / (1024 * 1024), 2),
                "arquivos_total": backup.arquivos_total,
                "erro": backup.erro,
                "caminho_arquivo": backup.caminho_arquivo
            }
            for backup in backups_recentes
        ]
    
    def obter_estatisticas_backup(self) -> Dict[str, Any]:
        """Retorna estatísticas de backup"""
        total_backups = len(self.historico_backups)
        backups_sucesso = len([b for b in self.historico_backups if b.status == StatusBackup.CONCLUIDO])
        backups_falhou = len([b for b in self.historico_backups if b.status == StatusBackup.FALHOU])
        
        # Backups dos últimos 7 dias
        uma_semana_atras = datetime.now() - timedelta(days=7)
        backups_semana = [b for b in self.historico_backups if b.inicio >= uma_semana_atras]
        
        # Tamanho total dos backups
        tamanho_total = sum(b.tamanho_bytes for b in self.historico_backups if b.status == StatusBackup.CONCLUIDO)
        
        # Próximos backups
        proximos_backups = []
        agora = datetime.now()
        
        for config in self.configuracoes.values():
            if not config.ativo:
                continue
            
            ultimo_backup = self._obter_ultimo_backup(config.id)
            if ultimo_backup:
                proximo = ultimo_backup.inicio + timedelta(hours=config.frequencia_horas)
            else:
                proximo = agora + timedelta(minutes=5)  # Primeiro backup em 5 minutos
            
            if proximo > agora:
                proximos_backups.append({
                    "config_id": config.id,
                    "config_nome": config.nome,
                    "proximo_backup": proximo.isoformat(),
                    "tempo_restante_horas": round((proximo - agora).total_seconds() / 3600, 1)
                })
        
        return {
            "resumo": {
                "total_backups": total_backups,
                "sucesso": backups_sucesso,
                "falhas": backups_falhou,
                "taxa_sucesso": round((backups_sucesso / total_backups * 100) if total_backups > 0 else 0, 1),
                "backups_esta_semana": len(backups_semana),
                "tamanho_total_gb": round(tamanho_total / (1024 * 1024 * 1024), 2)
            },
            "configuracoes_ativas": len([c for c in self.configuracoes.values() if c.ativo]),
            "backups_em_progresso": len(self.backup_em_progresso),
            "proximos_backups": sorted(proximos_backups, key=lambda x: x["proximo_backup"])[:5]
        }
    
    async def executar_backup_manual(self, config_id: str) -> RegistroBackup:
        """Executa backup manual de uma configuração"""
        if config_id not in self.configuracoes:
            raise ValueError(f"Configuração {config_id} não encontrada")
        
        if config_id in self.backup_em_progresso:
            raise ValueError(f"Backup da configuração {config_id} já em progresso")
        
        return await self._executar_backup(config_id)
    
    def criar_configuracao(self, configuracao: Dict[str, Any]) -> str:
        """Cria nova configuração de backup"""
        config_id = configuracao.get("id", str(uuid.uuid4()))
        
        config = ConfigBackup(
            id=config_id,
            nome=configuracao["nome"],
            tipo=TipoBackup(configuracao["tipo"]),
            origem=configuracao["origem"],
            destino=configuracao["destino"],
            frequencia_horas=configuracao["frequencia_horas"],
            retenção_dias=configuracao["retenção_dias"],
            compressao=configuracao.get("compressao", True),
            criptografia=configuracao.get("criptografia", False),
            ativo=configuracao.get("ativo", True)
        )
        
        self.configuracoes[config_id] = config
        return config_id
    
    def atualizar_configuracao(self, config_id: str, updates: Dict[str, Any]) -> bool:
        """Atualiza configuração de backup"""
        if config_id not in self.configuracoes:
            return False
        
        config = self.configuracoes[config_id]
        
        for campo, valor in updates.items():
            if hasattr(config, campo):
                setattr(config, campo, valor)
        
        return True
    
    def remover_configuracao(self, config_id: str) -> bool:
        """Remove configuração de backup"""
        if config_id not in self.configuracoes:
            return False
        
        # Não permite remover se há backup em progresso
        if config_id in self.backup_em_progresso:
            return False
        
        del self.configuracoes[config_id]
        return True
    
    async def restaurar_backup(self, backup_id: str, destino: str) -> Dict[str, Any]:
        """Restaura um backup específico"""
        backup = next((b for b in self.historico_backups if b.id == backup_id), None)
        
        if not backup:
            raise ValueError(f"Backup {backup_id} não encontrado")
        
        if backup.status != StatusBackup.CONCLUIDO:
            raise ValueError(f"Backup {backup_id} não está completo")
        
        if not backup.caminho_arquivo or not os.path.exists(backup.caminho_arquivo):
            raise ValueError(f"Arquivo de backup {backup_id} não encontrado")
        
        # Simula restauração
        await asyncio.sleep(1)
        
        resultado = {
            "backup_id": backup_id,
            "origem": backup.caminho_arquivo,
            "destino": destino,
            "inicio_restauracao": datetime.now().isoformat(),
            "status": "sucesso",
            "arquivos_restaurados": backup.arquivos_total,
            "tamanho_restaurado_mb": round(backup.tamanho_bytes / (1024 * 1024), 2)
        }
        
        print(f"✅ Backup {backup_id} restaurado para {destino}")
        return resultado
    
    def validar_integridade_backup(self, backup_id: str) -> Dict[str, Any]:
        """Valida integridade de um backup"""
        backup = next((b for b in self.historico_backups if b.id == backup_id), None)
        
        if not backup:
            raise ValueError(f"Backup {backup_id} não encontrado")
        
        if not backup.caminho_arquivo or not os.path.exists(backup.caminho_arquivo):
            return {
                "backup_id": backup_id,
                "integro": False,
                "erro": "Arquivo de backup não encontrado"
            }
        
        # Simula validação de integridade
        # Na implementação real, validaria checksum, estrutura do arquivo, etc.
        
        return {
            "backup_id": backup_id,
            "integro": True,
            "checksum_original": backup.checksum,
            "checksum_atual": backup.checksum,  # Simulado
            "tamanho_bytes": backup.tamanho_bytes,
            "verificado_em": datetime.now().isoformat()
        }
