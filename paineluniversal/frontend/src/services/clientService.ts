import { api } from './api';

export interface MeepClient {
  id: string;
  nome: string;
  cpf?: string;
  identificador?: string;
  telefone?: string;
  email?: string;
  data_nascimento?: string;
  sexo?: string;
  categoria_id?: string;
  status: string;
  valor_em_aberto: number;
  nome_na_lista: boolean;
  has_alert: boolean;
  empresa_id: number;
  criado_em: string;
  atualizado_em: string;
}

export interface ClientCategory {
  id: string;
  descricao: string;
  empresa_id: number;
  criado_em: string;
  atualizado_em: string;
}

export interface ClientBlockHistory {
  id: string;
  cliente_id: string;
  bloqueado_por?: string;
  data_bloqueio?: string;
  razao_bloqueio?: string;
  desbloqueado_por?: string;
  data_desbloqueio?: string;
  razao_desbloqueio?: string;
  criado_em: string;
}

export interface ClientFilters {
  nome?: string;
  cpf?: string;
  identificador?: string;
  categoria?: string;
  nome_na_lista?: boolean;
  somente_bloqueados?: boolean;
  somente_com_alertas?: boolean;
}

export const clientService = {
  async getClients(filters?: ClientFilters): Promise<MeepClient[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value.toString());
        }
      });
    }
    
    const response = await api.get(`/meep-clients?${params.toString()}`);
    return response.data;
  },

  async getClient(id: string): Promise<MeepClient> {
    const response = await api.get(`/meep-clients/${id}`);
    return response.data;
  },

  async createClient(clientData: Partial<MeepClient>): Promise<MeepClient> {
    const response = await api.post('/meep-clients', clientData);
    return response.data;
  },

  async updateClient(id: string, clientData: Partial<MeepClient>): Promise<MeepClient> {
    const response = await api.put(`/meep-clients/${id}`, clientData);
    return response.data;
  },

  async deleteClient(id: string): Promise<void> {
    await api.delete(`/meep-clients/${id}`);
  },

  async toggleClientBlock(id: string, reason?: string): Promise<void> {
    await api.patch(`/meep-clients/${id}/toggle-block`, { reason });
  },

  async getClientBlockHistory(id: string): Promise<ClientBlockHistory[]> {
    const response = await api.get(`/meep-clients/${id}/block-history`);
    return response.data;
  },

  async getCategories(): Promise<ClientCategory[]> {
    const response = await api.get('/client-categories');
    return response.data;
  },

  async createCategory(categoryData: { descricao: string }): Promise<ClientCategory> {
    const response = await api.post('/client-categories', categoryData);
    return response.data;
  },

  async deleteCategory(id: string): Promise<void> {
    await api.delete(`/client-categories/${id}`);
  }
};
