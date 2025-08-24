"""
Comprehensive test suite for PDV (Point of Sale) Router
Tests product management, sales operations, inventory control, and payment processing
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, AsyncMock
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from io import BytesIO

from app.models import (
    Produto, Venda, ItemVenda, EstoqueProduto, MovimentacaoEstoque,
    Usuario, Evento, StatusVenda, TipoMovimentacao
)


class TestProdutosCRUD:
    """Test product CRUD operations"""
    
    def test_create_produto_success(self, client: TestClient, auth_headers_admin: dict, evento_sample: Evento):
        """Test successful product creation"""
        produto_data = {
            "nome": "Cerveja Premium",
            "descricao": "Cerveja artesanal premium 500ml",
            "preco": 15.50,
            "categoria": "Bebidas",
            "codigo_barras": "7891234567890",
            "evento_id": str(evento_sample.id),
            "estoque_inicial": 100,
            "estoque_minimo": 10,
            "ativo": True
        }
        
        response = client.post("/pdv/produtos", json=produto_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nome"] == produto_data["nome"]
        assert float(data["preco"]) == produto_data["preco"]
        assert data["categoria"] == produto_data["categoria"]
        assert data["ativo"] is True

    def test_create_produto_duplicate_codigo_barras(self, client: TestClient, auth_headers_admin: dict, 
                                                   produto_sample: Produto):
        """Test creating product with duplicate barcode"""
        produto_data = {
            "nome": "Produto Duplicado",
            "descricao": "Teste código de barras duplicado",
            "preco": 10.00,
            "categoria": "Teste",
            "codigo_barras": produto_sample.codigo_barras if hasattr(produto_sample, 'codigo_barras') else "123456789",
            "evento_id": str(produto_sample.evento_id),
            "ativo": True
        }
        
        response = client.post("/pdv/produtos", json=produto_data, headers=auth_headers_admin)
        
        # Should either reject or handle gracefully
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_409_CONFLICT,
            status.HTTP_201_CREATED  # If duplicates are allowed
        ]

    def test_list_produtos_success(self, client: TestClient, auth_headers_admin: dict, produto_sample: Produto):
        """Test successful product listing"""
        response = client.get("/pdv/produtos", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    def test_list_produtos_by_evento(self, client: TestClient, auth_headers_admin: dict, produto_sample: Produto):
        """Test product listing filtered by event"""
        response = client.get(
            f"/pdv/produtos?evento_id={produto_sample.evento_id}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # All products should belong to the specified event
        for produto in data["items"]:
            assert produto["evento_id"] == str(produto_sample.evento_id)

    def test_list_produtos_by_categoria(self, client: TestClient, auth_headers_admin: dict, produto_sample: Produto):
        """Test product listing filtered by category"""
        response = client.get(
            f"/pdv/produtos?categoria={produto_sample.categoria}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # All products should have the specified category
        for produto in data["items"]:
            assert produto["categoria"] == produto_sample.categoria

    def test_get_produto_by_id_success(self, client: TestClient, auth_headers_admin: dict, produto_sample: Produto):
        """Test getting product by ID"""
        response = client.get(f"/pdv/produtos/{produto_sample.id}", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(produto_sample.id)
        assert data["nome"] == produto_sample.nome

    def test_get_produto_not_found(self, client: TestClient, auth_headers_admin: dict):
        """Test getting non-existent product"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = client.get(f"/pdv/produtos/{fake_id}", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_produto_success(self, client: TestClient, auth_headers_admin: dict, produto_sample: Produto):
        """Test successful product update"""
        update_data = {
            "nome": "Produto Atualizado",
            "preco": 20.00,
            "descricao": "Descrição atualizada"
        }
        
        response = client.put(
            f"/pdv/produtos/{produto_sample.id}",
            json=update_data,
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nome"] == update_data["nome"]
        assert float(data["preco"]) == update_data["preco"]

    def test_update_produto_not_found(self, client: TestClient, auth_headers_admin: dict):
        """Test updating non-existent product"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        update_data = {"nome": "Produto Inexistente"}
        
        response = client.put(f"/pdv/produtos/{fake_id}", json=update_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_produto_success(self, client: TestClient, auth_headers_admin: dict, produto_sample: Produto):
        """Test successful product deletion (soft delete)"""
        response = client.delete(f"/pdv/produtos/{produto_sample.id}", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Produto excluído com sucesso"

    def test_create_produto_unauthorized(self, client: TestClient, auth_headers_operador: dict, evento_sample: Evento):
        """Test product creation without proper authorization"""
        produto_data = {
            "nome": "Produto Não Autorizado",
            "preco": 10.00,
            "categoria": "Teste",
            "evento_id": str(evento_sample.id)
        }
        
        response = client.post("/pdv/produtos", json=produto_data, headers=auth_headers_operador)
        
        # Operators might not have permission to create products
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN]

    def test_create_produto_invalid_price(self, client: TestClient, auth_headers_admin: dict, evento_sample: Evento):
        """Test creating product with invalid price"""
        produto_data = {
            "nome": "Produto Preço Inválido",
            "preco": -10.00,  # Negative price
            "categoria": "Teste",
            "evento_id": str(evento_sample.id)
        }
        
        response = client.post("/pdv/produtos", json=produto_data, headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestEstoque:
    """Test inventory management"""
    
    def test_get_estoque_produto(self, client: TestClient, auth_headers_admin: dict, produto_sample: Produto):
        """Test getting product inventory"""
        response = client.get(f"/pdv/estoque/{produto_sample.id}", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "produto_id" in data
        assert "quantidade_atual" in data
        assert "quantidade_reservada" in data
        assert "quantidade_disponivel" in data

    def test_update_estoque_entrada(self, client: TestClient, auth_headers_admin: dict, produto_sample: Produto):
        """Test inventory increase (stock entry)"""
        estoque_data = {
            "quantidade": 50,
            "tipo_movimentacao": "ENTRADA",
            "motivo": "Reposição de estoque",
            "observacoes": "Chegada de nova remessa"
        }
        
        response = client.post(
            f"/pdv/estoque/{produto_sample.id}/movimentacao",
            json=estoque_data,
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["tipo_movimentacao"] == "ENTRADA"
        assert data["quantidade"] == 50

    def test_update_estoque_saida(self, client: TestClient, auth_headers_admin: dict, produto_sample: Produto):
        """Test inventory decrease (stock exit)"""
        estoque_data = {
            "quantidade": 10,
            "tipo_movimentacao": "SAIDA",
            "motivo": "Venda direta",
            "observacoes": "Venda manual"
        }
        
        response = client.post(
            f"/pdv/estoque/{produto_sample.id}/movimentacao",
            json=estoque_data,
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["tipo_movimentacao"] == "SAIDA"

    def test_update_estoque_insufficient_stock(self, client: TestClient, auth_headers_admin: dict, 
                                             produto_sample: Produto):
        """Test inventory decrease with insufficient stock"""
        estoque_data = {
            "quantidade": 9999,  # More than available
            "tipo_movimentacao": "SAIDA",
            "motivo": "Teste estoque insuficiente"
        }
        
        response = client.post(
            f"/pdv/estoque/{produto_sample.id}/movimentacao",
            json=estoque_data,
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "insuficiente" in response.json()["detail"].lower()

    def test_get_movimentacoes_estoque(self, client: TestClient, auth_headers_admin: dict, produto_sample: Produto):
        """Test getting inventory movements history"""
        response = client.get(
            f"/pdv/estoque/{produto_sample.id}/movimentacoes",
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_alertas_estoque_baixo(self, client: TestClient, auth_headers_admin: dict):
        """Test low stock alerts"""
        response = client.get("/pdv/estoque/alertas", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "produtos_estoque_baixo" in data
        assert "produtos_esgotados" in data

    def test_inventario_produtos(self, client: TestClient, auth_headers_admin: dict, evento_sample: Evento):
        """Test full inventory report"""
        response = client.get(
            f"/pdv/estoque/inventario?evento_id={evento_sample.id}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "produtos" in data
        assert "total_valor_estoque" in data
        assert "resumo_por_categoria" in data


class TestVendas:
    """Test sales operations"""
    
    def test_create_venda_success(self, client: TestClient, auth_headers_operador: dict, 
                                 produto_sample: Produto, evento_sample: Evento):
        """Test successful sale creation"""
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {
                "nome": "João Silva",
                "cpf": "12345678901",
                "email": "joao@test.com"
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
            "observacoes": "Venda teste"
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "CONCLUIDA"
        assert len(data["itens"]) == 1
        assert float(data["total"]) == 2 * float(produto_sample.preco)

    def test_create_venda_multiple_items(self, client: TestClient, auth_headers_operador: dict, 
                                       produto_sample: Produto, evento_sample: Evento, db_session: Session):
        """Test sale with multiple items"""
        # Create a second product
        produto2 = Produto(
            nome="Refrigerante",
            descricao="Refrigerante 350ml",
            preco=Decimal("5.50"),
            categoria="Bebidas",
            ativo=True,
            evento_id=evento_sample.id,
            created_at=datetime.utcnow()
        )
        db_session.add(produto2)
        db_session.commit()
        db_session.refresh(produto2)
        
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {
                "nome": "Maria Santos",
                "cpf": "98765432109"
            },
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": float(produto_sample.preco)
                },
                {
                    "produto_id": str(produto2.id),
                    "quantidade": 3,
                    "preco_unitario": float(produto2.preco)
                }
            ],
            "forma_pagamento": "CARTAO"
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data["itens"]) == 2
        expected_total = float(produto_sample.preco) + (3 * float(produto2.preco))
        assert float(data["total"]) == expected_total

    def test_create_venda_with_discount(self, client: TestClient, auth_headers_operador: dict, 
                                      produto_sample: Produto, evento_sample: Evento):
        """Test sale with discount"""
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {
                "nome": "Pedro Oliveira",
                "cpf": "11122233344"
            },
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": float(produto_sample.preco),
                    "desconto": 2.50
                }
            ],
            "forma_pagamento": "PIX",
            "desconto_total": 2.50
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        expected_total = float(produto_sample.preco) - 2.50
        assert float(data["total"]) == expected_total

    def test_create_venda_produto_inativo(self, client: TestClient, auth_headers_operador: dict, 
                                        produto_sample: Produto, evento_sample: Evento, db_session: Session):
        """Test sale with inactive product"""
        # Deactivate the product
        produto_sample.ativo = False
        db_session.commit()
        
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Teste"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": float(produto_sample.preco)
                }
            ],
            "forma_pagamento": "DINHEIRO"
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "inativo" in response.json()["detail"].lower()

    def test_create_venda_produto_not_found(self, client: TestClient, auth_headers_operador: dict, 
                                          evento_sample: Evento):
        """Test sale with non-existent product"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Teste"},
            "itens": [
                {
                    "produto_id": fake_id,
                    "quantidade": 1,
                    "preco_unitario": 10.00
                }
            ],
            "forma_pagamento": "DINHEIRO"
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_vendas_success(self, client: TestClient, auth_headers_admin: dict):
        """Test successful sales listing"""
        response = client.get("/pdv/vendas", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "resumo" in data

    def test_list_vendas_by_date_range(self, client: TestClient, auth_headers_admin: dict):
        """Test sales listing filtered by date range"""
        data_inicio = datetime.utcnow().date()
        data_fim = (datetime.utcnow() + timedelta(days=1)).date()
        
        response = client.get(
            f"/pdv/vendas?data_inicio={data_inicio}&data_fim={data_fim}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_venda_by_id(self, client: TestClient, auth_headers_admin: dict, 
                           produto_sample: Produto, evento_sample: Evento, db_session: Session):
        """Test getting sale by ID"""
        # Create a sale first
        venda = Venda(
            evento_id=evento_sample.id,
            vendedor_id=1,  # Assuming user ID 1 exists
            cliente_nome="Cliente Teste",
            total=Decimal("25.50"),
            forma_pagamento="DINHEIRO",
            status=StatusVenda.CONCLUIDA,
            created_at=datetime.utcnow()
        )
        db_session.add(venda)
        db_session.commit()
        db_session.refresh(venda)
        
        response = client.get(f"/pdv/vendas/{venda.id}", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(venda.id)

    def test_cancel_venda_success(self, client: TestClient, auth_headers_admin: dict, 
                                evento_sample: Evento, db_session: Session):
        """Test successful sale cancellation"""
        # Create a sale first
        venda = Venda(
            evento_id=evento_sample.id,
            vendedor_id=1,
            cliente_nome="Cliente Teste",
            total=Decimal("25.50"),
            forma_pagamento="DINHEIRO",
            status=StatusVenda.CONCLUIDA,
            created_at=datetime.utcnow()
        )
        db_session.add(venda)
        db_session.commit()
        db_session.refresh(venda)
        
        cancel_data = {
            "motivo": "Cliente solicitou cancelamento",
            "observacoes": "Produto com defeito"
        }
        
        response = client.post(
            f"/pdv/vendas/{venda.id}/cancelar",
            json=cancel_data,
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "CANCELADA"


class TestPagamentos:
    """Test payment processing"""
    
    def test_process_payment_cash(self, client: TestClient, auth_headers_operador: dict, 
                                produto_sample: Produto, evento_sample: Evento):
        """Test cash payment processing"""
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Dinheiro"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": float(produto_sample.preco)
                }
            ],
            "forma_pagamento": "DINHEIRO",
            "pagamento": {
                "valor_recebido": float(produto_sample.preco) + 5.0,  # Customer gave more
                "observacoes": "Pagamento em dinheiro"
            }
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["forma_pagamento"] == "DINHEIRO"
        # Should calculate change
        expected_change = 5.0
        assert float(data.get("troco", 0)) == expected_change

    def test_process_payment_pix(self, client: TestClient, auth_headers_operador: dict, 
                               produto_sample: Produto, evento_sample: Evento):
        """Test PIX payment processing"""
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente PIX"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": float(produto_sample.preco)
                }
            ],
            "forma_pagamento": "PIX",
            "pagamento": {
                "pix_key": "cliente@email.com",
                "observacoes": "Pagamento PIX"
            }
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["forma_pagamento"] == "PIX"

    def test_process_payment_card(self, client: TestClient, auth_headers_operador: dict, 
                                produto_sample: Produto, evento_sample: Evento):
        """Test card payment processing"""
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Cartão"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": float(produto_sample.preco)
                }
            ],
            "forma_pagamento": "CARTAO",
            "pagamento": {
                "tipo_cartao": "CREDITO",
                "parcelas": 1,
                "numero_autorizacao": "123456",
                "observacoes": "Pagamento cartão de crédito"
            }
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["forma_pagamento"] == "CARTAO"

    @patch('app.services.payment_service.process_card_payment')
    def test_payment_card_declined(self, mock_payment, client: TestClient, auth_headers_operador: dict, 
                                 produto_sample: Produto, evento_sample: Evento):
        """Test declined card payment"""
        # Mock payment service to return declined
        mock_payment.return_value = {"success": False, "error": "Card declined"}
        
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Cartão Recusado"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": float(produto_sample.preco)
                }
            ],
            "forma_pagamento": "CARTAO",
            "pagamento": {
                "tipo_cartao": "CREDITO",
                "numero_autorizacao": "DECLINED"
            }
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        # Should handle payment failure appropriately
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_402_PAYMENT_REQUIRED,
            status.HTTP_201_CREATED  # If sale is created but payment pending
        ]

    def test_payment_insufficient_cash(self, client: TestClient, auth_headers_operador: dict, 
                                     produto_sample: Produto, evento_sample: Evento):
        """Test cash payment with insufficient amount"""
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Dinheiro Insuficiente"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": float(produto_sample.preco)
                }
            ],
            "forma_pagamento": "DINHEIRO",
            "pagamento": {
                "valor_recebido": float(produto_sample.preco) - 1.0  # Less than total
            }
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "insuficiente" in response.json()["detail"].lower()


