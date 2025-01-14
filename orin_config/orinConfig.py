import os
import json
import socket
import yaml

class SimulatorConfig:
    def __init__(self):
        self.local_ip = self.get_local_ip()
        self.local_port = None
        # gs 和sat有不同的ip端口，但只能知道自己的啊,，所以通过yaml手动告诉他对方的
        # self.gs_ipPort = self.local_ip + ":65432"  # 卫星须知
        # self.master_satellite_ipPort = self.local_ip + ":65433" # gs须知
        self.simulated_role = None
        
        self.dataset_path = ""
        self.static_filter = "/root/nfs/project/vision_model/GeoChat/tables/staticfilter"
        self.question_path = "/root/nfs/project/vision_model/GeoChat/tables"
        self.output_path = "/root/nfs/project/vision_model/GeoChat/output/distoutput"
        
    
    def get_local_ip(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    
    def load_from_yaml(self,config_file):
        if not os.path.exists(config_file):
            raise FileNotFoundError("config file:{} not found".format(config_file))
        with open(config_file,"r") as f:
            config_dict = yaml.safe_load(f)
            for key,value in config_dict.items():
                # if(hasattr(self,key)):
                setattr(self,key,value)
            
            if hasattr(self,"simulated_role"):
                print("I’m {}, my address: {}:{},".format(self.simulated_role,self.local_ip,self.local_port))
                connectRole = self.gs_ipPort if hasattr(self, "gs_ipPort") else self.master_satellite_ipPort
                print("connecting to: {}\n".format(connectRole))
                
    # def load_from_json(self,config_file):
    #     if not os.path.exists(config_file):
    #         raise FileNotFoundError("config file:{} not found".format(config_file))
    #     with open(config_file,"r") as f:
    #         config_dict = json.load(f)
    #         for(key,value) in config_dict.items():
    #             # if(hasattr(self,key)):
    #             setattr(self,key,value)
            
    #         if hasattr(self,"simulated_role") :
    #             print("I’m {}, my address is {}:{},".format(self.simulated_role,self.local_ip,self.local_port))
    #             connectRole = self.gs_ipPort if hasattr(self, "gs_ipPort") else self.master_satellite_ipPort
    #             print("connecting to {}\n".format(connectRole))
                    
