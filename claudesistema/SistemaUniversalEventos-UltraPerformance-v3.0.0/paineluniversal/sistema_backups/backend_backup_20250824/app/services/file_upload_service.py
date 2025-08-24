"""
Serviço avançado de upload de arquivos para eventos
Sistema Universal de Gestão de Eventos - Sprint 3
"""

import os
import uuid
import logging
import mimetypes
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from PIL import Image, ImageOps
import aiofiles
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import EventoAnexo, Usuario, Evento

logger = logging.getLogger(__name__)

class FileUploadService:
    """Serviço avançado de upload de arquivos"""
    
    # Tipos de arquivo permitidos por categoria
    ALLOWED_TYPES = {
        'image': ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
        'document': ['application/pdf', 'application/msword', 
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'text/plain', 'application/rtf'],
        'video': ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo'],
        'audio': ['audio/mpeg', 'audio/wav', 'audio/ogg'],
        'archive': ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed']
    }
    
    # Tamanhos máximos por tipo (em bytes)
    MAX_FILE_SIZES = {
        'image': 10 * 1024 * 1024,      # 10MB
        'document': 50 * 1024 * 1024,   # 50MB
        'video': 500 * 1024 * 1024,     # 500MB
        'audio': 100 * 1024 * 1024,     # 100MB
        'archive': 100 * 1024 * 1024    # 100MB
    }
    
    # Dimensões para thumbnails
    THUMBNAIL_SIZES = {
        'small': (150, 150),
        'medium': (300, 300),
        'large': (800, 600)
    }
    
    def __init__(self):
        self.upload_base_dir = Path(settings.upload_dir)
        self.upload_base_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_category(self, mime_type: str) -> str:
        """Determina a categoria do arquivo baseado no mime type"""
        for category, types in self.ALLOWED_TYPES.items():
            if mime_type in types:
                return category
        return 'other'
    
    def _validate_file(self, file: UploadFile, categoria: str) -> None:
        """Valida o arquivo antes do upload"""
        # Verificar mime type
        if file.content_type not in self.ALLOWED_TYPES.get(categoria, []):
            allowed = ', '.join(self.ALLOWED_TYPES.get(categoria, []))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo não suportado para categoria {categoria}. Permitidos: {allowed}"
            )
        
        # Verificar tamanho
        max_size = self.MAX_FILE_SIZES.get(categoria, 10 * 1024 * 1024)  # Default 10MB
        if file.size and file.size > max_size:
            max_mb = max_size / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Arquivo muito grande. Máximo permitido para {categoria}: {max_mb}MB"
            )
        
        # Verificar extensão
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome do arquivo não pode estar vazio"
            )
        
        extension = Path(file.filename).suffix.lower()
        if not extension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo deve ter uma extensão válida"
            )
    
    def _generate_filename(self, original_filename: str, evento_id: str, categoria: str) -> str:
        """Gera nome único para o arquivo"""
        extension = Path(original_filename).suffix.lower()
        timestamp = uuid.uuid4().hex[:8]
        return f"evento_{evento_id}_{categoria}_{timestamp}{extension}"
    
    def _get_upload_path(self, evento_id: str, categoria: str) -> Path:
        """Retorna o caminho de upload para a categoria"""
        upload_dir = self.upload_base_dir / "eventos" / str(evento_id) / categoria
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir
    
    async def _create_image_thumbnail(self, image_path: Path, size: str = 'medium') -> Optional[Path]:
        """Cria thumbnail para imagem"""
        try:
            thumbnail_dir = image_path.parent / "thumbnails"
            thumbnail_dir.mkdir(exist_ok=True)
            
            thumbnail_path = thumbnail_dir / f"{image_path.stem}_{size}{image_path.suffix}"
            
            with Image.open(image_path) as img:
                # Converter para RGB se necessário
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Redimensionar mantendo proporção
                img_resized = ImageOps.fit(
                    img, 
                    self.THUMBNAIL_SIZES[size], 
                    Image.Resampling.LANCZOS
                )
                
                # Salvar thumbnail com qualidade otimizada
                img_resized.save(thumbnail_path, "JPEG", quality=85, optimize=True)
                
                return thumbnail_path
                
        except Exception as e:
            logger.error(f"Erro ao criar thumbnail para {image_path}: {e}")
            return None
    
    async def _extract_metadata(self, file_path: Path, mime_type: str) -> Dict[str, Any]:
        """Extrai metadados do arquivo"""
        metadata = {
            "size_bytes": file_path.stat().st_size,
            "mime_type": mime_type
        }
        
        try:
            if mime_type.startswith('image/'):
                with Image.open(file_path) as img:
                    metadata.update({
                        "width": img.width,
                        "height": img.height,
                        "format": img.format,
                        "mode": img.mode
                    })
                    
                    # Extrair EXIF se disponível
                    if hasattr(img, '_getexif') and img._getexif():
                        exif = img._getexif()
                        if exif:
                            metadata["exif"] = {
                                str(k): str(v) for k, v in exif.items() 
                                if isinstance(v, (str, int, float))
                            }
            
            # Para outros tipos, adicionar informações específicas conforme necessário
            
        except Exception as e:
            logger.error(f"Erro ao extrair metadados de {file_path}: {e}")
        
        return metadata
    
    async def upload_file(
        self, 
        file: UploadFile, 
        evento_id: str,
        categoria: str,
        descricao: Optional[str] = None,
        tags: Optional[List[str]] = None,
        publico: bool = True,
        requer_login: bool = False,
        user: Usuario = None,
        db: Session = None
    ) -> EventoAnexo:
        """
        Upload de arquivo para evento
        
        Args:
            file: Arquivo para upload
            evento_id: ID do evento
            categoria: Categoria do arquivo (logo, banner, documento, foto, video)
            descricao: Descrição do arquivo
            tags: Tags do arquivo
            publico: Se o arquivo é público
            requer_login: Se requer login para acessar
            user: Usuário que está fazendo o upload
            db: Sessão do banco de dados
        
        Returns:
            EventoAnexo: Registro do anexo criado
        """
        try:
            # Validar arquivo
            self._validate_file(file, categoria)
            
            # Verificar se evento existe
            evento = db.query(Evento).filter(Evento.id == evento_id).first()
            if not evento:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Evento não encontrado"
                )
            
            # Gerar nome único
            filename = self._generate_filename(file.filename, evento_id, categoria)
            
            # Definir caminho de upload
            upload_dir = self._get_upload_path(evento_id, categoria)
            file_path = upload_dir / filename
            
            # Salvar arquivo
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # URL do arquivo
            file_url = f"/uploads/eventos/{evento_id}/{categoria}/{filename}"
            
            # Criar thumbnail para imagens
            thumbnail_url = None
            if categoria == 'image' or file.content_type.startswith('image/'):
                thumbnail_path = await self._create_image_thumbnail(file_path)
                if thumbnail_path:
                    thumbnail_url = f"/uploads/eventos/{evento_id}/{categoria}/thumbnails/{thumbnail_path.name}"
            
            # Extrair metadados
            metadata = await self._extract_metadata(file_path, file.content_type)
            
            # Criar registro no banco
            db_anexo = EventoAnexo(
                evento_id=evento_id,
                nome_original=file.filename,
                nome_arquivo=filename,
                tipo_arquivo=self._get_file_category(file.content_type),
                mime_type=file.content_type,
                tamanho_bytes=file_path.stat().st_size,
                url_arquivo=file_url,
                url_thumbnail=thumbnail_url,
                categoria=categoria,
                descricao=descricao,
                tags=tags or [],
                publico=publico,
                requer_login=requer_login,
                uploaded_by=user.id,
                metadata=metadata
            )
            
            db.add(db_anexo)
            db.commit()
            db.refresh(db_anexo)
            
            logger.info(f"Arquivo uploaded: {file.filename} -> {filename} para evento {evento_id}")
            
            return db_anexo
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro no upload do arquivo: {e}")
            # Limpar arquivo se foi criado
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno no upload do arquivo"
            )
    
    async def upload_multiple_files(
        self,
        files: List[UploadFile],
        evento_id: str,
        categoria: str,
        user: Usuario,
        db: Session,
        **kwargs
    ) -> List[EventoAnexo]:
        """Upload de múltiplos arquivos"""
        uploaded_files = []
        
        try:
            for file in files:
                anexo = await self.upload_file(
                    file=file,
                    evento_id=evento_id,
                    categoria=categoria,
                    user=user,
                    db=db,
                    **kwargs
                )
                uploaded_files.append(anexo)
            
            return uploaded_files
            
        except Exception as e:
            # Rollback de todos os uploads em caso de erro
            for anexo in uploaded_files:
                try:
                    file_path = self.upload_base_dir / "eventos" / evento_id / categoria / anexo.nome_arquivo
                    if file_path.exists():
                        file_path.unlink()
                    
                    # Remover thumbnail se existir
                    if anexo.url_thumbnail:
                        thumbnail_path = file_path.parent / "thumbnails" / f"{file_path.stem}_medium{file_path.suffix}"
                        if thumbnail_path.exists():
                            thumbnail_path.unlink()
                            
                except Exception as cleanup_error:
                    logger.error(f"Erro no cleanup do arquivo {anexo.nome_arquivo}: {cleanup_error}")
            
            raise e
    
    async def delete_file(self, anexo: EventoAnexo) -> bool:
        """Remove arquivo e seu registro"""
        try:
            # Construir caminho do arquivo
            file_path = Path(settings.upload_dir) / "eventos" / str(anexo.evento_id) / anexo.categoria / anexo.nome_arquivo
            
            # Remover arquivo principal
            if file_path.exists():
                file_path.unlink()
            
            # Remover thumbnail se existir
            if anexo.url_thumbnail:
                thumbnail_path = file_path.parent / "thumbnails" / f"{file_path.stem}_medium{file_path.suffix}"
                if thumbnail_path.exists():
                    thumbnail_path.unlink()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo {anexo.nome_arquivo}: {e}")
            return False
    
    def get_file_info(self, anexo: EventoAnexo) -> Dict[str, Any]:
        """Retorna informações detalhadas do arquivo"""
        file_path = Path(settings.upload_dir) / "eventos" / str(anexo.evento_id) / anexo.categoria / anexo.nome_arquivo
        
        info = {
            "id": str(anexo.id),
            "nome_original": anexo.nome_original,
            "categoria": anexo.categoria,
            "tipo_arquivo": anexo.tipo_arquivo,
            "mime_type": anexo.mime_type,
            "tamanho_bytes": anexo.tamanho_bytes,
            "tamanho_formatado": self._format_file_size(anexo.tamanho_bytes),
            "url_arquivo": anexo.url_arquivo,
            "url_thumbnail": anexo.url_thumbnail,
            "publico": anexo.publico,
            "requer_login": anexo.requer_login,
            "tags": anexo.tags,
            "descricao": anexo.descricao,
            "metadata": anexo.metadata,
            "exists": file_path.exists(),
            "created_at": anexo.created_at.isoformat() if anexo.created_at else None
        }
        
        return info
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Formatar tamanho do arquivo"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    async def optimize_image(self, image_path: Path, quality: int = 85) -> Path:
        """Otimiza imagem reduzindo tamanho mantendo qualidade"""
        try:
            optimized_path = image_path.parent / f"optimized_{image_path.name}"
            
            with Image.open(image_path) as img:
                # Converter para RGB se necessário
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Redimensionar se muito grande
                max_dimension = 1920
                if max(img.size) > max_dimension:
                    ratio = max_dimension / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Salvar otimizada
                img.save(optimized_path, "JPEG", quality=quality, optimize=True)
            
            # Substituir arquivo original
            image_path.unlink()
            optimized_path.rename(image_path)
            
            return image_path
            
        except Exception as e:
            logger.error(f"Erro ao otimizar imagem {image_path}: {e}")
            return image_path

# Instância global do serviço
file_upload_service = FileUploadService()