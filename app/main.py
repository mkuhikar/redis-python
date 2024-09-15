import socket  # noqa: F401
import asyncio
from asyncio import Server
from utility.parser import Parser

async def handle_client(reader,writer):
    
    addr = writer.get_extra_info('peername')

    client_response = b'+PONG\r\n'
    while(True):
        data = await reader.read(100)
        if not data:
            break
        messages = data.decode()
        print(f"Received {messages} from {addr!r}")
        # messages = messages.split('\n')

        try:
            parsed_command = Parser.parse_input(messages).split('\n')
            print(f"Parsed RESP command: {parsed_command}")
        except Exception as e:
            print(f"Error parsing command: {e}")
            writer.write(b'-ERR invalid command\r\n')  # Send an error response
            await writer.drain()
            continue
        if parsed_command[0] == 'PING':
            writer.write(client_response)
        elif parsed_command[0] == 'ECHO':
            if len(parsed_command)>1:
                echo_message = parsed_command[1]
                echo_response = f'+{echo_message}\r\n'
                writer.write(echo_response.encode())
            else:
                writer.write(b'-ERR wrong number of arguments for \'ECHO\' command\r\n')

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
