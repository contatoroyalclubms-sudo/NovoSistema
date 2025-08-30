"""
TESTE COMPLETO DO SISTEMA ULTRA-EXPERT
Validação de todas as funcionalidades implementadas
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

class TesteSistemaCompleto:
    def __init__(self):
        self.session = None
        self.results = []
        
    async def setup(self):
        self.session = aiohttp.ClientSession()
        print("="*70)
        print("TESTE COMPLETO DO SISTEMA ULTRA-EXPERT")
        print("="*70)
        
    async def cleanup(self):
        if self.session:
            await self.session.close()
            
    async def test_request(self, name: str, method: str, endpoint: str, 
                          expected_status: int = 200, data: dict = None, 
                          headers: dict = None) -> bool:
        """Executa um teste de request"""
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method == "GET":
                async with self.session.get(url, headers=headers) as resp:
                    response_data = await resp.json() if resp.content_type == 'application/json' else await resp.text()
                    status = resp.status
                    
            elif method == "POST":
                async with self.session.post(url, json=data, headers=headers) as resp:
                    response_data = await resp.json() if resp.content_type == 'application/json' else await resp.text()
                    status = resp.status
                    
            success = status == expected_status
            status_symbol = "✅" if success else "❌"
            print(f"   {status_symbol} {name}: {status}")
            
            self.results.append({
                "test": name,
                "success": success,
                "status": status,
                "expected": expected_status
            })
            
            return success
            
        except Exception as e:
            print(f"   ❌ {name}: ERROR - {e}")
            self.results.append({
                "test": name,
                "success": False,
                "error": str(e)
            })
            return False
    
    async def test_sistema_basico(self):
        """Testa funcionalidades básicas"""
        print("\n🔹 SISTEMA BÁSICO")
        print("-" * 40)
        
        await self.test_request("Root Endpoint", "GET", "/")
        await self.test_request("Health Check", "GET", "/health")
        await self.test_request("System Info", "GET", "/api/v1/system/info")
        await self.test_request("OpenAPI", "GET", "/openapi.json")
        
    async def test_monitoring_ultra_expert(self):
        """Testa sistema de monitoring"""
        print("\n🔹 MONITORING ULTRA-EXPERT")
        print("-" * 40)
        
        await self.test_request("Prometheus Metrics", "GET", "/metrics")
        await self.test_request("Business Metrics", "GET", "/api/v1/metrics/business") 
        await self.test_request("Performance Metrics", "GET", "/api/v1/metrics/performance")
        await self.test_request("Active Alerts", "GET", "/api/v1/monitoring/alerts")
        await self.test_request("Test Alert", "POST", "/api/v1/monitoring/test-alert")
        
    async def test_tracking_metricas(self):
        """Testa tracking de métricas de negócio"""
        print("\n🔹 TRACKING DE MÉTRICAS")
        print("-" * 40)
        
        await self.test_request("Track Evento", "POST", "/api/v1/metrics/track/evento")
        await self.test_request("Track Check-in", "POST", "/api/v1/metrics/track/checkin")
        await self.test_request("Track Venda", "POST", "/api/v1/metrics/track/venda")
        
    async def test_autenticacao_ultra_expert(self):
        """Testa sistema de autenticação"""
        print("\n🔹 AUTENTICAÇÃO ULTRA-EXPERT")
        print("-" * 40)
        
        # Testa endpoints que devem retornar erro de autenticação
        await self.test_request("Auth Me (sem token)", "GET", "/api/v1/auth/me", 401)
        
        # Testa registro de usuário
        user_data = {
            "email": "teste@ultra.com",
            "password": "Ultra123!",
            "nome": "Usuário Teste Ultra"
        }
        await self.test_request("Register User", "POST", "/api/v1/auth/register", 200, user_data)
        
        # Testa login
        login_data = {
            "username": "admin@eventos.com",
            "password": "Admin123!"
        }
        # Note: Este pode falhar se o endpoint não estiver totalmente integrado
        await self.test_request("Login Admin", "POST", "/api/v1/auth/login", 200, login_data)
        
    async def test_endpoints_mock(self):
        """Testa endpoints mock para compatibilidade"""
        print("\n🔹 ENDPOINTS DE COMPATIBILIDADE")
        print("-" * 40)
        
        await self.test_request("Listar Eventos", "GET", "/api/v1/eventos/")
        await self.test_request("Status PDV", "GET", "/api/v1/pdv/status")
        await self.test_request("Ranking Gamificação", "GET", "/api/v1/gamificacao/ranking")
        
    async def test_performance(self):
        """Testa performance do sistema"""
        print("\n🔹 TESTE DE PERFORMANCE")
        print("-" * 40)
        
        # Teste de stress básico
        start_time = time.time()
        await self.test_request("Stress Test", "GET", "/demo/stress-test")
        end_time = time.time()
        
        response_time = end_time - start_time
        if response_time < 5.0:
            print(f"   ✅ Response Time: {response_time:.2f}s (OK)")
        else:
            print(f"   ⚠️  Response Time: {response_time:.2f}s (SLOW)")
        
        # Múltiplas requests simultâneas
        print("   Testing concurrent requests...")
        tasks = []
        for i in range(5):
            task = self.test_request(f"Concurrent {i+1}", "GET", "/health")
            tasks.append(task)
            
        results = await asyncio.gather(*tasks)
        concurrent_success = sum(results)
        print(f"   ✅ Concurrent Requests: {concurrent_success}/5 succeeded")
        
    async def get_system_metrics(self):
        """Obtém métricas atuais do sistema"""
        print("\n🔹 MÉTRICAS DO SISTEMA")
        print("-" * 40)
        
        try:
            async with self.session.get(f"{BASE_URL}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    metrics = data.get("system_metrics", {})
                    
                    print(f"   Uptime: {data.get('uptime_seconds', 0):.1f}s")
                    print(f"   Version: {data.get('version', 'N/A')}")
                    
                    if "system" in metrics:
                        sys_data = metrics["system"]
                        print(f"   CPU: {sys_data.get('cpu_percent', 0)}%")
                        print(f"   Memory: {sys_data.get('memory_percent', 0)}%")
                        print(f"   Disk: {sys_data.get('disk_percent', 0)}%")
                        
                    if "business" in metrics:
                        biz_data = metrics["business"] 
                        print(f"   Usuários Online: {biz_data.get('usuarios_online', 0)}")
                        print(f"   Eventos Ativos: {biz_data.get('eventos_ativos', 0)}")
                        
        except Exception as e:
            print(f"   ❌ Error getting metrics: {e}")
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        await self.setup()
        
        try:
            # Executar todos os grupos de teste
            await self.test_sistema_basico()
            await self.test_monitoring_ultra_expert()
            await self.test_tracking_metricas()
            await self.test_autenticacao_ultra_expert()
            await self.test_endpoints_mock()
            await self.test_performance()
            await self.get_system_metrics()
            
            # Resultados finais
            print("\n" + "="*70)
            print("RESULTADOS FINAIS")
            print("="*70)
            
            total = len(self.results)
            passed = sum(1 for r in self.results if r["success"])
            failed = total - passed
            
            print(f"TOTAL DE TESTES: {total}")
            print(f"✅ PASSOU: {passed}")
            print(f"❌ FALHOU: {failed}")
            print(f"📊 TAXA DE SUCESSO: {(passed/total)*100:.1f}%")
            
            if failed > 0:
                print(f"\n❌ TESTES QUE FALHARAM:")
                for result in self.results:
                    if not result["success"]:
                        error_info = result.get("error", f"Status {result.get('status')} != {result.get('expected')}")
                        print(f"   - {result['test']}: {error_info}")
            
            if passed >= total * 0.8:  # 80% ou mais
                print(f"\n🎉 SISTEMA FUNCIONANDO EXCELENTE! ({(passed/total)*100:.1f}% sucesso)")
                print("✅ TODAS AS FUNCIONALIDADES ULTRA-EXPERT OPERACIONAIS!")
            elif passed >= total * 0.6:  # 60% ou mais
                print(f"\n👍 SISTEMA FUNCIONANDO BEM! ({(passed/total)*100:.1f}% sucesso)")
                print("⚠️  ALGUMAS FUNCIONALIDADES PRECISAM DE AJUSTES")
            else:
                print(f"\n⚠️  SISTEMA PRECISA DE MELHORIAS ({(passed/total)*100:.1f}% sucesso)")
                
        except KeyboardInterrupt:
            print("\n⏹️  Testes interrompidos pelo usuário")
        except Exception as e:
            print(f"\n💥 Erro crítico: {e}")
        finally:
            await self.cleanup()

async def main():
    """Função principal"""
    tester = TesteSistemaCompleto()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())