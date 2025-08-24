import { http, HttpResponse } from 'msw'

const BASE_URL = 'http://localhost:8000'

export const handlers = [
  // Authentication handlers
  http.post(`${BASE_URL}/auth/login`, async ({ request }) => {
    const body = await request.json() as { email: string; senha: string }
    
    if (body.email === 'admin@test.com' && body.senha === 'admin123') {
      return HttpResponse.json({
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
        expires_in: 3600
      })
    }
    
    return HttpResponse.json(
      { detail: 'Credenciais inválidas' },
      { status: 401 }
    )
  }),

  http.get(`${BASE_URL}/auth/me`, ({ request }) => {
    const authorization = request.headers.get('authorization')
    
    if (!authorization?.includes('Bearer')) {
      return HttpResponse.json(
        { detail: 'Token não fornecido' },
        { status: 401 }
      )
    }
    
    return HttpResponse.json({
      id: '1',
      email: 'admin@test.com',
      nome: 'Admin Test',
      tipo: 'ADMIN',
      ativo: true,
      verificado: true
    })
  }),

  http.post(`${BASE_URL}/auth/refresh`, async ({ request }) => {
    const body = await request.json() as { refresh_token: string }
    
    if (body.refresh_token === 'mock-refresh-token') {
      return HttpResponse.json({
        access_token: 'new-mock-access-token',
        refresh_token: 'new-mock-refresh-token',
        token_type: 'bearer',
        expires_in: 3600
      })
    }
    
    return HttpResponse.json(
      { detail: 'Refresh token inválido' },
      { status: 401 }
    )
  }),

  // Events handlers
  http.get(`${BASE_URL}/eventos/`, () => {
    return HttpResponse.json({
      items: [
        {
          id: '1',
          nome: 'Evento Test 1',
          descricao: 'Descrição do evento teste 1',
          data_inicio: '2024-12-25T20:00:00Z',
          data_fim: '2024-12-26T02:00:00Z',
          local: 'Centro de Convenções',
          endereco: 'Av. Principal, 1000',
          capacidade_maxima: 500,
          status: 'ATIVO',
          preco_ingresso: 50.00
        },
        {
          id: '2',
          nome: 'Evento Test 2',
          descricao: 'Descrição do evento teste 2',
          data_inicio: '2024-12-30T19:00:00Z',
          data_fim: '2024-12-31T03:00:00Z',
          local: 'Salão de Festas',
          endereco: 'Rua das Flores, 500',
          capacidade_maxima: 200,
          status: 'ATIVO',
          preco_ingresso: 35.00
        }
      ],
      total: 2,
      page: 1,
      size: 20
    })
  }),

  http.get(`${BASE_URL}/eventos/:id`, ({ params }) => {
    const { id } = params
    
    if (id === '1') {
      return HttpResponse.json({
        id: '1',
        nome: 'Evento Test 1',
        descricao: 'Descrição detalhada do evento teste 1',
        data_inicio: '2024-12-25T20:00:00Z',
        data_fim: '2024-12-26T02:00:00Z',
        local: 'Centro de Convenções',
        endereco: 'Av. Principal, 1000',
        capacidade_maxima: 500,
        status: 'ATIVO',
        preco_ingresso: 50.00,
        total_participantes: 150,
        checkins_realizados: 75
      })
    }
    
    return HttpResponse.json(
      { detail: 'Evento não encontrado' },
      { status: 404 }
    )
  }),

  http.post(`${BASE_URL}/eventos/`, async ({ request }) => {
    const body = await request.json() as any
    
    return HttpResponse.json({
      id: 'new-event-id',
      ...body,
      status: 'ATIVO',
      created_at: new Date().toISOString()
    }, { status: 201 })
  }),

  // PDV/Products handlers
  http.get(`${BASE_URL}/pdv/produtos`, () => {
    return HttpResponse.json({
      items: [
        {
          id: '1',
          nome: 'Cerveja Premium',
          descricao: 'Cerveja artesanal premium 500ml',
          preco: 15.50,
          categoria: 'Bebidas',
          ativo: true,
          estoque: 100
        },
        {
          id: '2',
          nome: 'Refrigerante',
          descricao: 'Refrigerante 350ml',
          preco: 5.50,
          categoria: 'Bebidas',
          ativo: true,
          estoque: 200
        }
      ],
      total: 2,
      page: 1,
      size: 20
    })
  }),

  http.post(`${BASE_URL}/pdv/vendas`, async ({ request }) => {
    const body = await request.json() as any
    
    const total = body.itens.reduce((sum: number, item: any) => {
      return sum + (item.quantidade * item.preco_unitario)
    }, 0)
    
    return HttpResponse.json({
      id: 'new-sale-id',
      ...body,
      total,
      status: 'CONCLUIDA',
      created_at: new Date().toISOString()
    }, { status: 201 })
  }),

  // Check-in handlers
  http.get(`${BASE_URL}/checkins/stats/:eventoId`, ({ params }) => {
    const { eventoId } = params
    
    return HttpResponse.json({
      evento_id: eventoId,
      total_participantes: 150,
      checkins_realizados: 75,
      taxa_comparecimento: 50.0,
      checkins_por_tipo: {
        QR_CODE: 45,
        CPF: 20,
        MANUAL: 10
      },
      checkins_por_horario: {
        '18:00': 10,
        '19:00': 25,
        '20:00': 40
      }
    })
  }),

  http.post(`${BASE_URL}/checkins/manual`, async ({ request }) => {
    const body = await request.json() as any
    
    return HttpResponse.json({
      success: true,
      participante: {
        id: body.participante_id,
        nome: 'Participante Test',
        email: 'participante@test.com'
      },
      tipo_checkin: 'MANUAL',
      checkin_time: new Date().toISOString()
    })
  }),

  // Dashboard handlers
  http.get(`${BASE_URL}/eventos/dashboard`, () => {
    return HttpResponse.json({
      total_eventos: 25,
      eventos_ativos: 15,
      eventos_proximos: 5,
      receita_total: 125000.00,
      participantes_total: 2500,
      checkins_hoje: 150,
      vendas_hoje: 75
    })
  }),

  http.get(`${BASE_URL}/pdv/dashboard`, () => {
    return HttpResponse.json({
      vendas_hoje: 45,
      receita_total: 2500.00,
      produtos_mais_vendidos: [
        { nome: 'Cerveja Premium', vendas: 25 },
        { nome: 'Refrigerante', vendas: 20 }
      ],
      formas_pagamento: {
        DINHEIRO: 20,
        CARTAO: 15,
        PIX: 10
      },
      vendas_por_hora: {
        '18:00': 5,
        '19:00': 15,
        '20:00': 25
      }
    })
  }),

  // Error simulation handler
  http.get(`${BASE_URL}/error-test`, () => {
    return HttpResponse.json(
      { detail: 'Erro simulado para testes' },
      { status: 500 }
    )
  })
]