"""
Router para utilitários de validação de documentos brasileiros
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.utils.cpf_utils import (
    validar_cpf, validar_cpf_detalhado, formatar_cpf, 
    extrair_info_cpf, mascarar_cpf, gerar_cpf_valido
)
from app.utils.cnpj_utils import (
    validar_cnpj, validar_cnpj_detalhado, formatar_cnpj,
    extrair_info_cnpj, mascarar_cnpj, gerar_cnpj_valido
)

router = APIRouter(prefix="/utils", tags=["Utilitários"])

# ================== SCHEMAS ==================

class ValidarDocumentoRequest(BaseModel):
    documento: str

class ValidarDocumentoResponse(BaseModel):
    documento: str
    tipo: str
    valido: bool
    formatado: str
    mascarado: str
    informacoes: Dict[str, Any]
    erro: Optional[str] = None

class ListaDocumentosRequest(BaseModel):
    documentos: List[str]

class ListaDocumentosResponse(BaseModel):
    total: int
    validos: int
    invalidos: int
    duplicados: int
    taxa_validos: float
    detalhes: List[ValidarDocumentoResponse]

# ================== ENDPOINTS CPF ==================

@router.post("/cpf/validar", response_model=ValidarDocumentoResponse)
async def validar_cpf_endpoint(request: ValidarDocumentoRequest):
    """
    Valida um CPF e retorna informações detalhadas
    """
    try:
        cpf = request.documento
        
        # Validação básica
        is_valid = validar_cpf(cpf)
        
        # Validação detalhada
        valid_detailed, error_msg = validar_cpf_detalhado(cpf)
        
        # Extrai informações se válido
        if is_valid:
            info = extrair_info_cpf(cpf)
            cpf_formatado = formatar_cpf(cpf)
            cpf_mascarado = mascarar_cpf(cpf)
        else:
            info = {}
            cpf_formatado = cpf
            cpf_mascarado = "***.***.***-**"
        
        return ValidarDocumentoResponse(
            documento=cpf,
            tipo="cpf",
            valido=is_valid,
            formatado=cpf_formatado,
            mascarado=cpf_mascarado,
            informacoes=info,
            erro=error_msg if not valid_detailed else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao validar CPF: {str(e)}"
        )

@router.post("/cpf/gerar")
async def gerar_cpf_endpoint():
    """
    Gera um CPF válido aleatório (apenas para testes)
    """
    try:
        cpf_gerado = gerar_cpf_valido()
        info = extrair_info_cpf(cpf_gerado)
        
        return {
            "cpf": cpf_gerado,
            "informacoes": info,
            "observacao": "CPF gerado apenas para testes. Não usar em produção."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar CPF: {str(e)}"
        )

# ================== ENDPOINTS CNPJ ==================

@router.post("/cnpj/validar", response_model=ValidarDocumentoResponse)
async def validar_cnpj_endpoint(request: ValidarDocumentoRequest):
    """
    Valida um CNPJ e retorna informações detalhadas
    """
    try:
        cnpj = request.documento
        
        # Validação básica
        is_valid = validar_cnpj(cnpj)
        
        # Validação detalhada
        valid_detailed, error_msg = validar_cnpj_detalhado(cnpj)
        
        # Extrai informações se válido
        if is_valid:
            info = extrair_info_cnpj(cnpj)
            cnpj_formatado = formatar_cnpj(cnpj)
            cnpj_mascarado = mascarar_cnpj(cnpj)
        else:
            info = {}
            cnpj_formatado = cnpj
            cnpj_mascarado = "**.***.***/****-**"
        
        return ValidarDocumentoResponse(
            documento=cnpj,
            tipo="cnpj",
            valido=is_valid,
            formatado=cnpj_formatado,
            mascarado=cnpj_mascarado,
            informacoes=info,
            erro=error_msg if not valid_detailed else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao validar CNPJ: {str(e)}"
        )

@router.post("/cnpj/gerar")
async def gerar_cnpj_endpoint():
    """
    Gera um CNPJ válido aleatório (apenas para testes)
    """
    try:
        cnpj_gerado = gerar_cnpj_valido()
        info = extrair_info_cnpj(cnpj_gerado)
        
        return {
            "cnpj": cnpj_gerado,
            "informacoes": info,
            "observacao": "CNPJ gerado apenas para testes. Não usar em produção."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar CNPJ: {str(e)}"
        )

# ================== ENDPOINTS COMBINADOS ==================

@router.post("/documento/validar", response_model=ValidarDocumentoResponse)
async def validar_documento_automatico(request: ValidarDocumentoRequest):
    """
    Valida automaticamente CPF ou CNPJ baseado no tamanho
    """
    try:
        documento = request.documento
        documento_limpo = ''.join(filter(str.isdigit, documento))
        
        if len(documento_limpo) == 11:
            # É um CPF
            return await validar_cpf_endpoint(request)
        elif len(documento_limpo) == 14:
            # É um CNPJ
            return await validar_cnpj_endpoint(request)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Documento deve ter 11 dígitos (CPF) ou 14 dígitos (CNPJ)"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao validar documento: {str(e)}"
        )

@router.post("/lista/validar", response_model=ListaDocumentosResponse)
async def validar_lista_documentos(request: ListaDocumentosRequest):
    """
    Valida uma lista de documentos (CPFs e CNPJs misturados)
    """
    try:
        documentos = request.documentos
        detalhes = []
        
        for doc in documentos:
            try:
                # Tenta validar como documento automático
                resultado = await validar_documento_automatico(
                    ValidarDocumentoRequest(documento=doc)
                )
                detalhes.append(resultado)
            except Exception as e:
                # Se falhar, adiciona como inválido
                detalhes.append(ValidarDocumentoResponse(
                    documento=doc,
                    tipo="desconhecido",
                    valido=False,
                    formatado=doc,
                    mascarado="***",
                    informacoes={},
                    erro=str(e)
                ))
        
        # Calcula estatísticas
        total = len(detalhes)
        validos = len([d for d in detalhes if d.valido])
        invalidos = total - validos
        duplicados = total - len(set(d.documento for d in detalhes))
        taxa_validos = round((validos / total) * 100, 2) if total > 0 else 0
        
        return ListaDocumentosResponse(
            total=total,
            validos=validos,
            invalidos=invalidos,
            duplicados=duplicados,
            taxa_validos=taxa_validos,
            detalhes=detalhes
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao validar lista de documentos: {str(e)}"
        )

@router.get("/status")
async def status_utilitarios():
    """
    Verifica status dos utilitários de validação
    """
    try:
        # Testa CPF
        cpf_teste = gerar_cpf_valido()
        cpf_ok = validar_cpf(cpf_teste)
        
        # Testa CNPJ
        cnpj_teste = gerar_cnpj_valido()
        cnpj_ok = validar_cnpj(cnpj_teste)
        
        return {
            "status": "ok",
            "modulos": {
                "cpf_utils": cpf_ok,
                "cnpj_utils": cnpj_ok
            },
            "teste_cpf": cpf_teste,
            "teste_cnpj": cnpj_teste,
            "funcionalidades": [
                "validacao_cpf",
                "validacao_cnpj", 
                "formatacao",
                "mascaramento",
                "geracao_teste",
                "validacao_lote"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "erro": str(e),
            "modulos": {
                "cpf_utils": False,
                "cnpj_utils": False
            }
        }
