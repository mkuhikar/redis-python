import socket  # noqa: F401
import sys,os,json
import binascii
import argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio,time
from asyncio import Server
from utility.parser import Parser
import struct
from config import Config
from rdb.writer import RDBWriter








class Server:
    config = None
    config_instance = None

    async def main(self):
        self.config_instance = Config()
        config = self.config_instance.load_config()

        # You can use print statements as follows for debugging, they'll be visible when running tests.
        print("Logs from your program will appear here!")
        print("Starting the server")
        parser = argparse.ArgumentParser(description="Fetch the command line arguments")
        parser.add_argument('--dir',type=str,help="The RDB file path")
        parser.add_argument('--dbfilename',type=str,help='The RDB filename')
        args = parser.parse_args()
        print(f"obtained args {args}")
        # Load existing configuration from file if available
        
        directory = args.dir if args.dir else (config['dir'] if config and config['dir'] else None)
        dbfilename = args.dbfilename if args.dbfilename else (config['dbfilename'] if config and config['dbfilename'] else None)
        await self.config_instance.save_config(directory=directory,dbfilename=dbfilename)
        server = await asyncio.start_server(self.handle_client,'localhost',6379)
        addr = server.sockets[0].getsockname()
        print(f"Serving on {addr}")
        async with server:
            await server.serve_forever()

    async def handle_client(self,reader,writer):
    
        # self.config = config.load_config()
        metadata = {
        "redis-ver": "6.0.16"
    }
        print(f"obtained config {self.config}")
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
                # Parse the RESP message using the updated parser
                command, arguments = Parser.parse_resp(messages)
                print(f"Parsed command: {command}, arguments: {arguments}")
            except Exception as e:
                print(f"Error parsing RESP message: {e}")
                writer.write(b'-ERR invalid RESP format\r\n')  # Send an error response
                await writer.drain()
            

        # Handling the PING command
            if command == 'PING':
                writer.write(b'+PONG\r\n')

            # Handling the ECHO command
            elif command == 'ECHO':
                if len(arguments) > 0:
                    echo_response = f'+{arguments[0]}\r\n'
                    writer.write(echo_response.encode())
                else:
                    writer.write(b'-ERR wrong number of arguments for \'ECHO\' command\r\n')

            # Handling the SET command
            elif command == 'SET':
                print("Inside SET")
                if len(arguments) >= 2:
                    key = arguments[0]
                    value = arguments[1]
                    expiration_time = None

                    # Check for optional 'PX' argument for expiration
                    if len(arguments) >= 4 and arguments[2].lower() == 'px':
                        expiration_time = time.time() + (int(arguments[3]) / 1000)

                    redis_store[key] = (value, expiration_time)
                    print(f"Redis store updated: {redis_store}")
                    writer.write(b'+OK\r\n')
                    file = f"{self.config['dir']}/{self.config['dbfilename']}"
                    rdb_writer = RDBWriter()
                    rdb_writer.save_rdb_file(file,metadata,)
                else:
                    writer.write(b'-ERR wrong number of arguments for \'SET\' command\r\n')

            # Handling the GET command
            elif command == 'GET':
                if len(arguments) > 0:
                    
                    key = arguments[0]
                    if key in redis_store:
                        value, expiration_time = redis_store[key]
                        if expiration_time and time.time() > expiration_time:
                            del redis_store[key]  # Key has expired
                            writer.write(b'$-1\r\n')  # Key not found
                        else:
                            get_response = f'${len(value)}\r\n{value}\r\n'
                            print(f"GET value: {get_response}")
                            writer.write(get_response.encode())
                    else:
                        writer.write(b'$-1\r\n')  # Key not found
                else:
                    writer.write(b'-ERR wrong number of arguments for \'GET\' command\r\n')

            elif command == 'CONFIG':
                if arguments[0] == 'GET' and arguments[1] == 'dir':
                    
                    return_val= f"*2\r\n$3\r\ndir\r\n${len(self.config['dir'])}\r\n{self.config['dir']}\r\n"
                    writer.write(return_val.encode())
                elif arguments[0] == 'GET' and arguments[1] == 'dbfilename':
                    return_val= f"*2\r\n$3\r\ndbfilename\r\n${len(self.config['dbfilename'])}\r\n{self.config['dbfilename']}\r\n"
                    writer.write(return_val.encode())
        

        await writer.drain()

        print("Close the connection")
        writer.close()
        await writer.wait_closed()


    # Uncomment this to pass the first stage
    #
    # server_socket = socket.create_server(("localhost", 6379))

    

        


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.main())
