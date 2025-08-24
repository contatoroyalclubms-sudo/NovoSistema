"""
Serviço avançado de geração de QR Codes
Sistema Universal de Gestão de Eventos - Sprint 3
"""

import io
import base64
import uuid
import json
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colorfills import SolidFillColorMask, RadialGradiantColorMask, SquareGradiantColorMask
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

class QRCodeService:
    """Serviço avançado de geração de QR Codes com branding personalizado"""
    
    # Estilos disponíveis para módulos
    MODULE_STYLES = {
        'square': SquareModuleDrawer(),
        'rounded': RoundedModuleDrawer(),
        'circle': CircleModuleDrawer()
    }
    
    # Tamanhos padrão
    DEFAULT_SIZES = {
        'small': 200,
        'medium': 400,
        'large': 800,
        'xlarge': 1200
    }
    
    def __init__(self):
        self.base_upload_dir = Path(settings.upload_dir)
        self.qr_dir = self.base_upload_dir / "qrcodes"
        self.qr_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_qr_data(
        self,
        evento_id: str,
        participante_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        action: str = "checkin",
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gera dados para QR Code com informações de segurança
        
        Args:
            evento_id: ID do evento
            participante_id: ID do participante (opcional)
            expires_at: Data de expiração
            action: Ação do QR Code (checkin, checkout, access, etc.)
            extra_data: Dados adicionais
        
        Returns:
            Dict com dados do QR Code
        """
        qr_data = {
            "id": str(uuid.uuid4()),
            "evento_id": str(evento_id),
            "action": action,
            "created_at": datetime.utcnow().isoformat(),
            "version": "2.0"
        }
        
        if participante_id:
            qr_data["participante_id"] = str(participante_id)
        
        if expires_at:
            qr_data["expires_at"] = expires_at.isoformat()
        
        if extra_data:
            qr_data["extra"] = extra_data
        
        # Gerar hash de verificação simples
        qr_data["checksum"] = self._generate_checksum(qr_data)
        
        return qr_data
    
    def _generate_checksum(self, data: Dict[str, Any]) -> str:
        """Gera checksum para validação do QR Code"""
        import hashlib
        
        # Criar string determinística dos dados (excluindo checksum)
        data_copy = data.copy()
        data_copy.pop('checksum', None)
        
        data_string = json.dumps(data_copy, sort_keys=True)
        checksum = hashlib.sha256(data_string.encode()).hexdigest()[:16]
        
        return checksum
    
    def validate_qr_data(self, qr_data: Dict[str, Any]) -> bool:
        """Valida dados do QR Code"""
        try:
            # Verificar campos obrigatórios
            required_fields = ['id', 'evento_id', 'action', 'created_at', 'checksum']
            for field in required_fields:
                if field not in qr_data:
                    logger.warning(f"Campo obrigatório ausente no QR Code: {field}")
                    return False
            
            # Verificar checksum
            expected_checksum = self._generate_checksum(qr_data)
            if qr_data.get('checksum') != expected_checksum:
                logger.warning("Checksum inválido no QR Code")
                return False
            
            # Verificar expiração
            if 'expires_at' in qr_data:
                expires_at = datetime.fromisoformat(qr_data['expires_at'])
                if datetime.utcnow() > expires_at:
                    logger.warning("QR Code expirado")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação do QR Code: {e}")
            return False
    
    def create_basic_qr(
        self,
        data: str,
        size: int = 400,
        border: int = 4,
        error_correction: str = 'M'
    ) -> qrcode.QRCode:
        """Cria QR Code básico"""
        
        error_corrections = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_corrections.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
            box_size=size // 37,  # Ajustar box_size baseado no tamanho final
            border=border,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        return qr
    
    def create_styled_qr(
        self,
        data: str,
        style_config: Optional[Dict[str, Any]] = None,
        size: int = 400
    ) -> Image.Image:
        """
        Cria QR Code com estilo personalizado
        
        Args:
            data: Dados para o QR Code
            style_config: Configuração de estilo
            size: Tamanho da imagem final
        
        Returns:
            Imagem PIL do QR Code
        """
        if not style_config:
            style_config = {}
        
        # Configurações padrão
        config = {
            'fill_color': style_config.get('fill_color', '#000000'),
            'back_color': style_config.get('back_color', '#ffffff'),
            'module_style': style_config.get('module_style', 'square'),
            'gradient': style_config.get('gradient', None),
            'logo_path': style_config.get('logo_path', None),
            'logo_size_ratio': style_config.get('logo_size_ratio', 0.3),
            'border': style_config.get('border', 4)
        }
        
        # Criar QR Code básico
        qr = self.create_basic_qr(data, size, config['border'])
        
        # Aplicar estilo de módulo
        module_drawer = self.MODULE_STYLES.get(config['module_style'], SquareModuleDrawer())
        
        # Aplicar preenchimento de cor
        if config['gradient']:
            if config['gradient']['type'] == 'radial':
                color_mask = RadialGradiantColorMask(
                    back_color=config['back_color'],
                    center_color=config['gradient']['center_color'],
                    edge_color=config['gradient']['edge_color']
                )
            elif config['gradient']['type'] == 'square':
                color_mask = SquareGradiantColorMask(
                    back_color=config['back_color'],
                    center_color=config['gradient']['center_color'],
                    edge_color=config['gradient']['edge_color']
                )
            else:
                color_mask = SolidFillColorMask(config['fill_color'])
        else:
            color_mask = SolidFillColorMask(config['fill_color'])
        
        # Gerar imagem com estilo
        qr_img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=module_drawer,
            color_mask=color_mask,
            back_color=config['back_color']
        )
        
        # Redimensionar se necessário
        if qr_img.size[0] != size:
            qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Adicionar logo se especificado
        if config['logo_path'] and Path(config['logo_path']).exists():
            qr_img = self._add_logo_to_qr(qr_img, config['logo_path'], config['logo_size_ratio'])\n        \n        return qr_img\n    \n    def _add_logo_to_qr(self, qr_img: Image.Image, logo_path: str, size_ratio: float = 0.3) -> Image.Image:\n        \"\"\"Adiciona logo no centro do QR Code\"\"\"\n        try:\n            logo = Image.open(logo_path)\n            \n            # Calcular tamanho do logo\n            qr_width, qr_height = qr_img.size\n            logo_size = int(min(qr_width, qr_height) * size_ratio)\n            \n            # Redimensionar logo mantendo proporção\n            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)\n            \n            # Converter para RGBA se necessário\n            if logo.mode != 'RGBA':\n                logo = logo.convert('RGBA')\n            \n            # Criar máscara circular para o logo (opcional)\n            mask = Image.new('L', logo.size, 0)\n            draw = ImageDraw.Draw(mask)\n            draw.ellipse((0, 0) + logo.size, fill=255)\n            \n            # Criar fundo branco para o logo\n            logo_bg = Image.new('RGBA', logo.size, (255, 255, 255, 255))\n            logo_bg.paste(logo, (0, 0), logo)\n            \n            # Posicionar no centro\n            logo_pos = (\n                (qr_width - logo.size[0]) // 2,\n                (qr_height - logo.size[1]) // 2\n            )\n            \n            # Colar logo no QR Code\n            qr_img = qr_img.convert('RGBA')\n            qr_img.paste(logo_bg, logo_pos, mask)\n            \n            return qr_img\n            \n        except Exception as e:\n            logger.error(f\"Erro ao adicionar logo ao QR Code: {e}\")\n            return qr_img\n    \n    def create_branded_qr(\n        self,\n        data: str,\n        evento_config: Dict[str, Any],\n        size: str = 'medium',\n        include_branding: bool = True\n    ) -> Image.Image:\n        \"\"\"\n        Cria QR Code com branding do evento\n        \n        Args:\n            data: Dados para o QR Code\n            evento_config: Configurações visuais do evento\n            size: Tamanho do QR Code\n            include_branding: Se deve incluir elementos de branding\n        \n        Returns:\n            Imagem PIL do QR Code com branding\n        \"\"\"\n        qr_size = self.DEFAULT_SIZES.get(size, 400)\n        \n        # Configuração de estilo baseada no evento\n        style_config = {\n            'fill_color': evento_config.get('cor_primaria', '#000000'),\n            'back_color': '#FFFFFF',\n            'module_style': evento_config.get('qr_code_style', {}).get('module_style', 'rounded'),\n            'border': 4\n        }\n        \n        # Adicionar gradiente se configurado\n        if evento_config.get('cor_secundaria'):\n            style_config['gradient'] = {\n                'type': 'radial',\n                'center_color': evento_config['cor_primaria'],\n                'edge_color': evento_config['cor_secundaria']\n            }\n        \n        # Adicionar logo se disponível\n        if evento_config.get('logo_url') and include_branding:\n            # Aqui você baixaria e salvaria temporariamente o logo\n            # Para este exemplo, assumimos que o logo já está salvo localmente\n            logo_path = self._get_local_logo_path(evento_config.get('logo_url'))\n            if logo_path:\n                style_config['logo_path'] = logo_path\n        \n        # Criar QR Code estilizado\n        qr_img = self.create_styled_qr(data, style_config, qr_size)\n        \n        # Adicionar elementos de branding adicionais se solicitado\n        if include_branding:\n            qr_img = self._add_branding_elements(qr_img, evento_config)\n        \n        return qr_img\n    \n    def _get_local_logo_path(self, logo_url: str) -> Optional[str]:\n        \"\"\"Retorna caminho local do logo (implementar download se necessário)\"\"\"\n        # Implementar lógica para baixar logo da URL se necessário\n        # Por enquanto, retorna None\n        return None\n    \n    def _add_branding_elements(self, qr_img: Image.Image, evento_config: Dict[str, Any]) -> Image.Image:\n        \"\"\"\n        Adiciona elementos de branding ao redor do QR Code\n        \n        Args:\n            qr_img: Imagem do QR Code\n            evento_config: Configurações do evento\n        \n        Returns:\n            Imagem com elementos de branding\n        \"\"\"\n        try:\n            # Expandir canvas para adicionar elementos\n            original_size = qr_img.size\n            margin = 100\n            new_size = (original_size[0] + margin * 2, original_size[1] + margin * 2 + 80)\n            \n            # Criar nova imagem com fundo\n            branded_img = Image.new('RGB', new_size, '#FFFFFF')\n            \n            # Colar QR Code no centro\n            qr_pos = (margin, margin + 40)\n            branded_img.paste(qr_img, qr_pos)\n            \n            # Adicionar texto do evento\n            draw = ImageDraw.Draw(branded_img)\n            \n            try:\n                # Tentar usar fonte personalizada\n                title_font = ImageFont.truetype(\"arial.ttf\", 24)\n                subtitle_font = ImageFont.truetype(\"arial.ttf\", 16)\n            except:\n                # Usar fonte padrão\n                title_font = ImageFont.load_default()\n                subtitle_font = ImageFont.load_default()\n            \n            # Título do evento\n            evento_nome = evento_config.get('nome', 'Evento')\n            text_width = draw.textlength(evento_nome, title_font)\n            text_x = (new_size[0] - text_width) // 2\n            \n            draw.text(\n                (text_x, 10),\n                evento_nome,\n                fill=evento_config.get('cor_primaria', '#000000'),\n                font=title_font\n            )\n            \n            # Subtítulo (data ou tipo)\n            subtitle = evento_config.get('data_inicio', '').split('T')[0] if evento_config.get('data_inicio') else 'Check-in'\n            subtitle_width = draw.textlength(subtitle, subtitle_font)\n            subtitle_x = (new_size[0] - subtitle_width) // 2\n            \n            draw.text(\n                (subtitle_x, new_size[1] - 30),\n                subtitle,\n                fill=evento_config.get('cor_secundaria', '#666666'),\n                font=subtitle_font\n            )\n            \n            return branded_img\n            \n        except Exception as e:\n            logger.error(f\"Erro ao adicionar elementos de branding: {e}\")\n            return qr_img\n    \n    def save_qr_code(\n        self,\n        qr_img: Image.Image,\n        filename: str,\n        formato: str = 'PNG',\n        quality: int = 95\n    ) -> str:\n        \"\"\"\n        Salva QR Code no sistema de arquivos\n        \n        Args:\n            qr_img: Imagem do QR Code\n            filename: Nome do arquivo\n            formato: Formato da imagem (PNG, JPEG, etc.)\n            quality: Qualidade da imagem (para JPEG)\n        \n        Returns:\n            Caminho do arquivo salvo\n        \"\"\"\n        file_path = self.qr_dir / f\"{filename}.{formato.lower()}\"\n        \n        try:\n            if formato.upper() == 'JPEG':\n                # Converter para RGB para JPEG\n                if qr_img.mode == 'RGBA':\n                    rgb_img = Image.new('RGB', qr_img.size, (255, 255, 255))\n                    rgb_img.paste(qr_img, mask=qr_img.split()[-1] if qr_img.mode == 'RGBA' else None)\n                    qr_img = rgb_img\n                \n                qr_img.save(file_path, formato, quality=quality, optimize=True)\n            else:\n                qr_img.save(file_path, formato)\n            \n            logger.info(f\"QR Code salvo: {file_path}\")\n            return str(file_path)\n            \n        except Exception as e:\n            logger.error(f\"Erro ao salvar QR Code: {e}\")\n            raise e\n    \n    def generate_qr_code_url(\n        self,\n        evento_id: str,\n        participante_id: Optional[str] = None,\n        expires_at: Optional[datetime] = None,\n        action: str = \"checkin\"\n    ) -> str:\n        \"\"\"\n        Gera URL para QR Code que será decodificada pelo app\n        \n        Returns:\n            URL que será codificada no QR Code\n        \"\"\"\n        base_url = settings.frontend_url or \"https://app.eventosuniversal.com\"\n        \n        # Gerar dados do QR Code\n        qr_data = self.generate_qr_data(\n            evento_id=evento_id,\n            participante_id=participante_id,\n            expires_at=expires_at,\n            action=action\n        )\n        \n        # Codificar dados em base64\n        data_json = json.dumps(qr_data)\n        data_encoded = base64.urlsafe_b64encode(data_json.encode()).decode()\n        \n        # Construir URL\n        qr_url = f\"{base_url}/qr/{action}?data={data_encoded}\"\n        \n        return qr_url\n    \n    def decode_qr_url(self, qr_url: str) -> Optional[Dict[str, Any]]:\n        \"\"\"\n        Decodifica URL do QR Code e retorna dados\n        \n        Args:\n            qr_url: URL do QR Code\n        \n        Returns:\n            Dados decodificados do QR Code\n        \"\"\"\n        try:\n            # Extrair dados da URL\n            if '?data=' not in qr_url:\n                return None\n            \n            data_encoded = qr_url.split('?data=')[1].split('&')[0]\n            data_json = base64.urlsafe_b64decode(data_encoded).decode()\n            qr_data = json.loads(data_json)\n            \n            # Validar dados\n            if self.validate_qr_data(qr_data):\n                return qr_data\n            else:\n                return None\n                \n        except Exception as e:\n            logger.error(f\"Erro ao decodificar QR Code URL: {e}\")\n            return None\n    \n    def generate_evento_qr_package(\n        self,\n        evento_id: str,\n        evento_config: Dict[str, Any],\n        types: Optional[List[str]] = None\n    ) -> Dict[str, str]:\n        \"\"\"\n        Gera pacote completo de QR Codes para um evento\n        \n        Args:\n            evento_id: ID do evento\n            evento_config: Configurações do evento\n            types: Tipos de QR Code a gerar (checkin, checkout, access, etc.)\n        \n        Returns:\n            Dict com caminhos dos QR Codes gerados\n        \"\"\"\n        if not types:\n            types = ['checkin', 'checkout', 'access']\n        \n        qr_files = {}\n        \n        try:\n            for qr_type in types:\n                # Gerar URL específica para o tipo\n                qr_url = self.generate_qr_code_url(\n                    evento_id=evento_id,\n                    action=qr_type,\n                    expires_at=datetime.utcnow() + timedelta(days=30)  # QR válido por 30 dias\n                )\n                \n                # Criar QR Code com branding\n                qr_img = self.create_branded_qr(\n                    data=qr_url,\n                    evento_config=evento_config,\n                    size='large',\n                    include_branding=True\n                )\n                \n                # Salvar arquivo\n                filename = f\"evento_{evento_id}_{qr_type}_{uuid.uuid4().hex[:8]}\"\n                file_path = self.save_qr_code(qr_img, filename, 'PNG')\n                \n                qr_files[qr_type] = f\"/uploads/qrcodes/{filename}.png\"\n                \n            return qr_files\n            \n        except Exception as e:\n            logger.error(f\"Erro ao gerar pacote de QR Codes: {e}\")\n            raise e\n\n# Instância global do serviço\nqr_service = QRCodeService()"