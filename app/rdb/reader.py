import struct,os

class RDBReader:
    def read_rdb_file(self,file_path):
        if os.path.exists(file_path):
            with open(file_path,'rb') as rdb_file:
                rdb_content = str(rdb_file.read())
                print("RDB content =======================")
                print(rdb_content)
                if rdb_content:
                    key = self.parse_redis_file_format(rdb_content)
                    print(f"key {key}")
                    return key
                    # return "*1\r\n${}\r\n{}\r\n".format(len(key), key).encode()


    def parse_redis_file_format(self,file_format: str):
        splited_parts = file_format.split("\\")
        resizedb_index = splited_parts.index("xfb")
        key_index = resizedb_index + 4
        value_index = key_index + 1
        key_bytes = splited_parts[key_index]
        value_bytes = splited_parts[value_index]
        key = self.remove_bytes_characters(key_bytes)
        value  = self.remove_bytes_characters(value_bytes)
        return key,value
    
    def remove_bytes_characters(self,string: str):
        if string.startswith("x"):
            return string[3:]
        elif string.startswith("t"):
            return string[1:]




