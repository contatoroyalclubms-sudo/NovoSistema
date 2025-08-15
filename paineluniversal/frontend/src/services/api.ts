import axios from 'axios';

const API_BASE_URL = '/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('usuario');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginRequest {
  cpf: string;
  senha: string;
  codigo_verificacao?: string;
}

export interface Usuario {
  id: number;
  cpf: string;
  nome: string;
  email: string;
  tipo: 'admin' | 'promoter' | 'operador';
  empresa_id: number;
  ativo: boolean;
  criado_em: string;
  ultimo_login?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  usuario: Usuario;
}

export const authService = {
  async login(data: LoginRequest): Promise<Token> {
    const response = await api.post('/auth/login', data);
    return response.data;
  },

  async getProfile(): Promise<Usuario> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout');
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
  },

  async solicitarCodigo(cpf: string): Promise<any> {
    const response = await api.post('/auth/solicitar-codigo', { cpf });
    return response.data;
  }
};

export interface Empresa {
  id: number;
  nome: string;
  cnpj: string;
  email: string;
  telefone: string;
  endereco: string;
  ativa: boolean;
  criado_em: string;
}

export interface Evento {
  id: number;
  nome: string;
  descricao?: string;
  data_evento: string;
  local: string;
  endereco?: string;
  limite_idade: number;
  capacidade_maxima: number;
  status: 'ativo' | 'cancelado' | 'finalizado';
  empresa_id: number;
  criador_id: number;
  criado_em: string;
  atualizado_em?: string;
}

export interface EventoCreate {
  nome: string;
  descricao?: string;
  data_evento: string;
  local: string;
  endereco?: string;
  limite_idade: number;
  capacidade_maxima: number;
  empresa_id: number;
}

export interface EventoDetalhado extends Evento {
  total_vendas: number;
  receita_total: number;
  total_checkins: number;
  promoters_vinculados: Array<{
    id: number;
    promoter_id: number;
    nome: string;
    meta_vendas?: number;
    vendas_realizadas: number;
    comissao_percentual: number;
  }>;
  status_financeiro: 'sem_vendas' | 'baixo' | 'medio' | 'alto';
}

export interface EventoFiltros {
  nome?: string;
  status?: string;
  empresa_id?: number;
  data_inicio?: string;
  data_fim?: string;
  local?: string;
  limite_idade_min?: number;
  limite_idade_max?: number;
}

export interface PromoterEventoCreate {
  promoter_id: number;
  meta_vendas?: number;
  comissao_percentual?: number;
}

export interface Lista {
  id: number;
  nome: string;
  tipo: 'vip' | 'free' | 'pagante' | 'desconto' | 'aniversario' | 'promoter';
  preco: number;
  limite_pessoas: number;
  evento_id: number;
  promoter_id?: number;
  ativa: boolean;
  criado_em: string;
}

export interface Transacao {
  id: number;
  cpf_comprador: string;
  nome_comprador: string;
  email_comprador: string;
  telefone_comprador: string;
  valor: number;
  status: 'pendente' | 'aprovada' | 'rejeitada' | 'cancelada';
  lista_id: number;
  evento_id: number;
  criado_em: string;
}

export const empresaService = {
  async listar(): Promise<Empresa[]> {
    const response = await api.get('/empresas/');
    return response.data;
  },

  async obter(id: number): Promise<Empresa> {
    const response = await api.get(`/empresas/${id}`);
    return response.data;
  }
};

export const eventoService = {
  listar: (): Promise<Evento[]> => 
    api.get('/eventos/').then(response => response.data),
  
  obter: (id: number): Promise<Evento> => 
    api.get(`/eventos/${id}`).then(response => response.data),
  
  obterDetalhado: (id: number): Promise<EventoDetalhado> => 
    api.get(`/eventos/detalhado/${id}`).then(response => response.data),
  
  buscar: (filtros: EventoFiltros, skip = 0, limit = 100): Promise<Evento[]> => {
    const params = new URLSearchParams();
    Object.entries(filtros).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    
    return api.get(`/eventos/buscar?${params.toString()}`).then(response => response.data);
  },
  
  criar: (evento: EventoCreate): Promise<Evento> => 
    api.post('/eventos/', evento).then(response => response.data),
  
  atualizar: (id: number, evento: EventoCreate): Promise<Evento> => 
    api.put(`/eventos/${id}`, evento).then(response => response.data),
  
  cancelar: (id: number): Promise<void> => 
    api.delete(`/eventos/${id}`).then(response => response.data),
  
  vincularPromoter: (eventoId: number, promoterData: PromoterEventoCreate): Promise<any> => 
    api.post(`/eventos/${eventoId}/promoters`, promoterData).then(response => response.data),
  
  desvincularPromoter: (eventoId: number, promoterId: number): Promise<void> => 
    api.delete(`/eventos/${eventoId}/promoters/${promoterId}`).then(response => response.data),
  
  obterFinanceiro: (id: number): Promise<any> => 
    api.get(`/eventos/${id}/financeiro`).then(response => response.data),
  
  exportarCSV: (id: number): Promise<Blob> => 
    api.get(`/eventos/${id}/export/csv`, { responseType: 'blob' }).then(response => response.data),
  
  exportarPDF: (id: number): Promise<Blob> => 
    api.get(`/eventos/${id}/export/pdf`, { responseType: 'blob' }).then(response => response.data),
};

