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
  private isConnected = false;
  private isConnecting = false;

  /**
   * Connect to WebSocket server (idempotent - safe to call multiple times)
   */
  connect(): void {
    // Already connected or connecting - do nothing
    if (this.isConnected || this.isConnecting) {
      return;
    }

    // Close existing connection if in weird state
    if (this.ws) {
      const state = this.ws.readyState;
      if (state === WebSocket.OPEN || state === WebSocket.CONNECTING) {
        console.log("[WS] Closing stale connection");
        this.ws.close();
      }
      this.ws = null;
    }

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const url = `${protocol}//${host}/ws`;

    console.log("[WS] Connecting...");
    this.isConnecting = true;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log("[WS] Connected");
      this.isConnected = true;
      this.isConnecting = false;
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
      this.isConnecting = false;
    };

    this.ws.onclose = () => {
      console.log("[WS] Disconnected");
      this.isConnected = false;
      this.isConnecting = false;
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

    console.log(`[WS] Reconnecting in ${this.reconnectTimeout}ms...`);
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
   * Get connection status
   */
  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  /**
   * Disconnect from server
   */
  disconnect(): void {
    console.log("[WS] Manual disconnect");

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      // Remove event listeners to prevent reconnect on manual disconnect
      this.ws.onclose = null;
      this.ws.close();
      this.ws = null;
    }

    this.isConnected = false;
    this.isConnecting = false;
  }
}

export const wsManager = new WebSocketManager();
