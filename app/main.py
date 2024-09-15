import socket  # noqa: F401
import asyncio

async def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 6379))

    client, addr = server_socket.accept() # wait for client
    
    
    client_response = b'+PONG\r\n'
    while(True):
        messages = client.recv(1024).decode().split('\n')
        print(f"Messages {messages}")
        for message in messages:
            print(f"Individual message {message}")
            if 'PING' in message:
                client.sendall(client_response)

        


if __name__ == "__main__":
    asyncio.run(main())
