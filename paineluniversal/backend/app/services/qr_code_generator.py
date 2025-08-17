"""
Sistema de Geração de QR Codes
Gera QR Codes personalizados para diferentes tipos de dados
"""

import qrcode
import qrcode.constants
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer, CircleModuleDrawer
from qrcode.image.styles.colorfills import SolidFillColorMask
import io
import base64
import json
from typing import Dict, Any, Optional, Union
from datetime import datetime
import uuid
from PIL import Image, ImageDraw, ImageFont
import os

def gerar_qr_code(
    dados: Union[str, Dict[str, Any]], 
    tamanho: int = 10,
    borda: int = 4,
    formato: str = "base64",
    cor_fundo: str = "white",
    cor_qr: str = "black",
    estilo: str = "quadrado",
    logo_path: Optional[str] = None,
    incluir_texto: bool = False,
    texto_adicional: Optional[str] = None
) -> str:
    """
    Gera QR Code com várias opções de personalização
    
    Args:
        dados: Dados para codificar (string ou dict)
        tamanho: Tamanho do QR Code (1-40)
        borda: Largura da borda
        formato: Formato de saída ('base64', 'bytes', 'pil')
        cor_fundo: Cor de fundo
        cor_qr: Cor do QR Code
        estilo: Estilo dos módulos ('quadrado', 'redondo', 'circulo')
        logo_path: Caminho para logo a ser inserido
        incluir_texto: Se deve incluir texto abaixo do QR
        texto_adicional: Texto adicional a ser incluído
        
    Returns:
        str: QR Code no formato solicitado
    """
    
    # Converter dados para string se necessário
    if isinstance(dados, dict):
        dados_str = json.dumps(dados, ensure_ascii=False)
    else:
        dados_str = str(dados)
    
    # Configurar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta correção para permitir logo
        box_size=tamanho,
        border=borda,
    )
    
    qr.add_data(dados_str)
    qr.make(fit=True)
    
    # Escolher estilo do módulo
    module_drawer = SquareModuleDrawer()
    if estilo == "redondo":
        module_drawer = RoundedModuleDrawer()
    elif estilo == "circulo":
        module_drawer = CircleModuleDrawer()
    
    # Criar imagem
    img = qr.make_image(
        fill_color=cor_qr,
        back_color=cor_fundo,
        image_factory=StyledPilImage,
        module_drawer=module_drawer
    )
    
    # Adicionar logo se especificado
    if logo_path and os.path.exists(logo_path):
        img = _adicionar_logo(img, logo_path)
    
    # Adicionar texto se solicitado
    if incluir_texto and texto_adicional:
        img = _adicionar_texto(img, texto_adicional)
    
    # Retornar no formato solicitado
    if formato == "base64":
        return _imagem_para_base64(img)
    elif formato == "bytes":
        return _imagem_para_bytes(img)
    elif formato == "pil":
        return img
    else:
        raise ValueError("Formato inválido. Use: 'base64', 'bytes' ou 'pil'")

def _adicionar_logo(img_qr: Image.Image, logo_path: str) -> Image.Image:
    """Adiciona logo no centro do QR Code"""
    
    try:
        logo = Image.open(logo_path)
        
        # Calcular tamanho do logo (máximo 20% do QR)
        qr_width, qr_height = img_qr.size
        logo_size = min(qr_width, qr_height) // 5
        
        # Redimensionar logo
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # Criar máscara circular para o logo
        mask = Image.new('L', (logo_size, logo_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, logo_size, logo_size), fill=255)
        
        # Aplicar máscara
        logo.putalpha(mask)
        
        # Calcular posição central
        pos_x = (qr_width - logo_size) // 2
        pos_y = (qr_height - logo_size) // 2
        
        # Colar logo
        img_qr.paste(logo, (pos_x, pos_y), logo)
        
    except Exception as e:
        # Se houver erro, retorna QR original
        print(f"Erro ao adicionar logo: {e}")
    
    return img_qr

