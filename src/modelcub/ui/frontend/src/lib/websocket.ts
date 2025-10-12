/**
 * WebSocket manager for real-time updates
 */

type MessageHandler = (data: unknown) => void;
type MessageType = string;

interface WebSocketMessage {
  type: MessageType;
  [key: string]: unknown;
}

class WebSocketManager {
  private ws: WebSocket | null = null;
  private handlers = new Map<MessageType, Set<MessageHandler>>();
  private reconnectTimeout = 1000;
  private readonly maxReconnectTimeout = 30000;
  private reconnectTimer: number | null = null;

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const url = `${protocol}//${host}/ws`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log("[WS] Connected");
      this.reconnectTimeout = 1000;
    };

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as WebSocketMessage;
        const handlers = this.handlers.get(data.type);

        if (handlers) {
          handlers.forEach((handler) => handler(data));
        }
      } catch (error) {
        console.error("[WS] Error parsing message:", error);
      }
    };

    this.ws.onerror = (error) => {
      console.error("[WS] Error:", error);
    };

    this.ws.onclose = () => {
      console.log("[WS] Disconnected");
      this.scheduleReconnect();
    };
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return;
    }

    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
      this.reconnectTimeout = Math.min(
        this.reconnectTimeout * 2,
        this.maxReconnectTimeout
      );
    }, this.reconnectTimeout);
  }

  /**
   * Subscribe to message type
   */
  on(type: MessageType, handler: MessageHandler): void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler);
  }

  /**
   * Unsubscribe from message type
   */
  off(type: MessageType, handler: MessageHandler): void {
    const handlers = this.handlers.get(type);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  /**
   * Send message to server
   */
  send(data: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn("[WS] Cannot send, not connected");
    }
  }

  /**
   * Disconnect from server
   */
  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const wsManager = new WebSocketManager();
