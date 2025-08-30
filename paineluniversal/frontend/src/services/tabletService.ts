import { api } from './api';

export interface Tablet {
  id: string;
  nome: string;
  ip: string;
  porta: number;
  tipo: string;
  status: string;
  empresa_id: string;
  configuracao_meep?: any;
  criado_em: string;
  ultima_conexao?: string;
  ultima_sincronizacao?: string;
  versao_config?: string;
}

export interface TabletCreate {
  nome: string;
  ip: string;
  porta: number;
  tipo: string;
  configuracao_meep?: any;
}

export interface TabletUpdate {
  nome?: string;
  ip?: string;
  porta?: number;
  tipo?: string;
  status?: string;
  configuracao_meep?: any;
}

export interface TabletStatus {
  tablet_id: string;
  nome: string;
  ip: string;
  porta: number;
  status: string;
  online: boolean;
  ultima_conexao?: string;
  versao_config?: string;
  uptime?: number;
}

export interface MeepIntegrationRequest {
  tablet_id: string;
  config: any;
  force_sync?: boolean;
}

export const tabletService = {
  async listar(): Promise<Tablet[]> {
    const response = await api.get('/api/tablets/');
    return response.data;
  },

  async criar(tablet: TabletCreate): Promise<Tablet> {
    const response = await api.post('/api/tablets/', tablet);
    return response.data;
  },

  async atualizar(id: string, tablet: TabletUpdate): Promise<Tablet> {
    const response = await api.put(`/api/tablets/${id}`, tablet);
    return response.data;
  },

  async deletar(id: string): Promise<void> {
    await api.delete(`/api/tablets/${id}`);
  },

  async obter(id: string): Promise<Tablet> {
    const response = await api.get(`/api/tablets/${id}`);
    return response.data;
  },

  async verificarStatus(id: string): Promise<TabletStatus> {
    const response = await api.get(`/api/tablets/${id}/status`);
    return response.data;
  },

  async sincronizarConfig(id: string, config: any): Promise<any> {
    const response = await api.post(`/api/tablets/${id}/sync-config`, { config });
    return response.data;
  },

  async integrarMeep(integrationData: MeepIntegrationRequest): Promise<any> {
    const response = await api.post('/api/tablets/integrate', integrationData);
    return response.data;
  },

  async sincronizarTodos(tablet_ids: string[], configuracao: any, force: boolean = false): Promise<any> {
    const response = await api.post('/api/tablets/bulk-sync', {
      tablet_ids,
      configuracao,
      force
    });
    return response.data;
  },

  async listarLogs(tablet_id?: string): Promise<any[]> {
    const url = tablet_id ? `/api/tablets/logs?tablet_id=${tablet_id}` : '/api/tablets/logs';
    const response = await api.get(url);
    return response.data;
  },

  async testarConexao(ip: string, porta: number): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`http://${ip}:${porta}/health`, {
        method: 'GET',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      return false;
    }
  }
};
