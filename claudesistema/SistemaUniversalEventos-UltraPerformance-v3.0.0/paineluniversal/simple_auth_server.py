import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime, timedelta

PORT = 8001

class TestAuthHandler(http.server.BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def _send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/':
            self._send_json_response({
                "message": "Simple Test Auth API",
                "status": "running"
            })
        elif self.path == '/api/v1/auth/me':
            # Simular endpoint protegido
            auth_header = self.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                self._send_json_response({
                    "id": "1",
                    "email": "admin@teste.com",
                    "name": "Administrador",
                    "role": "admin",
                    "is_active": True,
                    "created_at": "2024-01-01T10:00:00Z",
                    "updated_at": "2024-01-01T10:00:00Z"
                })
            else:
                self._send_json_response({"detail": "Token não fornecido"}, 401)
        else:
            self._send_json_response({"detail": "Endpoint não encontrado"}, 404)
    
    def do_POST(self):
        if self.path == '/api/v1/auth/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                # Aceitar tanto email quanto username
                email = data.get('email') or data.get('username')
                password = data.get('password')
                
                if email == 'admin@teste.com' and password == '123456':
                    self._send_json_response({
                        "access_token": "test-access-token-123",
                        "refresh_token": "test-refresh-token-456",
                        "token_type": "bearer",
                        "user": {
                            "id": 1,
                            "username": "admin",
                            "email": "admin@teste.com",
                            "full_name": "Administrador",
                            "is_active": True,
                            "is_superuser": True,
                            "created_at": "2024-01-01T10:00:00Z",
                            "updated_at": "2024-01-01T10:00:00Z"
                        }
                    })
                else:
                    self._send_json_response({
                        "detail": "Email ou senha incorretos"
                    }, 401)
            except:
                self._send_json_response({
                    "detail": "Dados inválidos"
                }, 400)
        
        elif self.path == '/api/v1/auth/refresh':
            # Simular refresh token
            self._send_json_response({
                "access_token": "test-access-token-new-123",
                "refresh_token": "test-refresh-token-new-456",
                "token_type": "bearer"
            })
        else:
            self._send_json_response({"detail": "Endpoint não encontrado"}, 404)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), TestAuthHandler) as httpd:
        print(f"Simple Test Auth API rodando na porta {PORT}")
        print(f"Acesse: http://localhost:{PORT}")
        print("Credenciais de teste: admin@teste.com / 123456")
        print("Pressione Ctrl+C para parar")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nParando servidor...")
            httpd.shutdown()
