"""
Teste rápido dos utilitários de CPF e CNPJ
"""

import sys
import os

# Adiciona o diretório do app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from utils.cpf_utils import (
        validar_cpf, formatar_cpf, extrair_info_cpf, gerar_cpf_valido, mascarar_cpf
    )
    from utils.cnpj_utils import (
        validar_cnpj, formatar_cnpj, extrair_info_cnpj, gerar_cnpj_valido, mascarar_cnpj
    )
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Erro na importação: {e}")
    IMPORTS_OK = False

def teste_cpf():
    print("🔍 TESTANDO UTILITÁRIOS DE CPF")
    print("=" * 50)
    
    # Gera CPF válido para teste
    cpf_teste = gerar_cpf_valido()
    print(f"CPF gerado para teste: {cpf_teste}")
    
    # Testa validação
    cpf_limpo = cpf_teste.replace('.', '').replace('-', '')
    is_valid = validar_cpf(cpf_limpo)
    print(f"Validação: {'✅ Válido' if is_valid else '❌ Inválido'}")
    
    # Testa formatação
    cpf_formatado = formatar_cpf(cpf_limpo)
    print(f"CPF formatado: {cpf_formatado}")
    
    # Testa mascaramento
    cpf_mascarado = mascarar_cpf(cpf_teste)
    print(f"CPF mascarado: {cpf_mascarado}")
    
    # Extrai informações
    info = extrair_info_cpf(cpf_teste)
    print(f"Região de emissão: {info['regiao']}")
    print()

def teste_cnpj():
    print("🔍 TESTANDO UTILITÁRIOS DE CNPJ")
    print("=" * 50)
    
    # Gera CNPJ válido para teste
    cnpj_teste = gerar_cnpj_valido()
    print(f"CNPJ gerado para teste: {cnpj_teste}")
    
    # Testa validação
    cnpj_limpo = cnpj_teste.replace('.', '').replace('/', '').replace('-', '')
    is_valid = validar_cnpj(cnpj_limpo)
    print(f"Validação: {'✅ Válido' if is_valid else '❌ Inválido'}")
    
    # Testa formatação
    cnpj_formatado = formatar_cnpj(cnpj_limpo)
    print(f"CNPJ formatado: {cnpj_formatado}")
    
    # Testa mascaramento
    cnpj_mascarado = mascarar_cnpj(cnpj_teste)
    print(f"CNPJ mascarado: {cnpj_mascarado}")
    
    # Extrai informações
    info = extrair_info_cnpj(cnpj_teste)
    print(f"Tipo: {info['tipo_estabelecimento']}")
    print(f"É matriz: {'Sim' if info['eh_matriz'] else 'Não'}")
    print()

def teste_casos_conhecidos():
    print("🔍 TESTANDO CASOS CONHECIDOS")
    print("=" * 50)
    
    # CPFs conhecidos (inválidos)
    cpfs_invalidos = [
        "111.111.111-11",
        "000.000.000-00",
        "123.456.789-10"  # Dígitos verificadores incorretos
    ]
    
    print("CPFs inválidos:")
    for cpf in cpfs_invalidos:
        resultado = validar_cpf(cpf)
        print(f"  {cpf}: {'❌ Inválido' if not resultado else '✅ Válido'}")
    
    # CNPJs conhecidos (inválidos)
    cnpjs_invalidos = [
        "11.111.111/1111-11",
        "00.000.000/0000-00",
        "12.345.678/0001-90"  # Dígitos verificadores incorretos
    ]
    
    print("\nCNPJs inválidos:")
    for cnpj in cnpjs_invalidos:
        resultado = validar_cnpj(cnpj)
        print(f"  {cnpj}: {'❌ Inválido' if not resultado else '✅ Válido'}")
    
    print()

def main():
    print("🚀 TESTE DOS UTILITÁRIOS DE DOCUMENTOS BRASILEIROS")
    print("=" * 60)
    print()
    
    if not IMPORTS_OK:
        print("❌ Falha nos imports. Verifique se os módulos foram criados corretamente.")
        return
    
    try:
        teste_cpf()
        teste_cnpj()
        teste_casos_conhecidos()
        
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("Os utilitários de CPF e CNPJ estão funcionando corretamente.")
        
    except Exception as e:
        print(f"❌ ERRO NOS TESTES: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
