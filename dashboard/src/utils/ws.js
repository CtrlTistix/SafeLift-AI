const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/events';

class WebSocketClient {
    constructor() {
        this.ws = null;
        this.listeners = new Set();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.isIntentionallyClosed = false;
    }

    connect() {
        if (this.ws?.readyState === WebSocket.OPEN) {
            return;
        }

        this.isIntentionallyClosed = false;
        this.ws = new WebSocket(WS_URL);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;

            this.pingInterval = setInterval(() => {
                if (this.ws?.readyState === WebSocket.OPEN) {
                    this.ws.send('ping');
                }
            }, 30000);
        };

        this.ws.onmessage = (event) => {
            if (event.data === 'pong') {
                return;
            }

            try {
                const data = JSON.parse(event.data);
                this.notifyListeners(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');

            if (this.pingInterval) {
                clearInterval(this.pingInterval);
            }

            if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

                setTimeout(() => {
                    this.connect();
                }, this.reconnectDelay);
            }
        };
    }

    disconnect() {
        this.isIntentionallyClosed = true;

        if (this.pingInterval) {
            clearInterval(this.pingInterval);
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    subscribe(callback) {
        this.listeners.add(callback);

        return () => {
            this.listeners.delete(callback);
        };
    }

    notifyListeners(data) {
        this.listeners.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error('Error in WebSocket listener:', error);
            }
        });
    }

    getConnectionState() {
        if (!this.ws) return 'DISCONNECTED';

        switch (this.ws.readyState) {
            case WebSocket.CONNECTING:
                return 'CONNECTING';
            case WebSocket.OPEN:
                return 'CONNECTED';
            case WebSocket.CLOSING:
                return 'CLOSING';
            case WebSocket.CLOSED:
                return 'DISCONNECTED';
            default:
                return 'UNKNOWN';
        }
    }
}

export default new WebSocketClient();
