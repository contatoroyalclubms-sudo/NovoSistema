"""
Utilitários para validação e manipulação de CPF
Módulo completo para trabalhar com CPF brasileiro
"""

import re
from typing import Tuple, Optional

def limpar_cpf(cpf: str) -> str:
    """Remove caracteres não numéricos do CPF"""
    return re.sub(r'\D', '', cpf)

def formatar_cpf(cpf: str) -> str:
    """Formata CPF com pontos e traço"""
    cpf_limpo = limpar_cpf(cpf)
    if len(cpf_limpo) != 11:
        return cpf
    return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

def validar_cpf(cpf: str) -> bool:
    """
    Valida CPF usando algoritmo oficial da Receita Federal
    
    Args:
        cpf: String contendo o CPF (com ou sem formatação)
        
    Returns:
        bool: True se válido, False caso contrário
    """
    
    # Remove caracteres não numéricos
    cpf_limpo = limpar_cpf(cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf_limpo) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais (ex: 111.111.111-11)
    if cpf_limpo == cpf_limpo[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf_limpo[i]) * (10 - i)
    
    resto = soma % 11
    if resto < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto
    
    # Verifica o primeiro dígito
    if int(cpf_limpo[9]) != digito1:
        return False
    
    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf_limpo[i]) * (11 - i)
    
    resto = soma % 11
    if resto < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto
    
    # Verifica o segundo dígito
    if int(cpf_limpo[10]) != digito2:
        return False
    
    return True

