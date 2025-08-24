
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Event, User, Transaction

client = TestClient(app)

class TestSplitPayments:
    def test_create_split_rule(self):
        response = client.post("/api/split-rules/1", json={
            "rules": [
                {"participant_id": 1, "percentage": 70},
                {"participant_id": 2, "percentage": 30}
            ]
        })
        assert response.status_code == 200
    
    def test_process_split_payment(self):
        response = client.post("/api/process-split/1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 1
    
    def test_process_refund(self):
        response = client.post("/api/refund/1", json={
            "reason": "Customer request"
        })
        assert response.status_code == 200

class TestPerformance:
    def test_api_response_time(self):
        import time
        start = time.time()
        response = client.get("/api/eventos")
        elapsed = time.time() - start
        assert elapsed < 0.05  # Sub 50ms
        assert response.status_code == 200
    
    def test_concurrent_requests(self):
        import concurrent.futures
        
        def make_request():
            return client.get("/api/eventos")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            results = [f.result() for f in futures]
        
        assert all(r.status_code == 200 for r in results)

class TestSecurity:
    def test_jwt_required(self):
        response = client.get("/api/admin/users")
        assert response.status_code == 401
    
    def test_sql_injection_protection(self):
        response = client.get("/api/eventos?id=1' OR '1'='1")
        assert response.status_code == 422
    
    def test_xss_protection(self):
        response = client.post("/api/eventos", json={
            "nome": "<script>alert('xss')</script>"
        })
        data = response.json()
        assert "<script>" not in str(data)
