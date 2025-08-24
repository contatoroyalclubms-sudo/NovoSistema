import React, { useState, useEffect } from 'react';
import { Bell, Mail, MessageCircle, Smartphone, Send, Check, X, Clock } from 'lucide-react';

interface NotificationStats {
  total_notifications: number;
  success_rate: number;
  last_24h: number;
  queue_size: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  by_priority: Record<string, number>;
  is_processing: boolean;
}

interface NotificationTypes {
  types: string[];
  priorities: string[];
  statuses: string[];
}

const NotificationScreen: React.FC = () => {
  const [stats, setStats] = useState<NotificationStats | null>(null);
  const [types, setTypes] = useState<NotificationTypes | null>(null);
  const [loading, setLoading] = useState(true);
  const [testResult, setTestResult] = useState<string>('');
  
  // Form data para teste
  const [testForm, setTestForm] = useState({
    type: 'email',
    email: 'test@example.com',
    phone: '+5567999999999',
    pushToken: 'test-token-123',
    subject: 'Teste de Notificação',
    content: 'Esta é uma notificação de teste do sistema.'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Carregar estatísticas
      const statsResponse = await fetch('http://localhost:8005/api/notifications/stats');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData.data);
      }
      
      // Carregar tipos
      const typesResponse = await fetch('http://localhost:8005/api/notifications/types');
      if (typesResponse.ok) {
        const typesData = await typesResponse.json();
        setTypes(typesData.data);
      }
      
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const testNotification = async (type: string) => {
    try {
      setTestResult('Enviando...');
      
      let response;
      
      if (type === 'email') {
        response = await fetch('http://localhost:8005/api/notifications/test/email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: testForm.email,
            subject: testForm.subject,
            content: testForm.content
          })
        });
      } else if (type === 'sms') {
        response = await fetch('http://localhost:8005/api/notifications/test/sms', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            phone: testForm.phone,
            message: testForm.content
          })
        });
      } else if (type === 'push') {
        response = await fetch('http://localhost:8005/api/notifications/test/push', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            token: testForm.pushToken,
            title: testForm.subject,
            body: testForm.content
          })
        });
      }
      
      if (response?.ok) {
        const result = await response.json();
        setTestResult(`✅ ${result.message}`);
        loadData(); // Recarregar stats
      } else {
        setTestResult('❌ Erro ao enviar notificação');
      }
      
    } catch (error) {
      setTestResult('❌ Erro de conexão');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <Clock className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-500" />
          <p>Carregando sistema de notificações...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold mb-4 flex items-center">
            <Bell className="w-8 h-8 mr-3 text-blue-500" />
            🚀 SISTEMA DE NOTIFICAÇÕES v1.0
          </h1>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <h2 className="text-xl font-semibold text-green-800 mb-2">
              ✅ PRIORIDADE #8 - IMPLEMENTADA COM SUCESSO!
            </h2>
            <p className="text-green-700">
              Sistema completo de notificações com suporte a Email, SMS e Push Notifications
            </p>
          </div>

          {/* Status do Sistema */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h3 className="font-semibold text-blue-800">Total</h3>
                <p className="text-2xl font-bold text-blue-600">{stats.total_notifications}</p>
                <p className="text-sm text-blue-600">Notificações</p>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <h3 className="font-semibold text-green-800">Taxa Sucesso</h3>
                <p className="text-2xl font-bold text-green-600">{stats.success_rate}%</p>
                <p className="text-sm text-green-600">De entregas</p>
              </div>
              
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <h3 className="font-semibold text-yellow-800">Últimas 24h</h3>
                <p className="text-2xl font-bold text-yellow-600">{stats.last_24h}</p>
                <p className="text-sm text-yellow-600">Enviadas</p>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                <h3 className="font-semibold text-purple-800">Fila</h3>
                <p className="text-2xl font-bold text-purple-600">{stats.queue_size}</p>
                <p className="text-sm text-purple-600">Na fila</p>
              </div>
            </div>
          )}

          {/* Tipos e Status */}
          {types && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Tipos Suportados</h3>
                <div className="space-y-1">
                  {types.types.map(type => (
                    <span key={type} className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm mr-1">
                      {type}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Prioridades</h3>
                <div className="space-y-1">
                  {types.priorities.map(priority => (
                    <span key={priority} className="inline-block bg-green-100 text-green-800 px-2 py-1 rounded text-sm mr-1">
                      {priority}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Status</h3>
                <div className="space-y-1">
                  {types.statuses.map(status => (
                    <span key={status} className="inline-block bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm mr-1">
                      {status}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Testes de Notificação */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold mb-4">🧪 Teste de Notificações</h2>
          
          {/* Formulário de Teste */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                value={testForm.email}
                onChange={(e) => setTestForm({...testForm, email: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="test@example.com"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Telefone</label>
              <input
                type="tel"
                value={testForm.phone}
                onChange={(e) => setTestForm({...testForm, phone: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="+5567999999999"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Assunto</label>
              <input
                type="text"
                value={testForm.subject}
                onChange={(e) => setTestForm({...testForm, subject: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Push Token</label>
              <input
                type="text"
                value={testForm.pushToken}
                onChange={(e) => setTestForm({...testForm, pushToken: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="test-token-123"
              />
            </div>
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Conteúdo</label>
            <textarea
              value={testForm.content}
              onChange={(e) => setTestForm({...testForm, content: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          </div>

          {/* Botões de Teste */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <button
              onClick={() => testNotification('email')}
              className="flex items-center justify-center px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <Mail className="w-5 h-5 mr-2" />
              Testar Email
            </button>
            
            <button
              onClick={() => testNotification('sms')}
              className="flex items-center justify-center px-4 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              <MessageCircle className="w-5 h-5 mr-2" />
              Testar SMS
            </button>
            
            <button
              onClick={() => testNotification('push')}
              className="flex items-center justify-center px-4 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
            >
              <Smartphone className="w-5 h-5 mr-2" />
              Testar Push
            </button>
          </div>

          {/* Resultado do Teste */}
          {testResult && (
            <div className={`p-4 rounded-lg ${
              testResult.includes('✅') 
                ? 'bg-green-50 border border-green-200 text-green-800' 
                : 'bg-red-50 border border-red-200 text-red-800'
            }`}>
              <p className="font-semibold">{testResult}</p>
            </div>
          )}
        </div>

        {/* Funcionalidades Implementadas */}
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h2 className="text-2xl font-bold mb-4">🎯 Funcionalidades Implementadas</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-lg mb-3">Backend</h3>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> NotificationManager completo</li>
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> Provedores Email, SMS, Push</li>
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> Sistema de filas async</li>
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> Templates e destinatários</li>
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> Retry automático</li>
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> Logs e auditoria</li>
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> Agendamento de envios</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-lg mb-3">API Endpoints</h3>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> /notifications/health</li>
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> /notifications/stats</li>
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> /notifications/send</li>
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> /notifications/send-bulk</li>
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> /notifications/test/*</li>
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> /notifications/templates</li>
                <li className="flex items-center"><Check className="w-4 h-4 text-green-500 mr-2" /> /notifications/recipients</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationScreen;
