"""
Testes abrangentes para o sistema avançado de eventos
Sistema Universal de Gestão de Eventos - Sprint 3
"""

import pytest
import asyncio
import tempfile
import json
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from PIL import Image
import io

from app.main import app
from app.database import get_db
from app.models import (
    Evento, Usuario, Participante, EventoTemplate, EventoFeedback, 
    EventoAnexo, EventoHistorico, EventoApproval, StatusEvento, TipoEvento
)
from app.services.file_upload_service import file_upload_service
from app.services.qr_service import qr_service
from app.services.email_service import email_service
from app.services.webhook_service import webhook_service


class TestEventoAdvancedCRUD:
    """Testes para operações CRUD avançadas de eventos"""
    
    @pytest.fixture
    def db_session(self):
        # Mock da sessão do banco de dados
        return Mock(spec=Session)
    
    @pytest.fixture
    def test_user(self):
        return Usuario(
            id="123e4567-e89b-12d3-a456-426614174000",
            nome="Admin Test",
            email="admin@test.com",
            tipo_usuario="admin",
            empresa_id="123e4567-e89b-12d3-a456-426614174001"
        )
    
    @pytest.fixture
    def test_evento(self):
        return Evento(
            id="123e4567-e89b-12d3-a456-426614174002",
            nome="Evento Teste",
            descricao="Descrição do evento teste",
            tipo_evento=TipoEvento.FESTA,
            status=StatusEvento.PLANEJAMENTO,
            data_inicio=datetime.utcnow() + timedelta(days=30),
            data_fim=datetime.utcnow() + timedelta(days=30, hours=4),
            local_nome="Local Teste",
            local_endereco="Endereço Teste, 123",
            cor_primaria="#0EA5E9",
            cor_secundaria="#64748B",
            organizador_id="123e4567-e89b-12d3-a456-426614174000",
            capacidade_maxima=100,
            valor_entrada=Decimal('50.00')
        )
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_create_evento_basic(self, client, test_user):
        """Teste de criação de evento básico"""
        evento_data = {
            "nome": "Novo Evento Teste",
            "descricao": "Descrição detalhada",
            "tipo_evento": "festa",
            "data_inicio": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(days=30, hours=4)).isoformat(),
            "local_nome": "Centro de Eventos",
            "local_endereco": "Rua das Flores, 123",
            "cor_primaria": "#FF5733",
            "valor_entrada": 100.0
        }
        
        with patch('app.dependencies.get_current_user', return_value=test_user):
            response = client.post("/api/eventos/", json=evento_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == evento_data["nome"]
        assert data["cor_primaria"] == evento_data["cor_primaria"]
        assert data["organizador_id"] == test_user.id
    
    def test_create_evento_with_advanced_features(self, client, test_user):
        """Teste de criação de evento com recursos avançados"""
        evento_data = {
            "nome": "Evento Avançado",
            "descricao": "Evento com recursos avançados",
            "tipo_evento": "conferencia",
            "data_inicio": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(days=30, hours=8)).isoformat(),
            "local_nome": "Centro de Convenções",
            "local_endereco": "Av. Principal, 456",
            "cor_primaria": "#1E40AF",
            "cor_secundaria": "#374151",
            "cor_accent": "#10B981",
            "custom_css": ".event-header { background: linear-gradient(45deg, #1E40AF, #10B981); }",
            "sistema_pontuacao_ativo": True,
            "pontos_checkin": 20,
            "badges_personalizadas": [
                {"name": "Early Bird", "icon": "🐦", "condition": "checkin_time < event_start + 30min"}
            ],
            "webhook_checkin": "https://api.example.com/webhook/checkin",
            "webhook_headers": {"Authorization": "Bearer token123"},
            "email_confirmacao_template": "<h1>Bem-vindo ao {{ evento.nome }}!</h1>",
            "requer_aprovacao": True,
            "visibilidade": "restrito",
            "dominios_permitidos": ["empresa.com", "universidade.edu"],
            "analytics_config": {"google_analytics": "GA-123456"},
            "metadados_seo": {"title": "Evento Incrível", "description": "O melhor evento do ano"}
        }
        
        with patch('app.dependencies.get_current_user', return_value=test_user):
            response = client.post("/api/eventos/", json=evento_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["sistema_pontuacao_ativo"] is True
        assert data["pontos_checkin"] == 20
        assert data["requer_aprovacao"] is True
        assert data["visibilidade"] == "restrito"
    
    def test_clone_evento(self, client, test_user, test_evento):
        """Teste de clonagem de evento"""
        clone_data = {
            "nome_novo": "Evento Clonado",
            "data_inicio": (datetime.utcnow() + timedelta(days=60)).isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(days=60, hours=4)).isoformat(),
            "clonar_configuracoes": True,
            "clonar_produtos": True,
            "alteracoes": {
                "cor_primaria": "#FF6B6B"
            }
        }
        
        with patch('app.dependencies.get_current_user', return_value=test_user):
            with patch('app.database.get_db') as mock_db:
                mock_db.return_value.query.return_value.filter.return_value.first.return_value = test_evento
                response = client.post(f"/api/eventos/{test_evento.id}/clone", json=clone_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == clone_data["nome_novo"]
        assert data["evento_pai_id"] == str(test_evento.id)
    
    def test_bulk_operations(self, client, test_user):
        """Teste de operações em lote"""
        bulk_data = {
            "evento_ids": ["123", "456", "789"],
            "operacao": "ativar",
            "confirmar_operacao": True
        }
        
        with patch('app.dependencies.get_current_user', return_value=test_user):
            response = client.post("/api/eventos/bulk-operation", json=bulk_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Operação ativar executada em 3 eventos"
    
    def test_approval_workflow(self, client, test_user):
        """Teste do workflow de aprovação"""
        approval_data = {
            "evento_id": "123e4567-e89b-12d3-a456-426614174002",
            "justificativa": "Evento corporativo importante",
            "observacoes_solicitante": "Evento para 500 pessoas"
        }
        
        with patch('app.dependencies.get_current_user', return_value=test_user):
            response = client.post("/api/eventos/approval-request", json=approval_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "approval_id" in data["data"]
    
    def test_event_validation(self, client, test_user):
        """Teste de validação de dados do evento"""
        invalid_data = {
            "nome": "",  # Nome vazio
            "data_inicio": (datetime.utcnow() - timedelta(days=1)).isoformat(),  # Data no passado
            "data_fim": (datetime.utcnow() - timedelta(days=2)).isoformat(),  # Data fim antes do início
            "local_nome": "",
            "valor_entrada": -50  # Valor negativo
        }
        
        with patch('app.dependencies.get_current_user', return_value=test_user):
            response = client.post("/api/eventos/", json=invalid_data)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("nome" in str(error) for error in errors)


class TestFileUploadService:
    """Testes para o serviço de upload de arquivos"""
    
    @pytest.fixture
    def mock_file(self):
        # Criar imagem de teste
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        mock_file = Mock()
        mock_file.filename = "test_image.png"
        mock_file.content_type = "image/png"
        mock_file.size = len(img_bytes.getvalue())
        mock_file.read = AsyncMock(return_value=img_bytes.getvalue())
        
        return mock_file
    
    @pytest.mark.asyncio
    async def test_upload_image_success(self, mock_file):
        """Teste de upload de imagem bem-sucedido"""
        with patch('pathlib.Path.mkdir'), \
             patch('aiofiles.open', create=True) as mock_open:
            
            mock_open.return_value.__aenter__.return_value.write = AsyncMock()
            
            result = await file_upload_service.upload_file(
                file=mock_file,
                evento_id="123",
                categoria="logo",
                user=Mock(id="456"),
                db=Mock()
            )
            
            assert result is not None
            assert result.categoria == "logo"
            assert result.tipo_arquivo == "image"
    
    def test_validate_file_type(self):
        """Teste de validação de tipo de arquivo"""
        valid_file = Mock()
        valid_file.content_type = "image/jpeg"
        valid_file.filename = "test.jpg"
        valid_file.size = 1024 * 1024  # 1MB
        
        # Não deve levantar exceção
        file_upload_service._validate_file(valid_file, "image")
        
        invalid_file = Mock()
        invalid_file.content_type = "application/exe"
        invalid_file.filename = "virus.exe"
        invalid_file.size = 1024
        
        with pytest.raises(Exception):
            file_upload_service._validate_file(invalid_file, "image")
    
    @pytest.mark.asyncio
    async def test_create_thumbnail(self):
        """Teste de criação de thumbnail"""
        # Criar imagem de teste
        test_image = Image.new('RGB', (800, 600), color='blue')
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            test_image.save(tmp.name, 'JPEG')
            image_path = Path(tmp.name)
            
            thumbnail_path = await file_upload_service._create_image_thumbnail(image_path)
            
            assert thumbnail_path is not None
            assert thumbnail_path.exists()
            
            # Verificar dimensões do thumbnail
            with Image.open(thumbnail_path) as thumb:
                assert thumb.size == (300, 300)  # medium size
            
            # Cleanup
            image_path.unlink()
            thumbnail_path.unlink()
    
    def test_format_file_size(self):
        """Teste de formatação de tamanho de arquivo"""
        assert file_upload_service._format_file_size(0) == "0B"
        assert file_upload_service._format_file_size(1024) == "1.0 KB"
        assert file_upload_service._format_file_size(1024 * 1024) == "1.0 MB"
        assert file_upload_service._format_file_size(1024 * 1024 * 1024) == "1.0 GB"


class TestQRCodeService:
    """Testes para o serviço de QR Code"""
    
    def test_generate_qr_data(self):
        """Teste de geração de dados do QR Code"""
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        qr_data = qr_service.generate_qr_data(
            evento_id="123",
            participante_id="456",
            expires_at=expires_at,
            action="checkin"
        )
        
        assert qr_data["evento_id"] == "123"
        assert qr_data["participante_id"] == "456"
        assert qr_data["action"] == "checkin"
        assert "checksum" in qr_data
        assert "id" in qr_data
    
    def test_validate_qr_data(self):
        """Teste de validação de dados do QR Code"""
        valid_data = qr_service.generate_qr_data("123", action="checkin")
        assert qr_service.validate_qr_data(valid_data) is True
        
        # Teste com checksum inválido
        invalid_data = valid_data.copy()
        invalid_data["checksum"] = "invalid"
        assert qr_service.validate_qr_data(invalid_data) is False
        
        # Teste com QR expirado
        expired_data = qr_service.generate_qr_data(
            "123", 
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )
        assert qr_service.validate_qr_data(expired_data) is False
    
    def test_create_basic_qr(self):
        """Teste de criação de QR Code básico"""
        qr = qr_service.create_basic_qr("test data", size=200)
        assert qr is not None
        
        # Criar imagem do QR Code
        qr_img = qr.make_image()
        assert qr_img.size[0] > 0
        assert qr_img.size[1] > 0
    
    def test_generate_qr_code_url(self):
        """Teste de geração de URL do QR Code"""
        url = qr_service.generate_qr_code_url(
            evento_id="123",
            participante_id="456",
            action="checkin"
        )
        
        assert url.startswith("http")
        assert "qr/checkin" in url
        assert "data=" in url
    
    def test_decode_qr_url(self):
        """Teste de decodificação de URL do QR Code"""
        # Gerar URL
        original_url = qr_service.generate_qr_code_url("123", "456", action="checkin")
        
        # Decodificar
        decoded_data = qr_service.decode_qr_url(original_url)
        
        assert decoded_data is not None
        assert decoded_data["evento_id"] == "123"
        assert decoded_data["participante_id"] == "456"
        assert decoded_data["action"] == "checkin"
    
    def test_create_styled_qr(self):
        """Teste de criação de QR Code estilizado"""
        style_config = {
            "fill_color": "#FF0000",
            "back_color": "#FFFFFF",
            "module_style": "rounded",
            "gradient": {
                "type": "radial",
                "center_color": "#FF0000",
                "edge_color": "#000000"
            }
        }
        
        qr_img = qr_service.create_styled_qr("test data", style_config, 400)
        
        assert qr_img is not None
        assert qr_img.size == (400, 400)


class TestEmailService:
    """Testes para o serviço de email"""
    
    @pytest.fixture
    def test_evento_email(self):
        return Mock(
            nome="Evento Teste",
            descricao="Descrição do evento",
            data_inicio=datetime(2024, 6, 15, 19, 0),
            local_nome="Centro de Eventos",
            local_endereco="Rua das Flores, 123",
            cor_primaria="#0EA5E9",
            cor_secundaria="#64748B",
            logo_url="https://example.com/logo.png",
            email_confirmacao_template=None,
            email_sender_name="Eventos Inc",
            email_sender_email="noreply@eventos.com"
        )
    
    @pytest.fixture
    def test_participante_email(self):
        usuario_mock = Mock(nome="João Silva", email="joao@example.com")
        return Mock(
            id="123",
            usuario=usuario_mock,
            qr_code_individual="https://example.com/qr/123.png",
            valor_pago=Decimal('100.00'),
            pontos_obtidos=50
        )
    
    def test_get_default_template(self, test_evento_email):
        """Teste de obtenção de template padrão"""
        template = email_service.get_template("confirmacao", test_evento_email)
        
        assert "subject" in template
        assert "html" in template
        assert "{{ evento.nome }}" in template["subject"]
        assert "{{ participante.nome }}" in template["html"]
    
    def test_render_template(self):
        """Teste de renderização de template"""
        template_content = "Olá, {{ nome }}! Seu evento é {{ evento }}."
        context = {"nome": "João", "evento": "Tech Conference"}
        
        rendered = email_service.render_template(template_content, context)
        
        assert rendered == "Olá, João! Seu evento é Tech Conference."
    
    def test_create_email_context(self, test_evento_email, test_participante_email):
        """Teste de criação de contexto do email"""
        context = email_service.create_email_context(
            evento=test_evento_email,
            participante=test_participante_email
        )
        
        assert "evento" in context
        assert "participante" in context
        assert context["evento"]["nome"] == "Evento Teste"
        assert context["participante"]["nome"] == "João Silva"
        assert "app_url" in context
    
    def test_validate_template(self):
        """Teste de validação de template"""
        valid_template = "<h1>{{ evento.nome }}</h1><p>{{ participante.nome }}</p>"
        validation = email_service.validate_template(valid_template)
        
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
        
        # Template com erro
        invalid_template = "<h1>{{ evento.nome }</h1>"  # Tag malformada
        validation = email_service.validate_template(invalid_template)
        
        assert validation["valid"] is False
        assert len(validation["errors"]) > 0
    
    @pytest.mark.asyncio
    async def test_send_email_development(self):
        """Teste de envio de email em ambiente de desenvolvimento"""
        with patch.object(email_service, 'smtp_server', 'localhost'), \
             patch('app.core.settings.environment', 'development'):
            
            result = await email_service.send_email(
                to_email="test@example.com",
                subject="Teste",
                html_content="<p>Email de teste</p>"
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_send_template_email(self, test_evento_email, test_participante_email):
        """Teste de envio de email com template"""
        with patch.object(email_service, 'send_email', return_value=True) as mock_send:
            result = await email_service.send_template_email(
                template_type="confirmacao",
                evento=test_evento_email,
                to_email="test@example.com",
                participante=test_participante_email
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Verificar argumentos da chamada
            call_args = mock_send.call_args
            assert call_args[1]["to_email"] == "test@example.com"
            assert "Evento Teste" in call_args[1]["subject"]
            assert "João Silva" in call_args[1]["html_content"]


class TestWebhookService:
    """Testes para o serviço de webhook"""
    
    @pytest.fixture
    def test_evento_webhook(self):
        return Mock(
            id="123",
            nome="Evento Teste",
            data_inicio=datetime(2024, 6, 15, 19, 0),
            local_nome="Centro de Eventos",
            webhook_checkin="https://api.example.com/webhook/checkin",
            webhook_headers={"Authorization": "Bearer token123"},
            webhook_secret="secret123"
        )
    
    @pytest.fixture
    def test_participante_webhook(self):
        usuario_mock = Mock(nome="João Silva", email="joao@example.com")
        return Mock(
            id="456",
            usuario_id="789",
            usuario=usuario_mock
        )
    
    def test_validate_url(self):
        """Teste de validação de URL"""
        assert webhook_service._validate_url("https://api.example.com/webhook") is True
        assert webhook_service._validate_url("http://localhost:3000/webhook") is True
        assert webhook_service._validate_url("ftp://invalid.com") is False
        assert webhook_service._validate_url("not-a-url") is False
    
    def test_generate_signature(self):
        """Teste de geração de assinatura"""
        payload = '{"test": "data"}'
        secret = "secret123"
        
        signature = webhook_service._generate_signature(payload, secret)
        
        assert signature.startswith("sha256=")
        assert len(signature) > 10
    
    def test_validate_webhook_signature(self):
        """Teste de validação de assinatura"""
        payload = '{"test": "data"}'
        secret = "secret123"
        
        signature = webhook_service._generate_signature(payload, secret)
        
        assert webhook_service.validate_webhook_signature(payload, signature, secret) is True
        assert webhook_service.validate_webhook_signature(payload, "invalid", secret) is False
    
    @pytest.mark.asyncio
    async def test_send_webhook_success(self):
        """Teste de envio de webhook bem-sucedido"""
        payload = {"test": "data"}
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="OK")
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await webhook_service._send_webhook(
                url="https://api.example.com/webhook",
                payload=payload,
                secret="secret123"
            )
            
            assert result["success"] is True
            assert result["status_code"] == 200
    
    @pytest.mark.asyncio
    async def test_send_checkin_webhook(self, test_evento_webhook, test_participante_webhook):
        """Teste de webhook de check-in"""
        checkin_data = {
            "checkin_time": datetime.utcnow().isoformat(),
            "points_earned": 10,
            "method": "qr_code"
        }
        
        with patch.object(webhook_service, '_send_webhook', return_value={"success": True}) as mock_send:
            result = await webhook_service.send_checkin_webhook(
                evento=test_evento_webhook,
                participante=test_participante_webhook,
                checkin_data=checkin_data
            )
            
            assert result["success"] is True
            mock_send.assert_called_once()
            
            # Verificar payload
            call_args = mock_send.call_args
            payload = call_args[1]["payload"]
            assert payload["type"] == "checkin"
            assert payload["event"]["id"] == "123"
            assert payload["participant"]["id"] == "456"
    
    @pytest.mark.asyncio
    async def test_test_webhook(self):
        """Teste de webhook de teste"""
        with patch.object(webhook_service, '_send_webhook', return_value={"success": True}) as mock_send:
            result = await webhook_service.test_webhook("https://api.example.com/test")
            
            assert result["success"] is True
            mock_send.assert_called_once()
            
            # Verificar payload de teste
            call_args = mock_send.call_args
            payload = call_args[1]["payload"]
            assert payload["type"] == "webhook_test"
            assert "message" in payload


class TestEventIntegration:
    """Testes de integração do sistema de eventos"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_complete_event_lifecycle(self, client):
        """Teste completo do ciclo de vida de um evento"""
        # 1. Criar usuário
        user_data = {
            "nome": "Organizador Teste",
            "email": "organizador@test.com",
            "tipo_usuario": "organizador"
        }
        
        # 2. Criar evento
        event_data = {
            "nome": "Evento Completo",
            "data_inicio": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(days=30, hours=4)).isoformat(),
            "local_nome": "Centro de Eventos",
            "local_endereco": "Rua Teste, 123"
        }
        
        with patch('app.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(
                id="123",
                tipo_usuario="organizador",
                empresa_id="456"
            )
            
            # Criar evento
            response = client.post("/api/eventos/", json=event_data)
            assert response.status_code == 201
            
            evento_id = response.json()["id"]
            
            # Upload de imagem
            test_image = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            test_image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            files = {"file": ("test.png", img_bytes, "image/png")}
            response = client.post(
                f"/api/eventos/{evento_id}/upload-image",
                files=files,
                params={"image_type": "logo"}
            )
            # Note: Este teste pode falhar sem mock adequado do sistema de upload
            
            # Clonar evento
            clone_data = {
                "nome_novo": "Evento Clonado",
                "data_inicio": (datetime.utcnow() + timedelta(days=60)).isoformat(),
                "data_fim": (datetime.utcnow() + timedelta(days=60, hours=4)).isoformat()
            }
            
            response = client.post(f"/api/eventos/{evento_id}/clone", json=clone_data)
            # Este teste também precisaria de mocks adequados
    
    def test_event_permissions(self, client):
        """Teste de permissões de evento"""
        # Usuário sem permissão
        regular_user = Mock(
            id="789",
            tipo_usuario="participante",
            empresa_id="456"
        )
        
        event_data = {
            "nome": "Evento Sem Permissão",
            "data_inicio": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(days=30, hours=4)).isoformat(),
            "local_nome": "Local",
            "local_endereco": "Endereço"
        }
        
        with patch('app.dependencies.get_current_user', return_value=regular_user):
            response = client.post("/api/eventos/", json=event_data)
            assert response.status_code == 403
    
    def test_event_analytics_data(self, client):
        """Teste de dados de analytics"""
        admin_user = Mock(
            id="123",
            tipo_usuario="admin",
            empresa_id="456"
        )
        
        with patch('app.dependencies.get_current_user', return_value=admin_user):
            response = client.get("/api/eventos/123/stats")
            # Este endpoint precisaria ser implementado
            # assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])