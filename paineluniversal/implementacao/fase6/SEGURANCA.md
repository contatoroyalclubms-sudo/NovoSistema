# 🔒 FASE 6: Segurança e Compliance

## 📋 Checklist de Implementação

### 1. Security Hardening

#### 1.1 Input Validation & Sanitization
- [ ] **Arquivo:** `backend/app/security/validation.py`
- [ ] SQL injection protection
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Input sanitization

#### 1.2 Authentication Security
- [ ] **Arquivo:** `backend/app/security/auth_security.py`
- [ ] Password complexity rules
- [ ] Account lockout mechanism
- [ ] Session management
- [ ] Two-factor authentication

#### 1.3 API Security
- [ ] **Arquivo:** `backend/app/security/api_security.py`
- [ ] Rate limiting avançado
- [ ] CORS security
- [ ] Headers de segurança
- [ ] API key management

### 2. Audit System

#### 2.1 Activity Logging
- [ ] **Arquivo:** `backend/app/models/audit.py`
- [ ] User action tracking
- [ ] Data change logs
- [ ] Security event logging
- [ ] Compliance reporting

#### 2.2 Security Monitoring
- [ ] **Arquivo:** `backend/app/security/monitoring.py`
- [ ] Intrusion detection
- [ ] Anomaly detection
- [ ] Alert system
- [ ] Security dashboards

### 3. LGPD/GDPR Compliance

#### 3.1 Data Protection
- [ ] **Arquivo:** `backend/app/services/gdpr_service.py`
- [ ] Data anonymization
- [ ] Right to deletion
- [ ] Data export
- [ ] Consent management

#### 3.2 Privacy Controls
- [ ] **Arquivo:** `backend/app/privacy/controls.py`
- [ ] Data retention policies
- [ ] Access controls
- [ ] Data encryption
- [ ] Privacy by design

## 🛡️ Templates - Security

### Input Validation & Security
```python
# backend/app/security/validation.py
import re
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
import bleach
from pydantic import BaseModel, validator
import sqlalchemy
from sqlalchemy.sql import text

class SecurityValidator:
    """Validador de segurança para inputs"""
    
    # Padrões de validação
    CPF_PATTERN = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$'
    CNPJ_PATTERN = r'^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$'
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_PATTERN = r'^\(\d{2}\)\s\d{4,5}-\d{4}$'
    
    # Lista de palavras proibidas (SQL injection, XSS)
    FORBIDDEN_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
        r'union\s+select',
        r'drop\s+table',
        r'delete\s+from',
        r'insert\s+into',
        r'update\s+.*\s+set',
        r'exec\s*\(',
        r'execute\s*\(',
    ]
    
    @classmethod
    def sanitize_string(cls, value: str) -> str:
        """Sanitizar string removendo conteúdo malicioso"""
        if not value:
            return value
            
        # Remover tags HTML perigosas
        allowed_tags = ['b', 'i', 'u', 'strong', 'em']
        sanitized = bleach.clean(value, tags=allowed_tags, strip=True)
        
        # Verificar padrões proibidos
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Conteúdo não permitido detectado"
                )
        
        return sanitized.strip()
    
    @classmethod
    def validate_cpf(cls, cpf: str) -> bool:
        """Validar CPF"""
        if not re.match(cls.CPF_PATTERN, cpf):
            return False
            
        # Remover pontuação
        numbers = re.sub(r'\D', '', cpf)
        
        # Verificar se não é uma sequência repetida
        if len(set(numbers)) == 1:
            return False
        
        # Algoritmo de validação do CPF
        def calculate_digit(digits: str) -> int:
            sum_digits = sum(int(digit) * (len(digits) + 1 - i) for i, digit in enumerate(digits))
            remainder = sum_digits % 11
            return 0 if remainder < 2 else 11 - remainder
        
        first_digit = calculate_digit(numbers[:9])
        second_digit = calculate_digit(numbers[:10])
        
        return numbers[9] == str(first_digit) and numbers[10] == str(second_digit)
    
    @classmethod
    def validate_cnpj(cls, cnpj: str) -> bool:
        """Validar CNPJ"""
        if not re.match(cls.CNPJ_PATTERN, cnpj):
            return False
            
        numbers = re.sub(r'\D', '', cnpj)
        
        if len(set(numbers)) == 1:
            return False
        
        # Algoritmo de validação do CNPJ
        weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        weights_2 = [6, 7, 8, 9, 2, 3, 4, 5, 6, 7, 8, 9]
        
        def calculate_digit(digits: str, weights: List[int]) -> int:
            sum_digits = sum(int(digit) * weight for digit, weight in zip(digits, weights))
            remainder = sum_digits % 11
            return 0 if remainder < 2 else 11 - remainder
        
        first_digit = calculate_digit(numbers[:12], weights_1)
        second_digit = calculate_digit(numbers[:13], weights_2)
        
        return numbers[12] == str(first_digit) and numbers[13] == str(second_digit)

# Modelo base com validação de segurança
class SecureBaseModel(BaseModel):
    """Modelo base com validações de segurança"""
    
    @validator('*', pre=True)
    def sanitize_strings(cls, v):
        if isinstance(v, str):
            return SecurityValidator.sanitize_string(v)
        return v

# SQL Injection Protection
def safe_query(db_session, query_string: str, params: Dict[str, Any] = None):
    """Executar query de forma segura"""
    try:
        # Usar parâmetros nomeados para prevenir SQL injection
        query = text(query_string)
        result = db_session.execute(query, params or {})
        return result
    except sqlalchemy.exc.SQLAlchemyError as e:
        # Log do erro de segurança
        logger.warning(f"Tentativa de SQL injection detectada: {query_string}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query inválida"
        )
```

