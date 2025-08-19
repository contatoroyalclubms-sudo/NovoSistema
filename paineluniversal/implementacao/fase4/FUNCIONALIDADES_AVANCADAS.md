# 🚀 FASE 4: Funcionalidades Avançadas

## 📋 Checklist de Implementação

### 1. Sistema de Cache e Performance

#### 1.1 Redis Integration
- [ ] **Arquivo:** `backend/app/services/cache_service.py`
- [ ] Cache de métricas do dashboard
- [ ] Cache de sessões de usuário
- [ ] Cache de respostas de API
- [ ] Invalidação inteligente de cache

#### 1.2 Database Optimization
- [ ] **Arquivo:** `backend/app/database.py` (melhorias)
- [ ] Connection pooling
- [ ] Índices otimizados
- [ ] Query optimization
- [ ] Paginação eficiente

### 2. Analytics Avançado

#### 2.1 Métricas Detalhadas
- [ ] **Arquivo:** `backend/app/services/analytics_service.py`
- [ ] Tracking de comportamento
- [ ] Previsões de vendas
- [ ] Métricas de performance
- [ ] Cálculos de ROI

#### 2.2 Relatórios Personalizados
- [ ] **Arquivo:** `backend/app/routers/analytics.py`
- [ ] Report builder customizável
- [ ] Agendamento de relatórios
- [ ] Múltiplos formatos de export
- [ ] Gráficos dinâmicos

### 3. Integração de Pagamentos

#### 3.1 PIX Integration
- [ ] **Arquivo:** `backend/app/services/pix_service.py`
- [ ] Geração de QR Code PIX
- [ ] Validação de pagamentos
- [ ] Webhook handling
- [ ] Processamento de estornos

#### 3.2 Credit Card Processing
- [ ] **Arquivo:** `backend/app/services/card_service.py`
- [ ] Tokenização de cartões
- [ ] Processamento seguro
- [ ] Parcelamento
- [ ] Gestão de chargebacks

### 4. Mobile PWA Enhancement

#### 4.1 Service Worker
- [ ] **Arquivo:** `frontend/public/sw.js`
- [ ] Cache offline
- [ ] Background sync
- [ ] Push notifications
- [ ] Auto-update

#### 4.2 Mobile Optimization
- [ ] **Pasta:** `frontend/src/components/mobile/`
- [ ] Gestos touch
- [ ] Navegação mobile
- [ ] Design responsivo
- [ ] Integração com câmera

## 🗄️ Templates - Sistema de Cache

### cache_service.py
```python
# backend/app/services/cache_service.py
import redis
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
from functools import wraps
import hashlib

class CacheService:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.binary_client = redis.from_url(redis_url, decode_responses=False)
    
    def get(self, key: str) -> Optional[Any]:
        """Recuperar valor do cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except json.JSONDecodeError:
            # Tentar com pickle para objetos complexos
            try:
                value = self.binary_client.get(key)
                if value:
                    return pickle.loads(value)
            except:
                pass
            return None
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Armazenar valor no cache"""
        try:
            # Tentar serializar com JSON primeiro
            serialized = json.dumps(value, default=str)
            return self.redis_client.set(key, serialized, ex=expire)
        except (TypeError, ValueError):
            # Usar pickle para objetos complexos
            try:
                serialized = pickle.dumps(value)
                return self.binary_client.set(key, serialized, ex=expire)
            except:
                return False
    
    def delete(self, key: str) -> bool:
        """Remover chave do cache"""
        return bool(self.redis_client.delete(key))
    
    def clear_pattern(self, pattern: str) -> int:
        """Limpar chaves que correspondem ao padrão"""
        keys = self.redis_client.keys(pattern)
        if keys:
            return self.redis_client.delete(*keys)
        return 0
    
    def exists(self, key: str) -> bool:
        """Verificar se chave existe"""
        return bool(self.redis_client.exists(key))

# Instância global
cache = CacheService()

def cached(expire: int = 3600, key_prefix: str = ""):
    """Decorator para cache automático de funções"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave única baseada na função e parâmetros
            func_name = f"{key_prefix}{func.__module__}.{func.__name__}"
            params_str = str(args) + str(sorted(kwargs.items()))
            cache_key = f"{func_name}:{hashlib.md5(params_str.encode()).hexdigest()}"
            
            # Tentar recuperar do cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            cache.set(cache_key, result, expire)
            return result
        return wrapper
    return decorator

# Cache específico para dashboard
class DashboardCache:
    @staticmethod
    def get_metrics_key(usuario_id: int, evento_id: Optional[int] = None) -> str:
        if evento_id:
            return f"dashboard:metrics:user:{usuario_id}:evento:{evento_id}"
        return f"dashboard:metrics:user:{usuario_id}:all"
    
    @staticmethod
    def cache_metrics(usuario_id: int, metrics: dict, evento_id: Optional[int] = None):
        key = DashboardCache.get_metrics_key(usuario_id, evento_id)
        cache.set(key, metrics, expire=300)  # 5 minutos
    
    @staticmethod
    def get_cached_metrics(usuario_id: int, evento_id: Optional[int] = None) -> Optional[dict]:
        key = DashboardCache.get_metrics_key(usuario_id, evento_id)
        return cache.get(key)
    
    @staticmethod
    def invalidate_user_metrics(usuario_id: int):
        pattern = f"dashboard:metrics:user:{usuario_id}:*"
        cache.clear_pattern(pattern)
```

