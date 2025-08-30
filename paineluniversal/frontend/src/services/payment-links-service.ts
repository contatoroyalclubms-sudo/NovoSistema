/**
 * PaymentLinksService - API service for Payment Links
 * Sistema Universal de Gestão de Eventos
 */

import { 
  PaymentLink,
  PaymentLinkCreate,
  PaymentLinkUpdateData,
  PaymentLinksListResponse,
  PaymentLinkPaymentsResponse,
  LinkAnalytics,
  PaymentAttempt,
  PublicPaymentData,
  PaymentProcessingResult,
  PaymentLinkFilters,
  AnalyticsMetrics,
  ExportOptions,
  ApiError,
  ValidationError
} from '../types/payment-links';

import { cacheService } from './cache-service';

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const PAYMENT_LINKS_ENDPOINT = `${API_BASE_URL}/payment-links`;

class PaymentLinksApiService {
  private requestInterceptors: Array<(config: RequestInit) => RequestInit> = [];
  private responseInterceptors: Array<(response: Response) => Promise<Response>> = [];
  private maxRetries = 3;
  private retryDelay = 1000; // 1 second
  
  constructor() {
    // Add default error handling
    this.addResponseInterceptor(this.handleGlobalErrors.bind(this));
  }

  private getAuthHeaders(): Record<string, string> {
    const token = localStorage.getItem('authToken');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  // Request interceptors
  addRequestInterceptor(interceptor: (config: RequestInit) => RequestInit): void {
    this.requestInterceptors.push(interceptor);
  }

  // Response interceptors
  addResponseInterceptor(interceptor: (response: Response) => Promise<Response>): void {
    this.responseInterceptors.push(interceptor);
  }

  // Global error handler
  private async handleGlobalErrors(response: Response): Promise<Response> {
    if (response.status === 401) {
      // Handle authentication error
      localStorage.removeItem('authToken');
      window.location.href = '/login';
      throw new Error('Sessão expirada. Faça login novamente.');
    }

    if (response.status === 403) {
      throw new Error('Acesso negado. Você não tem permissão para esta operação.');
    }

    if (response.status === 429) {
      throw new Error('Muitas tentativas. Tente novamente em alguns minutos.');
    }

    if (response.status >= 500) {
      throw new Error('Erro interno do servidor. Tente novamente mais tarde.');
    }

    return response;
  }

  // Enhanced fetch with retry logic
  private async fetchWithRetry(
    url: string, 
    options: RequestInit, 
    attempt = 1
  ): Promise<Response> {
    try {
      // Apply request interceptors
      let modifiedOptions = { ...options };
      for (const interceptor of this.requestInterceptors) {
        modifiedOptions = interceptor(modifiedOptions);
      }

      const response = await fetch(url, modifiedOptions);

      // Apply response interceptors
      let modifiedResponse = response;
      for (const interceptor of this.responseInterceptors) {
        modifiedResponse = await interceptor(modifiedResponse);
      }

      return modifiedResponse;
    } catch (error) {
      // Retry logic for network errors
      if (attempt < this.maxRetries && this.isRetryableError(error)) {
        await this.delay(this.retryDelay * attempt);
        return this.fetchWithRetry(url, options, attempt + 1);
      }
      throw error;
    }
  }

  private isRetryableError(error: any): boolean {
    // Retry on network errors or 5xx status codes
    return (
      error instanceof TypeError || // Network error
      (error.status && error.status >= 500)
    );
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Enhanced error with context
  private enhanceError(error: any, context: string): Error {
    if (error instanceof Error) {
      error.message = `${context}: ${error.message}`;
      return error;
    }
    return new Error(`${context}: ${String(error)}`);
  }

  // Validation helpers
  private validateLinkData(data: PaymentLinkCreate): void {
    const errors: string[] = [];

    if (!data.title?.trim()) {
      errors.push('Título é obrigatório');
    }

    if (data.title && data.title.length > 100) {
      errors.push('Título deve ter no máximo 100 caracteres');
    }

    if (data.description && data.description.length > 500) {
      errors.push('Descrição deve ter no máximo 500 caracteres');
    }

    if (data.payment_type === 'single' && (!data.amount || data.amount <= 0)) {
      errors.push('Valor é obrigatório para pagamento único');
    }

    if (data.min_amount && data.max_amount && data.min_amount >= data.max_amount) {
      errors.push('Valor mínimo deve ser menor que o máximo');
    }

    if (data.webhook_url && !this.isValidUrl(data.webhook_url)) {
      errors.push('URL do webhook é inválida');
    }

    if (errors.length > 0) {
      throw new Error(errors.join('; '));
    }
  }

  private isValidUrl(url: string): boolean {
    try {
      new URL(url);
      return url.startsWith('http://') || url.startsWith('https://');
    } catch {
      return false;
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorData: any;
      
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: `HTTP Error: ${response.status}` };
      }

      const error: ApiError = {
        message: errorData.detail || errorData.message || 'An error occurred',
        code: errorData.code,
        status: response.status,
        details: errorData.details
      };

      throw error;
    }

    try {
      return await response.json();
    } catch {
      return {} as T;
    }
  }