export const listaService = {
  async listarPorEvento(eventoId: number): Promise<Lista[]> {
    const response = await api.get(`/listas/evento/${eventoId}`);
    return response.data;
  },

  async listarPorPromoter(promoterId: number): Promise<Lista[]> {
    const response = await api.get(`/listas/promoter/${promoterId}`);
    return response.data;
  },

  async criar(lista: any): Promise<Lista> {
    const response = await api.post('/listas/', lista);
    return response.data;
  },

  async atualizar(listaId: number, lista: any): Promise<Lista> {
    const response = await api.put(`/listas/${listaId}`, lista);
    return response.data;
  },

  async desativar(listaId: number): Promise<void> {
    await api.delete(`/listas/${listaId}`);
  },

  async obterDetalhada(listaId: number): Promise<any> {
    const response = await api.get(`/listas/detalhada/${listaId}`);
    return response.data;
  },

  async importarConvidados(listaId: number, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/listas/${listaId}/convidados/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  async exportarConvidados(listaId: number, formato: 'csv' | 'excel'): Promise<Blob> {
    const response = await api.get(`/listas/${listaId}/convidados/export/${formato}`, {
      responseType: 'blob'
    });
    return response.data;
  },

  async obterDashboard(eventoId: number): Promise<any> {
    const response = await api.get(`/listas/dashboard/${eventoId}`);
    return response.data;
  }
};

export const transacaoService = {
  async listar(eventoId?: number, cpf?: string, status?: string): Promise<Transacao[]> {
    const params = new URLSearchParams();
    if (eventoId) params.append('evento_id', eventoId.toString());
    if (cpf) params.append('cpf_comprador', cpf);
    if (status) params.append('status', status);
    
    const response = await api.get(`/transacoes/?${params.toString()}`);
    return response.data;
  },

  async criar(transacao: Partial<Transacao>): Promise<Transacao> {
    const response = await api.post('/transacoes/', transacao);
    return response.data;
  },

  async obter(id: number): Promise<Transacao> {
    const response = await api.get(`/transacoes/${id}`);
    return response.data;
  },

  async atualizar(id: number, dados: Partial<Transacao>): Promise<Transacao> {
    const response = await api.put(`/transacoes/${id}`, dados);
    return response.data;
  }
};

export const dashboardService = {
  async obterResumo(eventoId?: number): Promise<any> {
    const params = eventoId ? `?evento_id=${eventoId}` : '';
    const response = await api.get(`/dashboard/resumo${params}`);
    return response.data;
  },

  async obterRankingPromoters(eventoId?: number, limit: number = 10): Promise<any[]> {
    const params = new URLSearchParams();
    if (eventoId) params.append('evento_id', eventoId.toString());
    params.append('limit', limit.toString());
    
    const response = await api.get(`/dashboard/ranking-promoters?${params.toString()}`);
    return response.data;
  },

  obterDadosTempoReal: (eventoId: number): Promise<any> => api.get(`/dashboard/tempo-real/${eventoId}`).then(response => response.data),

  obterDashboardAvancado: (filtros: any): Promise<any> =>
    api.get('/dashboard/avancado', { params: filtros }).then(response => response.data),

  obterGraficosVendasTempo: (periodo: string, eventoId?: number): Promise<any> =>
    api.get('/dashboard/graficos/vendas-tempo', { 
      params: { periodo, evento_id: eventoId } 
    }).then(response => response.data),

  obterGraficosVendasLista: (eventoId?: number): Promise<any> =>
    api.get('/dashboard/graficos/vendas-lista', { 
      params: { evento_id: eventoId } 
    }).then(response => response.data),

  obterRankingAvancado: (eventoId?: number): Promise<any[]> =>
    api.get(`/dashboard/ranking-promoters-avancado${eventoId ? `?evento_id=${eventoId}` : ''}`).then(response => response.data),

  exportarDashboard: (formato: string, filtros: any): Promise<any> =>
    api.get(`/relatorios/dashboard/export/${formato}`, { 
      params: filtros,
      responseType: 'blob'
    }).then(response => response.data),
};

export const relatoriosService = {
  exportarVendasCSV: (eventoId: number): Promise<Blob> =>
    api.get(`/relatorios/vendas/${eventoId}/csv`, { responseType: 'blob' }).then(response => response.data),

  exportarCheckinsCSV: (eventoId: number): Promise<Blob> =>
    api.get(`/relatorios/checkins/${eventoId}/csv`, { responseType: 'blob' }).then(response => response.data),

  exportarVendasExcel: (eventoId: number): Promise<Blob> =>
    api.get(`/relatorios/vendas/${eventoId}/excel`, { responseType: 'blob' }).then(response => response.data),

  exportarCheckinsExcel: (eventoId: number): Promise<Blob> =>
    api.get(`/relatorios/checkins/${eventoId}/excel`, { responseType: 'blob' }).then(response => response.data),
};

export const cupomService = {
  criar: (cupomData: any): Promise<any> => api.post('/cupons/', cupomData).then(response => response.data),
  validar: (codigo: string): Promise<any> => api.post(`/cupons/validar/${codigo}`).then(response => response.data),
  usar: (codigo: string): Promise<any> => api.post(`/cupons/usar/${codigo}`).then(response => response.data),
  listarPorEvento: (eventoId: number): Promise<any> => api.get(`/cupons/evento/${eventoId}`).then(response => response.data)
};

export const whatsappService = {
  inicializar: (webhookUrl?: string): Promise<any> => api.post('/whatsapp/init', { webhook_url: webhookUrl }).then(response => response.data),
  obterStatus: (): Promise<any> => api.get('/whatsapp/status').then(response => response.data),
  enviarConvite: (conviteData: any): Promise<any> => api.post('/whatsapp/send-invite', conviteData).then(response => response.data),
  enviarConvitesMassa: (convitesData: any): Promise<any> => api.post('/whatsapp/send-bulk', convitesData).then(response => response.data),
  listarConvites: (eventoId: number): Promise<any> => api.get(`/whatsapp/eventos/${eventoId}/invites`).then(response => response.data)
};

export const n8nService = {
  triggerEventoCriado: (eventoId: number, webhookUrl: string): Promise<any> => 
    api.post('/n8n/trigger/evento-criado', { evento_id: eventoId, n8n_webhook_url: webhookUrl }).then(response => response.data),
  triggerVendaRealizada: (transacaoId: number, webhookUrl: string): Promise<any> => 
    api.post('/n8n/trigger/venda-realizada', { transacao_id: transacaoId, n8n_webhook_url: webhookUrl }).then(response => response.data)
};

export const usuarioService = {
  listar: (): Promise<Usuario[]> => 
    api.get('/usuarios/').then(response => response.data),
  
  listarPromoters: (): Promise<Usuario[]> => 
    api.get('/usuarios/?tipo=promoter').then(response => response.data),
  
  obter: (id: number): Promise<Usuario> => 
    api.get(`/usuarios/${id}`).then(response => response.data),
  
  criar: (usuario: any): Promise<Usuario> => 
    api.post('/usuarios/', usuario).then(response => response.data),
  
  atualizar: (id: number, usuario: any): Promise<Usuario> => 
    api.put(`/usuarios/${id}`, usuario).then(response => response.data),
  
  desativar: (id: number): Promise<void> => 
    api.delete(`/usuarios/${id}`).then(response => response.data),
};

export const pdvService = {
  listarProdutos: (eventoId: number, filtros?: any): Promise<any[]> =>
    api.get(`/pdv/produtos?evento_id=${eventoId}`, { params: filtros }).then(response => response.data),
  
  criarProduto: (produto: any): Promise<any> =>
    api.post('/pdv/produtos', produto).then(response => response.data),
  
  obterProduto: (produtoId: number): Promise<any> =>
    api.get(`/pdv/produtos/${produtoId}`).then(response => response.data),
  
  atualizarProduto: (produtoId: number, produto: any): Promise<any> =>
    api.put(`/pdv/produtos/${produtoId}`, produto).then(response => response.data),

  listarComandas: (eventoId: number, filtros?: any): Promise<any[]> =>
    api.get(`/pdv/comandas?evento_id=${eventoId}`, { params: filtros }).then(response => response.data),
  
  criarComanda: (comanda: any): Promise<any> =>
    api.post('/pdv/comandas', comanda).then(response => response.data),
  
  recarregarComanda: (comandaId: number, recarga: any): Promise<any> =>
    api.post(`/pdv/comandas/${comandaId}/recarga`, recarga).then(response => response.data),

  processarVenda: (venda: any): Promise<any> =>
    api.post('/pdv/vendas', venda).then(response => response.data),
  
  listarVendas: (eventoId: number, filtros?: any): Promise<any[]> =>
    api.get(`/pdv/vendas?evento_id=${eventoId}`, { params: filtros }).then(response => response.data),

  abrirCaixa: (caixa: any): Promise<any> =>
    api.post('/pdv/caixa/abrir', caixa).then(response => response.data),
  
  fecharCaixa: (caixaId: number, valorFechamento: number, observacoes?: string): Promise<any> =>
    api.post(`/pdv/caixa/${caixaId}/fechar`, { valor_fechamento: valorFechamento, observacoes }).then(response => response.data),

  obterDashboardPDV: (eventoId: number): Promise<any> =>
    api.get(`/pdv/dashboard/${eventoId}`).then(response => response.data),

  relatorioX: (caixaId: number): Promise<any> =>
    api.get(`/pdv/relatorios/x/${caixaId}`).then(response => response.data),
  
  relatorioZ: (caixaId: number): Promise<any> =>
    api.get(`/pdv/relatorios/z/${caixaId}`).then(response => response.data),
};

export const financeiroService = {
  async criarMovimentacao(movimentacao: any): Promise<any> {
    const response = await api.post('/financeiro/movimentacoes', movimentacao);
    return response.data;
  },

  async listarMovimentacoes(eventoId: number, filtros?: any): Promise<any[]> {
    const response = await api.get(`/financeiro/movimentacoes/${eventoId}`, { params: filtros });
    return response.data;
  },

  async atualizarMovimentacao(movimentacaoId: number, movimentacao: any): Promise<any> {
    const response = await api.put(`/financeiro/movimentacoes/${movimentacaoId}`, movimentacao);
    return response.data;
  },

  async uploadComprovante(movimentacaoId: number, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/financeiro/movimentacoes/${movimentacaoId}/comprovante`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  async obterDashboard(eventoId: number): Promise<any> {
    const response = await api.get(`/financeiro/dashboard/${eventoId}`);
    return response.data;
  },

  async exportarRelatorio(eventoId: number, formato: 'pdf' | 'excel' | 'csv', dataInicio?: string, dataFim?: string): Promise<Blob> {
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    
    const response = await api.get(`/financeiro/relatorio/${eventoId}/export/${formato}?${params}`, {
      responseType: 'blob'
    });
    return response.data;
  },

  async abrirCaixa(caixa: any): Promise<any> {
    const response = await api.post('/financeiro/caixa/abrir', caixa);
    return response.data;
  },

  async fecharCaixa(caixaId: number, observacoes?: string): Promise<any> {
    const response = await api.post(`/financeiro/caixa/${caixaId}/fechar`, { observacoes_fechamento: observacoes });
    return response.data;
  }
};

export const gamificacaoService = {
  async obterRanking(filtros?: any): Promise<any[]> {
    const response = await api.get('/gamificacao/ranking', { params: filtros });
    return response.data;
  },

  async obterDashboard(eventoId?: number): Promise<any> {
    const response = await api.get('/gamificacao/dashboard', { 
      params: eventoId ? { evento_id: eventoId } : {} 
    });
    return response.data;
  },

  async criarConquista(conquista: any): Promise<any> {
    const response = await api.post('/gamificacao/conquistas', conquista);
    return response.data;
  },

  async verificarConquistas(promoterId: number): Promise<any> {
    const response = await api.post(`/gamificacao/verificar-conquistas/${promoterId}`);
    return response.data;
  },

  async exportarRanking(formato: 'excel' | 'csv' | 'pdf', filtros?: any): Promise<Blob> {
    const response = await api.get(`/gamificacao/export/ranking/${formato}`, {
      params: filtros,
      responseType: 'blob'
    });
    return response.data;
  },

  async obterMetricasPromoter(promoterId: number, eventoId?: number): Promise<any> {
    const response = await api.get(`/gamificacao/metricas/${promoterId}`, {
      params: eventoId ? { evento_id: eventoId } : {}
    });
    return response.data;
  }
};

export const checkinService = {
  checkinCPF: (cpf: string, eventoId: number, validacaoCpf: string): Promise<any> =>
    api.post('/checkins/', {
      cpf: cpf.replace(/\D/g, ''),
      evento_id: eventoId,
      metodo_checkin: 'cpf',
      validacao_cpf: validacaoCpf
    }),
  
  checkinQR: (qrCode: string, validacaoCpf: string): Promise<any> =>
    api.post('/checkins/qr', {
      qr_code: qrCode,
      validacao_cpf: validacaoCpf
    }),
  
  listarCheckins: (eventoId: number): Promise<any[]> =>
    api.get(`/checkins/evento/${eventoId}`),
  
  verificarCPF: (cpf: string, eventoId: number): Promise<any> =>
    api.get(`/checkins/cpf/${cpf}?evento_id=${eventoId}`),
  
  obterDashboard: (eventoId: number): Promise<any> =>
    api.get(`/checkins/dashboard/${eventoId}`),
};
