import struct
# import binascii
# import crccheck
class RDBWriter:
    
    def __init__(self,file):
        self.file = file
    def write_rdb_header(self):
        header = b"REDIS0011"
        self.file.write(header)
    def write_rdb_metadata(self, metadata):
        for key, value in metadata.items():
            self.file.write(b'\xFA')  # Start of metadata subsection
            self.write_string(key)    # Write metadata key (string encoded)
            self.write_string(value)
    def write_string(self,string):
        length = len(string)
        self.file.write(struct.pack('B', length))  # Write the size of the string
        self.file.write(string.encode())  # Write the string itself
    def write_rdb_database(self,db_index,key_values):
        self.file.write(b'\xFE')
        self.file.write(struct.pack('B',db_index))
        
        self.file.write(b'\xFB')
        self.file.write(struct.pack('B',len(key_values)))
        self.file.write(struct.pack('B',sum(1 for k,v in key_values.items() if 'expire' in v)))

        
        for key,data in key_values.items():
            print(f"Key {key} data {data}")
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
                
                self.file.write(data.encode())
    def write_rdb_end(self):
        self.file.write(b'\xFF')  # End of self.file marker
        # crc64 = crccheck.crc.Crc64()
        # checksum = crc64.calc(self.file)  # Calculate checksum (using crc64)
        # self.file.write(checksum)
    def save_rdb_file(self,file_path, metadata, db_data):
        print(f"Attempting to store {db_data}")
        with open(file_path, 'wb') as file:
            self.file = file
            self.write_rdb_header()
            self.write_rdb_metadata(metadata)
            for db_index, key_values in db_data.items():
                
                self.write_rdb_database(db_index, key_values)
            self.write_rdb_end()