#!/usr/bin/env python3
"""tcp_server - TCP echo server and client."""
import sys, socket, threading
def server(host="127.0.0.1", port=9999):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((host,port)); s.listen(5); print(f"Listening on {host}:{port}")
    while True:
        conn,addr=s.accept(); print(f"Connected: {addr}")
        threading.Thread(target=handle,args=(conn,addr),daemon=True).start()
def handle(conn, addr):
    try:
        while True:
            data=conn.recv(4096)
            if not data: break
            print(f"[{addr}] {data.decode().strip()}"); conn.sendall(data)
    finally: conn.close(); print(f"Disconnected: {addr}")
def client(host="127.0.0.1", port=9999, msg="Hello"):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.connect((host,port))
    s.sendall(msg.encode()); print(f"Sent: {msg}"); print(f"Received: {s.recv(4096).decode()}"); s.close()
if __name__=="__main__":
    if len(sys.argv)<2: print("Usage: tcp_server <server|client> [host] [port]"); sys.exit(1)
    host=sys.argv[2] if len(sys.argv)>2 else "127.0.0.1"; port=int(sys.argv[3]) if len(sys.argv)>3 else 9999
    if sys.argv[1]=="server": server(host,port)
    elif sys.argv[1]=="client": client(host,port," ".join(sys.argv[4:]) or "Hello")
