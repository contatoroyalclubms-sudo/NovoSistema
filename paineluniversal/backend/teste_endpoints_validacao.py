"""
Teste dos endpoints de validação de documentos
"""

import requests
import json
from datetime import datetime

# Configuração base
BASE_URL = "http://localhost:8000/api/v1/utils"

def test_endpoint(endpoint, data=None, method="GET"):
    """Testa um endpoint e mostra o resultado"""
    print(f"\n{'='*60}")
    print(f"TESTANDO: {method} {endpoint}")
    print('='*60)
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"}
            )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCESSO!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ ERRO!")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")

def main():
    """Executa todos os testes"""
    print("🧪 INICIANDO TESTES DOS ENDPOINTS DE VALIDAÇÃO")
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # 1. Teste de status
    test_endpoint("/status")
    
    # 2. Teste de validação de CPF válido
    test_endpoint("/cpf/validar", {
        "documento": "123.456.789-09"
    }, "POST")
    
    # 3. Teste de validação de CPF inválido
    test_endpoint("/cpf/validar", {
        "documento": "123.456.789-99"
    }, "POST")
    
    # 4. Teste de geração de CPF
    test_endpoint("/cpf/gerar", method="POST")
    
    # 5. Teste de validação de CNPJ válido  
    test_endpoint("/cnpj/validar", {
        "documento": "11.222.333/0001-81"
    }, "POST")
    
    # 6. Teste de validação de CNPJ inválido
    test_endpoint("/cnpj/validar", {
        "documento": "11.222.333/0001-99"
    }, "POST")
    
    # 7. Teste de geração de CNPJ
    test_endpoint("/cnpj/gerar", method="POST")
    
    # 8. Teste de validação automática (CPF)
    test_endpoint("/documento/validar", {
        "documento": "12345678909"
    }, "POST")
    
    # 9. Teste de validação automática (CNPJ)
    test_endpoint("/documento/validar", {
        "documento": "11222333000181"
    }, "POST")
    
    # 10. Teste de validação de lista
    test_endpoint("/lista/validar", {
        "documentos": [
            "123.456.789-09",  # CPF válido
            "123.456.789-99",  # CPF inválido
            "11.222.333/0001-81",  # CNPJ válido
            "11.222.333/0001-99",  # CNPJ inválido
            "12345678909",  # CPF sem formatação
            "11222333000181",  # CNPJ sem formatação
            "123",  # Inválido
            ""  # Vazio
        ]
    }, "POST")
    
    print(f"\n{'='*60}")
    print("🏁 TESTES CONCLUÍDOS!")
    print('='*60)

if __name__ == "__main__":
    main()