### Authentication Security
```python
# backend/app/security/auth_security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets
import pyotp
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from ..models import Usuario, LoginAttempt
from ..database import get_db
import redis

# Cache para tentativas de login
login_cache = redis.Redis(host='localhost', port=6379, db=1)

class AuthSecurity:
    """Sistema de segurança para autenticação"""
    
    # Configurações de segurança
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 30  # minutos
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_COMPLEXITY_REQUIRED = True
    SESSION_TIMEOUT = 30  # minutos
    
    @classmethod
    def validate_password_strength(cls, password: str) -> Dict[str, Any]:
        """Validar força da senha"""
        issues = []
        score = 0
        
        if len(password) < cls.PASSWORD_MIN_LENGTH:
            issues.append(f"Senha deve ter pelo menos {cls.PASSWORD_MIN_LENGTH} caracteres")
        else:
            score += 1
            
        if not re.search(r'[A-Z]', password):
            issues.append("Senha deve conter pelo menos uma letra maiúscula")
        else:
            score += 1
            
        if not re.search(r'[a-z]', password):
            issues.append("Senha deve conter pelo menos uma letra minúscula")
        else:
            score += 1
            
        if not re.search(r'\d', password):
            issues.append("Senha deve conter pelo menos um número")
        else:
            score += 1
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Senha deve conter pelo menos um caractere especial")
        else:
            score += 1
        
        strength_levels = ["Muito Fraca", "Fraca", "Regular", "Boa", "Forte", "Muito Forte"]
        strength = strength_levels[min(score, 5)]
        
        return {
            "valid": len(issues) == 0 if cls.PASSWORD_COMPLEXITY_REQUIRED else score >= 3,
            "score": score,
            "strength": strength,
            "issues": issues
        }
    
    @classmethod
    def check_login_attempts(cls, identifier: str) -> bool:
        """Verificar se usuário está bloqueado por tentativas excessivas"""
        attempts_key = f"login_attempts:{identifier}"
        attempts = login_cache.get(attempts_key)
        
        if attempts and int(attempts) >= cls.MAX_LOGIN_ATTEMPTS:
            return False
        return True
    
    @classmethod
    def record_login_attempt(cls, identifier: str, success: bool, db: Session):
        """Registrar tentativa de login"""
        attempts_key = f"login_attempts:{identifier}"
        
        if success:
            # Limpar tentativas em caso de sucesso
            login_cache.delete(attempts_key)
        else:
            # Incrementar contador de tentativas
            current_attempts = login_cache.get(attempts_key) or 0
            new_attempts = int(current_attempts) + 1
            
            # Definir expiração baseada no número de tentativas
            expire_time = cls.LOCKOUT_DURATION * 60  # converter para segundos
            login_cache.setex(attempts_key, expire_time, new_attempts)
            
            # Registrar no banco para auditoria
            login_attempt = LoginAttempt(
                identifier=identifier,
                success=success,
                ip_address=request.client.host if 'request' in locals() else 'unknown',
                user_agent=request.headers.get('user-agent', 'unknown') if 'request' in locals() else 'unknown',
                timestamp=datetime.utcnow()
            )
            db.add(login_attempt)
            db.commit()
    
    @classmethod
    def generate_2fa_secret(cls) -> str:
        """Gerar segredo para 2FA"""
        return pyotp.random_base32()
    
    @classmethod
    def verify_2fa_token(cls, secret: str, token: str) -> bool:
        """Verificar token 2FA"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    @classmethod
    def generate_recovery_codes(cls, count: int = 10) -> List[str]:
        """Gerar códigos de recuperação"""
        return [secrets.token_hex(4).upper() for _ in range(count)]

# Middleware de segurança de sessão
class SessionSecurityMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Verificar headers de segurança
            headers = dict(scope["headers"])
            
            # Adicionar headers de segurança
            security_headers = {
                b"x-content-type-options": b"nosniff",
                b"x-frame-options": b"DENY",
                b"x-xss-protection": b"1; mode=block",
                b"strict-transport-security": b"max-age=31536000; includeSubDomains",
                b"content-security-policy": b"default-src 'self'",
                b"referrer-policy": b"strict-origin-when-cross-origin"
            }
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    message["headers"].extend(security_headers.items())
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
```

