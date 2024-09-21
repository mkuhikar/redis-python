import struct

class RDBReader:
    def read_rdb_file(self,file_path):
        with open(file_path, 'rb') as file:
            # Read the header (first 9 bytes are "REDIS0011")
            header = file.read(9)
            if header != b'REDIS0011':
                raise ValueError("Invalid RDB file or version")

            keys = []

            while True:
                byte = file.read(1)
                if not byte:
                    break  # EOF reached
                
                byte = byte[0]  # Convert byte to integer
                
                if byte == 0xFA:  # Metadata section marker
                    # Skip metadata subsections
                    self.read_metadata(file)
                
                elif byte == 0xFE:  # Database section marker
                    db_index = self.read_size_encoded(file)  # Read the database index (size encoded)
                    print(f"Reading database {db_index}")
                    keys += self.read_database(file)

                elif byte == 0xFF:  # End of file marker
                    break

            return keys

    def read_metadata(self,file):
        # Function to skip metadata subsections
        while True:
            byte = file.read(1)
            if not byte:
                break  # EOF reached
            byte = byte[0]
            if byte == 0xFF:  # End of metadata
                break
            # Otherwise, skip the metadata subsection (size-encoded key-value pair)
            key_len = self.read_size_encoded(file)
            file.read(key_len)  # Skip the key
            value_len = self.read_size_encoded(file)
            file.read(value_len)  # Skip the value

    def read_size_encoded(self,file):
        byte = file.read(1)[0]
        if byte < 0x40:
            return byte
        elif byte < 0x80:
            second_byte = file.read(1)[0]
            return ((byte & 0x3F) << 8) | second_byte
        else:
            return struct.unpack(">I", file.read(4))[0]

    def read_string(self,file):
        length = self.read_size_encoded(file)
        return file.read(length).decode()

    def read_database(self,file):
        keys = []
        while True:
            byte = file.read(1)
            if not byte:
                break
            byte = byte[0]

            if byte == 0xFB:  # Hash table size info
                key_count = self.read_size_encoded(file)
                expiring_key_count = self.read_size_encoded(file)
                print(f"Key count: {key_count}, Expiring key count: {expiring_key_count}")

            elif byte == 0xFD or byte == 0xFC:  # Expiration info (seconds or milliseconds)
                if byte == 0xFD:
                    file.read(4)  # Skip expiration time (4 bytes, seconds)
                elif byte == 0xFC:
                    file.read(8)  # Skip expiration time (8 bytes, milliseconds)

            elif byte == 0x00:  # Value type is string
                key = self.read_string(file)  # Read key
                value = self.read_string(file)  # Read value
                keys.append(key)
                print(f"Key: {key}, Value: {value}")

            elif byte == 0xFF:  # End of file
                break

        return keys

# Example usage:
# keys = read_rdb_file("dump.rdb")
# print("Keys in RDB file:", keys)
