export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  user_id?: number;
  evento_id?: number;
}

export interface ConnectionOptions {
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
  reconnectInterval?: number;
  heartbeatInterval?: number;
}

class WebSocketManager {
  private ws: WebSocket | null = null;
  private eventoId: number | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private heartbeatInterval = 30000;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private listeners: { [key: string]: ((data: WebSocketMessage) => void)[] } = {};
  private connectionOptions: ConnectionOptions = {};
  private isConnecting = false;

  /**
   * Conecta ao WebSocket de um evento específico
   */
  connect(eventoId: number, options?: ConnectionOptions) {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.eventoId = eventoId;
    this.connectionOptions = { 
      autoReconnect: true,
      maxReconnectAttempts: 5,
      reconnectInterval: 3000,
      heartbeatInterval: 30000,
      ...options 
    };
    
    this.maxReconnectAttempts = this.connectionOptions.maxReconnectAttempts!;
    this.reconnectInterval = this.connectionOptions.reconnectInterval!;
    this.heartbeatInterval = this.connectionOptions.heartbeatInterval!;

    this.connectWebSocket();
  }

  /**
   * Conecta ao WebSocket global (sem evento específico)
   */
  connectGlobal(options?: ConnectionOptions) {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.eventoId = null;
    this.connectionOptions = { 
      autoReconnect: true,
      maxReconnectAttempts: 5,
      reconnectInterval: 3000,
      heartbeatInterval: 30000,
      ...options 
    };

    this.connectWebSocket();
  }

  private connectWebSocket() {
    if (this.isConnecting) return;
    
    this.isConnecting = true;

    const baseUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8002';
    const token = localStorage.getItem('access_token');
    
    let wsUrl: string;
    if (this.eventoId) {
      wsUrl = `${baseUrl}/api/v1/ws/evento/${this.eventoId}?token=${token}`;
    } else {
      wsUrl = `${baseUrl}/api/v1/ws/global?token=${token}`;
    }
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log(`WebSocket conectado ${this.eventoId ? `ao evento ${this.eventoId}` : 'globalmente'}`);
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        this.emit('connected', { eventoId: this.eventoId });
      };
      
      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Erro ao processar mensagem WebSocket:', error);
        }
      };
      
      this.ws.onclose = (event) => {
        console.log('WebSocket desconectado', event);
        this.isConnecting = false;
        this.stopHeartbeat();
        this.emit('disconnected', { code: event.code, reason: event.reason });
        
        if (this.connectionOptions.autoReconnect) {
          this.attemptReconnect();
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('Erro WebSocket:', error);
        this.isConnecting = false;
        this.emit('error', { error });
      };
      
    } catch (error) {
      console.error('Erro ao conectar WebSocket:', error);
      this.isConnecting = false;
      
      if (this.connectionOptions.autoReconnect) {
        this.attemptReconnect();
      }
    }
  }

  private startHeartbeat() {
    this.stopHeartbeat();
    
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({
          type: 'ping',
          data: { timestamp: new Date().toISOString() }
        });
      }
    }, this.heartbeatInterval);
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Tentando reconectar WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connectWebSocket();
      }, this.reconnectInterval);
    } else {
      console.error('Máximo de tentativas de reconexão atingido');
      this.emit('reconnectFailed', { attempts: this.reconnectAttempts });
    }
  }

  private handleMessage(message: WebSocketMessage) {
    console.log('WebSocket message received:', message);
    
    // Responder a pings
    if (message.type === 'ping') {
      this.send({
        type: 'pong',
        data: { timestamp: new Date().toISOString() }
      });
      return;
    }
    
    // Emitir para listeners específicos do tipo
    if (this.listeners[message.type]) {
      this.listeners[message.type].forEach(callback => callback(message));
    }
    
    // Emitir para listeners globais
    if (this.listeners['*']) {
      this.listeners['*'].forEach(callback => callback(message));
    }
  }

  private emit(event: string, data: any) {
    const message: WebSocketMessage = {
      type: event,
      data,
      timestamp: new Date().toISOString()
    };
    
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(message));
    }
  }

  /**
   * Adiciona listener para um tipo de evento específico
   */
  on(event: string, callback: (message: WebSocketMessage) => void) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  /**
   * Remove listener para um tipo de evento específico
   */
  off(event: string, callback: (message: WebSocketMessage) => void) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }

  /**
   * Remove todos os listeners de um evento
   */
  removeAllListeners(event?: string) {
    if (event) {
      delete this.listeners[event];
    } else {
      this.listeners = {};
    }
  }

  /**
   * Envia mensagem pelo WebSocket
   */
  send(message: { type: string; data: any }) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const fullMessage: WebSocketMessage = {
        ...message,
        timestamp: new Date().toISOString(),
        evento_id: this.eventoId || undefined
      };
      
      this.ws.send(JSON.stringify(fullMessage));
      return true;
    }
    
    console.warn('WebSocket não está conectado. Mensagem não enviada:', message);
    return false;
  }

  /**
   * Envia evento específico do PDV
   */
  sendPDVEvent(eventType: string, data: any) {
    return this.send({
      type: `pdv_${eventType}`,
      data
    });
  }

  /**
   * Envia evento específico de check-in
   */
  sendCheckinEvent(eventType: string, data: any) {
    return this.send({
      type: `checkin_${eventType}`,
      data
    });
  }

  /**
   * Envia evento de gamificação
   */
  sendGamificationEvent(eventType: string, data: any) {
    return this.send({
      type: `gamification_${eventType}`,
      data
    });
  }

  /**
   * Desconecta do WebSocket
   */
  disconnect() {
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    this.listeners = {};
    this.eventoId = null;
    this.isConnecting = false;
  }

  /**
   * Verifica se está conectado
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Obtém status da conexão
   */
  getConnectionState(): string {
    if (!this.ws) return 'DISCONNECTED';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'CONNECTED';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'CLOSED';
      default:
        return 'UNKNOWN';
    }
  }
}

// Singleton instance
export const websocketService = new WebSocketManager();

// Eventos pré-definidos para facilitar uso
export const WS_EVENTS = {
  // Sistema
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
  ERROR: 'error',
  RECONNECT_FAILED: 'reconnectFailed',
  
  // PDV
  PDV_NEW_SALE: 'pdv_new_sale',
  PDV_SALE_CANCELLED: 'pdv_sale_cancelled',
  PDV_PRODUCT_LOW_STOCK: 'pdv_product_low_stock',
  PDV_CASH_OPENED: 'pdv_cash_opened',
  PDV_CASH_CLOSED: 'pdv_cash_closed',
  
  // Check-in
  CHECKIN_NEW: 'checkin_new',
  CHECKIN_CANCELLED: 'checkin_cancelled',
  CHECKIN_STATS_UPDATED: 'checkin_stats_updated',
  
  // Gamificação
  GAMIFICATION_POINTS_EARNED: 'gamification_points_earned',
  GAMIFICATION_ACHIEVEMENT_UNLOCKED: 'gamification_achievement_unlocked',
  GAMIFICATION_LEADERBOARD_UPDATED: 'gamification_leaderboard_updated',
  
  // Eventos
  EVENT_UPDATED: 'event_updated',
  EVENT_PARTICIPANT_JOINED: 'event_participant_joined',
  EVENT_PARTICIPANT_LEFT: 'event_participant_left',
  
  // Notificações
  NOTIFICATION_NEW: 'notification_new',
  NOTIFICATION_READ: 'notification_read',
} as const;

export default websocketService;