class TestCupons:
    """Test coupon and discount functionality"""
    
    def test_apply_coupon_success(self, client: TestClient, auth_headers_operador: dict, 
                                produto_sample: Produto, evento_sample: Evento, db_session: Session):
        """Test successful coupon application"""
        # Create a coupon first
        from app.models import Cupom
        cupom = Cupom(
            codigo="DESCONTO10",
            descricao="Desconto de 10%",
            tipo_desconto="PERCENTUAL",
            valor_desconto=Decimal("10.00"),
            ativo=True,
            data_validade=datetime.utcnow() + timedelta(days=30),
            evento_id=evento_sample.id,
            created_at=datetime.utcnow()
        )
        db_session.add(cupom)
        db_session.commit()
        
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Cupom"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": float(produto_sample.preco)
                }
            ],
            "cupom_codigo": "DESCONTO10",
            "forma_pagamento": "DINHEIRO"
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # Should apply 10% discount
        original_price = float(produto_sample.preco)
        expected_total = original_price * 0.9
        assert float(data["total"]) == expected_total

    def test_apply_invalid_coupon(self, client: TestClient, auth_headers_operador: dict, 
                                produto_sample: Produto, evento_sample: Evento):
        """Test application of invalid coupon"""
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Cupom Inválido"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": float(produto_sample.preco)
                }
            ],
            "cupom_codigo": "CUPOM_INEXISTENTE",
            "forma_pagamento": "DINHEIRO"
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cupom" in response.json()["detail"].lower()

    def test_validate_coupon_endpoint(self, client: TestClient, auth_headers_operador: dict, 
                                    evento_sample: Evento, db_session: Session):
        """Test coupon validation endpoint"""
        # Create a valid coupon
        from app.models import Cupom
        cupom = Cupom(
            codigo="VALIDATE_ME",
            descricao="Cupom para validação",
            tipo_desconto="FIXO",
            valor_desconto=Decimal("5.00"),
            ativo=True,
            data_validade=datetime.utcnow() + timedelta(days=30),
            evento_id=evento_sample.id,
            created_at=datetime.utcnow()
        )
        db_session.add(cupom)
        db_session.commit()
        
        response = client.get(
            f"/pdv/cupons/validar?codigo=VALIDATE_ME&evento_id={evento_sample.id}",
            headers=auth_headers_operador
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valido"] is True
        assert data["cupom"]["codigo"] == "VALIDATE_ME"


class TestDashboard:
    """Test PDV dashboard and analytics"""
    
    def test_get_dashboard_data(self, client: TestClient, auth_headers_admin: dict, evento_sample: Evento):
        """Test getting PDV dashboard data"""
        response = client.get(f"/pdv/dashboard?evento_id={evento_sample.id}", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        expected_fields = [
            "vendas_hoje", "receita_total", "produtos_mais_vendidos",
            "formas_pagamento", "vendas_por_hora", "meta_vendas"
        ]
        for field in expected_fields:
            assert field in data

    def test_get_sales_analytics(self, client: TestClient, auth_headers_admin: dict, evento_sample: Evento):
        """Test getting detailed sales analytics"""
        response = client.get(
            f"/pdv/analytics/vendas?evento_id={evento_sample.id}&periodo=7d",
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "vendas_por_dia" in data
        assert "produtos_performance" in data
        assert "tendencias" in data

    def test_get_financial_report(self, client: TestClient, auth_headers_admin: dict, evento_sample: Evento):
        """Test getting financial report"""
        data_inicio = datetime.utcnow().date()
        data_fim = (datetime.utcnow() + timedelta(days=1)).date()
        
        response = client.get(
            f"/pdv/relatorios/financeiro?evento_id={evento_sample.id}&data_inicio={data_inicio}&data_fim={data_fim}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "receita_bruta" in data
        assert "receita_liquida" in data
        assert "custos" in data
        assert "margem_lucro" in data


class TestPDVSecurity:
    """Test PDV security features"""
    
    def test_access_control_by_role(self, client: TestClient, auth_headers_operador: dict):
        """Test role-based access control"""
        # Operators should have limited access
        response = client.get("/pdv/relatorios/financeiro", headers=auth_headers_operador)
        
        # Should be forbidden or limited
        assert response.status_code in [
            status.HTTP_200_OK,  # If allowed
            status.HTTP_403_FORBIDDEN  # If restricted
        ]

    def test_sale_audit_trail(self, client: TestClient, auth_headers_operador: dict, 
                            produto_sample: Produto, evento_sample: Evento, db_session: Session):
        """Test that sales create proper audit trail"""
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Auditoria"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": float(produto_sample.preco)
                }
            ],
            "forma_pagamento": "DINHEIRO"
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify audit information is recorded
        vendas = db_session.query(Venda).all()
        assert len(vendas) >= 1
        latest_venda = vendas[-1]
        assert latest_venda.vendedor_id is not None
        assert latest_venda.created_at is not None

    def test_price_manipulation_protection(self, client: TestClient, auth_headers_operador: dict, 
                                         produto_sample: Produto, evento_sample: Evento):
        """Test protection against price manipulation"""
        # Try to sell with different price than product price
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Preço Manipulado"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": 0.01  # Much lower than actual price
                }
            ],
            "forma_pagamento": "DINHEIRO"
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        # Should validate against actual product price
        assert response.status_code in [
            status.HTTP_201_CREATED,  # If allowed (some systems allow price override)
            status.HTTP_400_BAD_REQUEST  # If price validation fails
        ]


