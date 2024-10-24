
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
