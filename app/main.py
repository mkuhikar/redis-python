import socket  # noqa: F401
import sys,os,json
import pdb

import argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio,time
from asyncio import Server
from utility.parser import Parser
import struct
from config import Config
from rdb.writer import RDBWriter
from rdb.reader import RDBReader



class Server:
    config_details = None
    config_instance = None
    arguments = None
    redis_store = {}
    writer = None

    async def main(self):
        self.config_instance = Config()
        self.config_details = self.config_instance.load_config()
        print(f"config loaded {self.config_details}")

        # You can use print statements as follows for debugging, they'll be visible when running tests.
        print("Logs from your program will appear here!")
        print("Starting the server")
        parser = argparse.ArgumentParser(description="Fetch the command line arguments")
        parser.add_argument('--dir',type=str,help="The RDB file path")
        parser.add_argument('--dbfilename',type=str,help='The RDB filename')
        args = parser.parse_args()
        print(f"obtained args {args}")
        # Load existing configuration from file if available
        
        directory = args.dir if args.dir else (self.config_details['dir'] if self.config_details and self.config_details['dir'] else None)
        dbfilename = args.dbfilename if args.dbfilename else (self.config_details['dbfilename'] if self.config_details and self.config_details['dbfilename'] else None)
        await self.config_instance.save_config(directory=directory,dbfilename=dbfilename)
        print(f"get config {self.config_details}")
        server = await asyncio.start_server(self.handle_client,'localhost',6379)
        addr = server.sockets[0].getsockname()
        print(f"Serving on {addr}")
        async with server:
            await server.serve_forever()
    def ping(self):
        response = b'+PONG\r\n'
        return response
    def echo(self):
        echo_response = f'+{self.arguments[0]}\r\n'
        return echo_response.encode()
    def set(self):
        if len(self.arguments) >= 2:
            key = self.arguments[0]
            value = self.arguments[1]
            db_data = {0:{key:value}}
            expiration_time = None

            # Check for optional 'PX' argument for expiration
            if len(self.arguments) >= 4 and self.arguments[2].lower() == 'px':
                expiration_time = time.time() + (int(self.arguments[3]) / 1000)

            self.redis_store[key] = (value, expiration_time)
            print(f"Redis store updated: {self.redis_store}")
            response = b'+OK\r\n'
            return response

    def get(self):
        response = None
        if len(self.arguments) > 0:
                    
            key = self.arguments[0]
            if key in self.redis_store:
                value, expiration_time = self.redis_store[key]
                if expiration_time and time.time() > expiration_time:
                    del self.redis_store[key]  # Key has expired
                    response = b'$-1\r\n'
                    # writer.write(b'$-1\r\n')  # Key not found
                else:
                    get_response = f'${len(value)}\r\n{value}\r\n'
                    response = get_response.encode()
                    print(f"GET value: {get_response}")
                    # writer.write(get_response.encode())
            else:
                rdb_file_path = os.path.join(self.config_details['dir'],self.config_details['dbfilename'])
                reader = RDBReader()
                rdb_file_key,rdb_file_value = reader.read_rdb_file(rdb_file_path)
                if rdb_file_key == key:
                    get_response = f'${len(rdb_file_value)}\r\n{rdb_file_value}\r\n'
                    print(f"GET {get_response}")
                    response = get_response.encode()
                    return response



                else:
                    response = b'$-1\r\n'
                # writer.write(b'$-1\r\n')  # Key not found
            return response
    def config(self):
       
        if self.arguments[0] == 'GET' and self.arguments[1] == 'dir':
            self.config_details = self.config_instance.load_config()
            return_val= f"*2\r\n$3\r\ndir\r\n${len(self.config_details['dir'])}\r\n{self.config_details['dir']}\r\n"
            return return_val.encode()
        elif self.arguments[0] == 'GET' and self.arguments[1] == 'dbfilename':
            return_val= f"*2\r\n$3\r\ndbfilename\r\n${len(self.config_details['dbfilename'])}\r\n{self.config_details['dbfilename']}\r\n"
            return return_val.encode()
    def keys(self):
        self.config_details = self.config_instance.load_config()
        if self.config_details:
            rdb_file_path = os.path.join(self.config_details['dir'],self.config_details['dbfilename'])
            reader = RDBReader()
            key,value = reader.read_rdb_file(rdb_file_path)
            print(f"Keys obtained {key}")
            return "*1\r\n${}\r\n{}\r\n".format(len(key), key).encode()
            # print(f"rdb file path {rdb_file_path}")
           
           


    async def handle_client(self,reader,writer):
        print(f"Inside handle client: Getting config {self.config_details}")
    
        # self.config = config.load_config()
        metadata = {
        "redis-ver": "6.0.16"
    }
        print(f"obtained config {self.config_details}")
        addr = writer.get_extra_info('peername')
        redis_store = {}

        client_response = b'+PONG\r\n'
        while(True):
            data = await reader.read(100)
            if not data:
                print("Breaking from while loop")
                break
            messages = data.decode()
            print(f"Received1 {messages} from {addr!r}")
            # pdb.set_trace()
            # messages = messages.split('\n')
            try:
                # Parse the RESP message using the updated parser
                command, arguments = Parser.parse_resp(messages)
                print(f"Parsed command: {command}, arguments: {arguments}")
                self.arguments = arguments
                
            except Exception as e:
                print(f"Error parsing RESP message: {e}")
                writer.write(b'-ERR invalid RESP format\r\n')  # Send an error response
                await writer.drain()
        # pdb.set_trace()
            print(f"Before attribute check {command.lower()}")

            if hasattr(self,command.lower()):
                print("Into attr")
                func = getattr(self,command.lower())
                response = func()
                writer.write(response)
            

        

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