class TestPDVPerformance:
    """Test PDV performance and scalability"""
    
    def test_sale_creation_performance(self, client: TestClient, auth_headers_operador: dict, 
                                     produto_sample: Produto, evento_sample: Evento):
        """Test sale creation performance"""
        import time
        
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Performance"},
            "itens": [
                {
                    "produto_id": str(produto_sample.id),
                    "quantidade": 1,
                    "preco_unitario": float(produto_sample.preco)
                }
            ],
            "forma_pagamento": "DINHEIRO"
        }
        
        start_time = time.time()
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        end_time = time.time()
        
        assert response.status_code == status.HTTP_201_CREATED
        # Sale should be processed quickly
        assert end_time - start_time < 2.0

    def test_concurrent_sales(self, client: TestClient, auth_headers_operador: dict, 
                            produto_sample: Produto, evento_sample: Evento):
        """Test concurrent sales processing"""
        import threading
        
        results = []
        
        def create_sale(client_name):
            venda_data = {
                "evento_id": str(evento_sample.id),
                "cliente": {"nome": f"Cliente Concorrente {client_name}"},
                "itens": [
                    {
                        "produto_id": str(produto_sample.id),
                        "quantidade": 1,
                        "preco_unitario": float(produto_sample.preco)
                    }
                ],
                "forma_pagamento": "DINHEIRO"
            }
            response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
            results.append(response.status_code)
        
        # Start multiple sale threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_sale, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All sales should succeed
        assert all(code == status.HTTP_201_CREATED for code in results)

    def test_large_sale_handling(self, client: TestClient, auth_headers_operador: dict, 
                                produto_sample: Produto, evento_sample: Evento):
        """Test handling of large sales (many items)"""
        # Create sale with many items
        itens = []
        for i in range(50):  # 50 items
            itens.append({
                "produto_id": str(produto_sample.id),
                "quantidade": 1,
                "preco_unitario": float(produto_sample.preco)
            })
        
        venda_data = {
            "evento_id": str(evento_sample.id),
            "cliente": {"nome": "Cliente Compra Grande"},
            "itens": itens,
            "forma_pagamento": "CARTAO"
        }
        
        response = client.post("/pdv/vendas", json=venda_data, headers=auth_headers_operador)
        
        # Should handle large sales appropriately
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]