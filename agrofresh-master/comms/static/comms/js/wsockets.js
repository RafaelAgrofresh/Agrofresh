class WebSocketConnection {
    constructor(url, reconnectInterval) {
        this.url = url || `ws://${window.location.host}`;
        this.reconnectInterval = reconnectInterval || 2000; // ms
        this.subscriptions = new Set();
        this.connect();
    }

    subscribe(subscription) {
        this.subscriptions.add(subscription);
    }

    unsubscribe(subscription) {
        this.subscriptions.delete(subscription);
    }

    connect() {
        this.dispose();

        this.ws = new WebSocket(this.url);
        this.ws.onopen = this.onOpen.bind(this);
        this.ws.onmessage = this.onMessage.bind(this);
        this.ws.onclose = this.onError.bind(this);
        this.ws.onerror = this.onError.bind(this);
    }

    dispose() {
        if (!this.ws) return;

        this.ws.onopen = null;
        this.ws.onmessage = null;
        this.ws.onclose = null;
        this.ws.onerror = null;
        this.ws.close();
    }

    sendToSubscribers(msg) {
        this.subscriptions.forEach(s => s(msg));
    }

    onOpen(event) {
        this.sendToSubscribers({
            type: 'status',
            value: 'connected',
            desc: 'websocket connected'
        });
    }

    onMessage(event) {
        // TODO check pong
        // TODO dispatch messages to subscribers
        this.sendToSubscribers(event);
    }

    onClose(event) {
        if (!event.wasClean)
            this.sendToSubscribers({
                type: 'status',
                value: 'closed',
                desc: `websocket error [${event.code}]: ${event.reason || 'unknown'}`,
            });

        setTimeout(() => this.connect(), this.reconnectInterval);
    }

    onError(event) {
        this.sendToSubscribers({
            type: 'status',
            value: 'error',
            desc: `websocket error [${event.code}]: ${event.reason || 'unknown'}`
        });

        setTimeout(() => this.connect(), this.reconnectInterval);
    }

    ping() {
        this.ws.send("ping");
        setTimeout(this.ping(), 1000);
    }
}

export const ws = new WebSocketConnection();