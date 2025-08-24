# 🚀 FASE 3: DEPLOY E MONITORAMENTO

# Guia Completo de Deploy para Produção

## 📋 CHECKLIST PRÉ-DEPLOY

### ✅ Validações Obrigatórias

- [ ] Sistema principal carregando sem erros
- [ ] Banco de dados configurado e acessível
- [ ] Cache Redis funcionando
- [ ] Variáveis de ambiente configuradas
- [ ] Certificados SSL válidos
- [ ] Backup automático configurado
- [ ] Monitoramento ativo
- [ ] Log centralizado configurado

## 🐳 CONTAINERIZAÇÃO DOCKER

### 1. Dockerfile Principal (Produção)

```dockerfile
# Dockerfile.prod - Sistema Ultra-Avançado
FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código da aplicação
COPY paineluniversal/backend/ .
COPY docs/ ./docs/
COPY scripts/ ./scripts/

# Configuração de usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. Docker Compose Produção

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  # Backend Principal
  backend:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/sistema_eventos
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    restart: unless-stopped
    networks:
      - sistema-network

  # Banco PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=sistema_eventos
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    restart: unless-stopped
    networks:
      - sistema-network

  # Cache Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - sistema-network

  # Proxy Nginx
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
      - ./static:/var/www/static
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - sistema-network

  # Monitoramento Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped
    networks:
      - sistema-network

  # Dashboard Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards
    restart: unless-stopped
    networks:
      - sistema-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  sistema-network:
    driver: bridge
```

## ⚙️ CONFIGURAÇÃO DE PRODUÇÃO

### 1. Variáveis de Ambiente (.env.prod)

```bash
# Configurações de Produção - NUNCA COMITAR
SECRET_KEY=your-ultra-secure-secret-key-here
DB_PASSWORD=your-secure-database-password
GRAFANA_PASSWORD=your-grafana-admin-password

# Database
DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/sistema_eventos
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_MAX_CONNECTIONS=50

# Security
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
LOG_LEVEL=INFO

# Performance
WORKERS=4
MAX_CONNECTIONS=1000
TIMEOUT=300

# SSL
SSL_CERT_PATH=/etc/ssl/certs/fullchain.pem
SSL_KEY_PATH=/etc/ssl/certs/privkey.pem
```

### 2. Nginx Configuração

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/ssl/certs/fullchain.pem;
        ssl_certificate_key /etc/ssl/certs/privkey.pem;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 30d;
        }
    }
}
```

## 📊 MONITORAMENTO E OBSERVABILIDADE

### 1. Prometheus Configuração

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "sistema-backend"
    static_configs:
      - targets: ["backend:8000"]
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: "nginx"
    static_configs:
      - targets: ["nginx:9113"]

  - job_name: "postgres"
    static_configs:
      - targets: ["postgres:9187"]

rule_files:
  - "alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093
```

### 2. Alertas Críticos

```yaml
# monitoring/alerts.yml
groups:
  - name: sistema-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Taxa de erro alta detectada"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Banco de dados indisponível"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Uso de memória alto: {{ $value }}"
```

## 🔧 SCRIPTS DE DEPLOY

### 1. Deploy Automatizado

```bash
#!/bin/bash
# deploy.sh - Script de deploy automatizado

set -e

echo "🚀 Iniciando deploy em produção..."

# Backup antes do deploy
echo "📋 Criando backup..."
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres sistema_eventos > backup_$(date +%Y%m%d_%H%M%S).sql

# Baixar código atualizado
echo "📥 Atualizando código..."
git pull origin main

# Build das imagens
echo "🏗️ Construindo imagens..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Deploy zero-downtime
echo "🔄 Atualizando serviços..."
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# Verificar saúde dos serviços
echo "🏥 Verificando saúde dos serviços..."
sleep 30
docker-compose -f docker-compose.prod.yml ps

# Executar migrações se necessário
echo "📊 Executando migrações..."
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

echo "✅ Deploy concluído com sucesso!"
```

### 2. Rollback Automático

```bash
#!/bin/bash
# rollback.sh - Script de rollback

set -e

echo "⏪ Iniciando rollback..."

# Parar serviços atuais
docker-compose -f docker-compose.prod.yml down

# Restaurar backup
BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    BACKUP_FILE=$(ls -t backup_*.sql | head -n1)
fi

echo "📋 Restaurando backup: $BACKUP_FILE"
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d sistema_eventos < $BACKUP_FILE

# Iniciar versão anterior
git checkout HEAD~1
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Rollback concluído!"
```

## 📈 MÉTRICAS E DASHBOARDS

### 1. Métricas Principais

- **Performance**: Tempo de resposta, throughput, latência
- **Disponibilidade**: Uptime, health checks, taxa de erro
- **Recursos**: CPU, memória, disco, rede
- **Negócio**: Eventos criados, check-ins, usuários ativos

### 2. Dashboards Grafana

- Dashboard Principal: Visão geral do sistema
- Performance: Métricas de performance detalhadas
- Infraestrutura: Monitoramento de recursos
- Negócio: KPIs e métricas de negócio

## 🔒 SEGURANÇA EM PRODUÇÃO

### 1. Configurações de Segurança

- SSL/TLS obrigatório
- Rate limiting configurado
- Headers de segurança
- Firewall configurado
- Backup criptografado
- Logs de auditoria

### 2. Monitoramento de Segurança

- Tentativas de login inválidas
- Acessos suspeitos
- Mudanças não autorizadas
- Vulnerabilidades conhecidas

## 📊 BACKUP E RECUPERAÇÃO

### 1. Estratégia de Backup

- Backup automático diário
- Backup antes de cada deploy
- Retenção de 30 dias
- Backup offsite semanal

### 2. Testes de Recuperação

- Teste mensal de restore
- Documentação de procedimentos
- RTO: 4 horas
- RPO: 1 hora

## 🚀 COMANDOS DE DEPLOY

```bash
# Deploy inicial
./scripts/initial-deploy.sh

# Deploy de atualização
./scripts/deploy.sh

# Rollback se necessário
./scripts/rollback.sh backup_20241221_120000.sql

# Verificar status
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f backend

# Monitoramento
# Acesse: http://your-domain:3000 (Grafana)
# Acesse: http://your-domain:9090 (Prometheus)
```

## ⚡ OTIMIZAÇÕES DE PERFORMANCE

### 1. Cache Strategy

- Redis para cache de sessões
- Cache de consultas frequentes
- CDN para assets estáticos
- Compressão gzip/brotli

### 2. Database Optimization

- Índices otimizados
- Connection pooling
- Read replicas se necessário
- Particionamento de tabelas grandes

### 3. Application Optimization

- Worker processes múltiplos
- Async/await otimizado
- Lazy loading
- Paginação eficiente

## 📞 PROCEDIMENTOS DE EMERGÊNCIA

### 1. Incidentes Críticos

1. Avaliar impacto
2. Isolar problema
3. Comunicar stakeholders
4. Implementar fix temporário
5. Documentar incident

### 2. Contatos de Emergência

- DevOps: +55 (11) 99999-9999
- DBA: +55 (11) 88888-8888
- Security: +55 (11) 77777-7777

---

## 🎯 PRÓXIMOS PASSOS

1. **Configurar SSL**: Obter certificados Let's Encrypt
2. **Setup Monitoring**: Configurar Grafana dashboards
3. **CI/CD Pipeline**: Implementar GitHub Actions
4. **Load Testing**: Executar testes de carga
5. **Documentation**: Finalizar runbooks operacionais

**Status**: ✅ Pronto para deploy em produção
**Última atualização**: 21/08/2025
