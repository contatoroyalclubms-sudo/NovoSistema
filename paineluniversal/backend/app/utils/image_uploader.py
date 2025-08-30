"""
Módulo para upload e gestão de imagens
"""
import os
import shutil
from typing import Optional
from pathlib import Path
import uuid
from fastapi import UploadFile, HTTPException


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def upload_image(file: UploadFile) -> str:
    """
    Faz upload de uma imagem
    
    Args:
        file: Arquivo da imagem
        
    Returns:
        str: Nome do arquivo salvo
    """
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
    
    # Gera nome único para o arquivo
    file_extension = Path(file.filename).suffix if file.filename else '.jpg'
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / filename
    
    # Salva o arquivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return filename


async def delete_image(filename: str) -> bool:
    """
    Deleta uma imagem
    
    Args:
        filename: Nome do arquivo a deletar
        
    Returns:
        bool: True se deletado com sucesso
    """
    try:
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception:
        return False


def get_image_url(filename: Optional[str]) -> Optional[str]:
    """
    Retorna a URL da imagem
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        str: URL da imagem ou None
    """
    if not filename:
        return None
    return f"/uploads/{filename}"
