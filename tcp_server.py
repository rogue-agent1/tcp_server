#!/usr/bin/env python3
"""TCP Server — non-blocking event loop with connection management."""
import socket, select, time

class TCPServer:
    def __init__(self, host='127.0.0.1', port=0):
        self.host = host; self.port = port
        self.server = None; self.clients = {}; self.handlers = {}
        self.running = False
    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setblocking(False); self.server.bind((self.host, self.port))
        self.port = self.server.getsockname()[1]; self.server.listen(128)
        self.running = True; return self.port
    def on(self, event, handler): self.handlers[event] = handler
    def poll(self, timeout=0.1):
        if not self.running: return
        readable, _, _ = select.select([self.server] + list(self.clients.values()), [], [], timeout)
        for sock in readable:
            if sock is self.server:
                conn, addr = sock.accept(); conn.setblocking(False)
                self.clients[addr] = conn
                if 'connect' in self.handlers: self.handlers['connect'](addr)
            else:
                addr = next(a for a, s in self.clients.items() if s is sock)
                try:
                    data = sock.recv(4096)
                    if data:
                        if 'data' in self.handlers: self.handlers['data'](addr, data)
                    else: self._disconnect(addr)
                except: self._disconnect(addr)
    def send(self, addr, data):
        if addr in self.clients: self.clients[addr].sendall(data)
    def _disconnect(self, addr):
        if addr in self.clients:
            self.clients[addr].close(); del self.clients[addr]
            if 'disconnect' in self.handlers: self.handlers['disconnect'](addr)
    def stop(self):
        self.running = False
        for sock in self.clients.values(): sock.close()
        self.clients.clear()
        if self.server: self.server.close()

if __name__ == "__main__":
    server = TCPServer()
    log = []
    server.on('connect', lambda addr: log.append(f"connected: {addr}"))
    server.on('data', lambda addr, data: (log.append(f"data from {addr}: {data}"), server.send(addr, b"echo:" + data)))
    server.on('disconnect', lambda addr: log.append(f"disconnected: {addr}"))
    port = server.start()
    # Quick self-test
    client = socket.socket(); client.connect(('127.0.0.1', port))
    server.poll(0.1); client.sendall(b"hello"); server.poll(0.1)
    echo = client.recv(1024); client.close(); server.poll(0.1); server.stop()
    print(f"Echo: {echo}"); print(f"Log: {log}")
