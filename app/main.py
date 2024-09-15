import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 6379))

    client, addr = server_socket.accept() # wait for client
    messages = client.recv(1024)
    for message in messages:
        if message == 'PING':
            client.sendall(b'PONG\n')

        


if __name__ == "__main__":
    main()
