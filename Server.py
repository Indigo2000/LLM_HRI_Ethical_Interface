import socket
import asyncio

# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(1)

# Asyncio event loop setup
loop = asyncio.get_event_loop()

async def run_server():
    print("Server listening for connections...")

    conn, addr = server_socket.accept()
    print(f"Connection from {addr}")

    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Received: {data.decode('utf-8')}")

    conn.close()

# Run both the server loop and asyncio loop
loop.run_until_complete(run_server())