  private buildQueryParams(params: Record<string, any>): string {
    const filtered = Object.entries(params)
      .filter(([, value]) => value !== undefined && value !== null && value !== '')
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
      .join('&');
    
    return filtered ? `?${filtered}` : '';
  }

  // ================================
  // PAYMENT LINKS MANAGEMENT
  // ================================

  async createPaymentLink(data: PaymentLinkCreate): Promise<PaymentLink> {
    try {
      // Client-side validation
      this.validateLinkData(data);

      const response = await this.fetchWithRetry(`${PAYMENT_LINKS_ENDPOINT}/create`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(data),
      });

      const result = await this.handleResponse<PaymentLink>(response);
      
      // Clear cache to ensure fresh data
      this.clearCache();
      
      return result;
    } catch (error) {
      throw this.enhanceError(error, 'Erro ao criar link de pagamento');
    }
  }

  async getPaymentLinks(filters?: PaymentLinkFilters): Promise<PaymentLinksListResponse> {
    const queryParams = this.buildQueryParams(filters || {});
    const response = await fetch(`${PAYMENT_LINKS_ENDPOINT}/list${queryParams}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse<PaymentLinksListResponse>(response);
  }

  async getPaymentLink(linkId: string): Promise<PaymentLink> {
    const response = await fetch(`${PAYMENT_LINKS_ENDPOINT}/${linkId}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse<PaymentLink>(response);
  }

  async updatePaymentLink(linkId: string, data: PaymentLinkUpdateData): Promise<PaymentLink> {
    const response = await fetch(`${PAYMENT_LINKS_ENDPOINT}/${linkId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });

    return this.handleResponse<PaymentLink>(response);
  }

  async deletePaymentLink(linkId: string): Promise<{ message: string }> {
    const response = await fetch(`${PAYMENT_LINKS_ENDPOINT}/${linkId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse<{ message: string }>(response);
  }

  async toggleLinkStatus(linkId: string, status: string): Promise<PaymentLink> {
    return this.updatePaymentLink(linkId, { status } as any);
  }

  // ================================
  // PUBLIC PAYMENT PROCESSING
  // ================================

  async getPublicPaymentLink(linkId: string): Promise<PaymentLink> {
    const response = await fetch(`${PAYMENT_LINKS_ENDPOINT}/p/${linkId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }, // No auth for public
    });

    // For public endpoints, we might get HTML, so handle differently
    if (response.headers.get('content-type')?.includes('text/html')) {
      throw new Error('Link não encontrado ou inválido');
    }

    return this.handleResponse<PaymentLink>(response);
  }

  async processPayment(linkId: string, data: PublicPaymentData): Promise<PaymentProcessingResult> {
    const response = await fetch(`${PAYMENT_LINKS_ENDPOINT}/p/${linkId}/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }, // No auth for public
      body: JSON.stringify(data),
    });

    return this.handleResponse<PaymentProcessingResult>(response);
  }

  // ================================
  // ANALYTICS AND REPORTING
  // ================================

  async getLinkAnalytics(linkId: string, periodDays: number = 30): Promise<LinkAnalytics> {
    const response = await fetch(
      `${PAYMENT_LINKS_ENDPOINT}/${linkId}/analytics?period_days=${periodDays}`,
      {
        method: 'GET',
        headers: this.getAuthHeaders(),
      }
    );

    return this.handleResponse<LinkAnalytics>(response);
  }

  async getLinkPayments(
    linkId: string,
    filters?: {
      status?: string;
      start_date?: string;
      end_date?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<PaymentLinkPaymentsResponse> {
    const queryParams = this.buildQueryParams(filters || {});
    const response = await fetch(
      `${PAYMENT_LINKS_ENDPOINT}/${linkId}/payments${queryParams}`,
      {
        method: 'GET',
        headers: this.getAuthHeaders(),
      }
    );

    return this.handleResponse<PaymentLinkPaymentsResponse>(response);
  }

  async getOverallAnalytics(
    periodDays: number = 30,
    filters?: Record<string, any>
  ): Promise<AnalyticsMetrics> {
    const params = { period_days: periodDays, ...filters };
    const queryParams = this.buildQueryParams(params);
    
    const response = await fetch(`${PAYMENT_LINKS_ENDPOINT}/analytics${queryParams}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse<AnalyticsMetrics>(response);
  }

  // ================================
  // BULK OPERATIONS
  // ================================

  async duplicatePaymentLink(linkId: string, newTitle?: string): Promise<PaymentLink> {
    const originalLink = await this.getPaymentLink(linkId);
    
    const duplicateData: PaymentLinkCreate = {
      title: newTitle || `${originalLink.title} (Cópia)`,
      description: originalLink.description,
      amount: originalLink.amount,
      min_amount: originalLink.min_amount,
      max_amount: originalLink.max_amount,
      currency: originalLink.currency,
      payment_type: originalLink.payment_type,
      theme: originalLink.theme,
      custom_css: originalLink.custom_css,
      logo_url: originalLink.logo_url,
      success_url: originalLink.success_url,
      cancel_url: originalLink.cancel_url,
      enable_split: originalLink.enable_split,
      split_recipients: originalLink.split_recipients,
      collect_customer_info: originalLink.collect_customer_info,
      send_receipt: originalLink.send_receipt,
      allow_installments: originalLink.allow_installments,
      webhook_url: originalLink.webhook_url,
      metadata: { ...originalLink.metadata, cloned_from: linkId }
    };

    return this.createPaymentLink(duplicateData);
  }

  async bulkUpdateStatus(linkIds: string[], status: string): Promise<{ success: number; failed: number }> {
    const results = await Promise.allSettled(
      linkIds.map(id => this.toggleLinkStatus(id, status))
    );

    const success = results.filter(r => r.status === 'fulfilled').length;
    const failed = results.filter(r => r.status === 'rejected').length;

    return { success, failed };
  }

  async bulkDelete(linkIds: string[]): Promise<{ success: number; failed: number }> {
    const results = await Promise.allSettled(
      linkIds.map(id => this.deletePaymentLink(id))
    );

    const success = results.filter(r => r.status === 'fulfilled').length;
    const failed = results.filter(r => r.status === 'rejected').length;

    return { success, failed };
  }

  // ================================
  // EXPORT AND REPORTING
  // ================================

  async exportPaymentLinks(options: ExportOptions): Promise<Blob> {
    const response = await fetch(`${PAYMENT_LINKS_ENDPOINT}/export`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(options),
    });

    if (!response.ok) {
      throw new Error('Falha na exportação');
    }

    return response.blob();
  }

  async generateQRCode(linkId: string, options?: {
    size?: number;
    format?: 'png' | 'svg';
    style?: string;
  }): Promise<string> {
    const queryParams = this.buildQueryParams(options || {});
    const response = await fetch(
      `${PAYMENT_LINKS_ENDPOINT}/${linkId}/qr${queryParams}`,
      {
        method: 'GET',
        headers: this.getAuthHeaders(),
      }
    );

    const result = await this.handleResponse<{ qr_code: string }>(response);
    return result.qr_code;
  }

  // ================================
  // UTILITIES
  // ================================

  async validateWebhookUrl(url: string): Promise<{ valid: boolean; message?: string }> {
    try {
      const response = await fetch(`${PAYMENT_LINKS_ENDPOINT}/webhook/test`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ url }),
      });

      return this.handleResponse<{ valid: boolean; message?: string }>(response);
    } catch (error) {
      return { 
        valid: false, 
        message: error instanceof Error ? error.message : 'Erro na validação do webhook' 
      };
    }
  }

  generateShareableUrl(linkId: string): string {
    return `${window.location.origin}/pay/${linkId}`;
  }

  generateEmbedCode(linkId: string, options?: {
    width?: number;
    height?: number;
    theme?: string;
  }): string {
    const width = options?.width || 400;
    const height = options?.height || 600;
    const theme = options?.theme || 'default';
    
    const embedUrl = `${window.location.origin}/embed/payment/${linkId}?theme=${theme}`;
    
    return `<iframe src="${embedUrl}" width="${width}" height="${height}" frameborder="0" style="border: none; border-radius: 8px;"></iframe>`;
  }

  // ================================
  // ERROR HANDLING HELPERS
  // ================================

  isValidationError(error: any): error is { validation_errors: ValidationError[] } {
    return error && typeof error === 'object' && Array.isArray(error.validation_errors);
  }

  extractValidationErrors(error: any): Record<string, string> {
    if (this.isValidationError(error)) {
      return error.validation_errors.reduce((acc, err) => {
        acc[err.field] = err.message;
        return acc;
      }, {} as Record<string, string>);
    }
    return {};
  }

  // ================================
  // CACHING AND PERFORMANCE
  // ================================

  private cache = new Map<string, { data: any; expiry: number }>();

  private getCacheKey(endpoint: string, params?: any): string {
    return `${endpoint}:${JSON.stringify(params || {})}`;
  }

  private getCachedData<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() < cached.expiry) {
      return cached.data;
    }
    this.cache.delete(key);
    return null;
  }

  private setCachedData<T>(key: string, data: T, ttlMs: number = 300000): void {
    this.cache.set(key, {
      data,
      expiry: Date.now() + ttlMs
    });
  }

  async getPaymentLinksWithCache(filters?: PaymentLinkFilters): Promise<PaymentLinksListResponse> {
    const cacheKey = this.getCacheKey('payment-links', filters);
    const cached = this.getCachedData<PaymentLinksListResponse>(cacheKey);
    
    if (cached) {
      return cached;
    }

    const data = await this.getPaymentLinks(filters);
    this.setCachedData(cacheKey, data, 60000); // 1 minute cache
    
    return data;
  }

  clearCache(): void {
    this.cache.clear();
  }

  // ================================
  // REAL-TIME UPDATES
  // ================================

  subscribeToLinkUpdates(linkId: string, callback: (data: any) => void): () => void {
    // Placeholder for WebSocket subscription
    // In a real implementation, this would set up a WebSocket connection
    console.log(`Subscribed to updates for link ${linkId}`);
    
    // Return unsubscribe function
    return () => {
      console.log(`Unsubscribed from updates for link ${linkId}`);
    };
  }

  subscribeToPaymentUpdates(callback: (data: any) => void): () => void {
    // Placeholder for real-time payment notifications
    console.log('Subscribed to payment updates');
    
    return () => {
      console.log('Unsubscribed from payment updates');
    };
  }
}

// Singleton instance
const paymentLinksService = new PaymentLinksApiService();

export { paymentLinksService, PaymentLinksApiService };
export default paymentLinksService;