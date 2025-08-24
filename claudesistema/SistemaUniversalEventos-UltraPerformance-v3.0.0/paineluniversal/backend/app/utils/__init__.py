"""
Módulo de utilitários do sistema
"""

from .cpf_utils import (
    limpar_cpf,
    formatar_cpf,
    validar_cpf,
    validar_cpf_detalhado,
    extrair_info_cpf,
    gerar_cpf_valido,
    obter_digitos_verificadores,
    comparar_cpfs,
    mascarar_cpf,
    validar_lista_cpfs,
    cpf_esta_formatado,
    normalizar_cpf,
    CPF_REGEX,
    CPF_LIMPO_REGEX
)

from .cnpj_utils import (
    limpar_cnpj,
    formatar_cnpj,
    validar_cnpj,
    validar_cnpj_detalhado,
    extrair_info_cnpj,
    gerar_cnpj_valido,
    obter_digitos_verificadores_cnpj,
    comparar_cnpjs,
    mascarar_cnpj,
    validar_lista_cnpjs,
    obter_cnpj_matriz,
    verificar_mesmo_grupo_empresarial,
    cnpj_esta_formatado,
    normalizar_cnpj,
    CNPJ_REGEX,
    CNPJ_LIMPO_REGEX
)

__all__ = [
    # CPF Utils
    'limpar_cpf',
    'formatar_cpf', 
    'validar_cpf',
    'validar_cpf_detalhado',
    'extrair_info_cpf',
    'gerar_cpf_valido',
    'obter_digitos_verificadores',
    'comparar_cpfs',
    'mascarar_cpf',
    'validar_lista_cpfs',
    'cpf_esta_formatado',
    'normalizar_cpf',
    'CPF_REGEX',
    'CPF_LIMPO_REGEX',
    
    # CNPJ Utils
    'limpar_cnpj',
    'formatar_cnpj',
    'validar_cnpj',
    'validar_cnpj_detalhado', 
    'extrair_info_cnpj',
    'gerar_cnpj_valido',
    'obter_digitos_verificadores_cnpj',
    'comparar_cnpjs',
    'mascarar_cnpj',
    'validar_lista_cnpjs',
    'obter_cnpj_matriz',
    'verificar_mesmo_grupo_empresarial',
    'cnpj_esta_formatado',
    'normalizar_cnpj',
    'CNPJ_REGEX',
    'CNPJ_LIMPO_REGEX'
]
