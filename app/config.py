import json,os,sys
class Config:
    config_file = None
    def __init__(self):
        self.config_file =  'snapshot_config.json'
    async def save_config(self,directory,dbfilename):
        """
        Save the provided directory and dbfilename to a JSON file for persistence.
        """
        config_file_details = {
            'dir':directory,
            'dbfilename':dbfilename

        }
        with open(self.config_file,'w') as file:
            json.dump(config_file_details,file)
        print(f"Configuration saved: {config_file_details}")
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file,'r') as f:
                config = json.load(f)
            print(f"Configuration loaded: {config}")
            return config
        else:
            print("No configuration file found, using command-line arguments.")
            return None