### LGPD Compliance Service
```python
# backend/app/services/gdpr_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..models import Usuario, DataProcessingConsent, DataExportRequest
import json
import hashlib
import logging

logger = logging.getLogger(__name__)

class LGPDService:
    """Serviço de conformidade com LGPD"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_consent(self, user_id: int, purpose: str, consent_given: bool) -> DataProcessingConsent:
        """Registrar consentimento do usuário"""
        consent = DataProcessingConsent(
            user_id=user_id,
            purpose=purpose,
            consent_given=consent_given,
            timestamp=datetime.utcnow(),
            ip_address=self._get_client_ip(),
            user_agent=self._get_user_agent()
        )
        
        self.db.add(consent)
        self.db.commit()
        
        logger.info(f"Consentimento registrado - Usuário: {user_id}, Propósito: {purpose}, Consentimento: {consent_given}")
        return consent
    
    def get_user_data_export(self, user_id: int) -> Dict[str, Any]:
        """Exportar todos os dados do usuário (Art. 15 LGPD)"""
        
        # Registrar solicitação
        export_request = DataExportRequest(
            user_id=user_id,
            requested_at=datetime.utcnow(),
            status='processing'
        )
        self.db.add(export_request)
        self.db.commit()
        
        try:
            # Coletar dados do usuário
            user_data = {
                "personal_info": self._get_personal_info(user_id),
                "transactions": self._get_user_transactions(user_id),
                "checkins": self._get_user_checkins(user_id),
                "consents": self._get_user_consents(user_id),
                "login_history": self._get_login_history(user_id),
                "export_metadata": {
                    "exported_at": datetime.utcnow().isoformat(),
                    "export_id": export_request.id,
                    "data_retention_policy": "Data será mantida por 5 anos após última atividade"
                }
            }
            
            # Atualizar status da solicitação
            export_request.status = 'completed'
            export_request.completed_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Exportação de dados concluída para usuário {user_id}")
            return user_data
            
        except Exception as e:
            export_request.status = 'failed'
            export_request.error_message = str(e)
            self.db.commit()
            logger.error(f"Erro na exportação de dados para usuário {user_id}: {e}")
            raise
    
    def anonymize_user_data(self, user_id: int, reason: str = "user_request") -> bool:
        """Anonimizar dados do usuário (Art. 16 LGPD)"""
        
        try:
            # Gerar hash anônimo baseado no ID
            anonymous_id = hashlib.sha256(f"anonymous_{user_id}_{datetime.utcnow()}".encode()).hexdigest()[:16]
            
            # Anonimizar dados pessoais
            self.db.execute(
                text("""
                UPDATE usuarios 
                SET 
                    nome = :anonymous_name,
                    email = :anonymous_email,
                    cpf = :anonymous_cpf,
                    telefone = :anonymous_phone,
                    endereco = NULL,
                    data_nascimento = NULL,
                    anonimizado = true,
                    anonimizado_em = :timestamp
                WHERE id = :user_id
                """),
                {
                    "anonymous_name": f"Usuário Anônimo {anonymous_id}",
                    "anonymous_email": f"anonimo_{anonymous_id}@exemplo.com",
                    "anonymous_cpf": f"***.***.***-{anonymous_id[:2]}",
                    "anonymous_phone": f"(**) ****-{anonymous_id[:4]}",
                    "timestamp": datetime.utcnow(),
                    "user_id": user_id
                }
            )
            
            # Anonimizar dados relacionados
            self._anonymize_related_data(user_id, anonymous_id)
            
            self.db.commit()
            
            # Log da ação
            logger.info(f"Dados do usuário {user_id} anonimizados. Motivo: {reason}")
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao anonimizar dados do usuário {user_id}: {e}")
            return False
    
    def delete_user_data(self, user_id: int, reason: str = "user_request") -> bool:
        """Deletar dados do usuário (Art. 18 LGPD)"""
        
        try:
            # Verificar se há restrições legais para manter os dados
            if self._has_legal_retention_requirement(user_id):
                # Se há obrigação legal, anonimizar ao invés de deletar
                return self.anonymize_user_data(user_id, f"legal_retention_{reason}")
            
            # Deletar dados relacionados primeiro (devido às foreign keys)
            self._delete_user_related_data(user_id)
            
            # Deletar usuário
            self.db.execute(
                text("DELETE FROM usuarios WHERE id = :user_id"),
                {"user_id": user_id}
            )
            
            self.db.commit()
            
            logger.info(f"Dados do usuário {user_id} deletados. Motivo: {reason}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar dados do usuário {user_id}: {e}")
            return False
    
    def _get_personal_info(self, user_id: int) -> Dict[str, Any]:
        """Obter informações pessoais do usuário"""
        result = self.db.execute(
            text("SELECT * FROM usuarios WHERE id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        
        if result:
            return dict(result._mapping)
        return {}
    
    def _has_legal_retention_requirement(self, user_id: int) -> bool:
        """Verificar se há obrigação legal de manter os dados"""
        # Verificar transações recentes (obrigação fiscal)
        recent_transactions = self.db.execute(
            text("""
            SELECT COUNT(*) as count 
            FROM transacoes 
            WHERE usuario_id = :user_id 
            AND criado_em > :cutoff_date
            """),
            {
                "user_id": user_id,
                "cutoff_date": datetime.utcnow() - timedelta(days=5*365)  # 5 anos
            }
        ).fetchone()
        
        return recent_transactions.count > 0 if recent_transactions else False

# Modelo para auditoria de consentimento
class DataProcessingConsent(Base):
    __tablename__ = "data_processing_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    purpose = Column(String(255), nullable=False)  # marketing, analytics, etc.
    consent_given = Column(Boolean, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    revoked_at = Column(DateTime(timezone=True))
    
    usuario = relationship("Usuario", back_populates="consents")
```

