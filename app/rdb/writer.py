import struct
import binascii
class RDBWriter:
    
    def __init__(self,file):
        self.file = self.file
    def write_rdb_header(self):
        header = b"REDIS0011"
        self.file.write(header)
    def write_rdb_metadata(self,metadata):
        for key,value in metadata.items():
            self.write_string.write(b'\xFA')
            self.write_string.write(self.file)
    def write_string(self,string):
        length = len(string)
        self.file.write(struct.pack('B', length))  # Write the size of the string
        self.file.write(string.encode())  # Write the string itself
    def write_rdb_database(self,file,db_index,key_values):
        self.file.write(b'\xFE')
        self.file.write(struct.pack('B',db_index))
        
        self.file.write(b'\xFB')
        self.file.write(struct.pack('B',len(key_values)))
        self.file.write(struct.pack('B',sum(1 for k,v in key_values.items() if 'expire' in v)))

        
        for key,data in key_values.items():
            # if isinstance(data['value'],str):
                # self.file.write(b'\x00')  # Value type is string (0x00)
        
                # # Encode key ("foo")
                # write_string(self.file, key)
                
                # # Encode value ("bar")
                # write_string(self.file, value)

                
            # write_string(self.file, key)  # Key
            # write_string(self.file, data['value'])  # Value
        # Hash table size information (key-value pair count)
            self.file.write(b'\xFB')  # Start of hash table size info
            self.file.write(struct.pack('B', len(key_values)))  # Total key-value count
            self.file.write(struct.pack('B', sum(1 for item in key_values if len(item) == 4)))  # Keys with expiry

            for item in key_values:
                key, value = item[0], item[1]
                
                # Check if there is an expiration
                if len(item) == 4 and item[2] == 'px':  # Expiration in milliseconds
                    expiration_time = item[3]
                    self.file.write(b'\xFC')  # Expiry in milliseconds
                    self.file.write(struct.pack('<Q', expiration_time))  # Expiry time in milliseconds
                
                self.file.write(b'\x00')
                self.file.write(key.encode())
                self.file.write(data['value'].encode())
    def write_rdb_end(self):
        self.file.write(b'\xFF')  # End of self.file marker
        checksum = binascii.crc64(self.file)  # Calculate checksum (using crc64)
        self.file.write(checksum)
    def save_rdb_file(self,file_path, metadata, db_data):
        with open(self.file_path, 'wb') as self.file:
            self.write_rdb_header(self.file)
            self.write_rdb_metadata(self.file, metadata)
            for db_index, key_values in db_data.items():
                self.write_rdb_database(self.file, db_index, key_values)
            self.write_rdb_end(self.file)