def validar_cpf_detalhado(cpf: str) -> Tuple[bool, Optional[str]]:
    """
    Valida CPF e retorna detalhes do erro se inválido
    
    Args:
        cpf: String contendo o CPF
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    
    if not cpf:
        return False, "CPF não informado"
    
    cpf_limpo = limpar_cpf(cpf)
    
    if len(cpf_limpo) != 11:
        return False, f"CPF deve ter 11 dígitos. Informado: {len(cpf_limpo)} dígitos"
    
    if not cpf_limpo.isdigit():
        return False, "CPF deve conter apenas números"
    
    if cpf_limpo == cpf_limpo[0] * 11:
        return False, "CPF não pode ter todos os dígitos iguais"
    
    # Lista de CPFs inválidos conhecidos
    cpfs_invalidos = [
        '00000000000', '11111111111', '22222222222', '33333333333',
        '44444444444', '55555555555', '66666666666', '77777777777',
        '88888888888', '99999999999'
    ]
    
    if cpf_limpo in cpfs_invalidos:
        return False, "CPF inválido"
    
    # Calcula primeiro dígito verificador
    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf_limpo[9]) != digito1:
        return False, "Primeiro dígito verificador inválido"
    
    # Calcula segundo dígito verificador
    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(cpf_limpo[10]) != digito2:
        return False, "Segundo dígito verificador inválido"
    
    return True, None

def extrair_info_cpf(cpf: str) -> dict:
    """
    Extrai informações básicas do CPF
    
    Args:
        cpf: String contendo o CPF
        
    Returns:
        dict: Informações do CPF
    """
    
    cpf_limpo = limpar_cpf(cpf)
    
    if not validar_cpf(cpf):
        return {
            "cpf": cpf,
            "cpf_formatado": formatar_cpf(cpf),
            "valido": False,
            "regiao": None,
            "digitos_verificadores": None
        }
    
    # Determina região baseada no primeiro dígito
    primeiro_digito = int(cpf_limpo[0])
    regioes = {
        1: "DF, GO, MS, MT, TO",
        2: "AC, AM, AP, PA, RO, RR", 
        3: "CE, MA, PI",
        4: "AL, PB, PE, RN",
        5: "BA, SE",
        6: "MG",
        7: "ES, RJ",
        8: "SP",
        9: "PR, SC",
        0: "RS"
    }
    
    return {
        "cpf": cpf_limpo,
        "cpf_formatado": formatar_cpf(cpf),
        "valido": True,
        "regiao": regioes.get(primeiro_digito, "Não identificada"),
        "digitos_verificadores": cpf_limpo[9:11],
        "primeira_emissao_regiao": primeiro_digito
    }

def gerar_cpf_valido() -> str:
    """
    Gera um CPF válido aleatório (apenas para testes)
    
    Returns:
        str: CPF válido formatado
    """
    import random
    
    # Gera os primeiros 9 dígitos
    cpf = [random.randint(0, 9) for _ in range(9)]
    
    # Calcula primeiro dígito verificador
    soma = sum(cpf[i] * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    cpf.append(digito1)
    
    # Calcula segundo dígito verificador
    soma = sum(cpf[i] * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    cpf.append(digito2)
    
    cpf_str = ''.join(map(str, cpf))
    return formatar_cpf(cpf_str)

def obter_digitos_verificadores(cpf: str) -> Tuple[int, int]:
    """
    Calcula os dígitos verificadores de um CPF
    
    Args:
        cpf: String com os primeiros 9 dígitos do CPF
        
    Returns:
        Tuple[int, int]: (primeiro_digito, segundo_digito)
    """
    
    cpf_limpo = limpar_cpf(cpf)
    
    if len(cpf_limpo) < 9:
        raise ValueError("CPF deve ter pelo menos 9 dígitos")
    
    # Pega apenas os primeiros 9 dígitos
    cpf_base = cpf_limpo[:9]
    
    # Calcula primeiro dígito
    soma = sum(int(cpf_base[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Calcula segundo dígito
    cpf_com_primeiro = cpf_base + str(digito1)
    soma = sum(int(cpf_com_primeiro[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return digito1, digito2

def comparar_cpfs(cpf1: str, cpf2: str) -> bool:
    """
    Compara dois CPFs ignorando formatação
    
    Args:
        cpf1: Primeiro CPF
        cpf2: Segundo CPF
        
    Returns:
        bool: True se são iguais, False caso contrário
    """
    
    return limpar_cpf(cpf1) == limpar_cpf(cpf2)

def mascarar_cpf(cpf: str, mostrar_inicio: int = 3, mostrar_fim: int = 2) -> str:
    """
    Mascara um CPF para exibição segura
    
    Args:
        cpf: CPF a ser mascarado
        mostrar_inicio: Quantos dígitos mostrar no início
        mostrar_fim: Quantos dígitos mostrar no fim
        
    Returns:
        str: CPF mascarado (ex: 123.***.***-89)
    """
    
    if not validar_cpf(cpf):
        return "CPF inválido"
    
    cpf_limpo = limpar_cpf(cpf)
    
    inicio = cpf_limpo[:mostrar_inicio]
    fim = cpf_limpo[-mostrar_fim:]
    meio = '*' * (11 - mostrar_inicio - mostrar_fim)
    
    cpf_mascarado = inicio + meio + fim
    return formatar_cpf(cpf_mascarado)

def validar_lista_cpfs(cpfs: list) -> dict:
    """
    Valida uma lista de CPFs
    
    Args:
        cpfs: Lista de CPFs para validar
        
    Returns:
        dict: Estatísticas da validação
    """
    
    validos = []
    invalidos = []
    duplicados = []
    cpfs_unicos = set()
    
    for cpf in cpfs:
        cpf_limpo = limpar_cpf(cpf)
        
        if cpf_limpo in cpfs_unicos:
            duplicados.append(cpf)
            continue
            
        cpfs_unicos.add(cpf_limpo)
        
        if validar_cpf(cpf):
            validos.append(cpf)
        else:
            invalidos.append(cpf)
    
    return {
        "total": len(cpfs),
        "validos": len(validos),
        "invalidos": len(invalidos),
        "duplicados": len(duplicados),
        "lista_validos": validos,
        "lista_invalidos": invalidos,
        "lista_duplicados": duplicados,
        "taxa_validos": round(len(validos) / len(cpfs) * 100, 2) if cpfs else 0
    }

# Constantes úteis
CPF_REGEX = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$'
CPF_LIMPO_REGEX = r'^\d{11}$'

def cpf_esta_formatado(cpf: str) -> bool:
    """Verifica se CPF está no formato XXX.XXX.XXX-XX"""
    return bool(re.match(CPF_REGEX, cpf))

def normalizar_cpf(cpf: str) -> str:
    """
    Normaliza CPF removendo formatação e validando
    
    Args:
        cpf: CPF com ou sem formatação
        
    Returns:
        str: CPF limpo (apenas números) se válido
        
    Raises:
        ValueError: Se CPF for inválido
    """
    
    if not cpf:
        raise ValueError("CPF não pode ser vazio")
    
    cpf_limpo = limpar_cpf(cpf)
    
    if not validar_cpf(cpf_limpo):
        raise ValueError(f"CPF inválido: {cpf}")
    
    return cpf_limpo