## 🔍 Security Monitoring Dashboard

### Security Dashboard Component
```typescript
// frontend/src/components/security/SecurityDashboard.tsx
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Shield, AlertTriangle, Eye, Lock } from 'lucide-react';

interface SecurityMetrics {
  failedLogins: number;
  blockedIPs: number;
  suspiciousActivity: number;
  dataRequests: number;
}

const SecurityDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<SecurityMetrics | null>(null);
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    loadSecurityMetrics();
    loadSecurityAlerts();
  }, []);

  const loadSecurityMetrics = async () => {
    try {
      const response = await fetch('/api/security/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Erro ao carregar métricas de segurança:', error);
    }
  };

  const loadSecurityAlerts = async () => {
    try {
      const response = await fetch('/api/security/alerts');
      const data = await response.json();
      setAlerts(data);
    } catch (error) {
      console.error('Erro ao carregar alertas de segurança:', error);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold flex items-center">
        <Shield className="mr-2" />
        Dashboard de Segurança
      </h2>

      {/* Métricas de Segurança */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tentativas de Login Falharam</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.failedLogins || 0}</div>
            <p className="text-xs text-muted-foreground">Últimas 24h</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">IPs Bloqueados</CardTitle>
            <Lock className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.blockedIPs || 0}</div>
            <p className="text-xs text-muted-foreground">Atualmente ativos</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Atividade Suspeita</CardTitle>
            <Eye className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.suspiciousActivity || 0}</div>
            <p className="text-xs text-muted-foreground">Eventos detectados</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Solicitações LGPD</CardTitle>
            <Shield className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.dataRequests || 0}</div>
            <p className="text-xs text-muted-foreground">Pendentes</p>
          </CardContent>
        </Card>
      </div>

      {/* Alertas de Segurança */}
      <Card>
        <CardHeader>
          <CardTitle>Alertas de Segurança Recentes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {alerts.map((alert, index) => (
              <Alert key={index} variant={alert.severity === 'high' ? 'destructive' : 'default'}>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <strong>{alert.title}</strong> - {alert.description}
                  <span className="text-xs text-muted-foreground ml-2">
                    {new Date(alert.timestamp).toLocaleString()}
                  </span>
                </AlertDescription>
              </Alert>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SecurityDashboard;
```

## 📊 Cronograma Fase 6

| Tarefa | Estimativa | Status |
|--------|------------|--------|
| Input validation & sanitization | 1 dia | ⏳ |
| Authentication security | 1 dia | ⏳ |
| API security hardening | 1 dia | ⏳ |
| Audit system implementation | 2 dias | ⏳ |
| LGPD compliance service | 2 dias | ⏳ |
| Security monitoring dashboard | 1 dia | ⏳ |

**Total:** 8 dias (1.6 semanas)

## 🎯 Security Compliance Checklist

- [ ] **OWASP Top 10** - Todas as vulnerabilidades mitigadas
- [ ] **LGPD/GDPR** - Conformidade total implementada
- [ ] **Penetration Testing** - Testes de segurança realizados
- [ ] **Security Audit** - Auditoria externa aprovada
- [ ] **Incident Response** - Plano de resposta a incidentes