def _adicionar_texto(img_qr: Image.Image, texto: str) -> Image.Image:
    """Adiciona texto abaixo do QR Code"""
    
    try:
        # Configurações do texto
        font_size = max(20, img_qr.width // 20)
        
        # Tentar carregar fonte
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Calcular dimensões do texto
        bbox = ImageDraw.Draw(img_qr).textbbox((0, 0), texto, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Criar nova imagem com espaço para texto
        nova_altura = img_qr.height + text_height + 20
        nova_img = Image.new('RGB', (img_qr.width, nova_altura), 'white')
        
        # Colar QR Code
        nova_img.paste(img_qr, (0, 0))
        
        # Adicionar texto
        draw = ImageDraw.Draw(nova_img)
        text_x = (img_qr.width - text_width) // 2
        text_y = img_qr.height + 10
        
        draw.text((text_x, text_y), texto, font=font, fill='black')
        
        return nova_img
        
    except Exception as e:
        print(f"Erro ao adicionar texto: {e}")
        return img_qr

def _imagem_para_base64(img: Image.Image) -> str:
    """Converte imagem PIL para base64"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()

def _imagem_para_bytes(img: Image.Image) -> bytes:
    """Converte imagem PIL para bytes"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.getvalue()

def gerar_qr_checkin(
    cpf: str, 
    evento_id: int, 
    nome: str,
    evento_nome: str,
    data_evento: datetime,
    valido_ate: Optional[datetime] = None
) -> str:
    """
    Gera QR Code específico para check-in
    
    Args:
        cpf: CPF do participante
        evento_id: ID do evento
        nome: Nome do participante
        evento_nome: Nome do evento
        data_evento: Data do evento
        valido_ate: Data limite de validade
        
    Returns:
        str: QR Code em base64
    """
    
    dados_checkin = {
        "tipo": "checkin",
        "cpf": cpf,
        "evento_id": evento_id,
        "nome": nome,
        "evento_nome": evento_nome,
        "data_evento": data_evento.isoformat(),
        "valido_ate": valido_ate.isoformat() if valido_ate else None,
        "gerado_em": datetime.now().isoformat(),
        "id_unico": str(uuid.uuid4())
    }
    
    return gerar_qr_code(
        dados=dados_checkin,
        tamanho=8,
        estilo="redondo",
        incluir_texto=True,
        texto_adicional=f"{nome} - {evento_nome}"
    )

def gerar_qr_evento(
    evento_id: int,
    nome_evento: str,
    data_evento: datetime,
    local: str,
    url_evento: Optional[str] = None
) -> str:
    """
    Gera QR Code para divulgação do evento
    
    Args:
        evento_id: ID do evento
        nome_evento: Nome do evento
        data_evento: Data do evento
        local: Local do evento
        url_evento: URL para mais informações
        
    Returns:
        str: QR Code em base64
    """
    
    dados_evento = {
        "tipo": "evento",
        "evento_id": evento_id,
        "nome": nome_evento,
        "data": data_evento.isoformat(),
        "local": local,
        "url": url_evento,
        "gerado_em": datetime.now().isoformat()
    }
    
    return gerar_qr_code(
        dados=dados_evento,
        tamanho=10,
        estilo="quadrado",
        incluir_texto=True,
        texto_adicional=nome_evento
    )

def gerar_qr_mesa_pdv(
    mesa_numero: str,
    evento_id: int,
    evento_nome: str
) -> str:
    """
    Gera QR Code para mesa do PDV
    
    Args:
        mesa_numero: Número da mesa
        evento_id: ID do evento
        evento_nome: Nome do evento
        
    Returns:
        str: QR Code em base64
    """
    
    dados_mesa = {
        "tipo": "mesa_pdv",
        "mesa": mesa_numero,
        "evento_id": evento_id,
        "evento_nome": evento_nome,
        "gerado_em": datetime.now().isoformat(),
        "id_unico": str(uuid.uuid4())
    }
    
    return gerar_qr_code(
        dados=dados_mesa,
        tamanho=6,
        estilo="circulo",
        incluir_texto=True,
        texto_adicional=f"Mesa {mesa_numero}"
    )

def gerar_qr_comanda(
    comanda_id: int,
    numero_comanda: str,
    evento_id: int,
    saldo_inicial: float = 0
) -> str:
    """
    Gera QR Code para comanda
    
    Args:
        comanda_id: ID da comanda
        numero_comanda: Número da comanda
        evento_id: ID do evento
        saldo_inicial: Saldo inicial da comanda
        
    Returns:
        str: QR Code em base64
    """
    
    dados_comanda = {
        "tipo": "comanda",
        "comanda_id": comanda_id,
        "numero": numero_comanda,
        "evento_id": evento_id,
        "saldo": saldo_inicial,
        "gerado_em": datetime.now().isoformat(),
        "id_unico": str(uuid.uuid4())
    }
    
    return gerar_qr_code(
        dados=dados_comanda,
        tamanho=7,
        estilo="redondo",
        cor_qr="navy",
        incluir_texto=True,
        texto_adicional=f"Comanda {numero_comanda}"
    )

def gerar_qr_produto(
    produto_id: int,
    nome_produto: str,
    preco: float,
    codigo: str
) -> str:
    """
    Gera QR Code para produto
    
    Args:
        produto_id: ID do produto
        nome_produto: Nome do produto
        preco: Preço do produto
        codigo: Código do produto
        
    Returns:
        str: QR Code em base64
    """
    
    dados_produto = {
        "tipo": "produto",
        "produto_id": produto_id,
        "nome": nome_produto,
        "preco": preco,
        "codigo": codigo,
        "gerado_em": datetime.now().isoformat()
    }
    
    return gerar_qr_code(
        dados=dados_produto,
        tamanho=5,
        estilo="quadrado",
        incluir_texto=True,
        texto_adicional=f"{nome_produto} - R$ {preco:.2f}"
    )

def gerar_qr_url(url: str, titulo: Optional[str] = None) -> str:
    """
    Gera QR Code simples para URL
    
    Args:
        url: URL a ser codificada
        titulo: Título opcional
        
    Returns:
        str: QR Code em base64
    """
    
    return gerar_qr_code(
        dados=url,
        tamanho=8,
        incluir_texto=bool(titulo),
        texto_adicional=titulo
    )

def decodificar_qr_dados(dados_qr: str) -> Dict[str, Any]:
    """
    Decodifica dados de QR Code gerado pelo sistema
    
    Args:
        dados_qr: String de dados do QR Code
        
    Returns:
        dict: Dados decodificados
    """
    
    try:
        # Tentar como JSON primeiro
        return json.loads(dados_qr)
    except json.JSONDecodeError:
        # Se não for JSON, retornar como texto simples
        return {"tipo": "texto", "dados": dados_qr}

def validar_qr_checkin(dados_qr: Dict[str, Any]) -> tuple[bool, str]:
    """
    Valida QR Code de check-in
    
    Args:
        dados_qr: Dados decodificados do QR
        
    Returns:
        tuple: (is_valid, message)
    """
    
    if dados_qr.get("tipo") != "checkin":
        return False, "QR Code não é válido para check-in"
    
    campos_obrigatorios = ["cpf", "evento_id", "nome"]
    for campo in campos_obrigatorios:
        if not dados_qr.get(campo):
            return False, f"Campo obrigatório '{campo}' não encontrado"
    
    # Verificar validade se especificada
    if dados_qr.get("valido_ate"):
        try:
            valido_ate = datetime.fromisoformat(dados_qr["valido_ate"])
            if datetime.now() > valido_ate:
                return False, "QR Code expirado"
        except ValueError:
            return False, "Data de validade inválida"
    
    return True, "QR Code válido"

def validar_qr_mesa(dados_qr: Dict[str, Any]) -> tuple[bool, str]:
    """
    Valida QR Code de mesa PDV
    
    Args:
        dados_qr: Dados decodificados do QR
        
    Returns:
        tuple: (is_valid, message)
    """
    
    if dados_qr.get("tipo") != "mesa_pdv":
        return False, "QR Code não é válido para mesa PDV"
    
    campos_obrigatorios = ["mesa", "evento_id"]
    for campo in campos_obrigatorios:
        if not dados_qr.get(campo):
            return False, f"Campo obrigatório '{campo}' não encontrado"
    
    return True, "QR Code de mesa válido"

def gerar_lote_qr_codes(
    dados_lista: list,
    tipo_qr: str,
    parametros_extras: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Gera múltiplos QR Codes em lote
    
    Args:
        dados_lista: Lista de dados para gerar QRs
        tipo_qr: Tipo de QR Code (checkin, produto, comanda, etc.)
        parametros_extras: Parâmetros extras para o QR
        
    Returns:
        dict: Mapeamento id -> qr_code_base64
    """
    
    qr_codes = {}
    params = parametros_extras or {}
    
    for dados in dados_lista:
        try:
            if tipo_qr == "checkin":
                qr_code = gerar_qr_checkin(**dados, **params)
                chave = f"{dados['cpf']}_{dados['evento_id']}"
                
            elif tipo_qr == "produto":
                qr_code = gerar_qr_produto(**dados, **params)
                chave = str(dados['produto_id'])
                
            elif tipo_qr == "comanda":
                qr_code = gerar_qr_comanda(**dados, **params)
                chave = str(dados['comanda_id'])
                
            elif tipo_qr == "mesa":
                qr_code = gerar_qr_mesa_pdv(**dados, **params)
                chave = f"{dados['mesa_numero']}_{dados['evento_id']}"
                
            else:
                qr_code = gerar_qr_code(dados, **params)
                chave = str(hash(str(dados)))
            
            qr_codes[chave] = qr_code
            
        except Exception as e:
            print(f"Erro ao gerar QR para {dados}: {e}")
            continue
    
    return qr_codes

def otimizar_qr_code(dados: str) -> Dict[str, Any]:
    """
    Otimiza dados para QR Code reduzindo tamanho
    
    Args:
        dados: Dados originais
        
    Returns:
        dict: Dados otimizados
    """
    
    try:
        dados_dict = json.loads(dados) if isinstance(dados, str) else dados
        
        # Remover campos desnecessários
        campos_remover = ["gerado_em", "id_unico"]
        for campo in campos_remover:
            dados_dict.pop(campo, None)
        
        # Encurtar nomes de campos
        mapeamento = {
            "evento_id": "eid",
            "evento_nome": "en",
            "data_evento": "de",
            "produto_id": "pid",
            "nome_produto": "pn",
            "comanda_id": "cid"
        }
        
        dados_otimizados = {}
        for chave, valor in dados_dict.items():
            nova_chave = mapeamento.get(chave, chave)
            dados_otimizados[nova_chave] = valor
        
        return dados_otimizados
        
    except Exception:
        return {"dados": dados}

def estatisticas_qr_code(dados: str) -> Dict[str, Any]:
    """
    Calcula estatísticas de um QR Code
    
    Args:
        dados: Dados do QR Code
        
    Returns:
        dict: Estatísticas do QR
    """
    
    qr = qrcode.QRCode()
    qr.add_data(dados)
    qr.make(fit=True)
    
    return {
        "versao": qr.version,
        "tamanho_dados": len(dados),
        "modulos": qr.modules_count,
        "capacidade_maxima": qr.data_list[0].get_length(),
        "nivel_correcao": qr.error_correction,
        "eficiencia": round(len(dados) / qr.data_list[0].get_length() * 100, 2)
    }
