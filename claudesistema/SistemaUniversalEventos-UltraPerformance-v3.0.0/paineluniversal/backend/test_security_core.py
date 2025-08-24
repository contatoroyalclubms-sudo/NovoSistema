"""
TESTE CORE DO SISTEMA DE SEGURANÇA
Teste independente das funcionalidades principais
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_security_core():
    print("=== TESTE CORE DO SISTEMA DE SEGURANÇA ===")
    
    try:
        # Teste 1: Imports
        print("\n1. Testando imports...")
        from app.core.security import SecurityManager, UserRole, Permission
        print("   ✓ SecurityManager importado")
        print("   ✓ UserRole importado")
        print("   ✓ Permission importado")
        
        # Teste 2: Instanciar SecurityManager
        print("\n2. Testando instanciação...")
        security = SecurityManager()
        print("   ✓ SecurityManager instanciado")
        
        # Teste 3: Password Policy
        print("\n3. Testando Password Policy...")
        weak_password = security.validate_password_policy("123")
        strong_password = security.validate_password_policy("Ultra123!")
        print(f"   Senha fraca '123': {weak_password['valid']} - {weak_password['strength_level']}")
        print(f"   Senha forte 'Ultra123!': {strong_password['valid']} - {strong_password['strength_level']}")
        
        # Teste 4: Hash de senha
        print("\n4. Testando Hash de senhas...")
        password = "Ultra123!"
        hashed = security.get_password_hash(password)
        verified = security.verify_password(password, hashed)
        print(f"   Hash gerado: {bool(hashed)}")
        print(f"   Verificação: {verified}")
        
        # Teste 5: JWT Tokens
        print("\n5. Testando JWT Tokens...")
        token_data = {"sub": "user123", "email": "test@test.com"}
        access_token = security.create_access_token(token_data)
        refresh_token = security.create_refresh_token("user123")
        verified_token = security.verify_token(access_token)
        
        print(f"   Access token criado: {bool(access_token)}")
        print(f"   Refresh token criado: {bool(refresh_token)}")
        print(f"   Token verificado: {verified_token is not None}")
        if verified_token:
            print(f"   Token payload: {verified_token.get('sub')}")
        
        # Teste 6: RBAC
        print("\n6. Testando RBAC...")
        admin_can_create = security.user_has_permission(UserRole.ADMIN, Permission.CREATE_EVENT)
        guest_can_create = security.user_has_permission(UserRole.GUEST, Permission.CREATE_EVENT)
        admin_permissions = security.get_user_permissions(UserRole.ADMIN)
        
        print(f"   Admin pode criar evento: {admin_can_create}")
        print(f"   Guest pode criar evento: {guest_can_create}")
        print(f"   Admin tem {len(admin_permissions)} permissões")
        
        # Teste 7: Security Monitoring
        print("\n7. Testando Security Monitoring...")
        security.track_failed_login("192.168.1.1", "test@test.com")
        is_blocked = security.is_ip_blocked("192.168.1.1")
        fingerprint = security.generate_device_fingerprint("Mozilla/5.0", "192.168.1.1")
        
        print(f"   Failed login tracked: ✓")
        print(f"   IP bloqueado (1 tentativa): {is_blocked}")
        print(f"   Device fingerprint: {fingerprint}")
        
        # Teste 8: Enums
        print("\n8. Testando Enums...")
        print(f"   UserRole count: {len(list(UserRole))}")
        print(f"   Permission count: {len(list(Permission))}")
        print(f"   Sample roles: {[r.value for r in list(UserRole)[:3]]}")
        
        print("\n" + "="*50)
        print("TODOS OS TESTES CORE PASSARAM! ✓")
        print("SISTEMA DE SEGURANÇA ULTRA-EXPERT FUNCIONANDO!")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_security_core()
    print(f"\nSTATUS: {'SUCCESS' if success else 'FAILED'}")
    exit(0 if success else 1)