### analytics_service.py
```python
# backend/app/services/analytics_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
from ..models import Evento, Transacao, Checkin, Usuario, PromoterEvento
from .cache_service import cached, cache
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    @cached(expire=1800, key_prefix="analytics:")
    def get_sales_predictions(self, evento_id: int, days_ahead: int = 30) -> Dict[str, Any]:
        """Prever vendas futuras baseado em dados históricos"""
        
        # Buscar dados históricos de vendas
        vendas = self.db.query(
            func.date(Transacao.criado_em).label('data'),
            func.count(Transacao.id).label('vendas'),
            func.sum(Transacao.valor).label('receita')
        ).filter(
            Transacao.evento_id == evento_id,
            Transacao.status == 'aprovada'
        ).group_by(
            func.date(Transacao.criado_em)
        ).order_by('data').all()
        
        if len(vendas) < 7:  # Dados insuficientes
            return {
                "prediction": None,
                "confidence": 0,
                "message": "Dados insuficientes para previsão"
            }
        
        # Preparar dados para ML
        df = pd.DataFrame(vendas)
        df['data'] = pd.to_datetime(df['data'])
        df['dias'] = (df['data'] - df['data'].min()).dt.days
        
        # Modelo de regressão linear
        X = df[['dias']].values
        y_vendas = df['vendas'].values
        y_receita = df['receita'].values
        
        model_vendas = LinearRegression().fit(X, y_vendas)
        model_receita = LinearRegression().fit(X, y_receita)
        
        # Prever próximos dias
        future_days = np.array([[df['dias'].max() + i] for i in range(1, days_ahead + 1)])
        pred_vendas = model_vendas.predict(future_days)
        pred_receita = model_receita.predict(future_days)
        
        # Calcular confiança baseada no R²
        confidence_vendas = model_vendas.score(X, y_vendas)
        confidence_receita = model_receita.score(X, y_receita)
        
        return {
            "prediction": {
                "vendas_previstas": max(0, int(pred_vendas.sum())),
                "receita_prevista": max(0, float(pred_receita.sum())),
                "vendas_por_dia": [max(0, int(v)) for v in pred_vendas],
                "receita_por_dia": [max(0, float(r)) for r in pred_receita]
            },
            "confidence": {
                "vendas": round(confidence_vendas * 100, 2),
                "receita": round(confidence_receita * 100, 2)
            },
            "period": {
                "start_date": datetime.now().date(),
                "end_date": (datetime.now() + timedelta(days=days_ahead)).date(),
                "days": days_ahead
            }
        }
    
    @cached(expire=3600, key_prefix="analytics:")
    def get_user_behavior_metrics(self, evento_id: int) -> Dict[str, Any]:
        """Métricas de comportamento dos usuários"""
        
        # Análise de conversão
        total_views = self.db.query(func.count(Transacao.id)).filter(
            Transacao.evento_id == evento_id
        ).scalar()
        
        conversoes = self.db.query(func.count(Transacao.id)).filter(
            Transacao.evento_id == evento_id,
            Transacao.status == 'aprovada'
        ).scalar()
        
        # Análise temporal de vendas
        vendas_por_hora = self.db.query(
            func.extract('hour', Transacao.criado_em).label('hora'),
            func.count(Transacao.id).label('vendas')
        ).filter(
            Transacao.evento_id == evento_id,
            Transacao.status == 'aprovada'
        ).group_by('hora').all()
        
        # Análise de promoters
        performance_promoters = self.db.query(
            Usuario.nome,
            func.count(Transacao.id).label('vendas'),
            func.sum(Transacao.valor).label('receita')
        ).join(
            PromoterEvento, PromoterEvento.promoter_id == Usuario.id
        ).join(
            Transacao, Transacao.promoter_id == Usuario.id
        ).filter(
            PromoterEvento.evento_id == evento_id,
            Transacao.status == 'aprovada'
        ).group_by(Usuario.id, Usuario.nome).all()
        
        return {
            "conversion": {
                "total_attempts": total_views,
                "successful_sales": conversoes,
                "conversion_rate": round((conversoes / max(total_views, 1)) * 100, 2)
            },
            "temporal_analysis": {
                "sales_by_hour": [
                    {"hour": int(hora), "sales": vendas} 
                    for hora, vendas in vendas_por_hora
                ]
            },
            "promoter_performance": [
                {
                    "name": nome,
                    "sales": vendas,
                    "revenue": float(receita)
                }
                for nome, vendas, receita in performance_promoters
            ]
        }
    
    def calculate_roi_metrics(self, evento_id: int) -> Dict[str, Any]:
        """Calcular métricas de ROI"""
        
        # Receita total
        receita_total = self.db.query(func.sum(Transacao.valor)).filter(
            Transacao.evento_id == evento_id,
            Transacao.status == 'aprovada'
        ).scalar() or 0
        
        # Custos (pode ser expandido com modelo de custos)
        # Por enquanto, estimativa baseada em comissões
        comissoes = self.db.query(
            func.sum(Transacao.valor * PromoterEvento.comissao_percentual / 100)
        ).join(
            PromoterEvento, PromoterEvento.promoter_id == Transacao.promoter_id
        ).filter(
            Transacao.evento_id == evento_id,
            Transacao.status == 'aprovada'
        ).scalar() or 0
        
        lucro_bruto = receita_total - comissoes
        roi = ((lucro_bruto - comissoes) / max(comissoes, 1)) * 100 if comissoes > 0 else 0
        
        return {
            "revenue": float(receita_total),
            "costs": float(comissoes),
            "gross_profit": float(lucro_bruto),
            "roi_percentage": round(roi, 2),
            "profit_margin": round((lucro_bruto / max(receita_total, 1)) * 100, 2)
        }
```

