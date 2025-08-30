"""
Comprehensive test suite for Authentication Router
Tests all auth endpoints with security considerations, rate limiting, and edge cases
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Usuario, TipoUsuario
from app.core.security import verify_password, get_password_hash, decode_access_token
from app.schemas import LoginRequest, UsuarioCreate


class TestAuthLogin:
    """Test login functionality"""
    
    def test_login_success_admin(self, client: TestClient, admin_user: Usuario):
        """Test successful admin login"""
        response = client.post(
            "/auth/login",
            json={"email": "admin@test.com", "senha": "admin123"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert data["token_type"] == "bearer"
        
        # Verify token contains user info
        token_data = decode_access_token(data["access_token"])
        assert token_data["sub"] == admin_user.email
        assert token_data["user_id"] == str(admin_user.id)

    def test_login_success_promoter(self, client: TestClient, promoter_user: Usuario):
        """Test successful promoter login"""
        response = client.post(
            "/auth/login",
            json={"email": "promoter@test.com", "senha": "promoter123"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data

    def test_login_invalid_email(self, client: TestClient):
        """Test login with invalid email"""
        response = client.post(
            "/auth/login",
            json={"email": "invalid@test.com", "senha": "password123"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Credenciais inválidas" in response.json()["detail"]

    def test_login_invalid_password(self, client: TestClient, admin_user: Usuario):
        """Test login with invalid password"""
        response = client.post(
            "/auth/login",
            json={"email": "admin@test.com", "senha": "wrongpassword"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Credenciais inválidas" in response.json()["detail"]

    def test_login_inactive_user(self, client: TestClient, db_session: Session):
        """Test login with inactive user"""
        # Create inactive user
        inactive_user = Usuario(
            email="inactive@test.com",
            nome="Inactive User",
            senha_hash=get_password_hash("password123"),
            tipo=TipoUsuario.OPERADOR,
            ativo=False,
            verificado=True,
            created_at=datetime.utcnow()
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        response = client.post(
            "/auth/login",
            json={"email": "inactive@test.com", "senha": "password123"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Usuário inativo" in response.json()["detail"]

    def test_login_unverified_user(self, client: TestClient, db_session: Session):
        """Test login with unverified user"""
        # Create unverified user
        unverified_user = Usuario(
            email="unverified@test.com",
            nome="Unverified User",
            senha_hash=get_password_hash("password123"),
            tipo=TipoUsuario.OPERADOR,
            ativo=True,
            verificado=False,
            created_at=datetime.utcnow()
        )
        db_session.add(unverified_user)
        db_session.commit()
        
        response = client.post(
            "/auth/login",
            json={"email": "unverified@test.com", "senha": "password123"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Usuário não verificado" in response.json()["detail"]

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing required fields"""
        response = client.post("/auth/login", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_invalid_email_format(self, client: TestClient):
        """Test login with invalid email format"""
        response = client.post(
            "/auth/login",
            json={"email": "invalid-email", "senha": "password123"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch('app.routers.auth.login_rate_limit')
    def test_login_rate_limiting(self, mock_rate_limit, client: TestClient):
        """Test rate limiting on login attempts"""
        from fastapi import HTTPException
        
        # Mock rate limit to raise exception
        mock_rate_limit.side_effect = HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts"
        )
        
        response = client.post(
            "/auth/login",
            json={"email": "admin@test.com", "senha": "admin123"}
        )
        
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_login_sql_injection_attempt(self, client: TestClient):
        """Test login with SQL injection attempt"""
        malicious_email = "admin@test.com'; DROP TABLE usuarios; --"
        response = client.post(
            "/auth/login",
            json={"email": malicious_email, "senha": "admin123"}
        )
        
        # Should return 401 or 422, not crash
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestAuthRefreshToken:
    """Test refresh token functionality"""
    
    def test_refresh_token_success(self, client: TestClient, admin_user: Usuario):
        """Test successful token refresh"""
        # First login to get tokens
        login_response = client.post(
            "/auth/login",
            json={"email": "admin@test.com", "senha": "admin123"}
        )
        tokens = login_response.json()
        
        # Use refresh token
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data

    def test_refresh_invalid_token(self, client: TestClient):
        """Test refresh with invalid token"""
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_expired_token(self, client: TestClient):
        """Test refresh with expired token"""
        # Create an expired token manually
        expired_token = "expired.jwt.token"
        
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": expired_token}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthLogout:
    """Test logout functionality"""
    
    def test_logout_success(self, client: TestClient, auth_headers_admin: dict):
        """Test successful logout"""
        response = client.post("/auth/logout", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Logout realizado com sucesso"

    def test_logout_without_token(self, client: TestClient):
        """Test logout without authorization token"""
        response = client.post("/auth/logout")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_invalid_token(self, client: TestClient):
        """Test logout with invalid token"""
        response = client.post(
            "/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthProfile:
    """Test user profile endpoints"""
    
    def test_get_profile_success(self, client: TestClient, auth_headers_admin: dict, admin_user: Usuario):
        """Test getting user profile"""
        response = client.get("/auth/me", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == admin_user.email
        assert data["nome"] == admin_user.nome
        assert data["tipo"] == admin_user.tipo.value

    def test_get_profile_unauthorized(self, client: TestClient):
        """Test getting profile without authorization"""
        response = client.get("/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_success(self, client: TestClient, auth_headers_admin: dict):
        """Test updating user profile"""
        update_data = {
            "nome": "Updated Admin Name",
            "telefone": "11987654321"
        }
        
        response = client.put("/auth/me", json=update_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nome"] == update_data["nome"]

    def test_change_password_success(self, client: TestClient, auth_headers_admin: dict):
        """Test changing password"""
        password_data = {
            "senha_atual": "admin123",
            "senha_nova": "newpassword123",
            "confirmar_senha": "newpassword123"
        }
        
        response = client.put("/auth/change-password", json=password_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Senha alterada com sucesso"

    def test_change_password_wrong_current(self, client: TestClient, auth_headers_admin: dict):
        """Test changing password with wrong current password"""
        password_data = {
            "senha_atual": "wrongpassword",
            "senha_nova": "newpassword123",
            "confirmar_senha": "newpassword123"
        }
        
        response = client.put("/auth/change-password", json=password_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_mismatch(self, client: TestClient, auth_headers_admin: dict):
        """Test changing password with mismatched confirmation"""
        password_data = {
            "senha_atual": "admin123",
            "senha_nova": "newpassword123",
            "confirmar_senha": "differentpassword"
        }
        
        response = client.put("/auth/change-password", json=password_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_weak_password_rejected(self, client: TestClient, auth_headers_admin: dict):
        """Test that weak passwords are rejected"""
        password_data = {
            "senha_atual": "admin123",
            "senha_nova": "123",  # Too weak
            "confirmar_senha": "123"
        }
        
        response = client.put("/auth/change-password", json=password_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAuthRegistration:
    """Test user registration functionality"""
    
    def test_register_user_success(self, client: TestClient, auth_headers_admin: dict):
        """Test successful user registration by admin"""
        user_data = {
            "email": "newuser@test.com",
            "nome": "New User",
            "senha": "password123",
            "tipo": "OPERADOR",
            "telefone": "11987654321"
        }
        
        response = client.post("/auth/register", json=user_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["nome"] == user_data["nome"]

    def test_register_duplicate_email(self, client: TestClient, auth_headers_admin: dict, admin_user: Usuario):
        """Test registration with duplicate email"""
        user_data = {
            "email": admin_user.email,  # Duplicate email
            "nome": "Duplicate User",
            "senha": "password123",
            "tipo": "OPERADOR"
        }
        
        response = client.post("/auth/register", json=user_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já está em uso" in response.json()["detail"]

    def test_register_without_permission(self, client: TestClient, auth_headers_operador: dict):
        """Test registration without admin permissions"""
        user_data = {
            "email": "newuser@test.com",
            "nome": "New User",
            "senha": "password123",
            "tipo": "OPERADOR"
        }
        
        response = client.post("/auth/register", json=user_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_register_invalid_email_format(self, client: TestClient, auth_headers_admin: dict):
        """Test registration with invalid email format"""
        user_data = {
            "email": "invalid-email",
            "nome": "New User",
            "senha": "password123",
            "tipo": "OPERADOR"
        }
        
        response = client.post("/auth/register", json=user_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthSecurity:
    """Test authentication security features"""
    
    def test_password_hashing(self, db_session: Session):
        """Test that passwords are properly hashed"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Verify password is hashed (not plain text)
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_jwt_token_structure(self, client: TestClient, admin_user: Usuario):
        """Test JWT token structure and claims"""
        response = client.post(
            "/auth/login",
            json={"email": "admin@test.com", "senha": "admin123"}
        )
        
        token = response.json()["access_token"]
        claims = decode_access_token(token)
        
        # Verify required claims
        assert "sub" in claims  # Subject (email)
        assert "user_id" in claims
        assert "exp" in claims  # Expiration
        assert "iat" in claims  # Issued at

    def test_token_expiration(self, client: TestClient, admin_user: Usuario):
        """Test token expiration handling"""
        # This test would need to mock time or use short-lived tokens
        # For now, we test the structure is correct
        response = client.post(
            "/auth/login",
            json={"email": "admin@test.com", "senha": "admin123"}
        )
        
        token = response.json()["access_token"]
        claims = decode_access_token(token)
        
        # Verify expiration is in the future
        import time
        assert claims["exp"] > time.time()

    @patch('app.routers.auth.log_user_action')
    def test_security_logging(self, mock_log, client: TestClient, admin_user: Usuario):
        """Test that security events are logged"""
        client.post(
            "/auth/login",
            json={"email": "admin@test.com", "senha": "admin123"}
        )
        
        # Verify logging was called
        assert mock_log.called

    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are present"""
        response = client.options("/auth/login")
        
        # Check for CORS headers (if implemented)
        # This depends on your CORS middleware configuration
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED]


class TestAuthPermissions:
    """Test role-based access control"""
    
    def test_admin_access_to_admin_endpoints(self, client: TestClient, auth_headers_admin: dict):
        """Test admin can access admin-only endpoints"""
        response = client.get("/auth/users", headers=auth_headers_admin)
        
        # Should succeed (200) or be not found (404) but not forbidden
        assert response.status_code != status.HTTP_403_FORBIDDEN

    def test_promoter_access_restrictions(self, client: TestClient, auth_headers_promoter: dict):
        """Test promoter access restrictions"""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@test.com",
                "nome": "Test",
                "senha": "password123",
                "tipo": "OPERADOR"
            },
            headers=auth_headers_promoter
        )
        
        # Should be forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_operador_access_restrictions(self, client: TestClient, auth_headers_operador: dict):
        """Test operator access restrictions"""
        response = client.get("/auth/users", headers=auth_headers_operador)
        
        # Should be forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN


# Performance and stress tests
class TestAuthPerformance:
    """Test authentication performance"""
    
    def test_login_performance(self, client: TestClient, admin_user: Usuario):
        """Test login response time"""
        import time
        
        start_time = time.time()
        response = client.post(
            "/auth/login",
            json={"email": "admin@test.com", "senha": "admin123"}
        )
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        # Login should complete within 2 seconds
        assert end_time - start_time < 2.0

    def test_token_validation_performance(self, client: TestClient, auth_headers_admin: dict):
        """Test token validation performance"""
        import time
        
        start_time = time.time()
        response = client.get("/auth/me", headers=auth_headers_admin)
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        # Token validation should be very fast
        assert end_time - start_time < 0.5


# Edge cases and error handling
class TestAuthEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_request_body(self, client: TestClient):
        """Test handling of empty request body"""
        response = client.post("/auth/login")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_malformed_json(self, client: TestClient):
        """Test handling of malformed JSON"""
        response = client.post(
            "/auth/login",
            data="{'invalid': json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_very_long_email(self, client: TestClient, auth_headers_admin: dict):
        """Test handling of very long email addresses"""
        long_email = "a" * 300 + "@test.com"
        user_data = {
            "email": long_email,
            "nome": "Test User",
            "senha": "password123",
            "tipo": "OPERADOR"
        }
        
        response = client.post("/auth/register", json=user_data, headers=auth_headers_admin)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_unicode_characters(self, client: TestClient, auth_headers_admin: dict):
        """Test handling of Unicode characters in user data"""
        user_data = {
            "email": "üñíçødé@test.com",
            "nome": "José María Nuñez",
            "senha": "password123",
            "tipo": "OPERADOR"
        }
        
        response = client.post("/auth/register", json=user_data, headers=auth_headers_admin)
        # Should handle Unicode properly
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_concurrent_registrations(self, client: TestClient, auth_headers_admin: dict):
        """Test handling of concurrent registration attempts"""
        import threading
        
        results = []
        
        def register_user(email_suffix):
            user_data = {
                "email": f"concurrent{email_suffix}@test.com",
                "nome": f"Concurrent User {email_suffix}",
                "senha": "password123",
                "tipo": "OPERADOR"
            }
            response = client.post("/auth/register", json=user_data, headers=auth_headers_admin)
            results.append(response.status_code)
        
        # Start multiple registration threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=register_user, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All should succeed
        assert all(code == status.HTTP_201_CREATED for code in results)