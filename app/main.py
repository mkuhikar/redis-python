import socket  # noqa: F401
import asyncio
from asyncio import Server

async def handle_client(reader,writer):
    
    addr = writer.get_extra_info('peername')

    

    
    client_response = b'+PONG\r\n'
    while(True):
        data = await reader.read(100)
        if not data:
            break
        messages = data.decode()
        print(f"Received {messages} from {addr!r}")
        messages = messages.split('\n')
        print(f"Messages {messages}")
        for message in messages:
            print(f"Individual message {message}")
            if 'PING' in message:
                writer.write(client_response)
                writer.drain()

    print("Close the connection")
    writer.close()
    await writer.wait_closed()

async def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    print("Starting the server")
    server = await asyncio.start_server(handle_client,'localhost',6379)
    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")
    async with server:
        await server.serve_forever()

    # Uncomment this to pass the first stage
    #
    # server_socket = socket.create_server(("localhost", 6379))

    

        


if __name__ == "__main__":
    asyncio.run(main())
