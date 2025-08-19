# 🧪 FASE 3: Testes e Qualidade

## 📋 Checklist de Implementação

### 1. Testes Backend (Python/Pytest)

#### 1.1 Setup de Testes
- [ ] **Arquivo:** `backend/tests/conftest.py` (configuração)
- [ ] **Arquivo:** `backend/pytest.ini` (configuração pytest)
- [ ] Database de teste SQLite
- [ ] Fixtures comuns
- [ ] Mocks para serviços externos

#### 1.2 Testes por Módulo
- [ ] `tests/test_auth.py` - Autenticação
- [ ] `tests/test_usuarios.py` - Gestão de usuários  
- [ ] `tests/test_empresas.py` - Gestão de empresas
- [ ] `tests/test_pdv.py` - Ponto de venda
- [ ] `tests/test_financeiro.py` - Sistema financeiro
- [ ] `tests/test_checkins.py` - Check-ins
- [ ] `tests/test_dashboard.py` - Dashboard e métricas
- [ ] `tests/test_gamificacao.py` - Sistema de gamificação

### 2. Testes Frontend (React Testing Library)

#### 2.1 Setup de Testes
- [ ] **Arquivo:** `frontend/src/setupTests.ts`
- [ ] **Arquivo:** `frontend/jest.config.js`
- [ ] Mocks para APIs
- [ ] Utilities de teste
- [ ] Test providers

#### 2.2 Testes de Componentes
- [ ] `__tests__/Dashboard.test.tsx`
- [ ] `__tests__/EventosModule.test.tsx`
- [ ] `__tests__/PDVModule.test.tsx`
- [ ] `__tests__/CheckinModule.test.tsx`
- [ ] `__tests__/LoginForm.test.tsx`
- [ ] `__tests__/UsuariosModule.test.tsx`

### 3. Testes de Integração

#### 3.1 API Integration Tests
- [ ] Testes de fluxo completo
- [ ] Testes de WebSocket
- [ ] Testes de upload de arquivos
- [ ] Testes de relatórios

#### 3.2 E2E Tests (Cypress)
- [ ] **Setup:** `frontend/cypress.config.ts`
- [ ] Login flow
- [ ] Criação de eventos
- [ ] Processo de vendas
- [ ] Check-in flow
- [ ] Dashboard navigation

## 🧪 Templates de Testes Backend

### conftest.py
```python
# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.main import app
from app.database import get_db, Base
from app.models import Usuario, Empresa, TipoUsuario
from app.auth import gerar_hash_senha, criar_access_token

# Database de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def empresa_teste(db_session):
    empresa = Empresa(
        nome="Empresa Teste",
        cnpj="12.345.678/0001-90",
        email="teste@empresa.com",
        telefone="11999999999",
        endereco="Rua Teste, 123"
    )
    db_session.add(empresa)
    db_session.commit()
    db_session.refresh(empresa)
    return empresa

@pytest.fixture
def admin_usuario(db_session, empresa_teste):
    usuario = Usuario(
        nome="Admin Teste",
        email="admin@teste.com",
        cpf="123.456.789-01",
        telefone="11999999999",
        tipo=TipoUsuario.ADMIN,
        empresa_id=empresa_teste.id,
        senha_hash=gerar_hash_senha("senha123"),
        ativo=True
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario

@pytest.fixture
def promoter_usuario(db_session, empresa_teste):
    usuario = Usuario(
        nome="Promoter Teste",
        email="promoter@teste.com",
        cpf="987.654.321-09",
        telefone="11888888888",
        tipo=TipoUsuario.PROMOTER,
        empresa_id=empresa_teste.id,
        senha_hash=gerar_hash_senha("senha123"),
        ativo=True
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario

@pytest.fixture
def admin_token(admin_usuario):
    return criar_access_token(data={"sub": admin_usuario.cpf})

@pytest.fixture
def promoter_token(promoter_usuario):
    return criar_access_token(data={"sub": promoter_usuario.cpf})

@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
```

