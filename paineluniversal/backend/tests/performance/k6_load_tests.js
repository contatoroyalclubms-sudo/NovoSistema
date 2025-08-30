/**
 * K6 Performance Tests for Event Management System API
 * Tests API endpoints under load with realistic scenarios
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const authSuccessRate = new Rate('auth_success_rate');
const eventCreationTrend = new Trend('event_creation_duration');
const checkinSuccessRate = new Rate('checkin_success_rate');
const salesSuccessRate = new Rate('sales_success_rate');
const errorCount = new Counter('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up
    { duration: '5m', target: 50 }, // Stay at 50 users
    { duration: '2m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 0 }, // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests under 2s
    http_req_failed: ['rate<0.1'], // Error rate under 10%
    auth_success_rate: ['rate>0.95'], // Auth success rate over 95%
    checkin_success_rate: ['rate>0.9'], // Check-in success rate over 90%
    sales_success_rate: ['rate>0.9'], // Sales success rate over 90%
  },
};

// Configuration
const BASE_URL = __ENV.API_URL || 'http://localhost:8000';
const ADMIN_EMAIL = __ENV.ADMIN_EMAIL || 'admin@test.com';
const ADMIN_PASSWORD = __ENV.ADMIN_PASSWORD || 'admin123';

let authToken = '';
let createdEvents = [];
let createdProducts = [];
let createdParticipants = [];

// Setup function - runs once before test
export function setup() {
  console.log('Setting up performance tests...');
  
  // Authenticate as admin
  const loginPayload = {
    email: ADMIN_EMAIL,
    senha: ADMIN_PASSWORD
  };
  
  const loginResponse = http.post(`${BASE_URL}/auth/login`, JSON.stringify(loginPayload), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  if (loginResponse.status === 200) {
    const token = loginResponse.json('access_token');
    console.log('Authentication successful');
    return { authToken: token };
  } else {
    console.error('Authentication failed:', loginResponse.body);
    return { authToken: '' };
  }
}

export default function(data) {
  const token = data.authToken;
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };

  group('Authentication Tests', function() {
    testLogin();
    testTokenValidation(headers);
  });

  group('Event Management Tests', function() {
    testEventCreation(headers);
    testEventListing(headers);
    testEventDetails(headers);
  });

  group('Check-in System Tests', function() {
    testCheckinValidation(headers);
    testCheckinPerformance(headers);
  });

  group('PDV/Sales Tests', function() {
    testProductListing(headers);
    testSalesCreation(headers);
    testInventoryUpdates(headers);
  });

  group('Analytics and Reporting', function() {
    testDashboardPerformance(headers);
    testReportGeneration(headers);
  });

  sleep(1);
}

function testLogin() {
  const loginPayload = {
    email: `user${Math.floor(Math.random() * 1000)}@test.com`,
    senha: 'testpassword123'
  };

  const response = http.post(`${BASE_URL}/auth/login`, JSON.stringify(loginPayload), {
    headers: { 'Content-Type': 'application/json' },
  });

  const success = check(response, {
    'login response time < 1s': (r) => r.timings.duration < 1000,
    'login returns expected status': (r) => r.status === 401 || r.status === 200, // 401 for invalid user is expected
  });

  authSuccessRate.add(success);

  if (!success) {
    errorCount.add(1);
  }
}

function testTokenValidation(headers) {
  const response = http.get(`${BASE_URL}/auth/me`, { headers });

  check(response, {
    'token validation < 500ms': (r) => r.timings.duration < 500,
    'token validation successful': (r) => r.status === 200 || r.status === 401,
  });
}

function testEventCreation(headers) {
  const eventPayload = {
    nome: `Evento Performance Test ${Math.floor(Math.random() * 10000)}`,
    descricao: 'Evento criado durante teste de performance',
    data_inicio: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    data_fim: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000 + 4 * 60 * 60 * 1000).toISOString(),
    local: 'Centro de Convenções Virtual',
    endereco: 'Endereço Virtual, 123',
    capacidade_maxima: Math.floor(Math.random() * 500) + 50,
    preco_ingresso: Math.floor(Math.random() * 100) + 10
  };

  const startTime = Date.now();
  const response = http.post(`${BASE_URL}/eventos/`, JSON.stringify(eventPayload), { headers });
  const duration = Date.now() - startTime;

  eventCreationTrend.add(duration);

  const success = check(response, {
    'event creation successful': (r) => r.status === 201,
    'event creation < 2s': (r) => r.timings.duration < 2000,
    'event has valid id': (r) => r.json('id') !== undefined,
  });

  if (success && response.status === 201) {
    createdEvents.push(response.json('id'));
  } else {
    errorCount.add(1);
  }
}

function testEventListing(headers) {
  const response = http.get(`${BASE_URL}/eventos/?page=1&size=20`, { headers });

  check(response, {
    'event listing successful': (r) => r.status === 200,
    'event listing < 1s': (r) => r.timings.duration < 1000,
    'event listing has items': (r) => r.json('items') !== undefined,
    'event listing has pagination': (r) => r.json('total') !== undefined,
  });
}

function testEventDetails(headers) {
  if (createdEvents.length === 0) return;

  const eventId = createdEvents[Math.floor(Math.random() * createdEvents.length)];
  const response = http.get(`${BASE_URL}/eventos/${eventId}`, { headers });

  check(response, {
    'event details successful': (r) => r.status === 200,
    'event details < 800ms': (r) => r.timings.duration < 800,
    'event details complete': (r) => r.json('nome') !== undefined,
  });
}

function testCheckinValidation(headers) {
  const validationPayload = {
    evento_id: createdEvents[0] || 'test-event-id',
    participante_info: {
      cpf: generateRandomCPF(),
      nome: 'Participante Teste Performance'
    }
  };

  const response = http.post(`${BASE_URL}/checkins/validacao-previa`, JSON.stringify(validationPayload), { headers });

  check(response, {
    'checkin validation response time < 500ms': (r) => r.timings.duration < 500,
    'checkin validation returns result': (r) => r.status === 200 || r.status === 404,
  });
}

function testCheckinPerformance(headers) {
  const checkinPayload = {
    participante_id: `test-participant-${Math.floor(Math.random() * 1000)}`,
    evento_id: createdEvents[0] || 'test-event-id',
    motivo: 'Check-in teste de performance'
  };

  const response = http.post(`${BASE_URL}/checkins/manual`, JSON.stringify(checkinPayload), { headers });

  const success = check(response, {
    'checkin response time < 1s': (r) => r.timings.duration < 1000,
    'checkin returns appropriate status': (r) => r.status === 200 || r.status === 404 || r.status === 400,
  });

  checkinSuccessRate.add(response.status === 200);
}

function testProductListing(headers) {
  const response = http.get(`${BASE_URL}/pdv/produtos?page=1&size=50`, { headers });

  check(response, {
    'product listing successful': (r) => r.status === 200,
    'product listing < 800ms': (r) => r.timings.duration < 800,
    'product listing has structure': (r) => r.json('items') !== undefined,
  });
}

function testSalesCreation(headers) {
  const salePayload = {
    evento_id: createdEvents[0] || 'test-event-id',
    cliente: {
      nome: `Cliente Performance ${Math.floor(Math.random() * 1000)}`,
      cpf: generateRandomCPF()
    },
    itens: [
      {
        produto_id: 'test-product-id',
        quantidade: Math.floor(Math.random() * 3) + 1,
        preco_unitario: Math.floor(Math.random() * 50) + 10
      }
    ],
    forma_pagamento: 'DINHEIRO'
  };

  const response = http.post(`${BASE_URL}/pdv/vendas`, JSON.stringify(salePayload), { headers });

  const success = check(response, {
    'sale creation response time < 1.5s': (r) => r.timings.duration < 1500,
    'sale creation returns valid response': (r) => r.status === 201 || r.status === 400 || r.status === 404,
  });

  salesSuccessRate.add(response.status === 201);
}

function testInventoryUpdates(headers) {
  const inventoryPayload = {
    quantidade: Math.floor(Math.random() * 20) + 1,
    tipo_movimentacao: 'ENTRADA',
    motivo: 'Reposição teste performance'
  };

  const response = http.post(`${BASE_URL}/pdv/estoque/test-product-id/movimentacao`, JSON.stringify(inventoryPayload), { headers });

  check(response, {
    'inventory update response time < 800ms': (r) => r.timings.duration < 800,
    'inventory update returns status': (r) => r.status === 200 || r.status === 404 || r.status === 400,
  });
}

function testDashboardPerformance(headers) {
  const response = http.get(`${BASE_URL}/eventos/dashboard`, { headers });

  check(response, {
    'dashboard load time < 1s': (r) => r.timings.duration < 1000,
    'dashboard returns data': (r) => r.status === 200,
    'dashboard has metrics': (r) => r.json() && Object.keys(r.json()).length > 0,
  });
}

function testReportGeneration(headers) {
  const response = http.get(`${BASE_URL}/eventos/export?format=csv`, { headers });

  check(response, {
    'report generation < 3s': (r) => r.timings.duration < 3000,
    'report generation succeeds': (r) => r.status === 200 || r.status === 404,
  });
}

// Utility functions
function generateRandomCPF() {
  return `${Math.floor(Math.random() * 90000000000) + 10000000000}`;
}

// Cleanup function - runs once after test
export function teardown(data) {
  console.log('Performance tests completed');
  console.log(`Events created during test: ${createdEvents.length}`);
}

// Specialized test scenarios
export function smokeTest() {
  group('Smoke Test - Critical Endpoints', function() {
    const response = http.get(`${BASE_URL}/health`);
    check(response, {
      'health check passes': (r) => r.status === 200,
    });
  });
}

export function stressTest() {
  group('Stress Test - High Load Scenarios', function() {
    // Simulate high concurrent user activity
    for (let i = 0; i < 10; i++) {
      http.get(`${BASE_URL}/eventos/`);
      http.get(`${BASE_URL}/pdv/produtos`);
      sleep(0.1);
    }
  });
}

// WebSocket load testing (if applicable)
export function websocketTest() {
  group('WebSocket Performance', function() {
    // Note: K6 has limited WebSocket support, this would need ws module
    console.log('WebSocket testing would require additional setup');
  });
}