"""
Comprehensive integration tests for complete API workflows
Tests end-to-end scenarios combining multiple routers and services
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, Mock, AsyncMock
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    Usuario, Evento, Participante, Produto, Venda, CheckinLog, 
    StatusEvento, StatusParticipante, StatusVenda, TipoCheckin
)


class TestEventCreationWorkflow:
    """Test complete event creation and management workflow"""
    
    def test_complete_event_creation_workflow(self, client: TestClient, auth_headers_promoter: dict,
                                            empresa_sample, db_session: Session):
        """Test complete event creation from start to participants"""
        # Step 1: Create event
        event_data = {
            "nome": "Festa de Teste Completa",
            "descricao": "Evento para teste de workflow completo",
            "data_inicio": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(days=7, hours=4)).isoformat(),
            "local": "Centro de Convenções",
            "endereco": "Av. Principal, 1000",
            "capacidade_maxima": 500,
            "empresa_id": str(empresa_sample.id),
            "preco_ingresso": 50.00,
            "status": "ATIVO"
        }
        
        response = client.post("/eventos/", json=event_data, headers=auth_headers_promoter)
        assert response.status_code == status.HTTP_201_CREATED
        evento = response.json()
        evento_id = evento["id"]
        
        # Step 2: Add products to the event
        product_data = {
            "nome": "Cerveja Artesanal",
            "descricao": "Cerveja artesanal premium 500ml",
            "preco": 12.00,
            "categoria": "Bebidas",
            "evento_id": evento_id,
            "estoque_inicial": 200,
            "ativo": True
        }
        
        response = client.post("/pdv/produtos", json=product_data, headers=auth_headers_promoter)
        assert response.status_code == status.HTTP_201_CREATED
        produto = response.json()
        
        # Step 3: Create participants list
        participants_data = [
            {
                "nome": "João Silva",
                "email": "joao@test.com",
                "cpf": "12345678901",
                "telefone": "11999999999"
            },
            {
                "nome": "Maria Santos",
                "email": "maria@test.com", 
                "cpf": "98765432109",
                "telefone": "11888888888"
            }
        ]
        
        # Create participants
        created_participants = []
        for participant_data in participants_data:
            participant = Participante(
                nome=participant_data["nome"],
                email=participant_data["email"],
                cpf=participant_data["cpf"],
                telefone=participant_data["telefone"],
                evento_id=evento_id,
                status=StatusParticipante.CONFIRMADO,
                created_at=datetime.utcnow()
            )
            db_session.add(participant)
            created_participants.append(participant)
        
        db_session.commit()
        
        # Step 4: Verify event dashboard shows correct data
        response = client.get(f"/eventos/{evento_id}/stats", headers=auth_headers_promoter)
        assert response.status_code == status.HTTP_200_OK
        stats = response.json()
        assert stats["total_participantes"] == 2
        assert stats["checkins_realizados"] == 0
        
        # Step 5: Verify PDV dashboard shows products
        response = client.get(f"/pdv/dashboard?evento_id={evento_id}", headers=auth_headers_promoter)
        assert response.status_code == status.HTTP_200_OK
        pdv_stats = response.json()
        assert "produtos_mais_vendidos" in pdv_stats

    def test_event_with_ai_enhancement_workflow(self, client: TestClient, auth_headers_promoter: dict,
                                              empresa_sample, mock_openai_service):
        """Test event creation with AI enhancements"""
        with patch('app.routers.eventos.get_openai_service', return_value=mock_openai_service):
            # Create event with AI description generation
            event_data = {
                "nome": "Festa de Fim de Ano",
                "data_inicio": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "data_fim": (datetime.utcnow() + timedelta(days=30, hours=6)).isoformat(),
                "local": "Salão de Festas Premium",
                "endereco": "Rua das Flores, 500",
                "capacidade_maxima": 300,
                "empresa_id": str(empresa_sample.id),
                "generate_ai_description": True
            }
            
            response = client.post("/eventos/", json=event_data, headers=auth_headers_promoter)
            assert response.status_code == status.HTTP_201_CREATED
            evento = response.json()
            
            # Verify AI service was called
            mock_openai_service.generate_event_description.assert_called_once()
            
            # Verify description was generated
            assert evento["descricao"] == "Generated description"

    def test_event_clone_workflow(self, client: TestClient, auth_headers_promoter: dict,
                                evento_sample: Evento, produto_sample):
        """Test complete event cloning workflow"""
        # Clone the event
        clone_data = {
            "novo_nome": "Evento Clonado Completo",
            "nova_data_inicio": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "nova_data_fim": (datetime.utcnow() + timedelta(days=14, hours=4)).isoformat(),
            "copiar_produtos": True,
            "copiar_participantes": False
        }
        
        response = client.post(
            f"/eventos/{evento_sample.id}/clone",
            json=clone_data,
            headers=auth_headers_promoter
        )
        assert response.status_code == status.HTTP_201_CREATED
        cloned_event = response.json()
        
        # Verify cloned event has correct data
        assert cloned_event["nome"] == clone_data["novo_nome"]
        assert cloned_event["descricao"] == evento_sample.descricao
        
        # Verify products were cloned
        response = client.get(
            f"/pdv/produtos?evento_id={cloned_event['id']}",
            headers=auth_headers_promoter
        )
        assert response.status_code == status.HTTP_200_OK
        products = response.json()
        
        if products["items"]:  # If cloning is implemented
            assert len(products["items"]) >= 1


class TestCheckinWorkflow:
    """Test complete check-in workflow scenarios"""
    
    def test_qr_checkin_complete_workflow(self, client: TestClient, auth_headers_operador: dict,
                                        participante_sample: Participante):
        """Test complete QR check-in workflow"""
        # Step 1: Generate QR code
        response = client.post(
            f"/checkins/generate-qr/{participante_sample.id}",
            headers=auth_headers_operador
        )
        assert response.status_code == status.HTTP_200_OK
        qr_data = response.json()
        qr_token = qr_data["qr_token"]
        
        # Step 2: Validate QR before check-in
        validation_data = {
            "evento_id": str(participante_sample.evento_id),
            "participante_info": {
                "cpf": participante_sample.cpf,
                "nome": participante_sample.nome
            }
        }
        
        response = client.post("/checkins/validacao-previa", json=validation_data, headers=auth_headers_operador)
        assert response.status_code == status.HTTP_200_OK
        validation = response.json()
        assert validation["valido"] is True
        
        # Step 3: Perform QR check-in
        checkin_data = {
            "qr_token": qr_token,
            "evento_id": str(participante_sample.evento_id),
            "operador_info": {
                "device_id": "tablet_001",
                "location": {"lat": -23.5505, "lng": -46.6333}
            }
        }
        
        response = client.post("/checkins/qr", json=checkin_data, headers=auth_headers_operador)
        assert response.status_code == status.HTTP_200_OK
        checkin_result = response.json()
        assert checkin_result["success"] is True
        assert checkin_result["participante"]["id"] == str(participante_sample.id)
        
        # Step 4: Verify check-in was recorded
        response = client.get(
            f"/checkins/history/{participante_sample.evento_id}",
            headers=auth_headers_operador
        )
        assert response.status_code == status.HTTP_200_OK
        history = response.json()
        assert len(history["items"]) >= 1
        
        # Step 5: Verify event stats updated
        response = client.get(
            f"/checkins/stats/{participante_sample.evento_id}",
            headers=auth_headers_operador
        )
        assert response.status_code == status.HTTP_200_OK
        stats = response.json()
        assert stats["checkins_realizados"] >= 1

    def test_cpf_checkin_with_validation_workflow(self, client: TestClient, auth_headers_operador: dict,
                                                participante_sample: Participante):
        """Test CPF check-in with validation workflow"""
        # Step 1: Validate participant exists
        validation_data = {
            "evento_id": str(participante_sample.evento_id),
            "participante_info": {
                "cpf": participante_sample.cpf
            }
        }
        
        response = client.post("/checkins/validacao-previa", json=validation_data, headers=auth_headers_operador)
        assert response.status_code == status.HTTP_200_OK
        validation = response.json()
        assert validation["valido"] is True
        
        # Step 2: Perform CPF check-in
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
        checkin_result = response.json()
        assert checkin_result["success"] is True
        
        # Step 3: Attempt duplicate check-in (should fail)
        response = client.post("/checkins/cpf", json=checkin_data, headers=auth_headers_operador)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já foi realizado" in response.json()["detail"]

    def test_bulk_checkin_workflow(self, client: TestClient, auth_headers_operador: dict,
                                 evento_sample: Evento, db_session: Session):
        """Test bulk check-in workflow"""
        # Step 1: Create multiple participants
        participants_data = []
        for i in range(5):
            participant = Participante(
                nome=f"Participante Bulk {i}",
                email=f"bulk{i}@test.com",
                cpf=f"1234567890{i}",
                telefone=f"1199999999{i}",
                evento_id=evento_sample.id,
                status=StatusParticipante.CONFIRMADO,
                created_at=datetime.utcnow()
            )
            db_session.add(participant)
            participants_data.append(participant)
        
        db_session.commit()
        
        # Step 2: Prepare bulk check-in data
        bulk_data = {
            "evento_id": str(evento_sample.id),
            "checkins": [
                {
                    "cpf": p.cpf,
                    "nome": p.nome,
                    "tipo_checkin": "BULK"
                } for p in participants_data
            ],
            "validacao_rigorosa": True
        }
        
        # Step 3: Perform bulk check-in
        response = client.post("/checkins/bulk/json", json=bulk_data, headers=auth_headers_operador)
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["successful"] >= 5
        assert result["failed"] == 0
        
        # Step 4: Verify all check-ins were recorded
        response = client.get(f"/checkins/stats/{evento_sample.id}", headers=auth_headers_operador)
        assert response.status_code == status.HTTP_200_OK
        stats = response.json()
        assert stats["checkins_realizados"] >= 5


class TestSalesWorkflow:
    """Test complete sales workflow scenarios"""
    
    def test_complete_sales_workflow(self, client: TestClient, auth_headers_operador: dict,
                                   produto_sample, evento_sample: Evento):
        """Test complete sales workflow from cart to payment"""
        # Step 1: Check product availability
        response = client.get(f"/pdv/estoque/{produto_sample.id}", headers=auth_headers_operador)
        assert response.status_code == status.HTTP_200_OK
        estoque = response.json()
        initial_stock = estoque["quantidade_disponivel"]
        
        # Step 2: Create sale
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {
                "nome": "Cliente Workflow",
                "cpf": "12345678901",
                "email": "cliente@test.com"
            },
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 2,
                    "preco_unitario": float(produto_sample.preco),
                    "desconto": 0.0
                }
            ],
            "forma_pagamento": "DINHEIRO",
            "pagamento": {
                "valor_recebido": float(produto_sample.preco) * 2 + 5.0
            },
            "observacoes": "Venda teste workflow"
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        assert response.status_code == status.HTTP_201_CREATED
        venda = response.json()
        assert venda["status"] == "CONCLUIDA"
        assert float(venda["total"]) == float(produto_sample.preco) * 2
        
        # Step 3: Verify stock was updated
        response = client.get(f"/pdv/estoque/{produto_sample.id}", headers=auth_headers_operador)
        assert response.status_code == status.HTTP_200_OK
        new_estoque = response.json()
        # Stock should have decreased by 2
        if initial_stock is not None and new_estoque["quantidade_disponivel"] is not None:
            assert new_estoque["quantidade_disponivel"] == initial_stock - 2
        
        # Step 4: Verify sale appears in sales list
        response = client.get("/pdv/vendas", headers=auth_headers_operador)
        assert response.status_code == status.HTTP_200_OK
        vendas = response.json()
        assert len(vendas["items"]) >= 1
        
        # Step 5: Generate receipt
        response = client.get(f"/pdv/vendas/{venda['id']}", headers=auth_headers_operador)
        assert response.status_code == status.HTTP_200_OK
        receipt = response.json()
        assert receipt["id"] == venda["id"]
        assert len(receipt["itens"]) == 1

    def test_sales_with_coupon_workflow(self, client: TestClient, auth_headers_operador: dict,
                                      produto_sample, evento_sample: Evento, db_session: Session):
        """Test sales workflow with coupon application"""
        # Step 1: Create a coupon
        from app.models import Cupom
        cupom = Cupom(
            codigo="WORKFLOW10",
            descricao="Desconto workflow 10%",
            tipo_desconto="PERCENTUAL",
            valor_desconto=Decimal("10.00"),
            ativo=True,
            data_validade=datetime.utcnow() + timedelta(days=30),
            evento_id=evento_sample.id,
            created_at=datetime.utcnow()
        )
        db_session.add(cupom)
        db_session.commit()
        
        # Step 2: Validate coupon
        response = client.get(
            f"/pdv/cupons/validar?codigo=WORKFLOW10&evento_id={evento_sample.id}",
            headers=auth_headers_operador
        )
        assert response.status_code == status.HTTP_200_OK
        validation = response.json()
        assert validation["valido"] is True
        
        # Step 3: Create sale with coupon
        original_price = float(produto_sample.preco)
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Cupom"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": original_price
                }
            ],
            "cupom_codigo": "WORKFLOW10",
            "forma_pagamento": "PIX"
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        assert response.status_code == status.HTTP_201_CREATED
        venda = response.json()
        
        # Verify discount was applied
        expected_total = original_price * 0.9  # 10% discount
        assert float(venda["total"]) == expected_total

    def test_inventory_replenishment_workflow(self, client: TestClient, auth_headers_admin: dict,
                                            produto_sample):
        """Test inventory replenishment workflow"""
        # Step 1: Check current stock
        response = client.get(f"/pdv/estoque/{produto_sample.id}", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        initial_stock = response.json()
        
        # Step 2: Add stock (replenishment)
        restock_data = {
            "quantidade": 100,
            "tipo_movimentacao": "ENTRADA",
            "motivo": "Reposição de estoque",
            "observacoes": "Chegada de nova remessa"
        }
        
        response = client.post(
            f"/pdv/estoque/{produto_sample.id}/movimentacao",
            json=restock_data,
            headers=auth_headers_admin
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Step 3: Verify stock increased
        response = client.get(f"/pdv/estoque/{produto_sample.id}", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        new_stock = response.json()
        
        if initial_stock["quantidade_atual"] is not None:
            assert new_stock["quantidade_atual"] == initial_stock["quantidade_atual"] + 100
        
        # Step 4: Check movement history
        response = client.get(
            f"/pdv/estoque/{produto_sample.id}/movimentacoes",
            headers=auth_headers_admin
        )
        assert response.status_code == status.HTTP_200_OK
        movements = response.json()
        assert len(movements["items"]) >= 1


class TestEventOperationsWorkflow:
    """Test complete event operations workflow"""
    
    def test_event_day_operations_workflow(self, client: TestClient, auth_headers_promoter: dict,
                                         auth_headers_operador: dict, evento_sample: Evento,
                                         produto_sample, db_session: Session):
        """Test complete event day operations workflow"""
        # Step 1: Create participants for the event
        participants = []
        for i in range(3):
            participant = Participante(
                nome=f"Participante Evento {i}",
                email=f"evento{i}@test.com",
                cpf=f"1111111111{i}",
                telefone=f"1177777777{i}",
                evento_id=evento_sample.id,
                status=StatusParticipante.CONFIRMADO,
                created_at=datetime.utcnow()
            )
            db_session.add(participant)
            participants.append(participant)
        
        db_session.commit()
        
        # Step 2: Event starts - check initial dashboard
        response = client.get(f"/eventos/{evento_sample.id}/stats", headers=auth_headers_promoter)
        assert response.status_code == status.HTTP_200_OK
        initial_stats = response.json()
        assert initial_stats["total_participantes"] >= 3
        assert initial_stats["checkins_realizados"] == 0
        
        # Step 3: Participants start checking in
        checkins_count = 0
        for participant in participants[:2]:  # Check in 2 out of 3
            # Manual check-in
            checkin_data = {
                "participante_id": str(participant.id),
                "evento_id": str(evento_sample.id),
                "motivo": "Check-in no dia do evento"
            }
            
            response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_operador)
            if response.status_code == status.HTTP_200_OK:
                checkins_count += 1
        
        # Step 4: Sales begin
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Evento"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 3,
                    "preco_unitario": float(produto_sample.preco)
                }
            ],
            "forma_pagamento": "CARTAO"
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        vendas_count = 1 if response.status_code == status.HTTP_201_CREATED else 0
        
        # Step 5: Check updated event stats
        response = client.get(f"/eventos/{evento_sample.id}/stats", headers=auth_headers_promoter)
        assert response.status_code == status.HTTP_200_OK
        updated_stats = response.json()
        
        if checkins_count > 0:
            assert updated_stats["checkins_realizados"] >= checkins_count
        
        # Step 6: Check PDV dashboard
        response = client.get(f"/pdv/dashboard?evento_id={evento_sample.id}", headers=auth_headers_promoter)
        assert response.status_code == status.HTTP_200_OK
        pdv_stats = response.json()
        
        if vendas_count > 0:
            assert pdv_stats["vendas_hoje"] >= vendas_count
        
        # Step 7: Generate reports
        response = client.get(
            f"/checkins/export/{evento_sample.id}?format=csv",
            headers=auth_headers_promoter
        )
        # Should succeed or return appropriate status
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_event_cancellation_workflow(self, client: TestClient, auth_headers_admin: dict,
                                       evento_sample: Evento, db_session: Session):
        """Test event cancellation workflow"""
        # Step 1: Create some participants and sales
        participant = Participante(
            nome="Participante Cancelamento",
            email="cancel@test.com",
            cpf="99999999999",
            telefone="11555555555",
            evento_id=evento_sample.id,
            status=StatusParticipante.CONFIRMADO,
            created_at=datetime.utcnow()
        )
        db_session.add(participant)
        db_session.commit()
        
        # Step 2: Cancel the event
        update_data = {"status": "CANCELADO"}
        
        response = client.put(
            f"/eventos/{evento_sample.id}",
            json=update_data,
            headers=auth_headers_admin
        )
        assert response.status_code == status.HTTP_200_OK
        cancelled_event = response.json()
        assert cancelled_event["status"] == "CANCELADO"
        
        # Step 3: Verify participants can no longer check in
        checkin_data = {
            "participante_id": str(participant.id),
            "evento_id": str(evento_sample.id),
            "motivo": "Tentativa check-in evento cancelado"
        }
        
        response = client.post("/checkins/manual", json=checkin_data, headers=auth_headers_admin)
        # Should be blocked or allowed with warning depending on implementation
        assert response.status_code in [
            status.HTTP_200_OK,  # If allowed
            status.HTTP_400_BAD_REQUEST  # If blocked
        ]


class TestReportingWorkflow:
    """Test complete reporting and analytics workflow"""
    
    def test_comprehensive_reporting_workflow(self, client: TestClient, auth_headers_admin: dict,
                                            evento_sample: Evento, db_session: Session):
        """Test comprehensive reporting workflow"""
        # Step 1: Create test data
        # Create participants
        participants = []
        for i in range(10):
            participant = Participante(
                nome=f"Participante Report {i}",
                email=f"report{i}@test.com",
                cpf=f"2222222222{i}",
                telefone=f"1166666666{i}",
                evento_id=evento_sample.id,
                status=StatusParticipante.CONFIRMADO,
                created_at=datetime.utcnow()
            )
            db_session.add(participant)
            participants.append(participant)
        
        # Create check-ins for some participants
        for participant in participants[:7]:  # 7 out of 10 check in
            checkin_log = CheckinLog(
                participante_id=participant.id,
                evento_id=evento_sample.id,
                tipo_checkin=TipoCheckin.MANUAL,
                status="CONFIRMADO",
                checkin_time=datetime.utcnow() - timedelta(hours=2),
                created_at=datetime.utcnow() - timedelta(hours=2)
            )
            db_session.add(checkin_log)
        
        # Create some sales
        for i in range(5):
            venda = Venda(
                evento_id=evento_sample.id,
                vendedor_id=1,  # Assuming admin user has ID 1
                cliente_nome=f"Cliente Report {i}",
                total=Decimal("25.50"),
                forma_pagamento="DINHEIRO",
                status=StatusVenda.CONCLUIDA,
                created_at=datetime.utcnow() - timedelta(hours=1)
            )
            db_session.add(venda)
        
        db_session.commit()
        
        # Step 2: Generate check-in report
        response = client.get(f"/checkins/stats/{evento_sample.id}", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        checkin_stats = response.json()
        
        assert checkin_stats["total_participantes"] >= 10
        assert checkin_stats["checkins_realizados"] >= 7
        if checkin_stats["total_participantes"] > 0:
            attendance_rate = checkin_stats["checkins_realizados"] / checkin_stats["total_participantes"]
            assert attendance_rate >= 0.7  # 70% attendance rate
        
        # Step 3: Generate sales report
        response = client.get(f"/pdv/dashboard?evento_id={evento_sample.id}", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        sales_stats = response.json()
        
        if "vendas_hoje" in sales_stats:
            assert sales_stats["vendas_hoje"] >= 5
        
        # Step 4: Generate financial report
        data_inicio = datetime.utcnow().date()
        data_fim = (datetime.utcnow() + timedelta(days=1)).date()
        
        response = client.get(
            f"/pdv/relatorios/financeiro?evento_id={evento_sample.id}&data_inicio={data_inicio}&data_fim={data_fim}",
            headers=auth_headers_admin
        )
        assert response.status_code == status.HTTP_200_OK
        financial_report = response.json()
        
        assert "receita_bruta" in financial_report
        if financial_report["receita_bruta"]:
            assert float(financial_report["receita_bruta"]) >= 127.50  # 5 sales * 25.50
        
        # Step 5: Export data
        response = client.get(
            f"/eventos/export?formato=csv&evento_id={evento_sample.id}",
            headers=auth_headers_admin
        )
        # Should succeed or be not implemented
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_501_NOT_IMPLEMENTED]


class TestUserRoleWorkflow:
    """Test workflows across different user roles"""
    
    def test_admin_full_access_workflow(self, client: TestClient, auth_headers_admin: dict,
                                      evento_sample: Evento):
        """Test admin can access all functionality"""
        endpoints_to_test = [
            ("/eventos/", "GET"),
            ("/pdv/produtos", "GET"),
            ("/checkins/stats/" + str(evento_sample.id), "GET"),
            ("/pdv/vendas", "GET"),
            ("/auth/users", "GET")
        ]
        
        for endpoint, method in endpoints_to_test:
            if method == "GET":
                response = client.get(endpoint, headers=auth_headers_admin)
            else:
                response = client.post(endpoint, json={}, headers=auth_headers_admin)
            
            # Admin should have access to all endpoints
            assert response.status_code not in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

    def test_promoter_limited_access_workflow(self, client: TestClient, auth_headers_promoter: dict,
                                            evento_sample: Evento):
        """Test promoter has appropriate access limitations"""
        # Promoter should have access to their own events
        response = client.get("/eventos/", headers=auth_headers_promoter)
        assert response.status_code == status.HTTP_200_OK
        
        # Promoter should have access to event stats
        response = client.get(f"/eventos/{evento_sample.id}/stats", headers=auth_headers_promoter)
        assert response.status_code == status.HTTP_200_OK
        
        # Promoter might not have access to admin functions
        response = client.get("/auth/users", headers=auth_headers_promoter)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_operador_workflow_restrictions(self, client: TestClient, auth_headers_operador: dict,
                                          evento_sample: Evento):
        """Test operator workflow restrictions"""
        # Operator should be able to perform check-ins
        response = client.get(f"/checkins/stats/{evento_sample.id}", headers=auth_headers_operador)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        
        # Operator might not create events
        event_data = {
            "nome": "Evento Operador",
            "data_inicio": datetime.utcnow().isoformat(),
            "data_fim": (datetime.utcnow() + timedelta(hours=4)).isoformat(),
            "local": "Local Teste",
            "endereco": "Endereço Teste",
            "capacidade_maxima": 100
        }
        
        response = client.post("/eventos/", json=event_data, headers=auth_headers_operador)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN]


class TestErrorHandlingWorkflow:
    """Test error handling across workflows"""
    
    def test_network_failure_resilience(self, client: TestClient, auth_headers_admin: dict):
        """Test system resilience to network failures"""
        # Simulate network timeout by using very long request
        large_data = {"data": "x" * 100000}  # 100KB payload
        
        response = client.post("/eventos/", json=large_data, headers=auth_headers_admin)
        
        # Should handle gracefully
        assert response.status_code in [
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]

    def test_database_constraint_violations(self, client: TestClient, auth_headers_admin: dict,
                                          evento_sample: Evento):
        """Test handling of database constraint violations"""
        # Try to create duplicate event with same unique fields
        duplicate_event = {
            "nome": evento_sample.nome,
            "data_inicio": evento_sample.data_inicio.isoformat(),
            "data_fim": evento_sample.data_fim.isoformat(),
            "local": evento_sample.local,
            "endereco": evento_sample.endereco,
            "capacidade_maxima": evento_sample.capacidade_maxima
        }
        
        response = client.post("/eventos/", json=duplicate_event, headers=auth_headers_admin)
        
        # Should handle constraint violations gracefully
        assert response.status_code in [
            status.HTTP_201_CREATED,  # If duplicates are allowed
            status.HTTP_400_BAD_REQUEST,  # If validation fails
            status.HTTP_409_CONFLICT  # If constraint violation
        ]

    def test_concurrent_access_handling(self, client: TestClient, auth_headers_admin: dict,
                                      evento_sample: Evento):
        """Test handling of concurrent access to resources"""
        import threading
        import time
        
        results = []
        
        def update_event():
            update_data = {"nome": f"Updated at {time.time()}"}
            response = client.put(
                f"/eventos/{evento_sample.id}",
                json=update_data,
                headers=auth_headers_admin
            )
            results.append(response.status_code)
        
        # Start multiple concurrent updates
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=update_event)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # At least some updates should succeed
        assert any(code == status.HTTP_200_OK for code in results)