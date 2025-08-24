import api from '../lib/api'
import { PaginatedResponse } from './eventos'

// Tipos para PDV
export interface Produto {
  id: number
  nome: string
  descricao?: string
  preco: number
  categoria: string
  codigo_barras?: string
  estoque_atual: number
  estoque_minimo: number
  is_ativo: boolean
  imagem_url?: string
  unidade_medida: string
  peso?: number
  marca?: string
  created_at: string
  updated_at: string
}

export interface CreateProdutoData {
  nome: string
  descricao?: string
  preco: number
  categoria: string
  codigo_barras?: string
  estoque_atual: number
  estoque_minimo: number
  is_ativo?: boolean
  imagem_url?: string
  unidade_medida: string
  peso?: number
  marca?: string
}

export interface ItemVenda {
  id?: number
  produto_id: number
  produto?: Produto
  quantidade: number
  preco_unitario: number
  desconto?: number
  subtotal: number
}

export interface Venda {
  id: number
  numero_venda: string
  cliente_id?: number
  cliente?: {
    id: number
    nome: string
    email?: string
    telefone?: string
  }
  vendedor_id: number
  vendedor?: {
    id: number
    username: string
    full_name?: string
  }
  itens: ItemVenda[]
  subtotal: number
  desconto_total: number
  imposto_total: number
  total: number
  forma_pagamento: 'dinheiro' | 'cartao_credito' | 'cartao_debito' | 'pix' | 'transferencia'
  status: 'pendente' | 'concluida' | 'cancelada'
  observacoes?: string
  data_venda: string
  created_at: string
  updated_at: string
}

export interface CreateVendaData {
  cliente_id?: number
  itens: Array<{
    produto_id: number
    quantidade: number
    preco_unitario?: number
    desconto?: number
  }>
  desconto_total?: number
  forma_pagamento: 'dinheiro' | 'cartao_credito' | 'cartao_debito' | 'pix' | 'transferencia'
  observacoes?: string
}

export interface ProdutoFilters {
  categoria?: string
  is_ativo?: boolean
  estoque_baixo?: boolean
  search?: string
}

export interface VendaFilters {
  data_inicio?: string
  data_fim?: string
  status?: string
  forma_pagamento?: string
  vendedor_id?: number
  cliente_id?: number
}

export interface RelatorioVendas {
  total_vendas: number
  total_valor: number
  vendas_por_dia: Array<{
    data: string
    quantidade: number
    valor: number
  }>
  produtos_mais_vendidos: Array<{
    produto: Produto
    quantidade_total: number
    valor_total: number
  }>
  vendedores_ranking: Array<{
    vendedor: {
      id: number
      username: string
      full_name?: string
    }
    total_vendas: number
    total_valor: number
  }>
}

// Serviços de PDV
export const pdvService = {
  // PRODUTOS
  
  // Listar produtos com filtros
  async getProdutos(
    page: number = 1,
    limit: number = 10,
    filters?: ProdutoFilters
  ): Promise<PaginatedResponse<Produto>> {
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

    const response = await api.get<PaginatedResponse<Produto>>(
      `/api/v1/pdv/produtos?${params.toString()}`
    )
    return response.data
  },

  // Obter produto por ID
  async getProduto(id: number): Promise<Produto> {
    const response = await api.get<Produto>(`/api/v1/pdv/produtos/${id}`)
    return response.data
  },

  // Buscar produto por código de barras
  async getProdutoPorCodigoBarras(codigoBarras: string): Promise<Produto> {
    const response = await api.get<Produto>(`/api/v1/pdv/produtos/codigo/${codigoBarras}`)
    return response.data
  },

  // Criar produto
  async createProduto(data: CreateProdutoData): Promise<Produto> {
    const response = await api.post<Produto>('/api/v1/pdv/produtos', data)
    return response.data
  },

  // Atualizar produto
  async updateProduto(id: number, data: Partial<CreateProdutoData>): Promise<Produto> {
    const response = await api.put<Produto>(`/api/v1/pdv/produtos/${id}`, data)
    return response.data
  },

  // Deletar produto
  async deleteProduto(id: number): Promise<void> {
    await api.delete(`/api/v1/pdv/produtos/${id}`)
  },

  // VENDAS

  // Listar vendas com filtros
  async getVendas(
    page: number = 1,
    limit: number = 10,
    filters?: VendaFilters
  ): Promise<PaginatedResponse<Venda>> {
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

    const response = await api.get<PaginatedResponse<Venda>>(
      `/api/v1/pdv/vendas?${params.toString()}`
    )
    return response.data
  },

  // Obter venda por ID
  async getVenda(id: number): Promise<Venda> {
    const response = await api.get<Venda>(`/api/v1/pdv/vendas/${id}`)
    return response.data
  },

  // Criar nova venda
  async createVenda(data: CreateVendaData): Promise<Venda> {
    const response = await api.post<Venda>('/api/v1/pdv/vendas', data)
    return response.data
  },

  // Cancelar venda
  async cancelarVenda(id: number): Promise<Venda> {
    const response = await api.put<Venda>(`/api/v1/pdv/vendas/${id}/cancelar`)
    return response.data
  },

  // RELATÓRIOS

  // Obter relatório de vendas
  async getRelatorioVendas(
    dataInicio?: string,
    dataFim?: string
  ): Promise<RelatorioVendas> {
    const params = new URLSearchParams()
    if (dataInicio) params.append('data_inicio', dataInicio)
    if (dataFim) params.append('data_fim', dataFim)

    const response = await api.get<RelatorioVendas>(
      `/api/v1/pdv/relatorios/vendas?${params.toString()}`
    )
    return response.data
  },

  // Obter produtos com estoque baixo
  async getProdutosEstoqueBaixo(): Promise<Produto[]> {
    const response = await api.get<Produto[]>('/api/v1/pdv/produtos/estoque-baixo')
    return response.data
  },

  // Obter vendas do dia
  async getVendasDia(data?: string): Promise<{
    vendas: Venda[]
    total_quantidade: number
    total_valor: number
  }> {
    const params = data ? `?data=${data}` : ''
    const response = await api.get(`/api/v1/pdv/vendas/dia${params}`)
    return response.data
  },

  // CAIXA

  // Abrir caixa
  async abrirCaixa(valorInicial: number): Promise<{
    id: number
    data_abertura: string
    valor_inicial: number
    status: string
  }> {
    const response = await api.post('/api/v1/pdv/caixa/abrir', {
      valor_inicial: valorInicial
    })
    return response.data
  },

  // Fechar caixa
  async fecharCaixa(valorFinal: number): Promise<{
    id: number
    data_fechamento: string
    valor_final: number
    valor_vendas: number
    diferenca: number
  }> {
    const response = await api.post('/api/v1/pdv/caixa/fechar', {
      valor_final: valorFinal
    })
    return response.data
  },

  // Status do caixa
  async getStatusCaixa(): Promise<{
    aberto: boolean
    data_abertura?: string
    valor_inicial?: number
    valor_atual?: number
  }> {
    const response = await api.get('/api/v1/pdv/caixa/status')
    return response.data
  }
}

export default pdvService
