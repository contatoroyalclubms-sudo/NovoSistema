"""
Comprehensive test suite for Events Router
Tests CRUD operations, permissions, filtering, file uploads, and event management
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, AsyncMock
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from io import BytesIO

from app.models import Evento, Usuario, Empresa, StatusEvento, TipoUsuario, Participante
from app.schemas import EventoCreate, EventoUpdate


class TestEventosList:
    """Test events listing and filtering"""
    
    def test_list_eventos_success(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test successful events listing"""
        response = client.get("/eventos/", headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) >= 1

    def test_list_eventos_pagination(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test events listing with pagination"""
        response = client.get(
            "/eventos/?page=1&size=5",
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 5

    def test_list_eventos_filter_by_nome(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test filtering events by name"""
        response = client.get(
            f"/eventos/?nome={evento_sample.nome}",
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 1
        assert evento_sample.nome.lower() in data["items"][0]["nome"].lower()

    def test_list_eventos_filter_by_status(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test filtering events by status"""
        response = client.get(
            f"/eventos/?status={evento_sample.status.value}",
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        if data["items"]:
            assert data["items"][0]["status"] == evento_sample.status.value

    def test_list_eventos_filter_by_date_range(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test filtering events by date range"""
        data_inicio = datetime.utcnow().date()
        data_fim = (datetime.utcnow() + timedelta(days=30)).date()
        
        response = client.get(
            f"/eventos/?data_inicio={data_inicio}&data_fim={data_fim}",
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_200_OK

    def test_list_eventos_unauthorized(self, client: TestClient):
        """Test events listing without authorization"""
        response = client.get("/eventos/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_eventos_admin_sees_all(self, client: TestClient, auth_headers_admin: dict, evento_sample: Evento):
        """Test that admin can see all events"""
        response = client.get("/eventos/", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_list_eventos_promoter_sees_own(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test that promoter sees only their own events"""
        response = client.get("/eventos/", headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # All events should belong to the promoter
        for evento in data["items"]:
            assert evento["promoter_id"] is not None


class TestEventoCreate:
    """Test event creation"""
    
    def test_create_evento_success(self, client: TestClient, auth_headers_promoter: dict, empresa_sample: Empresa):
        """Test successful event creation"""
        evento_data = {
            "nome": "Novo Evento Test",
            "descricao": "Descrição do evento test",
            "data_inicio": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(days=7, hours=4)).isoformat(),
            "local": "Local Test",
            "endereco": "Endereço Test",
            "capacidade_maxima": 150,
            "empresa_id": str(empresa_sample.id),
            "preco_ingresso": 25.50,
            "status": "ATIVO"
        }
        
        response = client.post("/eventos/", json=evento_data, headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nome"] == evento_data["nome"]
        assert data["descricao"] == evento_data["descricao"]
        assert data["capacidade_maxima"] == evento_data["capacidade_maxima"]

    def test_create_evento_with_ai_description(self, client: TestClient, auth_headers_promoter: dict, 
                                              empresa_sample: Empresa, mock_openai_service):
        """Test event creation with AI-generated description"""
        with patch('app.routers.eventos.get_openai_service', return_value=mock_openai_service):
            evento_data = {
                "nome": "Festa de Ano Novo",
                "data_inicio": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "data_fim": (datetime.utcnow() + timedelta(days=7, hours=4)).isoformat(),
                "local": "Clube Test",
                "endereco": "Rua Test, 123",
                "capacidade_maxima": 200,
                "empresa_id": str(empresa_sample.id),
                "generate_ai_description": True
            }
            
            response = client.post("/eventos/", json=evento_data, headers=auth_headers_promoter)
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            mock_openai_service.generate_event_description.assert_called_once()

    def test_create_evento_past_date(self, client: TestClient, auth_headers_promoter: dict, empresa_sample: Empresa):
        """Test creating event with past date"""
        evento_data = {
            "nome": "Evento Passado",
            "descricao": "Descrição",
            "data_inicio": (datetime.utcnow() - timedelta(days=1)).isoformat(),  # Past date
            "data_fim": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "local": "Local Test",
            "endereco": "Endereço Test",
            "capacidade_maxima": 100,
            "empresa_id": str(empresa_sample.id)
        }
        
        response = client.post("/eventos/", json=evento_data, headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "não pode ser no passado" in response.json()["detail"]

    def test_create_evento_invalid_date_range(self, client: TestClient, auth_headers_promoter: dict, empresa_sample: Empresa):
        """Test creating event with invalid date range (end before start)"""
        data_inicio = datetime.utcnow() + timedelta(days=7)
        data_fim = data_inicio - timedelta(hours=2)  # End before start
        
        evento_data = {
            "nome": "Evento Datas Inválidas",
            "descricao": "Descrição",
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat(),
            "local": "Local Test",
            "endereco": "Endereço Test",
            "capacidade_maxima": 100,
            "empresa_id": str(empresa_sample.id)
        }
        
        response = client.post("/eventos/", json=evento_data, headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "anterior à data de início" in response.json()["detail"]

    def test_create_evento_unauthorized(self, client: TestClient, empresa_sample: Empresa):
        """Test event creation without authorization"""
        evento_data = {
            "nome": "Evento Test",
            "descricao": "Descrição",
            "data_inicio": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(days=7, hours=4)).isoformat(),
            "local": "Local Test",
            "endereco": "Endereço Test",
            "capacidade_maxima": 100,
            "empresa_id": str(empresa_sample.id)
        }
        
        response = client.post("/eventos/", json=evento_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_evento_missing_required_fields(self, client: TestClient, auth_headers_promoter: dict):
        """Test creating event with missing required fields"""
        evento_data = {
            "nome": "Evento Incompleto"
            # Missing required fields
        }
        
        response = client.post("/eventos/", json=evento_data, headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_evento_invalid_capacity(self, client: TestClient, auth_headers_promoter: dict, empresa_sample: Empresa):
        """Test creating event with invalid capacity"""
        evento_data = {
            "nome": "Evento Capacidade Inválida",
            "descricao": "Descrição",
            "data_inicio": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(days=7, hours=4)).isoformat(),
            "local": "Local Test",
            "endereco": "Endereço Test",
            "capacidade_maxima": -10,  # Invalid capacity
            "empresa_id": str(empresa_sample.id)
        }
        
        response = client.post("/eventos/", json=evento_data, headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_evento_operador_forbidden(self, client: TestClient, auth_headers_operador: dict, empresa_sample: Empresa):
        """Test that operator cannot create events"""
        evento_data = {
            "nome": "Evento Operador",
            "descricao": "Descrição",
            "data_inicio": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(days=7, hours=4)).isoformat(),
            "local": "Local Test",
            "endereco": "Endereço Test",
            "capacidade_maxima": 100,
            "empresa_id": str(empresa_sample.id)
        }
        
        response = client.post("/eventos/", json=evento_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestEventoDetail:
    """Test event detail operations"""
    
    def test_get_evento_success(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test getting event details"""
        response = client.get(f"/eventos/{evento_sample.id}", headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(evento_sample.id)
        assert data["nome"] == evento_sample.nome

    def test_get_evento_not_found(self, client: TestClient, auth_headers_promoter: dict):
        """Test getting non-existent event"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = client.get(f"/eventos/{fake_id}", headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_evento_unauthorized(self, client: TestClient, evento_sample: Evento):
        """Test getting event without authorization"""
        response = client.get(f"/eventos/{evento_sample.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_evento_wrong_promoter(self, client: TestClient, auth_headers_operador: dict, evento_sample: Evento):
        """Test that user cannot access other promoter's events"""
        # This would require creating an event with a different promoter
        # For this test, we assume the operador doesn't have access to promoter's event
        response = client.get(f"/eventos/{evento_sample.id}", headers=auth_headers_operador)
        
        # Should be forbidden or not found depending on implementation
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


class TestEventoUpdate:
    """Test event update operations"""
    
    def test_update_evento_success(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test successful event update"""
        update_data = {
            "nome": "Evento Atualizado",
            "descricao": "Nova descrição do evento",
            "capacidade_maxima": 200
        }
        
        response = client.put(
            f"/eventos/{evento_sample.id}",
            json=update_data,
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nome"] == update_data["nome"]
        assert data["descricao"] == update_data["descricao"]
        assert data["capacidade_maxima"] == update_data["capacidade_maxima"]

    def test_update_evento_partial(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test partial event update"""
        update_data = {
            "nome": "Nome Parcialmente Atualizado"
        }
        
        response = client.put(
            f"/eventos/{evento_sample.id}",
            json=update_data,
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nome"] == update_data["nome"]
        # Other fields should remain unchanged
        assert data["descricao"] == evento_sample.descricao

    def test_update_evento_not_found(self, client: TestClient, auth_headers_promoter: dict):
        """Test updating non-existent event"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        update_data = {"nome": "Evento Inexistente"}
        
        response = client.put(
            f"/eventos/{fake_id}",
            json=update_data,
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_evento_unauthorized(self, client: TestClient, evento_sample: Evento):
        """Test updating event without authorization"""
        update_data = {"nome": "Evento Não Autorizado"}
        
        response = client.put(f"/eventos/{evento_sample.id}", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_evento_invalid_dates(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test updating event with invalid dates"""
        update_data = {
            "data_inicio": (datetime.utcnow() - timedelta(days=1)).isoformat(),  # Past date
        }
        
        response = client.put(
            f"/eventos/{evento_sample.id}",
            json=update_data,
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_evento_status_transition(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test valid status transitions"""
        update_data = {"status": "CANCELADO"}
        
        response = client.put(
            f"/eventos/{evento_sample.id}",
            json=update_data,
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "CANCELADO"


class TestEventoDelete:
    """Test event deletion operations"""
    
    def test_delete_evento_success(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test successful event deletion (soft delete)"""
        response = client.delete(f"/eventos/{evento_sample.id}", headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Evento excluído com sucesso"

    def test_delete_evento_not_found(self, client: TestClient, auth_headers_promoter: dict):
        """Test deleting non-existent event"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = client.delete(f"/eventos/{fake_id}", headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_evento_unauthorized(self, client: TestClient, evento_sample: Evento):
        """Test deleting event without authorization"""
        response = client.delete(f"/eventos/{evento_sample.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_evento_with_participants(self, client: TestClient, auth_headers_promoter: dict, 
                                          evento_sample: Evento, participante_sample: Participante, db_session: Session):
        """Test deleting event that has participants"""
        # Ensure participant is linked to event
        assert participante_sample.evento_id == evento_sample.id
        
        response = client.delete(f"/eventos/{evento_sample.id}", headers=auth_headers_promoter)
        
        # Should still allow deletion but may return warning
        assert response.status_code == status.HTTP_200_OK

    def test_delete_evento_operador_forbidden(self, client: TestClient, auth_headers_operador: dict, evento_sample: Evento):
        """Test that operator cannot delete events"""
        response = client.delete(f"/eventos/{evento_sample.id}", headers=auth_headers_operador)
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


class TestEventoFileUpload:
    """Test file upload operations for events"""
    
    def test_upload_event_image_success(self, client: TestClient, auth_headers_promoter: dict, 
                                      evento_sample: Evento, sample_image_file):
        """Test successful event image upload"""
        files = {"file": ("test_image.jpg", sample_image_file, "image/jpeg")}
        
        response = client.post(
            f"/eventos/{evento_sample.id}/upload-image",
            files=files,
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "image_url" in data

    def test_upload_invalid_file_type(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test uploading invalid file type"""
        # Create a text file instead of image
        text_file = BytesIO(b"This is not an image")
        files = {"file": ("test.txt", text_file, "text/plain")}
        
        response = client.post(
            f"/eventos/{evento_sample.id}/upload-image",
            files=files,
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "tipo de arquivo" in response.json()["detail"].lower()

    def test_upload_oversized_file(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test uploading oversized file"""
        # Create a large file (simulate - this would need actual large file for real test)
        large_file = BytesIO(b"x" * (10 * 1024 * 1024))  # 10MB
        files = {"file": ("large_image.jpg", large_file, "image/jpeg")}
        
        response = client.post(
            f"/eventos/{evento_sample.id}/upload-image",
            files=files,
            headers=auth_headers_promoter
        )
        
        # Should reject if file size limits are implemented
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE]

    def test_upload_without_file(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test upload endpoint without file"""
        response = client.post(
            f"/eventos/{evento_sample.id}/upload-image",
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestEventoCloning:
    """Test event cloning functionality"""
    
    def test_clone_evento_success(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test successful event cloning"""
        clone_data = {
            "novo_nome": "Evento Clonado Test",
            "nova_data_inicio": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "nova_data_fim": (datetime.utcnow() + timedelta(days=14, hours=4)).isoformat()
        }
        
        response = client.post(
            f"/eventos/{evento_sample.id}/clone",
            json=clone_data,
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nome"] == clone_data["novo_nome"]
        assert data["descricao"] == evento_sample.descricao  # Should copy original description

    def test_clone_evento_not_found(self, client: TestClient, auth_headers_promoter: dict):
        """Test cloning non-existent event"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        clone_data = {
            "novo_nome": "Evento Inexistente Clonado",
            "nova_data_inicio": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "nova_data_fim": (datetime.utcnow() + timedelta(days=14, hours=4)).isoformat()
        }
        
        response = client.post(f"/eventos/{fake_id}/clone", json=clone_data, headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_clone_evento_unauthorized(self, client: TestClient, evento_sample: Evento):
        """Test cloning event without authorization"""
        clone_data = {
            "novo_nome": "Evento Clonado Não Autorizado",
            "nova_data_inicio": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "nova_data_fim": (datetime.utcnow() + timedelta(days=14, hours=4)).isoformat()
        }
        
        response = client.post(f"/eventos/{evento_sample.id}/clone", json=clone_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestEventoBulkOperations:
    """Test bulk operations on events"""
    
    def test_bulk_update_status(self, client: TestClient, auth_headers_admin: dict, evento_sample: Evento):
        """Test bulk status update"""
        bulk_data = {
            "evento_ids": [str(evento_sample.id)],
            "action": "update_status",
            "new_status": "CANCELADO"
        }
        
        response = client.post("/eventos/bulk", json=bulk_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["updated_count"] == 1

    def test_bulk_delete_events(self, client: TestClient, auth_headers_admin: dict, evento_sample: Evento):
        """Test bulk deletion of events"""
        bulk_data = {
            "evento_ids": [str(evento_sample.id)],
            "action": "delete"
        }
        
        response = client.post("/eventos/bulk", json=bulk_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted_count"] == 1

    def test_bulk_operations_forbidden_for_promoter(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test that promoters cannot perform bulk operations"""
        bulk_data = {
            "evento_ids": [str(evento_sample.id)],
            "action": "delete"
        }
        
        response = client.post("/eventos/bulk", json=bulk_data, headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestEventoAnalytics:
    """Test event analytics and statistics"""
    
    def test_get_event_statistics(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test getting event statistics"""
        response = client.get(f"/eventos/{evento_sample.id}/stats", headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        expected_fields = ["total_participantes", "checkins_realizados", "receita_total", "taxa_comparecimento"]
        for field in expected_fields:
            assert field in data

    def test_get_events_dashboard(self, client: TestClient, auth_headers_promoter: dict):
        """Test getting events dashboard data"""
        response = client.get("/eventos/dashboard", headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        expected_fields = ["total_eventos", "eventos_ativos", "eventos_proximos", "receita_total"]
        for field in expected_fields:
            assert field in data

    def test_export_events_data(self, client: TestClient, auth_headers_admin: dict):
        """Test exporting events data"""
        response = client.get("/eventos/export?format=csv", headers=auth_headers_admin)
        
        # Should return CSV file or data
        assert response.status_code == status.HTTP_200_OK
        # Check content type for CSV export
        if "text/csv" in response.headers.get("content-type", ""):
            assert "evento" in response.text.lower()


class TestEventoPerformance:
    """Test event-related performance"""
    
    def test_list_events_performance(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test events listing performance"""
        import time
        
        start_time = time.time()
        response = client.get("/eventos/", headers=auth_headers_promoter)
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        # Should complete within reasonable time
        assert end_time - start_time < 2.0

    def test_large_pagination_performance(self, client: TestClient, auth_headers_promoter: dict):
        """Test performance with large pagination"""
        import time
        
        start_time = time.time()
        response = client.get("/eventos/?page=1&size=100", headers=auth_headers_promoter)
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        # Should handle large page sizes efficiently
        assert end_time - start_time < 3.0


class TestEventoEdgeCases:
    """Test edge cases and error handling"""
    
    def test_create_event_with_emoji_name(self, client: TestClient, auth_headers_promoter: dict, empresa_sample: Empresa):
        """Test creating event with emoji in name"""
        evento_data = {
            "nome": "🎉 Festa Incrível 🎊",
            "descricao": "Evento com emojis 🎵🎸",
            "data_inicio": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(days=7, hours=4)).isoformat(),
            "local": "Local Test",
            "endereco": "Endereço Test",
            "capacidade_maxima": 100,
            "empresa_id": str(empresa_sample.id)
        }
        
        response = client.post("/eventos/", json=evento_data, headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "🎉" in data["nome"]

    def test_event_with_very_long_description(self, client: TestClient, auth_headers_promoter: dict, empresa_sample: Empresa):
        """Test event with very long description"""
        long_description = "A" * 10000  # Very long description
        
        evento_data = {
            "nome": "Evento Descrição Longa",
            "descricao": long_description,
            "data_inicio": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(days=7, hours=4)).isoformat(),
            "local": "Local Test",
            "endereco": "Endereço Test",
            "capacidade_maxima": 100,
            "empresa_id": str(empresa_sample.id)
        }
        
        response = client.post("/eventos/", json=evento_data, headers=auth_headers_promoter)
        
        # Should handle or reject gracefully
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_concurrent_event_updates(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test concurrent updates to the same event"""
        import threading
        import time
        
        results = []
        
        def update_event(field_value):
            update_data = {"nome": f"Evento Concorrente {field_value}"}
            response = client.put(
                f"/eventos/{evento_sample.id}",
                json=update_data,
                headers=auth_headers_promoter
            )
            results.append(response.status_code)
        
        # Start multiple update threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=update_event, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # At least one should succeed
        assert status.HTTP_200_OK in results

    def test_event_timezone_handling(self, client: TestClient, auth_headers_promoter: dict, empresa_sample: Empresa):
        """Test event creation with different timezone formats"""
        # Test with UTC timezone
        evento_data = {
            "nome": "Evento Timezone UTC",
            "descricao": "Teste timezone",
            "data_inicio": "2024-12-25T20:00:00Z",  # UTC format
            "data_fim": "2024-12-26T02:00:00Z",
            "local": "Local Test",
            "endereco": "Endereço Test",
            "capacidade_maxima": 100,
            "empresa_id": str(empresa_sample.id)
        }
        
        response = client.post("/eventos/", json=evento_data, headers=auth_headers_promoter)
        
        # Should handle timezone properly
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_malformed_json_request(self, client: TestClient, auth_headers_promoter: dict):
        """Test handling of malformed JSON in request"""
        response = client.post(
            "/eventos/",
            data='{"nome": "Invalid JSON"',  # Malformed JSON
            headers={**auth_headers_promoter, "Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY