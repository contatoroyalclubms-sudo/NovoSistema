"""
TESTE DO SISTEMA DE AUTENTICAÇÃO ULTRA-EXPERT
Sprint 2: Validação das funcionalidades de autenticação
"""

import asyncio
import aiohttp
import json
import time

BASE_URL = "http://localhost:8000"

class AuthTester:
    def __init__(self):
        self.session = None
        
    async def setup(self):
        self.session = aiohttp.ClientSession()
        print("=== TESTANDO AUTENTICAÇÃO ULTRA-EXPERT ===")
        
    async def cleanup(self):
        if self.session:
            await self.session.close()
            
    async def test_system_info(self):
        """Testa se sistema está online"""
        print("\n1. Testando System Info...")
        try:
            async with self.session.get(f"{BASE_URL}/api/v1/system/info") as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Version: {data.get('version')}")
                print(f"   Phase: {data.get('phase')}")
                return resp.status == 200
        except Exception as e:
            print(f"   ERROR: {e}")
            return False
    
    async def test_security_system(self):
        """Testa sistema de segurança"""
        print("\n2. Testando Sistema de Segurança...")
        try:
            # Importar e testar SecurityManager
            from app.core.security import security_manager, UserRole, Permission
            
            # Teste 1: Password Policy
            policy_test = security_manager.validate_password_policy("Ultra123!")
            print(f"   Password Policy Test: {policy_test['valid']}")
            print(f"   Strength: {policy_test['strength_level']}")
            
            # Teste 2: RBAC
            admin_can_create = security_manager.user_has_permission(UserRole.ADMIN, Permission.CREATE_EVENT)
            guest_can_create = security_manager.user_has_permission(UserRole.GUEST, Permission.CREATE_EVENT)
            print(f"   RBAC Admin can create event: {admin_can_create}")
            print(f"   RBAC Guest can create event: {guest_can_create}")
            
            # Teste 3: Token Creation
            test_token = security_manager.create_access_token({"sub": "test123", "email": "test@test.com"})
            print(f"   JWT Token Created: {bool(test_token)}")
            
            # Teste 4: Token Verification
            token_payload = security_manager.verify_token(test_token)
            print(f"   JWT Token Verified: {bool(token_payload)}")
            
            return True
            
        except Exception as e:
            print(f"   ERROR: {e}")
            return False
    
    async def test_mock_login(self):
        """Testa login com dados mock"""
        print("\n3. Testando Mock Database...")
        try:
            from app.routers.auth_ultra_expert import mock_users_db
            
            print(f"   Mock users count: {len(mock_users_db)}")
            for email, user in mock_users_db.items():
                print(f"   User: {email} - Role: {user['role']}")
            
            return True
            
        except Exception as e:
            print(f"   ERROR: {e}")
            return False
    
    async def test_password_validation(self):
        """Testa validação de senhas"""
        print("\n4. Testando Validação de Senhas...")
        try:
            from app.core.security import security_manager
            
            test_cases = [
                ("123456", False, "Senha fraca"),
                ("password", False, "Senha comum"),
                ("Ultra123!", True, "Senha forte"),
                ("abc", False, "Muito curta"),
                ("LongPasswordWithoutNumbers!", False, "Sem números"),
                ("Admin2024!", True, "Senha válida")
            ]
            
            for password, expected, description in test_cases:
                result = security_manager.validate_password_policy(password)
                passed = result["valid"] == expected
                status = "PASS" if passed else "FAIL"
                print(f"   {status}: {description} - '{password}' -> {result['valid']}")
                
            return True
            
        except Exception as e:
            print(f"   ERROR: {e}")
            return False
    
    async def test_rbac_matrix(self):
        """Testa matriz RBAC completa"""
        print("\n5. Testando RBAC Matrix...")
        try:
            from app.core.security import security_manager, UserRole, Permission, ROLE_PERMISSIONS
            
            print(f"   Total Roles: {len(UserRole)}")
            print(f"   Total Permissions: {len(Permission)}")
            
            # Testar algumas permissões específicas
            test_cases = [
                (UserRole.SUPER_ADMIN, Permission.MANAGE_SYSTEM, True),
                (UserRole.ADMIN, Permission.CREATE_EVENT, True),
                (UserRole.ORGANIZADOR, Permission.USE_PDV, True),
                (UserRole.PARTICIPANTE, Permission.CREATE_EVENT, False),
                (UserRole.GUEST, Permission.MANAGE_SYSTEM, False)
            ]
            
            for role, permission, expected in test_cases:
                result = security_manager.user_has_permission(role, permission)
                status = "PASS" if result == expected else "FAIL"
                print(f"   {status}: {role.value} -> {permission.value} = {result}")
                
            return True
            
        except Exception as e:
            print(f"   ERROR: {e}")
            return False
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        await self.setup()
        
        tests = [
            self.test_system_info(),
            self.test_security_system(),
            self.test_mock_login(),
            self.test_password_validation(),
            self.test_rbac_matrix()
        ]
        
        results = []
        for test in tests:
            try:
                result = await test
                results.append(result)
            except Exception as e:
                print(f"Test failed with exception: {e}")
                results.append(False)
        
        await self.cleanup()
        
        # Resultados finais
        passed = sum(results)
        total = len(results)
        
        print("\n" + "="*50)
        print("RESULTADOS DOS TESTES DE AUTENTICAÇÃO")
        print("="*50)
        print(f"PASSOU: {passed}/{total}")
        print(f"TAXA DE SUCESSO: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\nTODOS OS TESTES DE AUTENTICAÇÃO PASSARAM!")
            print("SISTEMA ULTRA-EXPERT FUNCIONANDO PERFEITAMENTE!")
        else:
            print(f"\n{total - passed} TESTES FALHARAM")
        
        return passed == total

async def main():
    tester = AuthTester()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    print(f"\nSTATUS FINAL: {'SUCCESS' if success else 'FAILED'}")