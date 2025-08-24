"""
Router para Sistema de Geração de QR Codes
Endpoints para gerar e validar QR Codes
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List, Dict, Any, Optional
from datetime import datetime
import tempfile
import os

from ..services.qr_code_generator import (
    gerar_qr_code, gerar_qr_checkin, gerar_qr_evento, gerar_qr_mesa_pdv,
    gerar_qr_comanda, gerar_qr_produto, gerar_qr_url, decodificar_qr_dados,
    validar_qr_checkin, validar_qr_mesa, gerar_lote_qr_codes,
    otimizar_qr_code, estatisticas_qr_code
)
from ..schemas.responses import Response

router = APIRouter(prefix="/qr-codes", tags=["QR Codes"])

@router.post("/gerar", summary="Gerar QR Code Personalizado")
async def gerar_qr_personalizado(dados: Dict[str, Any]):
    """
    Gera QR Code personalizado com opções avançadas.
    
    Corpo da requisição:
    ```json
    {
        "dados": "Texto ou objeto JSON",
        "tamanho": 10,
        "borda": 4,
        "formato": "base64",
        "cor_fundo": "white",
        "cor_qr": "black",
        "estilo": "quadrado",
        "incluir_texto": false,
        "texto_adicional": null
    }
    ```
    """
    try:
        # Extrair parâmetros
        dados_qr = dados.get("dados")
        if not dados_qr:
            raise HTTPException(status_code=400, detail="Campo 'dados' é obrigatório")
        
        parametros = {
            "tamanho": dados.get("tamanho", 10),
            "borda": dados.get("borda", 4),
            "formato": dados.get("formato", "base64"),
            "cor_fundo": dados.get("cor_fundo", "white"),
            "cor_qr": dados.get("cor_qr", "black"),
            "estilo": dados.get("estilo", "quadrado"),
            "incluir_texto": dados.get("incluir_texto", False),
            "texto_adicional": dados.get("texto_adicional")
        }
        
        qr_code = gerar_qr_code(dados_qr, **parametros)
        
        return Response(
            success=True,
            message="QR Code gerado com sucesso",
            data={
                "qr_code": qr_code,
                "formato": parametros["formato"],
                "parametros": parametros,
                "gerado_em": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar QR Code: {str(e)}")

@router.post("/checkin", summary="Gerar QR Code para Check-in")
async def gerar_qr_checkin_endpoint(dados: Dict[str, Any]):
    """
    Gera QR Code específico para check-in de evento.
    
    Corpo da requisição:
    ```json
    {
        "cpf": "12345678901",
        "evento_id": 123,
        "nome": "João Silva",
        "evento_nome": "Conferência Tech 2024",
        "data_evento": "2024-12-01T09:00:00",
        "valido_ate": "2024-12-01T18:00:00"
    }
    ```
    """
    try:
        # Validar campos obrigatórios
        campos_obrigatorios = ["cpf", "evento_id", "nome", "evento_nome", "data_evento"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                raise HTTPException(status_code=400, detail=f"Campo obrigatório: {campo}")
        
        # Converter datas
        data_evento = datetime.fromisoformat(dados["data_evento"])
        valido_ate = None
        if dados.get("valido_ate"):
            valido_ate = datetime.fromisoformat(dados["valido_ate"])
        
        qr_code = gerar_qr_checkin(
            cpf=dados["cpf"],
            evento_id=dados["evento_id"],
            nome=dados["nome"],
            evento_nome=dados["evento_nome"],
            data_evento=data_evento,
            valido_ate=valido_ate
        )
        
        return Response(
            success=True,
            message="QR Code de check-in gerado com sucesso",
            data={
                "qr_code": qr_code,
                "tipo": "checkin",
                "participante": dados["nome"],
                "evento": dados["evento_nome"],
                "gerado_em": datetime.now().isoformat()
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Erro na data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar QR Code: {str(e)}")

@router.post("/evento", summary="Gerar QR Code para Evento")
async def gerar_qr_evento_endpoint(dados: Dict[str, Any]):
    """
    Gera QR Code para divulgação de evento.
    
    Corpo da requisição:
    ```json
    {
        "evento_id": 123,
        "nome_evento": "Conferência Tech 2024",
        "data_evento": "2024-12-01T09:00:00",
        "local": "Centro de Convenções",
        "url_evento": "https://evento.com.br"
    }
    ```
    """
    try:
        # Validar campos obrigatórios
        campos_obrigatorios = ["evento_id", "nome_evento", "data_evento", "local"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                raise HTTPException(status_code=400, detail=f"Campo obrigatório: {campo}")
        
        data_evento = datetime.fromisoformat(dados["data_evento"])
        
        qr_code = gerar_qr_evento(
            evento_id=dados["evento_id"],
            nome_evento=dados["nome_evento"],
            data_evento=data_evento,
            local=dados["local"],
            url_evento=dados.get("url_evento")
        )
        
        return Response(
            success=True,
            message="QR Code do evento gerado com sucesso",
            data={
                "qr_code": qr_code,
                "tipo": "evento",
                "evento": dados["nome_evento"],
                "data": dados["data_evento"],
                "local": dados["local"]
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Erro na data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar QR Code: {str(e)}")

@router.post("/mesa-pdv", summary="Gerar QR Code para Mesa PDV")
async def gerar_qr_mesa_endpoint(dados: Dict[str, Any]):
    """
    Gera QR Code para mesa do PDV.
    
    Corpo da requisição:
    ```json
    {
        "mesa_numero": "01",
        "evento_id": 123,
        "evento_nome": "Festa Junina 2024"
    }
    ```
    """
    try:
        campos_obrigatorios = ["mesa_numero", "evento_id", "evento_nome"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                raise HTTPException(status_code=400, detail=f"Campo obrigatório: {campo}")
        
        qr_code = gerar_qr_mesa_pdv(
            mesa_numero=dados["mesa_numero"],
            evento_id=dados["evento_id"],
            evento_nome=dados["evento_nome"]
        )
        
        return Response(
            success=True,
            message="QR Code da mesa gerado com sucesso",
            data={
                "qr_code": qr_code,
                "tipo": "mesa_pdv",
                "mesa": dados["mesa_numero"],
                "evento": dados["evento_nome"]
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar QR Code: {str(e)}")

@router.post("/comanda", summary="Gerar QR Code para Comanda")
async def gerar_qr_comanda_endpoint(dados: Dict[str, Any]):
    """
    Gera QR Code para comanda.
    
    Corpo da requisição:
    ```json
    {
        "comanda_id": 456,
        "numero_comanda": "C001",
        "evento_id": 123,
        "saldo_inicial": 50.0
    }
    ```
    """
    try:
        campos_obrigatorios = ["comanda_id", "numero_comanda", "evento_id"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                raise HTTPException(status_code=400, detail=f"Campo obrigatório: {campo}")
        
        qr_code = gerar_qr_comanda(
            comanda_id=dados["comanda_id"],
            numero_comanda=dados["numero_comanda"],
            evento_id=dados["evento_id"],
            saldo_inicial=dados.get("saldo_inicial", 0)
        )
        
        return Response(
            success=True,
            message="QR Code da comanda gerado com sucesso",
            data={
                "qr_code": qr_code,
                "tipo": "comanda",
                "numero": dados["numero_comanda"],
                "saldo": dados.get("saldo_inicial", 0)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar QR Code: {str(e)}")

@router.post("/produto", summary="Gerar QR Code para Produto")
async def gerar_qr_produto_endpoint(dados: Dict[str, Any]):
    """
    Gera QR Code para produto.
    
    Corpo da requisição:
    ```json
    {
        "produto_id": 789,
        "nome_produto": "Cerveja Artesanal",
        "preco": 15.90,
        "codigo": "CERV001"
    }
    ```
    """
    try:
        campos_obrigatorios = ["produto_id", "nome_produto", "preco", "codigo"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                raise HTTPException(status_code=400, detail=f"Campo obrigatório: {campo}")
        
        qr_code = gerar_qr_produto(
            produto_id=dados["produto_id"],
            nome_produto=dados["nome_produto"],
            preco=float(dados["preco"]),
            codigo=dados["codigo"]
        )
        
        return Response(
            success=True,
            message="QR Code do produto gerado com sucesso",
            data={
                "qr_code": qr_code,
                "tipo": "produto",
                "produto": dados["nome_produto"],
                "preco": dados["preco"],
                "codigo": dados["codigo"]
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar QR Code: {str(e)}")

@router.post("/url", summary="Gerar QR Code para URL")
async def gerar_qr_url_endpoint(dados: Dict[str, Any]):
    """
    Gera QR Code simples para URL.
    
    Corpo da requisição:
    ```json
    {
        "url": "https://exemplo.com",
        "titulo": "Site Exemplo"
    }
    ```
    """
    try:
        if "url" not in dados:
            raise HTTPException(status_code=400, detail="Campo 'url' é obrigatório")
        
        qr_code = gerar_qr_url(
            url=dados["url"],
            titulo=dados.get("titulo")
        )
        
        return Response(
            success=True,
            message="QR Code da URL gerado com sucesso",
            data={
                "qr_code": qr_code,
                "tipo": "url",
                "url": dados["url"],
                "titulo": dados.get("titulo")
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar QR Code: {str(e)}")

@router.post("/lote", summary="Gerar QR Codes em Lote")
async def gerar_qr_lote_endpoint(dados: Dict[str, Any]):
    """
    Gera múltiplos QR Codes em lote.
    
    Corpo da requisição:
    ```json
    {
        "tipo_qr": "produto",
        "dados_lista": [
            {"produto_id": 1, "nome_produto": "Item 1", "preco": 10.0, "codigo": "I001"},
            {"produto_id": 2, "nome_produto": "Item 2", "preco": 15.0, "codigo": "I002"}
        ],
        "parametros_extras": {"tamanho": 8}
    }
    ```
    """
    try:
        if "tipo_qr" not in dados or "dados_lista" not in dados:
            raise HTTPException(status_code=400, detail="Campos 'tipo_qr' e 'dados_lista' são obrigatórios")
        
        if not isinstance(dados["dados_lista"], list):
            raise HTTPException(status_code=400, detail="'dados_lista' deve ser uma lista")
        
        qr_codes = gerar_lote_qr_codes(
            dados_lista=dados["dados_lista"],
            tipo_qr=dados["tipo_qr"],
            parametros_extras=dados.get("parametros_extras")
        )
        
        return Response(
            success=True,
            message=f"{len(qr_codes)} QR Codes gerados em lote",
            data={
                "total_gerados": len(qr_codes),
                "tipo": dados["tipo_qr"],
                "qr_codes": qr_codes
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar QR Codes em lote: {str(e)}")

@router.post("/decodificar", summary="Decodificar QR Code")
async def decodificar_qr_endpoint(dados: Dict[str, Any]):
    """
    Decodifica dados de um QR Code.
    
    Corpo da requisição:
    ```json
    {
        "dados_qr": "{'tipo': 'checkin', 'cpf': '12345678901', ...}"
    }
    ```
    """
    try:
        if "dados_qr" not in dados:
            raise HTTPException(status_code=400, detail="Campo 'dados_qr' é obrigatório")
        
        dados_decodificados = decodificar_qr_dados(dados["dados_qr"])
        
        return Response(
            success=True,
            message="QR Code decodificado com sucesso",
            data={
                "dados_originais": dados["dados_qr"],
                "dados_decodificados": dados_decodificados,
                "tipo_detectado": dados_decodificados.get("tipo", "desconhecido")
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao decodificar QR Code: {str(e)}")

@router.post("/validar/checkin", summary="Validar QR Code de Check-in")
async def validar_qr_checkin_endpoint(dados: Dict[str, Any]):
    """
    Valida QR Code de check-in.
    
    Corpo da requisição:
    ```json
    {
        "dados_qr": "{'tipo': 'checkin', 'cpf': '12345678901', ...}"
    }
    ```
    """
    try:
        if "dados_qr" not in dados:
            raise HTTPException(status_code=400, detail="Campo 'dados_qr' é obrigatório")
        
        # Decodificar primeiro
        dados_decodificados = decodificar_qr_dados(dados["dados_qr"])
        
        # Validar
        is_valid, message = validar_qr_checkin(dados_decodificados)
        
        return Response(
            success=is_valid,
            message=message,
            data={
                "valido": is_valid,
                "dados": dados_decodificados if is_valid else None,
                "validado_em": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao validar QR Code: {str(e)}")

@router.post("/validar/mesa", summary="Validar QR Code de Mesa")
async def validar_qr_mesa_endpoint(dados: Dict[str, Any]):
    """
    Valida QR Code de mesa PDV.
    
    Corpo da requisição:
    ```json
    {
        "dados_qr": "{'tipo': 'mesa_pdv', 'mesa': '01', ...}"
    }
    ```
    """
    try:
        if "dados_qr" not in dados:
            raise HTTPException(status_code=400, detail="Campo 'dados_qr' é obrigatório")
        
        dados_decodificados = decodificar_qr_dados(dados["dados_qr"])
        is_valid, message = validar_qr_mesa(dados_decodificados)
        
        return Response(
            success=is_valid,
            message=message,
            data={
                "valido": is_valid,
                "dados": dados_decodificados if is_valid else None,
                "validado_em": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao validar QR Code: {str(e)}")

@router.post("/otimizar", summary="Otimizar QR Code")
async def otimizar_qr_endpoint(dados: Dict[str, Any]):
    """
    Otimiza dados de QR Code para reduzir tamanho.
    
    Corpo da requisição:
    ```json
    {
        "dados": "{'tipo': 'checkin', 'cpf': '12345678901', ...}"
    }
    ```
    """
    try:
        if "dados" not in dados:
            raise HTTPException(status_code=400, detail="Campo 'dados' é obrigatório")
        
        dados_otimizados = otimizar_qr_code(dados["dados"])
        
        return Response(
            success=True,
            message="QR Code otimizado com sucesso",
            data={
                "dados_originais": dados["dados"],
                "dados_otimizados": dados_otimizados,
                "reducao_tamanho": f"{len(str(dados['dados'])) - len(str(dados_otimizados))} caracteres"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao otimizar QR Code: {str(e)}")

@router.post("/estatisticas", summary="Estatísticas do QR Code")
async def estatisticas_qr_endpoint(dados: Dict[str, Any]):
    """
    Calcula estatísticas de um QR Code.
    
    Corpo da requisição:
    ```json
    {
        "dados": "Dados do QR Code"
    }
    ```
    """
    try:
        if "dados" not in dados:
            raise HTTPException(status_code=400, detail="Campo 'dados' é obrigatório")
        
        stats = estatisticas_qr_code(str(dados["dados"]))
        
        return Response(
            success=True,
            message="Estatísticas calculadas com sucesso",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular estatísticas: {str(e)}")

@router.get("/tipos", summary="Tipos de QR Code Disponíveis")
async def obter_tipos_qr():
    """
    Retorna os tipos de QR Code disponíveis no sistema.
    """
    try:
        tipos = [
            {
                "tipo": "checkin",
                "nome": "Check-in de Evento",
                "descricao": "QR Code para check-in de participantes em eventos",
                "campos_obrigatorios": ["cpf", "evento_id", "nome", "evento_nome", "data_evento"]
            },
            {
                "tipo": "evento",
                "nome": "Divulgação de Evento",
                "descricao": "QR Code para divulgar informações do evento",
                "campos_obrigatorios": ["evento_id", "nome_evento", "data_evento", "local"]
            },
            {
                "tipo": "mesa_pdv",
                "nome": "Mesa do PDV",
                "descricao": "QR Code para identificar mesas no sistema PDV",
                "campos_obrigatorios": ["mesa_numero", "evento_id", "evento_nome"]
            },
            {
                "tipo": "comanda",
                "nome": "Comanda",
                "descricao": "QR Code para comandas de consumo",
                "campos_obrigatorios": ["comanda_id", "numero_comanda", "evento_id"]
            },
            {
                "tipo": "produto",
                "nome": "Produto",
                "descricao": "QR Code para produtos do catálogo",
                "campos_obrigatorios": ["produto_id", "nome_produto", "preco", "codigo"]
            },
            {
                "tipo": "url",
                "nome": "URL Simples",
                "descricao": "QR Code simples para URLs",
                "campos_obrigatorios": ["url"]
            },
            {
                "tipo": "personalizado",
                "nome": "Personalizado",
                "descricao": "QR Code com dados personalizados",
                "campos_obrigatorios": ["dados"]
            }
        ]
        
        return Response(
            success=True,
            message="Tipos de QR Code obtidos com sucesso",
            data={"tipos": tipos}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter tipos: {str(e)}")

@router.get("/estilos", summary="Estilos Disponíveis")
async def obter_estilos_qr():
    """
    Retorna os estilos disponíveis para QR Codes.
    """
    try:
        configuracoes = {
            "estilos": [
                {"valor": "quadrado", "nome": "Quadrado", "descricao": "Módulos quadrados tradicionais"},
                {"valor": "redondo", "nome": "Redondo", "descricao": "Módulos com bordas arredondadas"},
                {"valor": "circulo", "nome": "Círculo", "descricao": "Módulos circulares"}
            ],
            "formatos": [
                {"valor": "base64", "nome": "Base64", "descricao": "Retorna string base64 da imagem"},
                {"valor": "bytes", "nome": "Bytes", "descricao": "Retorna bytes da imagem"},
                {"valor": "pil", "nome": "PIL Image", "descricao": "Retorna objeto PIL Image"}
            ],
            "cores_populares": [
                {"nome": "Preto", "valor": "black"},
                {"nome": "Azul", "valor": "blue"},
                {"nome": "Vermelho", "valor": "red"},
                {"nome": "Verde", "valor": "green"},
                {"nome": "Roxo", "valor": "purple"},
                {"nome": "Marrom", "valor": "brown"}
            ],
            "tamanhos_recomendados": [
                {"uso": "Impressão pequena", "tamanho": 5},
                {"uso": "Uso geral", "tamanho": 8},
                {"uso": "Impressão grande", "tamanho": 12},
                {"uso": "Banner/Display", "tamanho": 20}
            ]
        }
        
        return Response(
            success=True,
            message="Configurações de estilo obtidas com sucesso",
            data=configuracoes
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estilos: {str(e)}")
