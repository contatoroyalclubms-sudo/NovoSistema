"""
Utilitários para validação e manipulação de CNPJ
Módulo completo para trabalhar com CNPJ brasileiro
"""

import re
from typing import Tuple, Optional

def limpar_cnpj(cnpj: str) -> str:
    """Remove caracteres não numéricos do CNPJ"""
    return re.sub(r'\D', '', cnpj)

def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ com pontos, barra e traço"""
    cnpj_limpo = limpar_cnpj(cnpj)
    if len(cnpj_limpo) != 14:
        return cnpj
    return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"

def validar_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ usando algoritmo oficial da Receita Federal
    
    Args:
        cnpj: String contendo o CNPJ (com ou sem formatação)
        
    Returns:
        bool: True se válido, False caso contrário
    """
    
    # Remove caracteres não numéricos
    cnpj_limpo = limpar_cnpj(cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj_limpo) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj_limpo == cnpj_limpo[0] * 14:
        return False
    
    # Lista de CNPJs inválidos conhecidos
    cnpjs_invalidos = [
        '00000000000000', '11111111111111', '22222222222222', '33333333333333',
        '44444444444444', '55555555555555', '66666666666666', '77777777777777',
        '88888888888888', '99999999999999'
    ]
    
    if cnpj_limpo in cnpjs_invalidos:
        return False
    
    # Calcula o primeiro dígito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj_limpo[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Verifica o primeiro dígito
    if int(cnpj_limpo[12]) != digito1:
        return False
    
    # Calcula o segundo dígito verificador
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj_limpo[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    # Verifica o segundo dígito
    if int(cnpj_limpo[13]) != digito2:
        return False
    
    return True

def validar_cnpj_detalhado(cnpj: str) -> Tuple[bool, Optional[str]]:
    """
    Valida CNPJ e retorna detalhes do erro se inválido
    
    Args:
        cnpj: String contendo o CNPJ
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    
    if not cnpj:
        return False, "CNPJ não informado"
    
    cnpj_limpo = limpar_cnpj(cnpj)
    
    if len(cnpj_limpo) != 14:
        return False, f"CNPJ deve ter 14 dígitos. Informado: {len(cnpj_limpo)} dígitos"
    
    if not cnpj_limpo.isdigit():
        return False, "CNPJ deve conter apenas números"
    
    if cnpj_limpo == cnpj_limpo[0] * 14:
        return False, "CNPJ não pode ter todos os dígitos iguais"
    
    # Lista de CNPJs inválidos conhecidos
    cnpjs_invalidos = [
        '00000000000000', '11111111111111', '22222222222222', '33333333333333',
        '44444444444444', '55555555555555', '66666666666666', '77777777777777',
        '88888888888888', '99999999999999'
    ]
    
    if cnpj_limpo in cnpjs_invalidos:
        return False, "CNPJ inválido"
    
    # Calcula primeiro dígito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj_limpo[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj_limpo[12]) != digito1:
        return False, "Primeiro dígito verificador inválido"
    
    # Calcula segundo dígito verificador
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj_limpo[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj_limpo[13]) != digito2:
        return False, "Segundo dígito verificador inválido"
    
    return True, None

def extrair_info_cnpj(cnpj: str) -> dict:
    """
    Extrai informações básicas do CNPJ
    
    Args:
        cnpj: String contendo o CNPJ
        
    Returns:
        dict: Informações do CNPJ
    """
    
    cnpj_limpo = limpar_cnpj(cnpj)
    
    if not validar_cnpj(cnpj):
        return {
            "cnpj": cnpj,
            "cnpj_formatado": formatar_cnpj(cnpj),
            "valido": False,
            "numero_base": None,
            "ordem": None,
            "digitos_verificadores": None
        }
    
    # Extrai partes do CNPJ
    numero_base = cnpj_limpo[:8]  # 8 primeiros dígitos
    ordem = cnpj_limpo[8:12]      # 4 dígitos da ordem (filial)
    dv = cnpj_limpo[12:14]        # 2 dígitos verificadores
    
    # Determina se é matriz ou filial
    tipo_estabelecimento = "Matriz" if ordem == "0001" else f"Filial {ordem}"
    
    return {
        "cnpj": cnpj_limpo,
        "cnpj_formatado": formatar_cnpj(cnpj),
        "valido": True,
        "numero_base": numero_base,
        "ordem": ordem,
        "digitos_verificadores": dv,
        "tipo_estabelecimento": tipo_estabelecimento,
        "eh_matriz": ordem == "0001"
    }

def gerar_cnpj_valido() -> str:
    """
    Gera um CNPJ válido aleatório (apenas para testes)
    
    Returns:
        str: CNPJ válido formatado
    """
    import random
    
    # Gera os primeiros 12 dígitos
    cnpj = [random.randint(0, 9) for _ in range(8)]  # Base
    cnpj.extend([0, 0, 0, 1])  # Ordem da filial (0001 = matriz)
    
    # Calcula primeiro dígito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(cnpj[i] * pesos1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    cnpj.append(digito1)
    
    # Calcula segundo dígito verificador
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(cnpj[i] * pesos2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    cnpj.append(digito2)
    
    cnpj_str = ''.join(map(str, cnpj))
    return formatar_cnpj(cnpj_str)

def obter_digitos_verificadores_cnpj(cnpj: str) -> Tuple[int, int]:
    """
    Calcula os dígitos verificadores de um CNPJ
    
    Args:
        cnpj: String com os primeiros 12 dígitos do CNPJ
        
    Returns:
        Tuple[int, int]: (primeiro_digito, segundo_digito)
    """
    
    cnpj_limpo = limpar_cnpj(cnpj)
    
    if len(cnpj_limpo) < 12:
        raise ValueError("CNPJ deve ter pelo menos 12 dígitos")
    
    # Pega apenas os primeiros 12 dígitos
    cnpj_base = cnpj_limpo[:12]
    
    # Calcula primeiro dígito
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj_base[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Calcula segundo dígito
    cnpj_com_primeiro = cnpj_base + str(digito1)
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj_com_primeiro[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return digito1, digito2

def comparar_cnpjs(cnpj1: str, cnpj2: str) -> bool:
    """
    Compara dois CNPJs ignorando formatação
    
    Args:
        cnpj1: Primeiro CNPJ
        cnpj2: Segundo CNPJ
        
    Returns:
        bool: True se são iguais, False caso contrário
    """
    
    return limpar_cnpj(cnpj1) == limpar_cnpj(cnpj2)

def mascarar_cnpj(cnpj: str, mostrar_inicio: int = 4, mostrar_fim: int = 4) -> str:
    """
    Mascara um CNPJ para exibição segura
    
    Args:
        cnpj: CNPJ a ser mascarado
        mostrar_inicio: Quantos dígitos mostrar no início
        mostrar_fim: Quantos dígitos mostrar no fim
        
    Returns:
        str: CNPJ mascarado (ex: 12.34*.****/****-67)
    """
    
    if not validar_cnpj(cnpj):
        return "CNPJ inválido"
    
    cnpj_limpo = limpar_cnpj(cnpj)
    
    inicio = cnpj_limpo[:mostrar_inicio]
    fim = cnpj_limpo[-mostrar_fim:]
    meio = '*' * (14 - mostrar_inicio - mostrar_fim)
    
    cnpj_mascarado = inicio + meio + fim
    return formatar_cnpj(cnpj_mascarado)

def validar_lista_cnpjs(cnpjs: list) -> dict:
    """
    Valida uma lista de CNPJs
    
    Args:
        cnpjs: Lista de CNPJs para validar
        
    Returns:
        dict: Estatísticas da validação
    """
    
    validos = []
    invalidos = []
    duplicados = []
    cnpjs_unicos = set()
    
    for cnpj in cnpjs:
        cnpj_limpo = limpar_cnpj(cnpj)
        
        if cnpj_limpo in cnpjs_unicos:
            duplicados.append(cnpj)
            continue
            
        cnpjs_unicos.add(cnpj_limpo)
        
        if validar_cnpj(cnpj):
            validos.append(cnpj)
        else:
            invalidos.append(cnpj)
    
    return {
        "total": len(cnpjs),
        "validos": len(validos),
        "invalidos": len(invalidos),
        "duplicados": len(duplicados),
        "lista_validos": validos,
        "lista_invalidos": invalidos,
        "lista_duplicados": duplicados,
        "taxa_validos": round(len(validos) / len(cnpjs) * 100, 2) if cnpjs else 0
    }

def obter_cnpj_matriz(cnpj: str) -> str:
    """
    Obtém o CNPJ da matriz a partir de qualquer CNPJ (matriz ou filial)
    
    Args:
        cnpj: CNPJ da empresa (matriz ou filial)
        
    Returns:
        str: CNPJ da matriz formatado
    """
    
    if not validar_cnpj(cnpj):
        raise ValueError("CNPJ inválido")
    
    cnpj_limpo = limpar_cnpj(cnpj)
    
    # Substitui a ordem por 0001 (matriz)
    cnpj_matriz = cnpj_limpo[:8] + "0001"
    
    # Recalcula os dígitos verificadores
    digito1, digito2 = obter_digitos_verificadores_cnpj(cnpj_matriz)
    cnpj_matriz_completo = cnpj_matriz + str(digito1) + str(digito2)
    
    return formatar_cnpj(cnpj_matriz_completo)

def verificar_mesmo_grupo_empresarial(cnpj1: str, cnpj2: str) -> bool:
    """
    Verifica se dois CNPJs pertencem ao mesmo grupo empresarial (mesmo número base)
    
    Args:
        cnpj1: Primeiro CNPJ
        cnpj2: Segundo CNPJ
        
    Returns:
        bool: True se pertencem ao mesmo grupo, False caso contrário
    """
    
    if not (validar_cnpj(cnpj1) and validar_cnpj(cnpj2)):
        return False
    
    cnpj1_limpo = limpar_cnpj(cnpj1)
    cnpj2_limpo = limpar_cnpj(cnpj2)
    
    # Compara os primeiros 8 dígitos (número base)
    return cnpj1_limpo[:8] == cnpj2_limpo[:8]

# Constantes úteis
CNPJ_REGEX = r'^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$'
CNPJ_LIMPO_REGEX = r'^\d{14}$'

def cnpj_esta_formatado(cnpj: str) -> bool:
    """Verifica se CNPJ está no formato XX.XXX.XXX/XXXX-XX"""
    return bool(re.match(CNPJ_REGEX, cnpj))

def normalizar_cnpj(cnpj: str) -> str:
    """
    Normaliza CNPJ removendo formatação e validando
    
    Args:
        cnpj: CNPJ com ou sem formatação
        
    Returns:
        str: CNPJ limpo (apenas números) se válido
        
    Raises:
        ValueError: Se CNPJ for inválido
    """
    
    if not cnpj:
        raise ValueError("CNPJ não pode ser vazio")
    
    cnpj_limpo = limpar_cnpj(cnpj)
    
    if not validar_cnpj(cnpj_limpo):
        raise ValueError(f"CNPJ inválido: {cnpj}")
    
    return cnpj_limpo
