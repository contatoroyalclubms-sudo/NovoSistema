import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

from app.main import app
from app.database import get_db, Base
from app.models import Usuario, Empresa, Evento, PromoterEvento, Lista, Transacao, TipoUsuario, StatusEvento
from app.auth import criar_access_token

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

@pytest.fixture(scope="module")
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
        cnpj="12345678000199",
        email="teste@empresa.com",
        telefone="11999999999"
    )
    db_session.add(empresa)
    db_session.commit()
    db_session.refresh(empresa)
    return empresa

@pytest.fixture
def usuario_admin(db_session, empresa_teste):
    usuario = Usuario(
        nome="Admin Teste",
        email="admin@teste.com",
        cpf="12345678901",
        telefone="11999999999",
        tipo=TipoUsuario.ADMIN,
        empresa_id=empresa_teste.id,
        senha_hash="$2b$12$test",
        ativo=True
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario

@pytest.fixture
def usuario_promoter(db_session, empresa_teste):
    usuario = Usuario(
        nome="Promoter Teste",
        email="promoter@teste.com",
        cpf="98765432109",
        telefone="11888888888",
        tipo=TipoUsuario.PROMOTER,
        empresa_id=empresa_teste.id,
        senha_hash="$2b$12$test",
        ativo=True
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario

@pytest.fixture
def token_admin(usuario_admin):
    return criar_access_token(data={"sub": usuario_admin.cpf})

@pytest.fixture
def token_promoter(usuario_promoter):
    return criar_access_token(data={"sub": usuario_promoter.cpf})

@pytest.fixture
def evento_teste(db_session, empresa_teste, usuario_admin):
    evento = Evento(
        nome="Evento Teste",
        descricao="Descrição do evento teste",
        data_evento=datetime.now() + timedelta(days=30),
        local="Local Teste",
        endereco="Endereço Teste",
        limite_idade=18,
        capacidade_maxima=100,
        status=StatusEvento.ATIVO,
        empresa_id=empresa_teste.id,
        criador_id=usuario_admin.id
    )
    db_session.add(evento)
    db_session.commit()
    db_session.refresh(evento)
    return evento

class TestEventosCRUD:
    
    def test_criar_evento_admin(self, client, token_admin, empresa_teste):
        headers = {"Authorization": f"Bearer {token_admin}"}
        evento_data = {
            "nome": "Novo Evento",
            "descricao": "Descrição do novo evento",
            "data_evento": (datetime.now() + timedelta(days=30)).isoformat(),
            "local": "Novo Local",
            "endereco": "Novo Endereço",
            "limite_idade": 21,
            "capacidade_maxima": 200,
            "empresa_id": empresa_teste.id
        }
        
        response = client.post("/api/eventos/", json=evento_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nome"] == evento_data["nome"]
        assert data["local"] == evento_data["local"]
        assert data["limite_idade"] == evento_data["limite_idade"]
    
    def test_criar_evento_promoter(self, client, token_promoter, empresa_teste):
        headers = {"Authorization": f"Bearer {token_promoter}"}
        evento_data = {
            "nome": "Evento Promoter",
            "descricao": "Evento criado por promoter",
            "data_evento": (datetime.now() + timedelta(days=30)).isoformat(),
            "local": "Local Promoter",
            "limite_idade": 18,
            "capacidade_maxima": 150,
            "empresa_id": empresa_teste.id
        }
        
        response = client.post("/api/eventos/", json=evento_data, headers=headers)
        assert response.status_code == 200
    
    def test_criar_evento_data_passada(self, client, token_admin, empresa_teste):
        headers = {"Authorization": f"Bearer {token_admin}"}
        evento_data = {
            "nome": "Evento Passado",
            "data_evento": (datetime.now() - timedelta(days=1)).isoformat(),
            "local": "Local",
            "limite_idade": 18,
            "capacidade_maxima": 100,
            "empresa_id": empresa_teste.id
        }
        
        response = client.post("/api/eventos/", json=evento_data, headers=headers)
        assert response.status_code == 400
        assert "Data do evento deve ser futura" in response.json()["detail"]
    
    def test_listar_eventos(self, client, token_admin, evento_teste):
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.get("/api/eventos/", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        assert any(evento["id"] == evento_teste.id for evento in data)
    
    def test_obter_evento(self, client, token_admin, evento_teste):
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.get(f"/api/eventos/{evento_teste.id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == evento_teste.id
        assert data["nome"] == evento_teste.nome
    
    def test_obter_evento_inexistente(self, client, token_admin):
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.get("/api/eventos/99999", headers=headers)
        assert response.status_code == 404
    
    def test_atualizar_evento(self, client, token_admin, evento_teste):
        headers = {"Authorization": f"Bearer {token_admin}"}
        evento_update = {
            "nome": "Evento Atualizado",
            "descricao": "Descrição atualizada",
            "data_evento": (datetime.now() + timedelta(days=45)).isoformat(),
            "local": "Local Atualizado",
            "limite_idade": 21,
            "capacidade_maxima": 150,
            "empresa_id": evento_teste.empresa_id
        }
        
        response = client.put(f"/api/eventos/{evento_teste.id}", json=evento_update, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nome"] == "Evento Atualizado"
        assert data["limite_idade"] == 21
    
    def test_cancelar_evento(self, client, token_admin, evento_teste):
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.delete(f"/api/eventos/{evento_teste.id}", headers=headers)
        assert response.status_code == 200
        assert "cancelado com sucesso" in response.json()["mensagem"]

class TestEventosDetalhado:
    
    def test_obter_evento_detalhado(self, client, token_admin, evento_teste, db_session):
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.get(f"/api/eventos/detalhado/{evento_teste.id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == evento_teste.id
        assert "total_vendas" in data
        assert "receita_total" in data
        assert "total_checkins" in data
        assert "promoters_vinculados" in data
        assert "status_financeiro" in data
    
    def test_buscar_eventos_por_nome(self, client, token_admin, evento_teste):
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.get(f"/api/eventos/buscar?nome={evento_teste.nome}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        assert any(evento["nome"] == evento_teste.nome for evento in data)
    
    def test_buscar_eventos_por_status(self, client, token_admin, evento_teste):
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.get("/api/eventos/buscar?status=ATIVO", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert all(evento["status"] == "ativo" for evento in data)
    
    def test_buscar_eventos_por_local(self, client, token_admin):
        """Teste busca de eventos por local"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get("/api/eventos/buscar?local=Teste", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_buscar_eventos_admin_com_empresa_id(self, client, token_admin):
        """Teste busca de eventos por admin com filtro de empresa"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get("/api/eventos/buscar?empresa_id=1", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_listar_eventos_admin_com_empresa_id(self, client, token_admin):
        """Teste listagem de eventos por admin com filtro de empresa"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get("/api/eventos/?empresa_id=1", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_listar_eventos_com_status_filter(self, client, token_admin):
        """Teste listagem de eventos com filtro de status"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get("/api/eventos/?status=ativo", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestPromotersVinculacao:
    
    def test_vincular_promoter(self, client, token_admin, evento_teste, usuario_promoter):
        headers = {"Authorization": f"Bearer {token_admin}"}
        promoter_data = {
            "promoter_id": usuario_promoter.id,
            "meta_vendas": 50,
            "comissao_percentual": 10.5
        }
        
        response = client.post(f"/api/eventos/{evento_teste.id}/promoters", json=promoter_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["promoter_id"] == usuario_promoter.id
        assert data["meta_vendas"] == 50
        assert float(data["comissao_percentual"]) == 10.5
    
    def test_vincular_promoter_inexistente(self, client, token_admin, evento_teste):
        headers = {"Authorization": f"Bearer {token_admin}"}
        promoter_data = {
            "promoter_id": 99999,
            "meta_vendas": 50
        }
        
        response = client.post(f"/api/eventos/{evento_teste.id}/promoters", json=promoter_data, headers=headers)
        assert response.status_code == 404
    
    def test_desvincular_promoter(self, client, token_admin, evento_teste, usuario_promoter, db_session):
        promoter_evento = PromoterEvento(
            evento_id=evento_teste.id,
            promoter_id=usuario_promoter.id,
            meta_vendas=50,
            ativo=True
        )
        db_session.add(promoter_evento)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.delete(f"/api/eventos/{evento_teste.id}/promoters/{usuario_promoter.id}", headers=headers)
        assert response.status_code == 200

class TestEventosExportacao:
    
    def test_exportar_csv(self, client, token_admin, evento_teste):
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.get(f"/api/eventos/{evento_teste.id}/export/csv", headers=headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    def test_exportar_pdf(self, client, token_admin, evento_teste):
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.get(f"/api/eventos/{evento_teste.id}/export/pdf", headers=headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

class TestEventosPermissoes:
    
    def test_acesso_negado_sem_token(self, client):
        response = client.get("/api/eventos/")
        assert response.status_code == 403
    
    def test_promoter_nao_pode_cancelar_evento(self, client, token_promoter, evento_teste):
        headers = {"Authorization": f"Bearer {token_promoter}"}
        
        response = client.delete(f"/api/eventos/{evento_teste.id}", headers=headers)
        assert response.status_code == 403

    def test_promoter_nao_pode_acessar_evento_outra_empresa(self, client, db_session):
        """Teste que promoter não pode acessar evento de outra empresa"""
        from app.models import Usuario, TipoUsuario, Empresa, Evento
        from app.auth import gerar_hash_senha, criar_access_token
        
        empresa1 = Empresa(nome="Empresa 1", cnpj="11.111.111/0001-11", email="emp1@test.com")
        empresa2 = Empresa(nome="Empresa 2", cnpj="22.222.222/0001-22", email="emp2@test.com")
        db_session.add_all([empresa1, empresa2])
        db_session.commit()
        
        promoter = Usuario(
            cpf="777.666.555-44",
            nome="Promoter Teste",
            email="promoter3@test.com",
            senha_hash=gerar_hash_senha("senha123"),
            tipo=TipoUsuario.PROMOTER,
            empresa_id=empresa1.id
        )
        db_session.add(promoter)
        db_session.commit()
        
        evento_outra_empresa = Evento(
            nome="Evento Empresa 2",
            data_evento=datetime(2025, 12, 31, 22, 0),
            local="Local Teste",
            empresa_id=empresa2.id,
            criador_id=1
        )
        db_session.add(evento_outra_empresa)
        db_session.commit()
        
        token = criar_access_token(data={"sub": promoter.cpf})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/eventos/{evento_outra_empresa.id}", headers=headers)
        assert response.status_code == 403

    def test_atualizar_evento_inexistente(self, client, token_admin):
        """Teste atualizar evento que não existe"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        evento_data = {
            "nome": "Evento Atualizado",
            "data_evento": "2025-12-31T22:00:00",
            "local": "Local Atualizado",
            "empresa_id": 1
        }
        
        response = client.put("/api/eventos/999", json=evento_data, headers=headers)
        assert response.status_code == 404

    def test_atualizar_evento_data_passada(self, client, token_admin, evento_teste):
        """Teste atualizar evento com data passada"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        evento_data = {
            "nome": "Evento Atualizado",
            "data_evento": "2020-01-01T22:00:00",
            "local": "Local Atualizado",
            "empresa_id": 1
        }
        
        response = client.put(f"/api/eventos/{evento_teste.id}", json=evento_data, headers=headers)
        assert response.status_code == 400

    def test_cancelar_evento_inexistente(self, client, token_admin):
        """Teste cancelar evento que não existe"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.delete("/api/eventos/999", headers=headers)
        assert response.status_code == 404

    def test_promoter_nao_pode_atualizar_evento_outra_empresa(self, client, db_session):
        """Teste que promoter não pode atualizar evento de outra empresa"""
        from app.models import Usuario, TipoUsuario, Empresa, Evento
        from app.auth import gerar_hash_senha, criar_access_token
        
        empresa1 = Empresa(nome="Empresa 1", cnpj="33.333.333/0001-33", email="emp1@test.com")
        empresa2 = Empresa(nome="Empresa 2", cnpj="44.444.444/0001-44", email="emp2@test.com")
        db_session.add_all([empresa1, empresa2])
        db_session.commit()
        
        promoter = Usuario(
            cpf="666.555.444-33",
            nome="Promoter Teste",
            email="promoter4@test.com",
            senha_hash=gerar_hash_senha("senha123"),
            tipo=TipoUsuario.PROMOTER,
            empresa_id=empresa1.id
        )
        db_session.add(promoter)
        db_session.commit()
        
        evento_outra_empresa = Evento(
            nome="Evento Empresa 2",
            data_evento=datetime(2025, 12, 31, 22, 0),
            local="Local Teste",
            empresa_id=empresa2.id,
            criador_id=1
        )
        db_session.add(evento_outra_empresa)
        db_session.commit()
        
        token = criar_access_token(data={"sub": promoter.cpf})
        headers = {"Authorization": f"Bearer {token}"}
        
        evento_data = {
            "nome": "Evento Atualizado",
            "data_evento": "2025-12-31T22:00:00",
            "local": "Local Atualizado",
            "empresa_id": empresa2.id
        }
        
        response = client.put(f"/api/eventos/{evento_outra_empresa.id}", json=evento_data, headers=headers)
        assert response.status_code == 403
    
    def test_usuario_cliente_nao_pode_criar_evento(self, client, db_session):
        """Teste que usuário tipo cliente não pode criar eventos"""
        from app.models import Usuario, TipoUsuario
        from app.auth import gerar_hash_senha, criar_access_token
        
        cliente = Usuario(
            cpf="999.888.777-66",
            nome="Cliente Teste",
            email="cliente@test.com",
            senha_hash=gerar_hash_senha("senha123"),
            tipo=TipoUsuario.CLIENTE,
            empresa_id=1
        )
        db_session.add(cliente)
        db_session.commit()
        
        token = criar_access_token(data={"sub": cliente.cpf})
        headers = {"Authorization": f"Bearer {token}"}
        
        evento_data = {
            "nome": "Evento Teste Cliente",
            "data_evento": "2025-12-31T22:00:00",
            "local": "Local Teste",
            "empresa_id": 1
        }
        
        response = client.post("/api/eventos/", json=evento_data, headers=headers)
        assert response.status_code == 403
        assert "apenas admins e promoters podem criar eventos" in response.json()["detail"]
    
    def test_promoter_nao_pode_criar_evento_outra_empresa(self, client, db_session):
        """Teste que promoter não pode criar evento para outra empresa"""
        from app.models import Usuario, TipoUsuario, Empresa
        from app.auth import gerar_hash_senha, criar_access_token
        
        empresa2 = Empresa(
            nome="Empresa 2",
            cnpj="98.765.432/0001-10",
            email="empresa2@test.com"
        )
        db_session.add(empresa2)
        db_session.commit()
        
        empresa1 = Empresa(
            nome="Empresa 1",
            cnpj="12.345.678/0001-99",
            email="empresa1@test.com"
        )
        db_session.add(empresa1)
        db_session.commit()
        
        promoter = Usuario(
            cpf="888.777.666-55",
            nome="Promoter Teste",
            email="promoter2@test.com",
            senha_hash=gerar_hash_senha("senha123"),
            tipo=TipoUsuario.PROMOTER,
            empresa_id=empresa1.id
        )
        db_session.add(promoter)
        db_session.commit()
        
        token = criar_access_token(data={"sub": promoter.cpf})
        headers = {"Authorization": f"Bearer {token}"}
        
        evento_data = {
            "nome": "Evento Outra Empresa",
            "data_evento": "2025-12-31T22:00:00",
            "local": "Local Teste",
            "empresa_id": empresa2.id  # Tentando criar para empresa 2
        }
        
        response = client.post("/api/eventos/", json=evento_data, headers=headers)
        assert response.status_code == 403
        assert "você só pode criar eventos para sua empresa" in response.json()["detail"]

class TestEventosFinanceiro:
    
    def test_obter_status_financeiro(self, client, token_admin, evento_teste, db_session):
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.get(f"/api/eventos/{evento_teste.id}/financeiro", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_receita" in data
        assert "total_vendas" in data
        assert "vendas_por_lista" in data
        assert "vendas_por_promoter" in data

class TestEventosDetalhesErros:
    
    def test_obter_evento_detalhado_inexistente(self, client, token_admin):
        """Teste obter detalhes de evento que não existe"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get("/api/eventos/999/detalhado", headers=headers)
        assert response.status_code == 404

    def test_obter_evento_detalhado_promoter_outra_empresa(self, client, db_session):
        """Teste que promoter não pode ver detalhes de evento de outra empresa"""
        from app.models import Usuario, TipoUsuario, Empresa, Evento
        from app.auth import gerar_hash_senha, criar_access_token
        
        empresa1 = Empresa(nome="Empresa 1", cnpj="99.999.999/0001-99", email="emp1@test.com")
        empresa2 = Empresa(nome="Empresa 2", cnpj="88.888.888/0001-88", email="emp2@test.com")
        db_session.add_all([empresa1, empresa2])
        db_session.commit()
        
        promoter = Usuario(
            cpf="333.222.111-00",
            nome="Promoter Teste",
            email="promoter7@test.com",
            senha_hash=gerar_hash_senha("senha123"),
            tipo=TipoUsuario.PROMOTER,
            empresa_id=empresa1.id
        )
        db_session.add(promoter)
        db_session.commit()
        
        evento_outra_empresa = Evento(
            nome="Evento Empresa 2",
            data_evento=datetime(2025, 12, 31, 22, 0),
            local="Local Teste",
            empresa_id=empresa2.id,
            criador_id=1
        )
        db_session.add(evento_outra_empresa)
        db_session.commit()
        
        token = criar_access_token(data={"sub": promoter.cpf})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/eventos/{evento_outra_empresa.id}/detalhado", headers=headers)
        assert response.status_code == 404

class TestEventosVinculacaoErros:
    
    def test_vincular_promoter_evento_inexistente(self, client, token_admin):
        """Teste vincular promoter a evento que não existe"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        promoter_data = {"promoter_id": 1, "meta_vendas": 100}
        
        response = client.post("/api/eventos/999/promoters", json=promoter_data, headers=headers)
        assert response.status_code == 404

    def test_vincular_promoter_sem_permissao(self, client, db_session):
        """Teste que promoter não pode vincular promoter a evento de outra empresa"""
        from app.models import Usuario, TipoUsuario, Empresa, Evento
        from app.auth import gerar_hash_senha, criar_access_token
        
        empresa1 = Empresa(nome="Empresa 1", cnpj="11.222.333/0001-11", email="emp1@test.com")
        empresa2 = Empresa(nome="Empresa 2", cnpj="22.333.444/0001-22", email="emp2@test.com")
        db_session.add_all([empresa1, empresa2])
        db_session.commit()
        
        promoter = Usuario(
            cpf="111.222.333-44",
            nome="Promoter Teste",
            email="promoter8@test.com",
            senha_hash=gerar_hash_senha("senha123"),
            tipo=TipoUsuario.PROMOTER,
            empresa_id=empresa1.id
        )
        db_session.add(promoter)
        db_session.commit()
        
        evento_outra_empresa = Evento(
            nome="Evento Empresa 2",
            data_evento=datetime(2025, 12, 31, 22, 0),
            local="Local Teste",
            empresa_id=empresa2.id,
            criador_id=1
        )
        db_session.add(evento_outra_empresa)
        db_session.commit()
        
        token = criar_access_token(data={"sub": promoter.cpf})
        headers = {"Authorization": f"Bearer {token}"}
        promoter_data = {"promoter_id": promoter.id, "meta_vendas": 100}
        
        response = client.post(f"/api/eventos/{evento_outra_empresa.id}/promoters", json=promoter_data, headers=headers)
        assert response.status_code == 403

    def test_vincular_promoter_ja_vinculado(self, client, token_admin, evento_teste, usuario_promoter, db_session):
        """Teste vincular promoter que já está vinculado ao evento"""
        from app.models import PromoterEvento
        
        promoter_evento = PromoterEvento(
            evento_id=evento_teste.id,
            promoter_id=usuario_promoter.id,
            meta_vendas=50,
            ativo=True
        )
        db_session.add(promoter_evento)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {token_admin}"}
        promoter_data = {"promoter_id": usuario_promoter.id, "meta_vendas": 100}
        
        response = client.post(f"/api/eventos/{evento_teste.id}/promoters", json=promoter_data, headers=headers)
        assert response.status_code == 400

    def test_desvincular_promoter_evento_inexistente(self, client, token_admin):
        """Teste desvincular promoter de evento que não existe"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.delete("/api/eventos/999/promoters/1", headers=headers)
        assert response.status_code == 404

    def test_desvincular_promoter_sem_permissao(self, client, db_session):
        """Teste que promoter não pode desvincular promoter de evento de outra empresa"""
        from app.models import Usuario, TipoUsuario, Empresa, Evento
        from app.auth import gerar_hash_senha, criar_access_token
        
        empresa1 = Empresa(nome="Empresa 1", cnpj="55.666.777/0001-55", email="emp1@test.com")
        empresa2 = Empresa(nome="Empresa 2", cnpj="66.777.888/0001-66", email="emp2@test.com")
        db_session.add_all([empresa1, empresa2])
        db_session.commit()
        
        promoter = Usuario(
            cpf="555.666.777-88",
            nome="Promoter Teste",
            email="promoter9@test.com",
            senha_hash=gerar_hash_senha("senha123"),
            tipo=TipoUsuario.PROMOTER,
            empresa_id=empresa1.id
        )
        db_session.add(promoter)
        db_session.commit()
        
        evento_outra_empresa = Evento(
            nome="Evento Empresa 2",
            data_evento=datetime(2025, 12, 31, 22, 0),
            local="Local Teste",
            empresa_id=empresa2.id,
            criador_id=1
        )
        db_session.add(evento_outra_empresa)
        db_session.commit()
        
        token = criar_access_token(data={"sub": promoter.cpf})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(f"/api/eventos/{evento_outra_empresa.id}/promoters/1", headers=headers)
        assert response.status_code == 403

    def test_desvincular_promoter_vinculacao_inexistente(self, client, token_admin, evento_teste):
        """Teste desvincular promoter que não está vinculado ao evento"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.delete(f"/api/eventos/{evento_teste.id}/promoters/999", headers=headers)
        assert response.status_code == 404

class TestEventosFinanceiroErros:
    
    def test_obter_status_financeiro_evento_inexistente(self, client, token_admin):
        """Teste obter status financeiro de evento que não existe"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.get("/api/eventos/999/financeiro", headers=headers)
        assert response.status_code == 404

    def test_obter_status_financeiro_sem_permissao(self, client, db_session):
        """Teste que promoter não pode ver status financeiro de evento de outra empresa"""
        from app.models import Usuario, TipoUsuario, Empresa, Evento
        from app.auth import gerar_hash_senha, criar_access_token
        
        empresa1 = Empresa(nome="Empresa 1", cnpj="77.888.999/0001-77", email="emp1@test.com")
        empresa2 = Empresa(nome="Empresa 2", cnpj="88.999.000/0001-88", email="emp2@test.com")
        db_session.add_all([empresa1, empresa2])
        db_session.commit()
        
        promoter = Usuario(
            cpf="777.888.999-00",
            nome="Promoter Teste",
            email="promoter10@test.com",
            senha_hash=gerar_hash_senha("senha123"),
            tipo=TipoUsuario.PROMOTER,
            empresa_id=empresa1.id
        )
        db_session.add(promoter)
        db_session.commit()
        
        evento_outra_empresa = Evento(
            nome="Evento Empresa 2",
            data_evento=datetime(2025, 12, 31, 22, 0),
            local="Local Teste",
            empresa_id=empresa2.id,
            criador_id=1
        )
        db_session.add(evento_outra_empresa)
        db_session.commit()
        
        token = criar_access_token(data={"sub": promoter.cpf})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/eventos/{evento_outra_empresa.id}/financeiro", headers=headers)
        assert response.status_code == 403

class TestEventosExportacaoErros:
    
    def test_exportar_csv_evento_inexistente(self, client, token_admin):
        """Teste exportar CSV de evento que não existe"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.get("/api/eventos/999/export/csv", headers=headers)
        assert response.status_code == 404

    def test_exportar_csv_sem_permissao(self, client, db_session):
        """Teste que promoter não pode exportar CSV de evento de outra empresa"""
        from app.models import Usuario, TipoUsuario, Empresa, Evento
        from app.auth import gerar_hash_senha, criar_access_token
        
        empresa1 = Empresa(nome="Empresa 1", cnpj="99.000.111/0001-99", email="emp1@test.com")
        empresa2 = Empresa(nome="Empresa 2", cnpj="00.111.222/0001-00", email="emp2@test.com")
        db_session.add_all([empresa1, empresa2])
        db_session.commit()
        
        promoter = Usuario(
            cpf="999.000.111-22",
            nome="Promoter Teste",
            email="promoter11@test.com",
            senha_hash=gerar_hash_senha("senha123"),
            tipo=TipoUsuario.PROMOTER,
            empresa_id=empresa1.id
        )
        db_session.add(promoter)
        db_session.commit()
        
        evento_outra_empresa = Evento(
            nome="Evento Empresa 2",
            data_evento=datetime(2025, 12, 31, 22, 0),
            local="Local Teste",
            empresa_id=empresa2.id,
            criador_id=1
        )
        db_session.add(evento_outra_empresa)
        db_session.commit()
        
        token = criar_access_token(data={"sub": promoter.cpf})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/eventos/{evento_outra_empresa.id}/export/csv", headers=headers)
        assert response.status_code == 403

    def test_exportar_pdf_evento_inexistente(self, client, token_admin):
        """Teste exportar PDF de evento que não existe"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        response = client.get("/api/eventos/999/export/pdf", headers=headers)
        assert response.status_code == 404

    def test_exportar_pdf_sem_permissao(self, client, db_session):
        """Teste que promoter não pode exportar PDF de evento de outra empresa"""
        from app.models import Usuario, TipoUsuario, Empresa, Evento
        from app.auth import gerar_hash_senha, criar_access_token
        
        empresa1 = Empresa(nome="Empresa 1", cnpj="11.222.333/0001-11", email="emp1@test.com")
        empresa2 = Empresa(nome="Empresa 2", cnpj="22.333.444/0001-22", email="emp2@test.com")
        db_session.add_all([empresa1, empresa2])
        db_session.commit()
        
        promoter = Usuario(
            cpf="111.222.333-44",
            nome="Promoter Teste",
            email="promoter12@test.com",
            senha_hash=gerar_hash_senha("senha123"),
            tipo=TipoUsuario.PROMOTER,
            empresa_id=empresa1.id
        )
        db_session.add(promoter)
        db_session.commit()
        
        evento_outra_empresa = Evento(
            nome="Evento Empresa 2",
            data_evento=datetime(2025, 12, 31, 22, 0),
            local="Local Teste",
            empresa_id=empresa2.id,
            criador_id=1
        )
        db_session.add(evento_outra_empresa)
        db_session.commit()
        
        token = criar_access_token(data={"sub": promoter.cpf})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/eventos/{evento_outra_empresa.id}/export/pdf", headers=headers)
        assert response.status_code == 403

class TestEventosListagemFiltros:
    
    def test_listar_eventos_promoter_filtro_empresa(self, client, db_session):
        """Teste que promoter só vê eventos da sua empresa"""
        from app.models import Usuario, TipoUsuario, Empresa, Evento
        from app.auth import gerar_hash_senha, criar_access_token
        
        empresa1 = Empresa(nome="Empresa 1", cnpj="55.555.555/0001-55", email="emp1@test.com")
        empresa2 = Empresa(nome="Empresa 2", cnpj="66.666.666/0001-66", email="emp2@test.com")
        db_session.add_all([empresa1, empresa2])
        db_session.commit()
        
        promoter = Usuario(
            cpf="555.444.333-22",
            nome="Promoter Teste",
            email="promoter5@test.com",
            senha_hash=gerar_hash_senha("senha123"),
            tipo=TipoUsuario.PROMOTER,
            empresa_id=empresa1.id
        )
        db_session.add(promoter)
        db_session.commit()
        
        evento1 = Evento(
            nome="Evento Empresa 1",
            data_evento=datetime(2025, 12, 31, 22, 0),
            local="Local 1",
            empresa_id=empresa1.id,
            criador_id=promoter.id
        )
        evento2 = Evento(
            nome="Evento Empresa 2",
            data_evento=datetime(2025, 12, 31, 22, 0),
            local="Local 2",
            empresa_id=empresa2.id,
            criador_id=1
        )
        db_session.add_all([evento1, evento2])
        db_session.commit()
        
        token = criar_access_token(data={"sub": promoter.cpf})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/eventos/", headers=headers)
        assert response.status_code == 200
        eventos = response.json()
        
        assert len(eventos) == 1
        assert eventos[0]["empresa_id"] == empresa1.id

    def test_buscar_eventos_promoter_filtro_empresa(self, client, db_session):
        """Teste que promoter só busca eventos da sua empresa"""
        from app.models import Usuario, TipoUsuario, Empresa, Evento
        from app.auth import gerar_hash_senha, criar_access_token
        
        empresa1 = Empresa(nome="Empresa 1", cnpj="77.777.777/0001-77", email="emp1@test.com")
        empresa2 = Empresa(nome="Empresa 2", cnpj="88.888.888/0001-88", email="emp2@test.com")
        db_session.add_all([empresa1, empresa2])
        db_session.commit()
        
        promoter = Usuario(
            cpf="444.333.222-11",
            nome="Promoter Teste",
            email="promoter6@test.com",
            senha_hash=gerar_hash_senha("senha123"),
            tipo=TipoUsuario.PROMOTER,
            empresa_id=empresa1.id
        )
        db_session.add(promoter)
        db_session.commit()
        
        evento1 = Evento(
            nome="Evento Empresa 1",
            data_evento=datetime(2025, 12, 31, 22, 0),
            local="Local 1",
            empresa_id=empresa1.id,
            criador_id=promoter.id
        )
        evento2 = Evento(
            nome="Evento Empresa 2",
            data_evento=datetime(2025, 12, 31, 22, 0),
            local="Local 2",
            empresa_id=empresa2.id,
            criador_id=1
        )
        db_session.add_all([evento1, evento2])
        db_session.commit()
        
        token = criar_access_token(data={"sub": promoter.cpf})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/eventos/buscar?nome=Evento", headers=headers)
        assert response.status_code == 200
        eventos = response.json()
        
        assert len(eventos) == 1
        assert eventos[0]["empresa_id"] == empresa1.id
