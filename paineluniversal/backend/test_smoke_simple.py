"""
SMOKE TESTS ULTRA-EXPERT - Sistema Universal de Gestao de Eventos
Versao simplificada sem emojis para compatibilidade Windows
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

class SmokeTests:
    def __init__(self):
        self.session = None
        self.total = 0
        self.passed = 0
        self.failed = 0
        
    async def setup(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TIMEOUT))
        print("=== SMOKE TESTS ULTRA-EXPERT ===")
        
    async def cleanup(self):
        if self.session:
            await self.session.close()
        print("\n=== RESULTADOS ===")
        print(f"TOTAL: {self.total}")
        print(f"PASSOU: {self.passed}")
        print(f"FALHOU: {self.failed}")
        print(f"TAXA SUCESSO: {(self.passed/self.total)*100:.1f}%")
        return self.failed == 0
        
    async def test(self, name, method, endpoint, expected=200, data=None):
        self.total += 1
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method == "GET":
                async with self.session.get(url) as resp:
                    status = resp.status
            elif method == "POST":
                async with self.session.post(url, json=data) as resp:
                    status = resp.status
                    
            if status == expected:
                self.passed += 1
                print(f"PASS: {name} ({status})")
            else:
                self.failed += 1
                print(f"FAIL: {name} ({status}, esperado {expected})")
                
        except Exception as e:
            self.failed += 1
            print(f"ERROR: {name} - {e}")
    
    async def run_all(self):
        await self.setup()
        
        # Endpoints basicos
        print("\n--- ENDPOINTS BASICOS ---")
        await self.test("Root", "GET", "/")
        await self.test("Health", "GET", "/health")
        await self.test("System Info", "GET", "/api/v1/system/info")
        
        # Monitoring
        print("\n--- MONITORING ---")
        await self.test("Metrics", "GET", "/metrics")
        await self.test("Business Metrics", "GET", "/api/v1/metrics/business")
        await self.test("Performance", "GET", "/api/v1/metrics/performance")
        await self.test("Alerts", "GET", "/api/v1/monitoring/alerts")
        
        # Tracking
        await self.test("Track Evento", "POST", "/api/v1/metrics/track/evento",
                       data={"tipo_evento": "test", "organizador_tipo": "test"})
        
        # Auth (should fail)
        print("\n--- AUTENTICACAO ---")
        await self.test("Login Fail", "POST", "/api/v1/auth/login", 422,
                       data={"username": "test", "password": "test"})
        await self.test("Auth Me", "GET", "/api/v1/auth/me", 401)
        
        # Eventos
        print("\n--- EVENTOS ---")
        await self.test("Listar Eventos", "GET", "/api/v1/eventos/")
        
        # PDV
        print("\n--- PDV ---")
        await self.test("Status PDV", "GET", "/api/v1/pdv/status")
        
        # Gamificacao
        print("\n--- GAMIFICACAO ---")
        await self.test("Ranking", "GET", "/api/v1/gamificacao/ranking")
        
        return await self.cleanup()

async def main():
    tester = SmokeTests()
    success = await tester.run_all()
    
    if success:
        print("\nTODOS OS TESTES PASSARAM!")
    else:
        print("\nALGUNS TESTES FALHARAM!")
        
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)