## 📱 Templates - PWA Enhancement

### sw.js (Service Worker)
```javascript
// frontend/public/sw.js
const CACHE_NAME = 'eventos-app-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
];

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

// Push notifications
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'Nova notificação',
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    actions: [
      {
        action: 'view',
        title: 'Ver detalhes'
      },
      {
        action: 'dismiss',
        title: 'Dispensar'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Sistema de Eventos', options)
  );
});

async function doBackgroundSync() {
  // Sincronizar dados offline
  const offlineData = await getOfflineData();
  if (offlineData.length > 0) {
    try {
      await syncOfflineData(offlineData);
      await clearOfflineData();
    } catch (error) {
      console.error('Erro na sincronização:', error);
    }
  }
}
```

### MobileOptimizedComponent.tsx
```typescript
// frontend/src/components/mobile/MobileOptimizedComponent.tsx
import React, { useState, useEffect } from 'react';
import { useSwipeable } from 'react-swipeable';
import { Camera, Wifi, WifiOff } from 'lucide-react';

interface MobileOptimizedComponentProps {
  children: React.ReactNode;
  enableSwipe?: boolean;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
}

const MobileOptimizedComponent: React.FC<MobileOptimizedComponentProps> = ({
  children,
  enableSwipe = false,
  onSwipeLeft,
  onSwipeRight
}) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [installPrompt, setInstallPrompt] = useState<any>(null);

  // Detectar status de conexão
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // PWA Install prompt
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  // Configurar gestos de swipe
  const handlers = useSwipeable({
    onSwipedLeft: onSwipeLeft,
    onSwipedRight: onSwipeRight,
    preventDefaultTouchmoveEvent: true,
    trackMouse: true
  });

  const handleInstallApp = async () => {
    if (installPrompt) {
      installPrompt.prompt();
      const result = await installPrompt.userChoice;
      if (result.outcome === 'accepted') {
        setInstallPrompt(null);
      }
    }
  };

  return (
    <div 
      className={`mobile-optimized ${enableSwipe ? 'swipeable' : ''}`}
      {...(enableSwipe ? handlers : {})}
    >
      {/* Status bar */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-blue-600 text-white px-4 py-1 text-sm flex justify-between items-center md:hidden">
        <span>Sistema de Eventos</span>
        <div className="flex items-center space-x-2">
          {isOnline ? (
            <Wifi className="w-4 h-4" />
          ) : (
            <WifiOff className="w-4 h-4" />
          )}
          {installPrompt && (
            <button 
              onClick={handleInstallApp}
              className="text-xs bg-white text-blue-600 px-2 py-1 rounded"
            >
              Instalar
            </button>
          )}
        </div>
      </div>

      {/* Conteúdo principal */}
      <div className="pt-8 md:pt-0">
        {!isOnline && (
          <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4">
            <p className="font-bold">Modo Offline</p>
            <p className="text-sm">Algumas funcionalidades podem estar limitadas.</p>
          </div>
        )}
        {children}
      </div>
    </div>
  );
};

export default MobileOptimizedComponent;
```

