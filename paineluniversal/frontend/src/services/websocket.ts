class WebSocketService {
  private ws: WebSocket | null = null;
  private eventoId: number | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private listeners: { [key: string]: ((data: any) => void)[] } = {};

  connect(eventoId: number) {
    this.eventoId = eventoId;
    this.connectWebSocket();
  }

  private connectWebSocket() {
    if (!this.eventoId) return;

    const wsUrl = `ws://localhost:8000/api/ws/${this.eventoId}`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket conectado ao PDV');
        this.reconnectAttempts = 0;
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Erro ao processar mensagem WebSocket:', error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket desconectado');
        this.attemptReconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('Erro WebSocket:', error);
      };
      
    } catch (error) {
      console.error('Erro ao conectar WebSocket:', error);
      this.attemptReconnect();
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
    }
  }

  private handleMessage(data: any) {
    const { type } = data;
    
    if (this.listeners[type]) {
      this.listeners[type].forEach(callback => callback(data));
    }
    
    if (this.listeners['*']) {
      this.listeners['*'].forEach(callback => callback(data));
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  off(event: string, callback: (data: any) => void) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners = {};
  }
}

export const websocketService = new WebSocketService();
