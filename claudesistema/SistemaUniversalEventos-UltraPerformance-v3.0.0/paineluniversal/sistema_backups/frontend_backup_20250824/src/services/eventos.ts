import api from '../lib/api'

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  pages: number
}

// Tipos para eventos
export interface Evento {
  id: number
  nome: string
  descricao?: string
  data_inicio: string
  data_fim: string
  local?: string
  capacidade_maxima?: number
  preco?: number
  status: 'planejado' | 'ativo' | 'finalizado' | 'cancelado'
  tipo_evento: string
  organizador?: string
  imagem_url?: string
  categoria?: string
  is_publico: boolean
  participantes_atuais: number
  created_at: string
  updated_at: string
}

export interface CreateEventoData {
  nome: string
  descricao?: string
  data_inicio: string
  data_fim: string
  local?: string
  capacidade_maxima?: number
  preco?: number
  tipo_evento: string
  organizador?: string
  imagem_url?: string
  categoria?: string
  is_publico?: boolean
}

export interface UpdateEventoData extends Partial<CreateEventoData> {
  status?: 'planejado' | 'ativo' | 'finalizado' | 'cancelado'
}

export interface EventoFilters {
  status?: string
  tipo_evento?: string
  categoria?: string
  data_inicio?: string
  data_fim?: string
  is_publico?: boolean
  search?: string
}

export interface ParticipanteEvento {
  id: number
  evento_id: number
  user_id: number
  user: {
    id: number
    username: string
    email: string
    full_name?: string
  }
  data_inscricao: string
  status_participacao: 'confirmado' | 'pendente' | 'cancelado'
  observacoes?: string
}

// Serviços de eventos
export const eventosService = {
  // Listar eventos com filtros e paginação
  async getEventos(
    page: number = 1,
    limit: number = 10,
    filters?: EventoFilters
  ): Promise<PaginatedResponse<Evento>> {
    const params = new URLSearchParams()
    params.append('page', page.toString())
    params.append('limit', limit.toString())
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString())
        }
      })
    }

    const response = await api.get<PaginatedResponse<Evento>>(
      `/api/v1/eventos?${params.toString()}`
    )
    return response.data
  },

  // Obter evento por ID
  async getEvento(id: number): Promise<Evento> {
    const response = await api.get<Evento>(`/api/v1/eventos/${id}`)
    return response.data
  },

  // Criar novo evento
  async createEvento(data: CreateEventoData): Promise<Evento> {
    const response = await api.post<Evento>('/api/v1/eventos', data)
    return response.data
  },

  // Atualizar evento
  async updateEvento(id: number, data: UpdateEventoData): Promise<Evento> {
    const response = await api.put<Evento>(`/api/v1/eventos/${id}`, data)
    return response.data
  },

  // Deletar evento
  async deleteEvento(id: number): Promise<void> {
    await api.delete(`/api/v1/eventos/${id}`)
  },

  // Inscrever-se em evento
  async inscreverEvento(
    eventoId: number,
    observacoes?: string
  ): Promise<ParticipanteEvento> {
    const response = await api.post<ParticipanteEvento>(
      `/api/v1/eventos/${eventoId}/inscrever`,
      { observacoes }
    )
    return response.data
  },

  // Cancelar inscrição
  async cancelarInscricao(eventoId: number): Promise<void> {
    await api.delete(`/api/v1/eventos/${eventoId}/inscrever`)
  },

  // Listar participantes de um evento
  async getParticipantes(
    eventoId: number,
    page: number = 1,
    limit: number = 10
  ): Promise<PaginatedResponse<ParticipanteEvento>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString()
    })

    const response = await api.get<PaginatedResponse<ParticipanteEvento>>(
      `/api/v1/eventos/${eventoId}/participantes?${params.toString()}`
    )
    return response.data
  },

  // Verificar se usuário está inscrito no evento
  async isInscrito(eventoId: number): Promise<boolean> {
    try {
      const response = await api.get<{ inscrito: boolean }>(
        `/api/v1/eventos/${eventoId}/inscrito`
      )
      return response.data.inscrito
    } catch {
      return false
    }
  },

  // Obter estatísticas de eventos
  async getEstatisticas(): Promise<{
    total_eventos: number
    eventos_ativos: number
    eventos_finalizados: number
    total_participantes: number
    eventos_por_categoria: Record<string, number>
  }> {
    const response = await api.get('/api/v1/eventos/estatisticas')
    return response.data
  },

  // Buscar eventos próximos
  async getEventosProximos(limit: number = 5): Promise<Evento[]> {
    const response = await api.get<Evento[]>(`/api/v1/eventos/proximos?limit=${limit}`)
    return response.data
  },

  // Obter eventos do usuário atual
  async getMeusEventos(
    page: number = 1,
    limit: number = 10
  ): Promise<PaginatedResponse<Evento>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString()
    })

    const response = await api.get<PaginatedResponse<Evento>>(
      `/api/v1/eventos/meus?${params.toString()}`
    )
    return response.data
  },

  // Upload de imagem para evento
  async uploadImagem(eventoId: number, file: File): Promise<{ url: string }> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post<{ url: string }>(
      `/api/v1/eventos/${eventoId}/upload-imagem`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    return response.data
  }
}

export default eventosService
