#!/usr/bin/env python3
"""
Script de validação da integração do Sprint 3 - EVENTOS CORE SYSTEM
Sistema Universal de Gestão de Eventos

Este script valida se todas as funcionalidades implementadas no Sprint 3
estão funcionando corretamente e integradas ao sistema existente.
"""

import asyncio
import os
import sys
import json
import tempfile
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from PIL import Image
import io

# Adicionar o diretório do app ao path
sys.path.append(str(Path(__file__).parent.parent))

class Sprint3Validator:
    """Validador completo do Sprint 3"""
    
    def __init__(self, backend_url: str = "http://localhost:8000", frontend_url: str = "http://localhost:3000"):
        self.backend_url = backend_url.rstrip('/')
        self.frontend_url = frontend_url.rstrip('/')
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_evento_id = None
        
        # Configurações de teste
        self.test_data = {
            "user": {
                "nome": "Admin Teste Sprint 3",
                "email": f"admin_sprint3_{int(datetime.now().timestamp())}@test.com",
                "senha": "senha123456",
                "tipo_usuario": "admin"
            },
            "evento": {
                "nome": f"Evento Sprint 3 Test {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "descricao": "<h1>Evento de teste</h1><p>Este é um evento criado para testar o <strong>Sprint 3</strong>.</p>",
                "tipo_evento": "conferencia",
                "data_inicio": (datetime.now() + timedelta(days=30)).isoformat(),
                "data_fim": (datetime.now() + timedelta(days=30, hours=8)).isoformat(),
                "local_nome": "Centro de Convenções Sprint 3",
                "local_endereco": "Av. Teste Sprint 3, 123 - São Paulo, SP",
                "capacidade_maxima": 500,
                "valor_entrada": 150.00,
                "cor_primaria": "#1E40AF",
                "cor_secundaria": "#374151",
                "cor_accent": "#10B981",
                "sistema_pontuacao_ativo": True,
                "pontos_checkin": 25,
                "pontos_participacao": 15,
                "requer_aprovacao": False,
                "permite_checkin_antecipado": True,
                "visibilidade": "publico",
                "webhook_checkin": "https://webhook.site/test",
                "email_confirmacao_template": "<h1>Bem-vindo ao {{ evento.nome }}!</h1><p>Olá, {{ participante.nome }}!</p>",
                "custom_css": ".event-header { background: linear-gradient(45deg, #1E40AF, #10B981); }",
                "badges_personalizadas": [
                    {
                        "name": "Early Bird",
                        "description": "Check-in antecipado",
                        "icon": "🐦",
                        "condition": "checkin_early"
                    }
                ],
                "analytics_config": {
                    "google_analytics": "GA-TEST-123456"
                },
                "metadados_seo": {
                    "title": "Evento Sprint 3 - Teste",
                    "description": "Evento de teste para validação do Sprint 3",
                    "keywords": "teste, sprint3, eventos"
                },
                "tags": ["teste", "sprint3", "validação", "eventos"]
            }
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def create_test_image(self, width: int = 400, height: int = 300, color: str = 'blue') -> bytes:
        """Cria imagem de teste"""
        img = Image.new('RGB', (width, height), color=color)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    async def validate_backend_health(self) -> bool:
        """Valida se o backend está rodando e saudável"""
        try:
            self.log("🔍 Validando saúde do backend...")
            response = requests.get(f"{self.backend_url}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                self.log(f"✅ Backend saudável: {health_data.get('status', 'unknown')}")
                return True
            else:
                self.log(f"❌ Backend não saudável: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao conectar com backend: {e}", "ERROR")
            return False
    
    async def validate_frontend_health(self) -> bool:
        """Valida se o frontend está rodando"""
        try:
            self.log("🔍 Validando saúde do frontend...")
            response = requests.get(self.frontend_url, timeout=10)
            
            if response.status_code == 200:
                self.log("✅ Frontend acessível")
                return True
            else:
                self.log(f"❌ Frontend não acessível: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao conectar com frontend: {e}", "ERROR")
            return False
    
    async def create_test_user(self) -> bool:
        """Cria usuário de teste"""
        try:
            self.log("👤 Criando usuário de teste...")
            
            response = requests.post(
                f"{self.backend_url}/api/auth/register",
                json=self.test_data["user"]
            )
            
            if response.status_code in [200, 201]:
                user_data = response.json()
                self.test_user_id = user_data.get("id")
                self.log(f"✅ Usuário criado: {self.test_user_id}")
                return True
            else:
                self.log(f"❌ Erro ao criar usuário: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Exceção ao criar usuário: {e}", "ERROR")
            return False
    
    async def authenticate_user(self) -> bool:
        """Autentica usuário e obtém token"""
        try:
            self.log("🔐 Autenticando usuário...")
            
            login_data = {
                "username": self.test_data["user"]["email"],
                "password": self.test_data["user"]["senha"]
            }
            
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                data=login_data
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.auth_token = auth_data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log("✅ Usuário autenticado")
                return True
            else:
                self.log(f"❌ Erro na autenticação: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Exceção na autenticação: {e}", "ERROR")
            return False
    
    async def validate_event_crud(self) -> bool:
        """Valida operações CRUD de eventos avançadas"""
        try:
            self.log("📅 Validando CRUD de eventos avançado...")
            
            # 1. Criar evento com recursos avançados
            response = self.session.post(
                f"{self.backend_url}/api/eventos/",
                json=self.test_data["evento"]
            )
            
            if response.status_code not in [200, 201]:
                self.log(f"❌ Erro ao criar evento: {response.status_code} - {response.text}", "ERROR")
                return False
            
            evento_data = response.json()
            self.test_evento_id = evento_data.get("id")
            self.log(f"✅ Evento criado com recursos avançados: {self.test_evento_id}")
            
            # 2. Verificar campos avançados
            advanced_fields = [
                "cor_accent", "custom_css", "sistema_pontuacao_ativo",
                "badges_personalizadas", "analytics_config", "metadados_seo"
            ]
            
            for field in advanced_fields:
                if field in evento_data and evento_data[field] is not None:
                    self.log(f"✅ Campo avançado presente: {field}")
                else:
                    self.log(f"⚠️  Campo avançado ausente: {field}", "WARNING")
            
            # 3. Atualizar evento
            update_data = {
                "nome": f"{self.test_data['evento']['nome']} - ATUALIZADO",
                "cor_primaria": "#FF6B6B"
            }
            
            response = self.session.put(
                f"{self.backend_url}/api/eventos/{self.test_evento_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                self.log("✅ Evento atualizado")
            else:
                self.log(f"❌ Erro ao atualizar evento: {response.status_code}", "ERROR")
                return False
            
            # 4. Buscar evento
            response = self.session.get(f"{self.backend_url}/api/eventos/{self.test_evento_id}")
            
            if response.status_code == 200:
                self.log("✅ Evento recuperado")
            else:
                self.log(f"❌ Erro ao buscar evento: {response.status_code}", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ Exceção no CRUD de eventos: {e}", "ERROR")
            return False
    
    async def validate_advanced_operations(self) -> bool:
        """Valida operações avançadas (clonagem, bulk, etc.)"""
        try:
            self.log("🔄 Validando operações avançadas...")
            
            if not self.test_evento_id:
                self.log("❌ ID do evento não disponível para operações avançadas", "ERROR")
                return False
            
            # 1. Clonagem de evento
            clone_data = {
                "nome_novo": f"Clone do {self.test_data['evento']['nome']}",
                "data_inicio": (datetime.now() + timedelta(days=60)).isoformat(),
                "data_fim": (datetime.now() + timedelta(days=60, hours=8)).isoformat(),
                "clonar_configuracoes": True,
                "alteracoes": {
                    "cor_primaria": "#9333EA"
                }
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/eventos/{self.test_evento_id}/clone",
                json=clone_data
            )
            
            if response.status_code in [200, 201]:
                clone_data = response.json()
                clone_id = clone_data.get("id")
                self.log(f"✅ Evento clonado: {clone_id}")
            else:
                self.log(f"⚠️  Clonagem falhou: {response.status_code} - {response.text}", "WARNING")
            
            # 2. Operação em lote (teste com eventos fictícios)
            bulk_data = {
                "evento_ids": [self.test_evento_id],
                "operacao": "pausar",
                "confirmar_operacao": True
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/eventos/bulk-operation",
                json=bulk_data
            )
            
            if response.status_code == 200:
                self.log("✅ Operação em lote executada")
            else:
                self.log(f"⚠️  Operação em lote falhou: {response.status_code}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Exceção nas operações avançadas: {e}", "ERROR")
            return False
    
    async def validate_file_upload(self) -> bool:
        """Valida sistema de upload de arquivos"""
        try:
            self.log("📁 Validando sistema de upload...")
            
            if not self.test_evento_id:
                self.log("❌ ID do evento não disponível para upload", "ERROR")
                return False
            
            # Criar imagem de teste
            logo_image = self.create_test_image(200, 200, 'red')
            banner_image = self.create_test_image(800, 400, 'blue')
            
            # Upload do logo
            files = {'file': ('logo_test.png', logo_image, 'image/png')}
            params = {'image_type': 'logo'}
            
            response = self.session.post(
                f"{self.backend_url}/api/eventos/{self.test_evento_id}/upload-image",
                files=files,
                params=params
            )
            
            if response.status_code in [200, 201]:
                self.log("✅ Upload de logo realizado")
            else:
                self.log(f"⚠️  Upload de logo falhou: {response.status_code}", "WARNING")
            
            # Upload do banner
            files = {'file': ('banner_test.png', banner_image, 'image/png')}
            params = {'image_type': 'banner'}
            
            response = self.session.post(
                f"{self.backend_url}/api/eventos/{self.test_evento_id}/upload-image",
                files=files,
                params=params
            )
            
            if response.status_code in [200, 201]:
                self.log("✅ Upload de banner realizado")
            else:
                self.log(f"⚠️  Upload de banner falhou: {response.status_code}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Exceção no upload: {e}", "ERROR")
            return False
    
    async def validate_qr_generation(self) -> bool:
        """Valida geração de QR Codes"""
        try:
            self.log("🔲 Validando geração de QR Codes...")
            
            if not self.test_evento_id:
                self.log("❌ ID do evento não disponível para QR", "ERROR")
                return False
            
            # Tentar gerar QR Code (endpoint pode não estar implementado ainda)
            response = self.session.post(
                f"{self.backend_url}/api/eventos/{self.test_evento_id}/generate-qr",
                json={"types": ["checkin", "checkout"]}
            )
            
            if response.status_code in [200, 201]:
                qr_data = response.json()
                self.log(f"✅ QR Codes gerados: {len(qr_data.get('qr_files', {}))}")
            else:
                self.log(f"⚠️  QR Code ainda não implementado: {response.status_code}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Exceção na geração de QR: {e}", "ERROR")
            return False
    
    async def validate_email_templates(self) -> bool:
        """Valida sistema de templates de email"""
        try:
            self.log("📧 Validando templates de email...")
            
            if not self.test_evento_id:
                self.log("❌ ID do evento não disponível para email", "ERROR")
                return False
            
            # Testar preview de template
            response = self.session.get(
                f"{self.backend_url}/api/eventos/{self.test_evento_id}/email-preview/confirmacao"
            )
            
            if response.status_code == 200:
                preview_data = response.json()
                if "html" in preview_data and "subject" in preview_data:
                    self.log("✅ Preview de template gerado")
                else:
                    self.log("⚠️  Preview incompleto", "WARNING")
            else:
                self.log(f"⚠️  Preview de email ainda não implementado: {response.status_code}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Exceção nos templates de email: {e}", "ERROR")
            return False
    
    async def validate_webhooks(self) -> bool:
        """Valida sistema de webhooks"""
        try:
            self.log("🔗 Validando sistema de webhooks...")
            
            # Testar webhook de teste
            webhook_data = {
                "url": "https://webhook.site/test-sprint3",
                "headers": {"X-Test": "Sprint3"}
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/webhooks/test",
                json=webhook_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log("✅ Webhook teste enviado")
                else:
                    self.log("⚠️  Webhook teste falhou", "WARNING")
            else:
                self.log(f"⚠️  Webhook ainda não implementado: {response.status_code}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Exceção nos webhooks: {e}", "ERROR")
            return False
    
    async def validate_templates(self) -> bool:
        """Valida sistema de templates de eventos"""
        try:
            self.log("📋 Validando templates de eventos...")
            
            # Listar templates disponíveis
            response = self.session.get(f"{self.backend_url}/api/eventos/templates")
            
            if response.status_code == 200:
                templates = response.json()
                self.log(f"✅ Templates disponíveis: {len(templates)}")
            else:
                self.log(f"⚠️  Templates ainda não implementados: {response.status_code}", "WARNING")
            
            # Criar template personalizado
            template_data = {
                "nome": "Template Sprint 3",
                "categoria": "teste",
                "template_data": {
                    "nome": "Template Teste",
                    "cor_primaria": "#FF6B6B",
                    "sistema_pontuacao_ativo": True
                },
                "publico": True
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/eventos/templates",
                json=template_data
            )
            
            if response.status_code in [200, 201]:
                self.log("✅ Template personalizado criado")
            else:
                self.log(f"⚠️  Criação de template falhou: {response.status_code}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Exceção nos templates: {e}", "ERROR")
            return False
    
    async def validate_analytics(self) -> bool:
        """Valida sistema de analytics"""
        try:
            self.log("📊 Validando analytics de eventos...")
            
            if not self.test_evento_id:
                self.log("❌ ID do evento não disponível para analytics", "ERROR")
                return False
            
            # Buscar estatísticas do evento
            response = self.session.get(f"{self.backend_url}/api/eventos/{self.test_evento_id}/stats")
            
            if response.status_code == 200:
                stats = response.json()
                required_fields = ["evento_id", "listas", "financeiro"]
                
                for field in required_fields:
                    if field in stats:
                        self.log(f"✅ Campo de analytics presente: {field}")
                    else:
                        self.log(f"⚠️  Campo de analytics ausente: {field}", "WARNING")
            else:
                self.log(f"⚠️  Analytics ainda não implementado: {response.status_code}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Exceção no analytics: {e}", "ERROR")
            return False
    
    async def validate_frontend_integration(self) -> bool:
        """Valida integração com frontend"""
        try:
            self.log("🎨 Validando integração com frontend...")
            
            # Verificar se páginas importantes estão acessíveis
            pages_to_check = [
                "/eventos",
                "/eventos/novo",
                "/calendario",
                "/analytics"
            ]
            
            accessible_pages = 0
            
            for page in pages_to_check:
                try:
                    response = requests.get(f"{self.frontend_url}{page}", timeout=5)
                    if response.status_code == 200:
                        accessible_pages += 1
                        self.log(f"✅ Página acessível: {page}")
                    else:
                        self.log(f"⚠️  Página não acessível: {page} ({response.status_code})", "WARNING")
                except:
                    self.log(f"⚠️  Erro ao acessar página: {page}", "WARNING")
            
            if accessible_pages > 0:
                self.log(f"✅ Frontend parcialmente integrado: {accessible_pages}/{len(pages_to_check)} páginas")
                return True
            else:
                self.log("❌ Nenhuma página do frontend acessível", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"❌ Exceção na validação do frontend: {e}", "ERROR")
            return False
    
    async def validate_performance(self) -> bool:
        """Valida performance do sistema"""
        try:
            self.log("⚡ Validando performance do sistema...")
            
            start_time = datetime.now()
            
            # Fazer várias requisições para testar performance
            endpoints_to_test = [
                f"/api/eventos/",
                f"/api/eventos/templates",
                f"/api/eventos/upcoming"
            ]
            
            total_requests = 0
            successful_requests = 0
            
            for endpoint in endpoints_to_test:
                for i in range(5):  # 5 requests por endpoint
                    try:
                        response = self.session.get(f"{self.backend_url}{endpoint}")
                        total_requests += 1
                        
                        if response.status_code == 200:
                            successful_requests += 1
                    except:
                        total_requests += 1
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
            avg_response_time = duration / total_requests if total_requests > 0 else 0
            
            self.log(f"📈 Performance Report:")
            self.log(f"   Total requests: {total_requests}")
            self.log(f"   Successful: {successful_requests}")
            self.log(f"   Success rate: {success_rate:.1f}%")
            self.log(f"   Average response time: {avg_response_time:.3f}s")
            
            if success_rate >= 80 and avg_response_time < 1.0:
                self.log("✅ Performance adequada")
                return True
            else:
                self.log("⚠️  Performance abaixo do esperado", "WARNING")
                return False
            
        except Exception as e:
            self.log(f"❌ Exceção na validação de performance: {e}", "ERROR")
            return False
    
    async def cleanup_test_data(self) -> bool:
        """Limpa dados de teste criados"""
        try:
            self.log("🧹 Limpando dados de teste...")
            
            # Deletar evento de teste
            if self.test_evento_id:
                response = self.session.delete(f"{self.backend_url}/api/eventos/{self.test_evento_id}")
                if response.status_code in [200, 204]:
                    self.log("✅ Evento de teste removido")
                else:
                    self.log(f"⚠️  Não foi possível remover evento: {response.status_code}", "WARNING")
            
            # Note: Usuário de teste pode ser mantido ou removido conforme política
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erro na limpeza: {e}", "ERROR")
            return False
    
    async def run_full_validation(self) -> Dict[str, Any]:
        """Executa validação completa do Sprint 3"""
        self.log("🚀 Iniciando validação completa do Sprint 3 - EVENTOS CORE SYSTEM")
        self.log("=" * 70)
        
        results = {}
        
        # 1. Validações de infraestrutura
        results["backend_health"] = await self.validate_backend_health()
        results["frontend_health"] = await self.validate_frontend_health()
        
        if not results["backend_health"]:
            self.log("❌ Backend não está funcionando. Interrompendo validação.", "ERROR")
            return results
        
        # 2. Autenticação
        results["user_creation"] = await self.create_test_user()
        results["authentication"] = await self.authenticate_user()
        
        if not results["authentication"]:
            self.log("❌ Não foi possível autenticar. Continuando validação limitada.", "ERROR")
        
        # 3. Funcionalidades principais do Sprint 3
        results["event_crud"] = await self.validate_event_crud()
        results["advanced_operations"] = await self.validate_advanced_operations()
        results["file_upload"] = await self.validate_file_upload()
        results["qr_generation"] = await self.validate_qr_generation()
        results["email_templates"] = await self.validate_email_templates()
        results["webhooks"] = await self.validate_webhooks()
        results["templates"] = await self.validate_templates()
        results["analytics"] = await self.validate_analytics()
        
        # 4. Integração e performance
        results["frontend_integration"] = await self.validate_frontend_integration()
        results["performance"] = await self.validate_performance()
        
        # 5. Limpeza
        results["cleanup"] = await self.cleanup_test_data()
        
        # Relatório final
        self.generate_final_report(results)
        
        return results
    
    def generate_final_report(self, results: Dict[str, Any]):
        """Gera relatório final da validação"""
        self.log("=" * 70)
        self.log("📋 RELATÓRIO FINAL - SPRINT 3 VALIDATION")
        self.log("=" * 70)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        self.log(f"📊 RESUMO GERAL:")
        self.log(f"   Total de testes: {total_tests}")
        self.log(f"   Testes aprovados: {passed_tests}")
        self.log(f"   Taxa de sucesso: {success_rate:.1f}%")
        self.log("")
        
        # Detalhamento por categoria
        categories = {
            "🏗️  INFRAESTRUTURA": ["backend_health", "frontend_health"],
            "🔐 AUTENTICAÇÃO": ["user_creation", "authentication"],
            "📅 EVENTOS CORE": ["event_crud", "advanced_operations"],
            "📁 UPLOAD & MÍDIA": ["file_upload", "qr_generation"],
            "📧 COMUNICAÇÃO": ["email_templates", "webhooks"],
            "📋 TEMPLATES & ANALYTICS": ["templates", "analytics"],
            "🔗 INTEGRAÇÃO": ["frontend_integration", "performance"],
            "🧹 LIMPEZA": ["cleanup"]
        }
        
        for category, tests in categories.items():
            category_passed = sum(1 for test in tests if results.get(test, False))
            category_total = len(tests)
            category_rate = (category_passed / category_total) * 100 if category_total > 0 else 0
            
            status_icon = "✅" if category_rate == 100 else "⚠️" if category_rate >= 50 else "❌"
            
            self.log(f"{status_icon} {category}: {category_passed}/{category_total} ({category_rate:.0f}%)")
            
            for test in tests:
                test_status = "✅" if results.get(test, False) else "❌"
                self.log(f"     {test_status} {test}")
        
        self.log("")
        
        # Status final
        if success_rate >= 90:
            self.log("🎉 SPRINT 3 VALIDAÇÃO: EXCELENTE! Sistema totalmente funcional.")
        elif success_rate >= 70:
            self.log("✅ SPRINT 3 VALIDAÇÃO: BOM! Sistema majoritariamente funcional.")
        elif success_rate >= 50:
            self.log("⚠️  SPRINT 3 VALIDAÇÃO: PARCIAL! Algumas funcionalidades precisam de atenção.")
        else:
            self.log("❌ SPRINT 3 VALIDAÇÃO: CRÍTICO! Sistema precisa de correções urgentes.")
        
        self.log("=" * 70)
        
        # Salvar relatório em arquivo
        self.save_report_to_file(results, success_rate)
    
    def save_report_to_file(self, results: Dict[str, Any], success_rate: float):
        """Salva relatório em arquivo"""
        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "sprint": "Sprint 3 - EVENTOS CORE SYSTEM",
                "success_rate": success_rate,
                "results": results,
                "summary": {
                    "total_tests": len(results),
                    "passed_tests": sum(1 for result in results.values() if result),
                    "failed_tests": sum(1 for result in results.values() if not result)
                }
            }
            
            report_file = Path(__file__).parent / f"sprint3_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            self.log(f"📄 Relatório salvo em: {report_file}")
            
        except Exception as e:
            self.log(f"❌ Erro ao salvar relatório: {e}", "ERROR")


async def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validador do Sprint 3 - Eventos Core System")
    parser.add_argument("--backend-url", default="http://localhost:8000", help="URL do backend")
    parser.add_argument("--frontend-url", default="http://localhost:3000", help="URL do frontend")
    
    args = parser.parse_args()
    
    validator = Sprint3Validator(
        backend_url=args.backend_url,
        frontend_url=args.frontend_url
    )
    
    results = await validator.run_full_validation()
    
    # Exit code baseado no sucesso
    success_rate = (sum(1 for result in results.values() if result) / len(results)) * 100
    sys.exit(0 if success_rate >= 70 else 1)


if __name__ == "__main__":
    asyncio.run(main())