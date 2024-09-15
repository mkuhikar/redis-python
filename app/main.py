import socket  # noqa: F401
import asyncio
from asyncio import Server
from utility.parser import Parser

async def handle_client(reader,writer):
    
    addr = writer.get_extra_info('peername')
    redis_store = {}

    client_response = b'+PONG\r\n'
    while(True):
        data = await reader.read(100)
        if not data:
            break
        messages = data.decode()
        print(f"Received {messages} from {addr!r}")
        # messages = messages.split('\n')
        try:
            command,argument,argument2,command2,argument3 = Parser.parse_resp(messages)
            print(f"Parsed command: {command}, argument: {argument} argument2 {argument2}")
        except Exception as e:
            print(f"Error parsing RESP message: {e}")
            writer.write(b'-ERR invalid RESP format\r\n')  # Send an error response
            await writer.drain()
            continue

       
        if command == 'PING':
            writer.write(client_response)
        elif command == 'ECHO':

            echo_response = f'+{argument}\r\n'
            writer.write(echo_response.encode())
        elif command == 'SET':
            print("Inside SET")
            redis_store[argument] = argument2
            print(f"Redis store {redis_store}")
            ok_response = f"+OK\r\n"
            writer.write(ok_response.encode())
        elif command == 'GET':
            print("Inside SET")
            value = redis_store[argument]
            set_response = f'+{value}\r\n'
            print(f"GET value {set_response}")
            writer.write(set_response.encode())

           

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
