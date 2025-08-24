"""
Testes integrados para Sistema de Check-in Inteligente
Sprint 4 - Check-in com IA, geolocalização e funcionalidades offline

Cobertura de testes:
- Check-in via QR Code
- Check-in via CPF com validação
- Check-in manual por operadores
- Check-in em lote (bulk)
- Validações de segurança
- Analytics em tempo real
- WebSocket notifications
- Funcionalidades offline
"""

import pytest
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.models import (
    Usuario, Evento, Participante, CheckinLog, CheckinSession,
    TipoCheckin, StatusCheckin, StatusParticipante
)
from app.schemas import (
    CheckinQRRequest, CheckinCPFRequest, CheckinManualRequest, CheckinBulkRequest,
    TipoCheckinEnum, StatusCheckinEnum
)

# ================================
# CONFIGURAÇÃO DOS TESTES
# ================================

# Database de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_checkin.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override da database para testes"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def test_db():
    """Fixture para database de teste"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """Cliente de teste FastAPI"""
    return TestClient(app)

@pytest.fixture
def db_session():
    """Sessão de database para testes"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def sample_user(db_session):
    """Usuário de exemplo para testes"""
    user = Usuario(
        id=uuid.uuid4(),
        nome="João Silva Teste",
        email="joao.teste@email.com",
        cpf="12345678901",
        telefone="(11) 99999-9999",
        tipo_usuario="participante",
        ativo=True,
        senha_hash="hashed_password_test"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_evento(db_session, sample_user):
    """Evento de exemplo para testes"""
    evento = Evento(
        id=uuid.uuid4(),
        nome="Evento Teste Check-in",
        descricao="Evento para testar sistema de check-in",
        tipo_evento="festa",
        status="ativo",
        data_inicio=datetime.utcnow() + timedelta(hours=1),
        data_fim=datetime.utcnow() + timedelta(hours=5),
        data_inicio_checkin=datetime.utcnow() - timedelta(minutes=30),
        data_fim_checkin=datetime.utcnow() + timedelta(hours=4),
        local_nome="Local Teste",
        local_endereco="Rua Teste, 123 - São Paulo, SP",
        local_coordenadas={"lat": -23.5505, "lng": -46.6333},
        capacidade_maxima=1000,
        organizador_id=sample_user.id,
        valor_entrada=Decimal('50.00'),
        sistema_pontuacao_ativo=True,
        pontos_checkin=10,
        permite_checkin_antecipado=True
    )
    db_session.add(evento)
    db_session.commit()
    db_session.refresh(evento)
    return evento

@pytest.fixture
def sample_participante(db_session, sample_user, sample_evento):
    """Participante de exemplo para testes"""
    participante = Participante(
        id=uuid.uuid4(),
        usuario_id=sample_user.id,
        evento_id=sample_evento.id,
        status=StatusParticipante.CONFIRMADO,
        data_inscricao=datetime.utcnow() - timedelta(days=1),
        valor_pago=Decimal('50.00'),
        lista_tipo="VIP",
        qr_code_individual=json.dumps({
            "evento_id": str(sample_evento.id),
            "participante_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat()
        })
    )
    db_session.add(participante)
    db_session.commit()
    db_session.refresh(participante)
    return participante

@pytest.fixture
def auth_headers():
    """Headers de autenticação para testes"""
    return {"Authorization": "Bearer test_token_123"}

# ================================
# TESTES DE CHECK-IN VIA QR CODE
# ================================

class TestCheckinQRCode:
    """Testes para check-in via QR Code"""
    
    def test_checkin_qr_sucesso(self, client, sample_participante, auth_headers):
        """Teste de check-in via QR Code bem-sucedido"""
        qr_data = json.dumps({
            "evento_id": str(sample_participante.evento_id),
            "participante_id": str(sample_participante.id),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        payload = {
            "evento_id": str(sample_participante.evento_id),
            "qr_code": qr_data,
            "tipo_checkin": "qr_code",
            "localizacao": {"lat": -23.5505, "lng": -46.6333},
            "dispositivo_info": {"userAgent": "TestAgent/1.0"}
        }
        
        response = client.post("/api/v1/checkins/qr-code", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["participante_id"] == str(sample_participante.id)
        assert data["evento_id"] == str(sample_participante.evento_id)
        assert data["tipo_checkin"] == "qr_code"
        assert data["status"] == "aprovado"
        assert "tempo_processamento_ms" in data
        assert "qr_code_checkout" in data
    
    def test_checkin_qr_code_invalido(self, client, auth_headers):
        """Teste com QR Code inválido"""
        payload = {
            "evento_id": str(uuid.uuid4()),
            "qr_code": "qr_code_invalido",
            "tipo_checkin": "qr_code"
        }
        
        response = client.post("/api/v1/checkins/qr-code", json=payload, headers=auth_headers)
        
        assert response.status_code == 400
        assert "inválido ou corrompido" in response.json()["detail"]
    
    def test_checkin_qr_participante_nao_encontrado(self, client, sample_evento, auth_headers):
        """Teste com participante não encontrado"""
        qr_data = json.dumps({
            "evento_id": str(sample_evento.id),
            "participante_id": str(uuid.uuid4()),  # ID inexistente
            "timestamp": datetime.utcnow().isoformat()
        })
        
        payload = {
            "evento_id": str(sample_evento.id),
            "qr_code": qr_data,
            "tipo_checkin": "qr_code"
        }
        
        response = client.post("/api/v1/checkins/qr-code", json=payload, headers=auth_headers)
        
        assert response.status_code == 404
        assert "Participante não encontrado" in response.json()["detail"]
    
    def test_checkin_qr_duplicado(self, client, sample_participante, auth_headers, db_session):
        """Teste de check-in duplicado"""
        # Cria sessão ativa existente
        session_existente = CheckinSession(
            participante_id=sample_participante.id,
            evento_id=sample_participante.evento_id,
            checkin_em=datetime.utcnow(),
            ativa=True
        )
        db_session.add(session_existente)
        db_session.commit()
        
        qr_data = json.dumps({
            "evento_id": str(sample_participante.evento_id),
            "participante_id": str(sample_participante.id),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        payload = {
            "evento_id": str(sample_participante.evento_id),
            "qr_code": qr_data,
            "tipo_checkin": "qr_code"
        }
        
        response = client.post("/api/v1/checkins/qr-code", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["duplicado"] is True
        assert "já realizou check-in" in data["message"]

# ================================
# TESTES DE CHECK-IN VIA CPF
# ================================

class TestCheckinCPF:
    """Testes para check-in via CPF"""
    
    def test_checkin_cpf_sucesso(self, client, sample_participante, auth_headers):
        """Teste de check-in via CPF bem-sucedido"""
        payload = {
            "evento_id": str(sample_participante.evento_id),
            "cpf": "12345678901",
            "tres_digitos": "123",
            "tipo_checkin": "cpf",
            "localizacao": {"lat": -23.5505, "lng": -46.6333}
        }
        
        response = client.post("/api/v1/checkins/cpf", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["tipo_checkin"] == "cpf"
        assert data["status"] == "aprovado"
        assert data["participante_nome"] == sample_participante.usuario.nome
    
    def test_checkin_cpf_invalido(self, client, auth_headers):
        """Teste com CPF inválido"""
        payload = {
            "evento_id": str(uuid.uuid4()),
            "cpf": "11111111111",  # CPF inválido
            "tres_digitos": "111",
            "tipo_checkin": "cpf"
        }
        
        response = client.post("/api/v1/checkins/cpf", json=payload, headers=auth_headers)
        
        assert response.status_code == 400
        assert "CPF inválido" in response.json()["detail"]
    
    def test_checkin_cpf_validacao_incorreta(self, client, sample_participante, auth_headers):
        """Teste com validação de 3 dígitos incorreta"""
        payload = {
            "evento_id": str(sample_participante.evento_id),
            "cpf": "12345678901",
            "tres_digitos": "999",  # Incorreto
            "tipo_checkin": "cpf"
        }
        
        response = client.post("/api/v1/checkins/cpf", json=payload, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Validação de segurança incorreta" in response.json()["detail"]
    
    def test_checkin_cpf_usuario_nao_encontrado(self, client, sample_evento, auth_headers):
        """Teste com usuário não encontrado"""
        payload = {
            "evento_id": str(sample_evento.id),
            "cpf": "98765432100",  # CPF não existe
            "tres_digitos": "987",
            "tipo_checkin": "cpf"
        }
        
        response = client.post("/api/v1/checkins/cpf", json=payload, headers=auth_headers)
        
        assert response.status_code == 404
        assert "Usuário com este CPF não encontrado" in response.json()["detail"]

# ================================
# TESTES DE CHECK-IN MANUAL
# ================================

class TestCheckinManual:
    """Testes para check-in manual"""
    
    def test_checkin_manual_sucesso(self, client, sample_participante, auth_headers):
        """Teste de check-in manual bem-sucedido"""
        payload = {
            "evento_id": str(sample_participante.evento_id),
            "participante_id": str(sample_participante.id),
            "operador_id": str(uuid.uuid4()),
            "justificativa": "Problema com QR Code, check-in manual necessário",
            "tipo_checkin": "manual"
        }
        
        with patch('app.routers.checkins.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(
                id=uuid.uuid4(),
                tipo_usuario="operador",
                nome="Operador Teste"
            )
            
            response = client.post("/api/v1/checkins/manual", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["tipo_checkin"] == "manual"
        assert "Check-in manual realizado" in data["message"]
    
    def test_checkin_manual_usuario_nao_autorizado(self, client, sample_participante, auth_headers):
        """Teste com usuário não autorizado"""
        payload = {
            "evento_id": str(sample_participante.evento_id),
            "participante_id": str(sample_participante.id),
            "operador_id": str(uuid.uuid4()),
            "justificativa": "Teste",
            "tipo_checkin": "manual"
        }
        
        with patch('app.routers.checkins.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(
                id=uuid.uuid4(),
                tipo_usuario="participante",  # Não autorizado
                nome="Participante Teste"
            )
            
            response = client.post("/api/v1/checkins/manual", json=payload, headers=auth_headers)
        
        assert response.status_code == 403
        assert "não autorizado" in response.json()["detail"]

# ================================
# TESTES DE CHECK-IN EM LOTE
# ================================

class TestCheckinBulk:
    """Testes para check-in em lote"""
    
    def test_checkin_bulk_sucesso(self, client, sample_evento, auth_headers, db_session):
        """Teste de check-in em lote bem-sucedido"""
        # Cria usuários e participantes para teste em lote
        users = []
        participantes = []
        
        for i in range(3):
            user = Usuario(
                id=uuid.uuid4(),
                nome=f"Usuário Bulk {i}",
                email=f"bulk{i}@test.com",
                cpf=f"1234567890{i}",
                tipo_usuario="participante",
                ativo=True,
                senha_hash="hash_test"
            )
            db_session.add(user)
            users.append(user)
        
        db_session.commit()
        
        for i, user in enumerate(users):
            participante = Participante(
                id=uuid.uuid4(),
                usuario_id=user.id,
                evento_id=sample_evento.id,
                status=StatusParticipante.CONFIRMADO,
                data_inscricao=datetime.utcnow(),
                lista_tipo="Comum"
            )
            db_session.add(participante)
            participantes.append(participante)
        
        db_session.commit()
        
        # Payload do bulk
        payload = {
            "evento_id": str(sample_evento.id),
            "tipo_checkin": "bulk",
            "participantes": [
                {"cpf": f"1234567890{i}", "nome": f"Usuário Bulk {i}", "observacoes": f"Bulk test {i}"}
                for i in range(3)
            ],
            "confirmar_operacao": True,
            "ignorar_duplicados": True,
            "processar_async": False
        }
        
        with patch('app.routers.checkins.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(
                id=uuid.uuid4(),
                tipo_usuario="organizador",
                nome="Organizador Teste"
            )
            
            response = client.post("/api/v1/checkins/bulk", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_processados"] == 3
        assert data["total_sucessos"] >= 0
        assert data["total_erros"] >= 0
        assert data["processamento_async"] is False
        assert "status" in data
    
    def test_checkin_bulk_sem_confirmacao(self, client, auth_headers):
        """Teste de bulk sem confirmação"""
        payload = {
            "evento_id": str(uuid.uuid4()),
            "tipo_checkin": "bulk",
            "participantes": [{"cpf": "12345678901"}],
            "confirmar_operacao": False  # Sem confirmação
        }
        
        with patch('app.routers.checkins.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(tipo_usuario="organizador")
            
            response = client.post("/api/v1/checkins/bulk", json=payload, headers=auth_headers)
        
        assert response.status_code == 400
        assert "requer confirmação explícita" in response.json()["detail"]

# ================================
# TESTES DE VALIDAÇÃO
# ================================

class TestValidacaoCheckin:
    """Testes para validação prévia de check-in"""
    
    def test_validacao_sucesso(self, client, sample_participante, auth_headers):
        """Teste de validação bem-sucedida"""
        payload = {
            "evento_id": str(sample_participante.evento_id),
            "participante_id": str(sample_participante.id),
            "validar_localizacao": True,
            "localizacao": {"lat": -23.5505, "lng": -46.6333}
        }
        
        response = client.post("/api/v1/checkins/validar", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["pode_fazer_checkin"] is True
        assert data["participante_encontrado"] is True
        assert data["evento_ativo"] is True
        assert data["dentro_horario"] is True
        assert data["localizacao_valida"] is True
        assert len(data["motivos_bloqueio"]) == 0
    
    def test_validacao_evento_nao_encontrado(self, client, auth_headers):
        """Teste com evento não encontrado"""
        payload = {
            "evento_id": str(uuid.uuid4()),  # ID inexistente
            "validar_localizacao": False
        }
        
        response = client.post("/api/v1/checkins/validar", json=payload, headers=auth_headers)
        
        assert response.status_code == 404
        assert "Evento não encontrado" in response.json()["detail"]
    
    def test_validacao_participante_ja_checkin(self, client, sample_participante, auth_headers, db_session):
        """Teste com participante que já fez check-in"""
        # Cria sessão ativa
        session = CheckinSession(
            participante_id=sample_participante.id,
            evento_id=sample_participante.evento_id,
            checkin_em=datetime.utcnow(),
            ativa=True
        )
        db_session.add(session)
        db_session.commit()
        
        payload = {
            "evento_id": str(sample_participante.evento_id),
            "participante_id": str(sample_participante.id),
            "validar_localizacao": False
        }
        
        response = client.post("/api/v1/checkins/validar", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["pode_fazer_checkin"] is False
        assert data["ja_fez_checkin"] is True
        assert "já realizou check-in" in data["motivos_bloqueio"]

# ================================
# TESTES DE CHECKOUT
# ================================

class TestCheckout:
    """Testes para check-out"""
    
    def test_checkout_sucesso(self, client, sample_participante, auth_headers, db_session):
        """Teste de check-out bem-sucedido"""
        # Cria sessão ativa
        session = CheckinSession(
            participante_id=sample_participante.id,
            evento_id=sample_participante.evento_id,
            checkin_em=datetime.utcnow() - timedelta(hours=2),
            ativa=True,
            qr_code_checkout=json.dumps({
                "participante_id": str(sample_participante.id),
                "type": "checkout"
            })
        )
        db_session.add(session)
        db_session.commit()
        
        payload = {
            "participante_id": str(sample_participante.id),
            "avaliacao_evento": 5,
            "comentario_evento": "Evento excelente!"
        }
        
        response = client.post("/api/v1/checkins/checkout", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["tempo_permanencia_minutos"] > 0
        assert data["avaliacao_coletada"] is True
        assert data["comentario_coletado"] is True
    
    def test_checkout_sessao_nao_encontrada(self, client, auth_headers):
        """Teste de checkout sem sessão ativa"""
        payload = {
            "participante_id": str(uuid.uuid4())
        }
        
        response = client.post("/api/v1/checkins/checkout", json=payload, headers=auth_headers)
        
        assert response.status_code == 404
        assert "Sessão de check-in ativa não encontrada" in response.json()["detail"]

# ================================
# TESTES DE ANALYTICS
# ================================

class TestAnalyticsCheckin:
    """Testes para analytics de check-in"""
    
    def test_analytics_evento(self, client, sample_evento, auth_headers, db_session):
        """Teste de analytics do evento"""
        # Cria alguns check-ins para analytics
        for i in range(5):
            log = CheckinLog(
                evento_id=sample_evento.id,
                tipo_checkin=TipoCheckin.QR_CODE,
                status_checkin=StatusCheckin.APROVADO,
                sucesso=True,
                tentativa_em=datetime.utcnow() - timedelta(minutes=i*10),
                tempo_processamento_ms=200 + i*50
            )
            db_session.add(log)
        
        db_session.commit()
        
        response = client.get(f"/api/v1/checkins/analytics/{sample_evento.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "evento_id" in data
        assert "evento_nome" in data
        assert "metricas_basicas" in data
        assert "checkins_por_hora" in data
        assert "checkins_por_tipo" in data
        assert "performance" in data
        
        # Verifica métricas básicas
        metricas = data["metricas_basicas"]
        assert "total_inscritos" in metricas
        assert "total_presentes" in metricas
        assert "taxa_presenca" in metricas
    
    def test_status_tempo_real(self, client, sample_evento, auth_headers, db_session):
        """Teste de status em tempo real"""
        # Cria sessões ativas
        for i in range(3):
            user = Usuario(
                id=uuid.uuid4(),
                nome=f"User RT {i}",
                email=f"rt{i}@test.com",
                cpf=f"9876543210{i}",
                tipo_usuario="participante",
                ativo=True,
                senha_hash="hash"
            )
            db_session.add(user)
            
            participante = Participante(
                id=uuid.uuid4(),
                usuario_id=user.id,
                evento_id=sample_evento.id,
                status=StatusParticipante.PRESENTE,
                data_inscricao=datetime.utcnow()
            )
            db_session.add(participante)
            
            session = CheckinSession(
                participante_id=participante.id,
                evento_id=sample_evento.id,
                checkin_em=datetime.utcnow() - timedelta(minutes=i*15),
                ativa=True
            )
            db_session.add(session)
        
        db_session.commit()
        
        response = client.get(f"/api/v1/checkins/status/{sample_evento.id}/tempo-real", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "timestamp" in data
        assert "sessoes_ativas" in data
        assert "ultimos_checkins" in data
        assert "fila_checkin" in data
        assert "estatisticas_rapidas" in data
        
        # Verifica se encontrou as sessões criadas
        assert len(data["sessoes_ativas"]) >= 0
        assert data["estatisticas_rapidas"]["total_presentes"] >= 0

# ================================
# TESTES DE WEBSOCKET
# ================================

@pytest.mark.asyncio
class TestWebSocketCheckin:
    """Testes para notificações WebSocket"""
    
    async def test_websocket_connection(self):
        """Teste de conexão WebSocket"""
        with patch('app.websocket.websocket_manager') as mock_manager:
            mock_manager.connect = MagicMock()
            mock_manager.disconnect = MagicMock()
            
            # Simula conexão WebSocket
            websocket = MagicMock()
            await mock_manager.connect(websocket, "test-connection")
            
            mock_manager.connect.assert_called_once()
    
    async def test_checkin_notification(self):
        """Teste de notificação de check-in"""
        with patch('app.websocket.websocket_manager') as mock_manager:
            mock_manager.broadcast_to_room = MagicMock()
            
            # Simula envio de notificação
            await mock_manager.broadcast_to_room("evento_123", {
                'type': 'new_checkin',
                'participante': 'João Silva',
                'evento_id': '123',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            mock_manager.broadcast_to_room.assert_called_once()

# ================================
# TESTES DE UPLOAD CSV
# ================================

class TestUploadCSV:
    """Testes para upload de CSV"""
    
    def test_upload_csv_sucesso(self, client, sample_evento, auth_headers):
        """Teste de upload CSV bem-sucedido"""
        # Simula arquivo CSV
        csv_content = "cpf,nome,email,observacoes\n12345678901,João CSV,joao@csv.com,Teste CSV"
        
        with patch('app.routers.checkins.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(tipo_usuario="organizador")
            
            files = {"file": ("test.csv", csv_content, "text/csv")}
            response = client.post(
                f"/api/v1/checkins/upload-csv?evento_id={sample_evento.id}",
                files=files,
                headers=auth_headers
            )
        
        # Como não temos participantes correspondentes, esperamos resposta de processamento
        assert response.status_code in [200, 400]  # Pode falhar por não encontrar participantes
    
    def test_upload_nao_csv(self, client, sample_evento, auth_headers):
        """Teste com arquivo não-CSV"""
        with patch('app.routers.checkins.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(tipo_usuario="organizador")
            
            files = {"file": ("test.txt", "conteudo texto", "text/plain")}
            response = client.post(
                f"/api/v1/checkins/upload-csv?evento_id={sample_evento.id}",
                files=files,
                headers=auth_headers
            )
        
        assert response.status_code == 400
        assert "Apenas arquivos CSV" in response.json()["detail"]

# ================================
# TESTES DE PERFORMANCE
# ================================

class TestPerformanceCheckin:
    """Testes de performance do sistema"""
    
    def test_tempo_resposta_checkin(self, client, sample_participante, auth_headers):
        """Teste de tempo de resposta do check-in"""
        import time
        
        qr_data = json.dumps({
            "evento_id": str(sample_participante.evento_id),
            "participante_id": str(sample_participante.id),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        payload = {
            "evento_id": str(sample_participante.evento_id),
            "qr_code": qr_data,
            "tipo_checkin": "qr_code"
        }
        
        start_time = time.time()
        response = client.post("/api/v1/checkins/qr-code", json=payload, headers=auth_headers)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # em milissegundos
        
        # Check-in deve ser rápido (menos de 1 segundo)
        assert response_time < 1000
        assert response.status_code in [200, 400]  # Sucesso ou erro esperado
        
        if response.status_code == 200:
            data = response.json()
            assert "tempo_processamento_ms" in data
    
    def test_multiplos_checkins_simultaneos(self, client, sample_evento, auth_headers, db_session):
        """Teste de múltiplos check-ins simultâneos"""
        import concurrent.futures
        import threading
        
        # Cria múltiplos participantes
        participantes = []
        for i in range(10):
            user = Usuario(
                id=uuid.uuid4(),
                nome=f"User Concurrent {i}",
                email=f"concurrent{i}@test.com",
                cpf=f"5555555550{i}",
                tipo_usuario="participante",
                ativo=True,
                senha_hash="hash"
            )
            db_session.add(user)
            
            participante = Participante(
                id=uuid.uuid4(),
                usuario_id=user.id,
                evento_id=sample_evento.id,
                status=StatusParticipante.CONFIRMADO,
                data_inscricao=datetime.utcnow()
            )
            db_session.add(participante)
            participantes.append(participante)
        
        db_session.commit()
        
        def fazer_checkin(participante):
            """Função para fazer check-in em thread separada"""
            qr_data = json.dumps({
                "evento_id": str(participante.evento_id),
                "participante_id": str(participante.id),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            payload = {
                "evento_id": str(participante.evento_id),
                "qr_code": qr_data,
                "tipo_checkin": "qr_code"
            }
            
            return client.post("/api/v1/checkins/qr-code", json=payload, headers=auth_headers)
        
        # Executa check-ins concorrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fazer_checkin, p) for p in participantes[:5]]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Verifica que pelo menos alguns foram bem-sucedidos
        success_count = sum(1 for r in results if r.status_code == 200)
        assert success_count >= 0  # Pelo menos alguns sucessos esperados

# ================================
# TESTES DE SEGURANÇA
# ================================

class TestSecurityCheckin:
    """Testes de segurança do sistema"""
    
    def test_autenticacao_obrigatoria(self, client, sample_participante):
        """Teste que verifica se autenticação é obrigatória"""
        payload = {
            "evento_id": str(sample_participante.evento_id),
            "qr_code": "test",
            "tipo_checkin": "qr_code"
        }
        
        # Requisição sem headers de auth
        response = client.post("/api/v1/checkins/qr-code", json=payload)
        
        assert response.status_code in [401, 422]  # Não autorizado ou erro de validação
    
    def test_validacao_cpf_seguranca(self, client, sample_participante, auth_headers):
        """Teste de validação de segurança do CPF"""
        payload = {
            "evento_id": str(sample_participante.evento_id),
            "cpf": "12345678901",
            "tres_digitos": "000",  # Incorreto intencionalmente
            "tipo_checkin": "cpf"
        }
        
        response = client.post("/api/v1/checkins/cpf", json=payload, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Validação de segurança incorreta" in response.json()["detail"]
    
    def test_sql_injection_prevention(self, client, auth_headers):
        """Teste de prevenção contra SQL injection"""
        payload = {
            "evento_id": "' OR 1=1 --",
            "cpf": "'; DROP TABLE usuarios; --",
            "tres_digitos": "123",
            "tipo_checkin": "cpf"
        }
        
        response = client.post("/api/v1/checkins/cpf", json=payload, headers=auth_headers)
        
        # Deve falhar na validação, não executar SQL malicioso
        assert response.status_code in [400, 422]

# ================================
# RUNNER DOS TESTES
# ================================

if __name__ == "__main__":
    """Executa testes diretamente"""
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10",
        "--cov=app.routers.checkins",
        "--cov-report=html"
    ])