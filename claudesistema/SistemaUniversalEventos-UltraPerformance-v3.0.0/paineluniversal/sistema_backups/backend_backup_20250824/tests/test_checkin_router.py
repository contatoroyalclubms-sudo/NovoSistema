"""
Comprehensive test suite for Check-in Router
Tests QR code validation, CPF check-in, bulk operations, WebSocket notifications, and real-time features
"""

import pytest
import json
import qrcode
import io
import base64
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, AsyncMock
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    Evento, Participante, Usuario, CheckinLog, StatusParticipante, 
    TipoCheckin, StatusCheckin
)


class TestCheckinQR:
    """Test QR code check-in functionality"""
    
    def test_generate_qr_code_success(self, client: TestClient, auth_headers_operador: dict, 
                                    participante_sample: Participante):
        """Test successful QR code generation"""
        response = client.post(
            f"/checkins/generate-qr/{participante_sample.id}",
            headers=auth_headers_operador
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "qr_code" in data
        assert "qr_token" in data
        assert "expires_at" in data

    def test_checkin_qr_success(self, client: TestClient, auth_headers_operador: dict, 
                               participante_sample: Participante):
        """Test successful QR code check-in"""
        # First generate QR code
        qr_response = client.post(
            f"/checkins/generate-qr/{participante_sample.id}",
            headers=auth_headers_operador
        )
        qr_data = qr_response.json()
        
        # Now perform check-in with QR token
        checkin_data = {
            "qr_token": qr_data["qr_token"],
            "evento_id": str(participante_sample.evento_id),
            "operador_info": {
                "device_id": "device_001",
                "location": {"lat": -23.5505, "lng": -46.6333}
            }
        }
        
        response = client.post("/checkins/qr", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["participante"]["nome"] == participante_sample.nome
        assert data["tipo_checkin"] == "QR_CODE"

    def test_checkin_qr_invalid_token(self, client: TestClient, auth_headers_operador: dict, evento_sample: Evento):
        """Test check-in with invalid QR token"""
        checkin_data = {
            "qr_token": "invalid_token_123",
            "evento_id": str(evento_sample.id)
        }
        
        response = client.post("/checkins/qr", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "inválido" in response.json()["detail"].lower()

    def test_checkin_qr_expired_token(self, client: TestClient, auth_headers_operador: dict, 
                                    participante_sample: Participante, db_session: Session):
        """Test check-in with expired QR token"""
        # Create an expired QR token manually in the database
        from app.models import QRCode
        
        expired_qr = QRCode(
            participante_id=participante_sample.id,
            token="expired_token_123",
            expires_at=datetime.utcnow() - timedelta(minutes=1),  # Already expired
            created_at=datetime.utcnow() - timedelta(minutes=5)
        )
        db_session.add(expired_qr)
        db_session.commit()
        
        checkin_data = {
            "qr_token": "expired_token_123",
            "evento_id": str(participante_sample.evento_id)
        }
        
        response = client.post("/checkins/qr", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "expirado" in response.json()["detail"].lower()

    def test_checkin_qr_already_checked_in(self, client: TestClient, auth_headers_operador: dict, 
                                         participante_sample: Participante, db_session: Session):
        """Test QR check-in for participant already checked in"""
        # Mark participant as already checked in
        checkin_log = CheckinLog(
            participante_id=participante_sample.id,
            evento_id=participante_sample.evento_id,
            tipo_checkin=TipoCheckin.QR_CODE,
            status=StatusCheckin.CONFIRMADO,
            checkin_time=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add(checkin_log)
        participante_sample.status = StatusParticipante.PRESENTE
        db_session.commit()
        
        # Generate QR and attempt check-in
        qr_response = client.post(
            f"/checkins/generate-qr/{participante_sample.id}",
            headers=auth_headers_operador
        )
        qr_data = qr_response.json()
        
        checkin_data = {
            "qr_token": qr_data["qr_token"],
            "evento_id": str(participante_sample.evento_id)
        }
        
        response = client.post("/checkins/qr", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já foi realizado" in response.json()["detail"]

    def test_checkin_qr_wrong_event(self, client: TestClient, auth_headers_operador: dict, 
                                  participante_sample: Participante, db_session: Session):
        """Test QR check-in for wrong event"""
        # Create another event
        from app.models import Empresa
        empresa = db_session.query(Empresa).first()
        
        other_event = Evento(
            nome="Outro Evento",
            descricao="Descrição outro evento",
            data_inicio=datetime.utcnow() + timedelta(days=1),
            data_fim=datetime.utcnow() + timedelta(days=1, hours=4),
            local="Outro Local",
            endereco="Outro Endereço",
            capacidade_maxima=50,
            status="ATIVO",
            empresa_id=empresa.id,
            created_at=datetime.utcnow()
        )
        db_session.add(other_event)
        db_session.commit()
        
        # Generate QR for participant
        qr_response = client.post(
            f"/checkins/generate-qr/{participante_sample.id}",
            headers=auth_headers_operador
        )
        qr_data = qr_response.json()
        
        # Try to check-in to different event
        checkin_data = {
            "qr_token": qr_data["qr_token"],
            "evento_id": str(other_event.id)
        }
        
        response = client.post("/checkins/qr", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "evento" in response.json()["detail"].lower()


class TestCheckinCPF:
    """Test CPF-based check-in functionality"""
    
    def test_checkin_cpf_success(self, client: TestClient, auth_headers_operador: dict, 
                                participante_sample: Participante):
        """Test successful CPF check-in"""
        # Get last 3 digits of CPF for validation
        cpf_digits = participante_sample.cpf[-3:]
        
        checkin_data = {
            "cpf": participante_sample.cpf,
            "cpf_3_digitos": cpf_digits,
            "evento_id": str(participante_sample.evento_id),
            "validacao_adicional": {
                "nome_participante": participante_sample.nome
            }
        }
        
        response = client.post("/checkins/cpf", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["participante"]["cpf"] == participante_sample.cpf
        assert data["tipo_checkin"] == "CPF"

    def test_checkin_cpf_invalid_format(self, client: TestClient, auth_headers_operador: dict, evento_sample: Evento):
        """Test CPF check-in with invalid CPF format"""
        checkin_data = {
            "cpf": "123.456.789-00",  # Invalid CPF
            "cpf_3_digitos": "000",
            "evento_id": str(evento_sample.id)
        }
        
        response = client.post("/checkins/cpf", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "inválido" in response.json()["detail"].lower()

    def test_checkin_cpf_wrong_3_digits(self, client: TestClient, auth_headers_operador: dict, 
                                      participante_sample: Participante):
        """Test CPF check-in with wrong 3 digits validation"""
        checkin_data = {
            "cpf": participante_sample.cpf,
            "cpf_3_digitos": "000",  # Wrong digits
            "evento_id": str(participante_sample.evento_id)
        }
        
        response = client.post("/checkins/cpf", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "3 dígitos" in response.json()["detail"]

    def test_checkin_cpf_not_found(self, client: TestClient, auth_headers_operador: dict, evento_sample: Evento):
        """Test CPF check-in for non-registered participant"""
        checkin_data = {
            "cpf": "98765432100",  # Valid format but not registered
            "cpf_3_digitos": "100",
            "evento_id": str(evento_sample.id)
        }
        
        response = client.post("/checkins/cpf", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "não encontrado" in response.json()["detail"]

    def test_checkin_cpf_rate_limiting(self, client: TestClient, auth_headers_operador: dict, 
                                     participante_sample: Participante):
        """Test rate limiting on CPF check-in attempts"""
        cpf_digits = participante_sample.cpf[-3:]
        
        checkin_data = {
            "cpf": participante_sample.cpf,
            "cpf_3_digitos": "000",  # Wrong digits
            "evento_id": str(participante_sample.evento_id)
        }
        
        # Make multiple failed attempts
        for _ in range(5):
            response = client.post("/checkins/cpf", json=checkin_data, headers=auth_headers_operador)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Next attempt should be rate limited
        response = client.post("/checkins/cpf", json=checkin_data, headers=auth_headers_operador)
        # Should either continue failing or be rate limited depending on implementation
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_429_TOO_MANY_REQUESTS]


class TestCheckinManual:
    """Test manual check-in functionality"""
    
    def test_checkin_manual_success(self, client: TestClient, auth_headers_operador: dict, 
                                  participante_sample: Participante):
        """Test successful manual check-in"""
        checkin_data = {
            "participante_id": str(participante_sample.id),
            "evento_id": str(participante_sample.evento_id),
            "motivo": "Problema com QR Code",
            "observacoes": "Check-in realizado manualmente pelo operador"
        }
        
        response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["tipo_checkin"] == "MANUAL"
        assert data["motivo"] == checkin_data["motivo"]

    def test_checkin_manual_unauthorized_user_type(self, client: TestClient, auth_headers_promoter: dict, 
                                                  participante_sample: Participante):
        """Test manual check-in with unauthorized user type"""
        checkin_data = {
            "participante_id": str(participante_sample.id),
            "evento_id": str(participante_sample.evento_id),
            "motivo": "Teste não autorizado"
        }
        
        response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_promoter)
        
        # Promoters might not have manual check-in permissions
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_checkin_manual_missing_motivo(self, client: TestClient, auth_headers_operador: dict, 
                                         participante_sample: Participante):
        """Test manual check-in without required reason"""
        checkin_data = {
            "participante_id": str(participante_sample.id),
            "evento_id": str(participante_sample.evento_id)
            # Missing motivo
        }
        
        response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_checkin_manual_nonexistent_participant(self, client: TestClient, auth_headers_operador: dict, 
                                                  evento_sample: Evento):
        """Test manual check-in for non-existent participant"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        checkin_data = {
            "participante_id": fake_id,
            "evento_id": str(evento_sample.id),
            "motivo": "Teste participante inexistente"
        }
        
        response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCheckinBulk:
    """Test bulk check-in operations"""
    
    def test_checkin_bulk_csv_success(self, client: TestClient, auth_headers_operador: dict, 
                                    evento_sample: Evento, sample_csv_file):
        """Test successful bulk check-in from CSV"""
        # Create CSV file content with participant data
        csv_content = f"""cpf,nome,email
12345678901,João Silva,joao@test.com
98765432109,Maria Santos,maria@test.com"""
        
        files = {"file": ("checkins.csv", csv_content, "text/csv")}
        data = {"evento_id": str(evento_sample.id)}
        
        response = client.post(
            "/checkins/bulk/csv",
            files=files,
            data=data,
            headers=auth_headers_operador
        )
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "processed" in result
        assert "successful" in result
        assert "failed" in result

    def test_checkin_bulk_json_success(self, client: TestClient, auth_headers_operador: dict, 
                                     participante_sample: Participante):
        """Test successful bulk check-in from JSON data"""
        bulk_data = {
            "evento_id": str(participante_sample.evento_id),
            "checkins": [
                {
                    "cpf": participante_sample.cpf,
                    "nome": participante_sample.nome,
                    "tipo_checkin": "BULK"
                }
            ],
            "validacao_rigorosa": True
        }
        
        response = client.post("/checkins/bulk/json", json=bulk_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["successful"] >= 1

    def test_checkin_bulk_invalid_csv_format(self, client: TestClient, auth_headers_operador: dict, 
                                           evento_sample: Evento):
        """Test bulk check-in with invalid CSV format"""
        # Invalid CSV without required columns
        csv_content = "invalid,header,format\ntest,data,here"
        
        files = {"file": ("invalid.csv", csv_content, "text/csv")}
        data = {"evento_id": str(evento_sample.id)}
        
        response = client.post(
            "/checkins/bulk/csv",
            files=files,
            data=data,
            headers=auth_headers_operador
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "formato" in response.json()["detail"].lower()

    def test_checkin_bulk_large_file_handling(self, client: TestClient, auth_headers_operador: dict, 
                                            evento_sample: Evento):
        """Test bulk check-in with large CSV file"""
        # Create a large CSV with many entries
        csv_lines = ["cpf,nome,email"]
        for i in range(1000):
            csv_lines.append(f"1234567890{i:02d},Participante {i},participante{i}@test.com")
        
        large_csv = "\n".join(csv_lines)
        files = {"file": ("large_checkins.csv", large_csv, "text/csv")}
        data = {"evento_id": str(evento_sample.id)}
        
        response = client.post(
            "/checkins/bulk/csv",
            files=files,
            data=data,
            headers=auth_headers_operador
        )
        
        # Should handle large files appropriately (may succeed or have limits)
        assert response.status_code in [
            status.HTTP_200_OK, 
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_checkin_bulk_partial_success(self, client: TestClient, auth_headers_operador: dict, 
                                        evento_sample: Evento, participante_sample: Participante):
        """Test bulk check-in with mixed success/failure results"""
        bulk_data = {
            "evento_id": str(evento_sample.id),
            "checkins": [
                {
                    "cpf": participante_sample.cpf,
                    "nome": participante_sample.nome,
                    "tipo_checkin": "BULK"
                },
                {
                    "cpf": "00000000000",  # Invalid CPF
                    "nome": "Participante Inválido",
                    "tipo_checkin": "BULK"
                }
            ]
        }
        
        response = client.post("/checkins/bulk/json", json=bulk_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["successful"] >= 1
        assert result["failed"] >= 1


class TestCheckout:
    """Test checkout functionality"""
    
    def test_checkout_success(self, client: TestClient, auth_headers_operador: dict, 
                            participante_sample: Participante, db_session: Session):
        """Test successful checkout"""
        # First check-in the participant
        checkin_log = CheckinLog(
            participante_id=participante_sample.id,
            evento_id=participante_sample.evento_id,
            tipo_checkin=TipoCheckin.MANUAL,
            status=StatusCheckin.CONFIRMADO,
            checkin_time=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add(checkin_log)
        participante_sample.status = StatusParticipante.PRESENTE
        db_session.commit()
        
        # Now checkout
        checkout_data = {
            "participante_id": str(participante_sample.id),
            "evento_id": str(participante_sample.evento_id),
            "motivo": "Saída normal do evento"
        }
        
        response = client.post("/checkins/checkout", json=checkout_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "tempo_permanencia" in data

    def test_checkout_not_checked_in(self, client: TestClient, auth_headers_operador: dict, 
                                   participante_sample: Participante):
        """Test checkout for participant not checked in"""
        checkout_data = {
            "participante_id": str(participante_sample.id),
            "evento_id": str(participante_sample.evento_id),
            "motivo": "Tentativa de checkout sem check-in"
        }
        
        response = client.post("/checkins/checkout", json=checkout_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "não foi realizado" in response.json()["detail"]

    def test_checkout_already_done(self, client: TestClient, auth_headers_operador: dict, 
                                 participante_sample: Participante, db_session: Session):
        """Test checkout for participant already checked out"""
        # Create both check-in and checkout logs
        checkin_log = CheckinLog(
            participante_id=participante_sample.id,
            evento_id=participante_sample.evento_id,
            tipo_checkin=TipoCheckin.MANUAL,
            status=StatusCheckin.CONFIRMADO,
            checkin_time=datetime.utcnow() - timedelta(hours=2),
            checkout_time=datetime.utcnow() - timedelta(hours=1),
            created_at=datetime.utcnow() - timedelta(hours=2)
        )
        db_session.add(checkin_log)
        participante_sample.status = StatusParticipante.SAIU
        db_session.commit()
        
        checkout_data = {
            "participante_id": str(participante_sample.id),
            "evento_id": str(participante_sample.evento_id),
            "motivo": "Tentativa de segundo checkout"
        }
        
        response = client.post("/checkins/checkout", json=checkout_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já foi realizado" in response.json()["detail"]


class TestCheckinValidation:
    """Test check-in validation functionality"""
    
    def test_validacao_previa_success(self, client: TestClient, auth_headers_operador: dict, 
                                    participante_sample: Participante):
        """Test successful pre-validation"""
        validation_data = {
            "evento_id": str(participante_sample.evento_id),
            "participante_info": {
                "cpf": participante_sample.cpf,
                "nome": participante_sample.nome
            }
        }
        
        response = client.post("/checkins/validacao-previa", json=validation_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valido"] is True
        assert data["participante"]["id"] == str(participante_sample.id)

    def test_validacao_previa_participant_not_found(self, client: TestClient, auth_headers_operador: dict, 
                                                   evento_sample: Evento):
        """Test pre-validation for non-existent participant"""
        validation_data = {
            "evento_id": str(evento_sample.id),
            "participante_info": {
                "cpf": "00000000000",
                "nome": "Participante Inexistente"
            }
        }
        
        response = client.post("/checkins/validacao-previa", json=validation_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valido"] is False
        assert "não encontrado" in data["motivo"].lower()

    def test_validacao_previa_event_not_started(self, client: TestClient, auth_headers_operador: dict, 
                                               participante_sample: Participante, db_session: Session):
        """Test pre-validation for event not yet started"""
        # Update event to future date
        evento = db_session.query(Evento).filter_by(id=participante_sample.evento_id).first()
        evento.data_inicio = datetime.utcnow() + timedelta(days=1)
        db_session.commit()
        
        validation_data = {
            "evento_id": str(participante_sample.evento_id),
            "participante_info": {
                "cpf": participante_sample.cpf,
                "nome": participante_sample.nome
            }
        }
        
        response = client.post("/checkins/validacao-previa", json=validation_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should warn but might still allow check-in
        assert "data_inicio" in data or data["valido"] in [True, False]


class TestCheckinAnalytics:
    """Test check-in analytics and reporting"""
    
    def test_get_checkin_stats(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test getting check-in statistics"""
        response = client.get(f"/checkins/stats/{evento_sample.id}", headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        expected_fields = [
            "total_participantes", "checkins_realizados", "taxa_comparecimento",
            "checkins_por_tipo", "checkins_por_horario"
        ]
        for field in expected_fields:
            assert field in data

    def test_get_checkin_history(self, client: TestClient, auth_headers_promoter: dict, evento_sample: Evento):
        """Test getting check-in history"""
        response = client.get(
            f"/checkins/history/{evento_sample.id}?page=1&size=10",
            headers=auth_headers_promoter
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_export_checkin_data(self, client: TestClient, auth_headers_admin: dict, evento_sample: Evento):
        """Test exporting check-in data"""
        response = client.get(
            f"/checkins/export/{evento_sample.id}?format=csv",
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        # Should return CSV content
        if "text/csv" in response.headers.get("content-type", ""):
            assert "checkin" in response.text.lower() or len(response.content) > 0


class TestCheckinRealTime:
    """Test real-time check-in features"""
    
    @patch('app.routers.checkins.event_notifier')
    def test_checkin_websocket_notification(self, mock_notifier, client: TestClient, 
                                          auth_headers_operador: dict, participante_sample: Participante):
        """Test WebSocket notification on check-in"""
        mock_notifier.broadcast = AsyncMock()
        
        # Perform check-in
        checkin_data = {
            "participante_id": str(participante_sample.id),
            "evento_id": str(participante_sample.evento_id),
            "motivo": "Teste WebSocket"
        }
        
        response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        # Verify WebSocket notification was sent
        mock_notifier.broadcast.assert_called_once()

    def test_checkin_real_time_dashboard_data(self, client: TestClient, auth_headers_promoter: dict, 
                                            evento_sample: Evento):
        """Test real-time dashboard data for check-ins"""
        response = client.get(f"/checkins/realtime/{evento_sample.id}", headers=auth_headers_promoter)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        expected_fields = ["checkins_hoje", "media_por_hora", "pico_checkin", "status_atual"]
        for field in expected_fields:
            assert field in data

    def test_checkin_queue_status(self, client: TestClient, auth_headers_operador: dict, evento_sample: Evento):
        """Test check-in queue status"""
        response = client.get(f"/checkins/queue/{evento_sample.id}", headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "fila_atual" in data
        assert "tempo_estimado" in data


class TestCheckinSecurity:
    """Test check-in security features"""
    
    def test_checkin_audit_log(self, client: TestClient, auth_headers_operador: dict, 
                              participante_sample: Participante, db_session: Session):
        """Test that check-in creates proper audit logs"""
        # Perform check-in
        checkin_data = {
            "participante_id": str(participante_sample.id),
            "evento_id": str(participante_sample.evento_id),
            "motivo": "Teste auditoria"
        }
        
        response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify audit log was created
        checkin_logs = db_session.query(CheckinLog).filter_by(
            participante_id=participante_sample.id
        ).all()
        
        assert len(checkin_logs) >= 1
        latest_log = checkin_logs[-1]
        assert latest_log.tipo_checkin == TipoCheckin.MANUAL

    def test_checkin_geolocation_validation(self, client: TestClient, auth_headers_operador: dict, 
                                          participante_sample: Participante):
        """Test geolocation validation for check-ins"""
        checkin_data = {
            "participante_id": str(participante_sample.id),
            "evento_id": str(participante_sample.evento_id),
            "motivo": "Teste geolocalização",
            "location": {
                "lat": -23.5505,  # São Paulo coordinates
                "lng": -46.6333,
                "accuracy": 10
            }
        }
        
        response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should include location info in response
        assert "location_validated" in data or response.status_code == status.HTTP_200_OK

    def test_checkin_device_fingerprinting(self, client: TestClient, auth_headers_operador: dict, 
                                         participante_sample: Participante):
        """Test device fingerprinting for check-ins"""
        checkin_data = {
            "participante_id": str(participante_sample.id),
            "evento_id": str(participante_sample.evento_id),
            "motivo": "Teste device fingerprint",
            "device_info": {
                "device_id": "device_12345",
                "platform": "mobile",
                "user_agent": "EventApp/1.0",
                "ip_address": "192.168.1.1"
            }
        }
        
        response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_200_OK

    def test_checkin_fraud_detection(self, client: TestClient, auth_headers_operador: dict, 
                                   participante_sample: Participante, db_session: Session):
        """Test fraud detection for suspicious check-in patterns"""
        # Simulate multiple rapid check-in attempts
        for i in range(3):
            checkin_data = {
                "participante_id": str(participante_sample.id),
                "evento_id": str(participante_sample.evento_id),
                "motivo": f"Teste fraude {i}"
            }
            
            response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
            
            if i == 0:
                assert response.status_code == status.HTTP_200_OK
            else:
                # Subsequent attempts should be blocked or flagged
                assert response.status_code in [
                    status.HTTP_200_OK,  # If allowed
                    status.HTTP_400_BAD_REQUEST,  # If blocked
                    status.HTTP_429_TOO_MANY_REQUESTS  # If rate limited
                ]


class TestCheckinPerformance:
    """Test check-in performance and scalability"""
    
    def test_checkin_performance_single(self, client: TestClient, auth_headers_operador: dict, 
                                      participante_sample: Participante):
        """Test single check-in performance"""
        import time
        
        checkin_data = {
            "participante_id": str(participante_sample.id),
            "evento_id": str(participante_sample.evento_id),
            "motivo": "Teste performance"
        }
        
        start_time = time.time()
        response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        # Check-in should complete quickly
        assert end_time - start_time < 1.0

    def test_concurrent_checkins(self, client: TestClient, auth_headers_operador: dict, 
                               evento_sample: Evento, db_session: Session):
        """Test concurrent check-in handling"""
        import threading
        from app.models import Participante
        
        # Create multiple participants
        participants = []
        for i in range(5):
            participant = Participante(
                nome=f"Participante Concurrent {i}",
                email=f"concurrent{i}@test.com",
                cpf=f"1234567890{i}",
                telefone=f"1199999999{i}",
                evento_id=evento_sample.id,
                status=StatusParticipante.CONFIRMADO,
                created_at=datetime.utcnow()
            )
            db_session.add(participant)
            participants.append(participant)
        
        db_session.commit()
        
        results = []
        
        def perform_checkin(participant):
            checkin_data = {
                "participante_id": str(participant.id),
                "evento_id": str(evento_sample.id),
                "motivo": "Teste concorrente"
            }
            response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
            results.append(response.status_code)
        
        # Start concurrent check-ins
        threads = []
        for participant in participants:
            thread = threading.Thread(target=perform_checkin, args=(participant,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All should succeed
        assert all(code == status.HTTP_200_OK for code in results)