## 💳 Templates - Sistema de Pagamentos

### pix_service.py
```python
# backend/app/services/pix_service.py
import qrcode
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import base64
from io import BytesIO

class PIXService:
    def __init__(self, merchant_key: str, merchant_city: str = "SAO PAULO"):
        self.merchant_key = merchant_key
        self.merchant_city = merchant_city
    
    def generate_pix_code(
        self, 
        amount: float, 
        description: str,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gerar código PIX"""
        
        if not transaction_id:
            transaction_id = str(uuid.uuid4())
        
        # Formato do PIX (simplificado)
        pix_payload = self._build_pix_payload(amount, description, transaction_id)
        
        # Gerar QR Code
        qr_code_base64 = self._generate_qr_code(pix_payload)
        
        return {
            "transaction_id": transaction_id,
            "pix_code": pix_payload,
            "qr_code_base64": qr_code_base64,
            "amount": amount,
            "description": description,
            "expires_at": datetime.now() + timedelta(minutes=30)
        }
    
    def _build_pix_payload(self, amount: float, description: str, transaction_id: str) -> str:
        """Construir payload do PIX"""
        # Implementação simplificada do formato PIX
        payload = f"00020126580014br.gov.bcb.pix0136{self.merchant_key}0208{transaction_id}520400005303986540{amount:.2f}5802BR5913{self.merchant_city}6008{self.merchant_city}62070503***6304"
        
        # Calcular CRC16 (implementação simplificada)
        crc = self._calculate_crc16(payload)
        
        return f"{payload}{crc:04X}"
    
    def _generate_qr_code(self, payload: str) -> str:
        """Gerar QR Code em base64"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(payload)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter para base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    def _calculate_crc16(self, payload: str) -> int:
        """Calcular CRC16 para PIX"""
        # Implementação simplificada do CRC16
        crc = 0xFFFF
        for char in payload:
            crc ^= ord(char) << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return crc
    
    def validate_payment(self, transaction_id: str, webhook_data: Dict[str, Any]) -> bool:
        """Validar pagamento via webhook"""
        # Implementar validação do webhook do banco
        # Esta é uma implementação de exemplo
        
        required_fields = ['transaction_id', 'status', 'amount', 'timestamp']
        
        if not all(field in webhook_data for field in required_fields):
            return False
        
        if webhook_data['transaction_id'] != transaction_id:
            return False
        
        if webhook_data['status'] != 'paid':
            return False
        
        return True
```

## 📊 Cronograma Fase 4

| Tarefa | Estimativa | Status |
|--------|------------|--------|
| Sistema de cache Redis | 2 dias | ⏳ |
| Analytics e previsões | 3 dias | ⏳ |
| Integração PIX | 3 dias | ⏳ |
| Integração cartão | 3 dias | ⏳ |
| PWA enhancements | 2 dias | ⏳ |
| Mobile optimization | 2 dias | ⏳ |
| Relatórios personalizados | 3 dias | ⏳ |
| Testes e validação | 2 dias | ⏳ |

**Total:** 20 dias (4 semanas)