### test_usuarios.py
```python
# backend/tests/test_usuarios.py
import pytest
from fastapi.testclient import TestClient
from app.models import Usuario, TipoUsuario

class TestUsuariosCRUD:
    
    def test_listar_usuarios_admin(self, client, auth_headers):
        """Admin pode listar todos os usuários"""
        response = client.get("/api/usuarios/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_criar_usuario_admin(self, client, auth_headers, empresa_teste):
        """Admin pode criar novos usuários"""
        usuario_data = {
            "nome": "Novo Usuario",
            "email": "novo@teste.com",
            "cpf": "111.222.333-44",
            "telefone": "11777777777",
            "tipo": "promoter",
            "empresa_id": empresa_teste.id,
            "senha": "senha123"
        }
        
        response = client.post("/api/usuarios/", json=usuario_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nome"] == usuario_data["nome"]
        assert data["email"] == usuario_data["email"]
        assert data["cpf"] == usuario_data["cpf"]
    
    def test_criar_usuario_cpf_duplicado(self, client, auth_headers, empresa_teste, admin_usuario):
        """Não deve permitir CPF duplicado"""
        usuario_data = {
            "nome": "Usuario Duplicado",
            "email": "duplicado@teste.com",
            "cpf": admin_usuario.cpf,  # CPF já existe
            "tipo": "promoter",
            "empresa_id": empresa_teste.id,
            "senha": "senha123"
        }
        
        response = client.post("/api/usuarios/", json=usuario_data, headers=auth_headers)
        assert response.status_code == 400
        assert "CPF já cadastrado" in response.json()["detail"]
    
    def test_atualizar_usuario(self, client, auth_headers, promoter_usuario):
        """Admin pode atualizar usuários"""
        update_data = {
            "nome": "Nome Atualizado",
            "telefone": "11666666666"
        }
        
        response = client.put(f"/api/usuarios/{promoter_usuario.id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nome"] == update_data["nome"]
        assert data["telefone"] == update_data["telefone"]
    
    def test_desativar_usuario(self, client, auth_headers, promoter_usuario):
        """Admin pode desativar usuários"""
        response = client.patch(f"/api/usuarios/{promoter_usuario.id}/desativar", headers=auth_headers)
        assert response.status_code == 200
        
        # Verificar se foi desativado
        response = client.get(f"/api/usuarios/{promoter_usuario.id}", headers=auth_headers)
        data = response.json()
        assert data["ativo"] == False

class TestUsuariosPermissoes:
    
    def test_promoter_nao_pode_criar_usuario(self, client, promoter_token, empresa_teste):
        """Promoter não pode criar usuários"""
        headers = {"Authorization": f"Bearer {promoter_token}"}
        usuario_data = {
            "nome": "Tentativa Usuario",
            "email": "tentativa@teste.com",
            "cpf": "555.666.777-88",
            "tipo": "promoter",
            "empresa_id": empresa_teste.id,
            "senha": "senha123"
        }
        
        response = client.post("/api/usuarios/", json=usuario_data, headers=headers)
        assert response.status_code == 403
    
    def test_usuario_sem_token_negado(self, client):
        """Requisições sem token devem ser negadas"""
        response = client.get("/api/usuarios/")
        assert response.status_code == 403

class TestUsuariosFiltros:
    
    def test_filtrar_por_tipo(self, client, auth_headers):
        """Deve filtrar usuários por tipo"""
        response = client.get("/api/usuarios/?tipo=admin", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        for usuario in data:
            assert usuario["tipo"] == "admin"
    
    def test_buscar_por_nome(self, client, auth_headers):
        """Deve buscar usuários por nome"""
        response = client.get("/api/usuarios/?busca=Admin", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        assert any("Admin" in usuario["nome"] for usuario in data)
```

## 🎭 Templates de Testes Frontend

### setupTests.ts
```typescript
// frontend/src/setupTests.ts
import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Mock do localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

// Mock do WebSocket
global.WebSocket = jest.fn(() => ({
  close: jest.fn(),
  send: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
})) as any;

// Setup MSW
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Dashboard.test.tsx
```typescript
// frontend/src/components/__tests__/Dashboard.test.tsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../dashboard/Dashboard';
import { AuthProvider } from '../../contexts/AuthContext';

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        {component}
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('Dashboard', () => {
  test('deve renderizar título do dashboard', () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  test('deve carregar métricas do dashboard', async () => {
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Total de Eventos')).toBeInTheDocument();
      expect(screen.getByText('Total de Vendas')).toBeInTheDocument();
      expect(screen.getByText('Total de Check-ins')).toBeInTheDocument();
    });
  });

  test('deve mostrar loading inicial', () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  test('deve permitir seleção de evento', async () => {
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      const select = screen.getByRole('combobox');
      expect(select).toBeInTheDocument();
    });
  });
});
```

## 🎪 Testes E2E com Cypress

### cypress.config.ts
```typescript
// frontend/cypress.config.ts
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
```

### login-flow.cy.ts
```typescript
// frontend/cypress/e2e/login-flow.cy.ts
describe('Login Flow', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('deve fazer login com credenciais válidas', () => {
    cy.get('[data-testid="cpf-input"]').type('123.456.789-01');
    cy.get('[data-testid="senha-input"]').type('senha123');
    cy.get('[data-testid="login-button"]').click();
    
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid="user-menu"]').should('be.visible');
  });

  it('deve mostrar erro com credenciais inválidas', () => {
    cy.get('[data-testid="cpf-input"]').type('000.000.000-00');
    cy.get('[data-testid="senha-input"]').type('senhaerrada');
    cy.get('[data-testid="login-button"]').click();
    
    cy.get('[data-testid="error-message"]').should('contain', 'Credenciais inválidas');
  });

  it('deve validar campos obrigatórios', () => {
    cy.get('[data-testid="login-button"]').click();
    
    cy.get('[data-testid="cpf-error"]').should('be.visible');
    cy.get('[data-testid="senha-error"]').should('be.visible');
  });
});
```

## 📊 Cronograma Fase 3

| Tarefa | Estimativa | Status |
|--------|------------|--------|
| Setup testes backend | 1 dia | ⏳ |
| Testes módulos backend | 4 dias | ⏳ |
| Setup testes frontend | 1 dia | ⏳ |
| Testes componentes frontend | 3 dias | ⏳ |
| Testes E2E Cypress | 2 dias | ⏳ |
| Cobertura e relatórios | 1 dia | ⏳ |
| CI/CD integration | 1 dia | ⏳ |

**Total:** 13 dias (2.6 semanas)

## 🎯 Metas de Cobertura

- **Backend:** >85% cobertura de código
- **Frontend:** >80% cobertura de componentes
- **E2E:** Fluxos críticos 100% cobertos
- **Performance:** Todos os testes <5s