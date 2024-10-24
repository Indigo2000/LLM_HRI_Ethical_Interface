<<<<<<< HEAD
import socket
=======
>>>>>>> 04d01ba4bca8e1cc630a59f42f570b47d5895c7e
import asyncio

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connection from {addr}")
    
    while True:
        data = await reader.read(100)  # Asynchronously read data from the client
        if not data:
            break
        message = data.decode('utf-8')
        print(f"Received: {message}")
        
        # Echoing the message back to the client (optional)
        writer.write(data)
        await writer.drain()  # Ensure the data is sent out

<<<<<<< HEAD
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
=======
    print(f"Closing connection to {addr}")
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, 'localhost', 12345)
    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")
    
    async with server:
        await server.serve_forever()

# Run the asyncio event loop
asyncio.run(main())
>>>>>>> 04d01ba4bca8e1cc630a59f42f570b47d5895c7e
