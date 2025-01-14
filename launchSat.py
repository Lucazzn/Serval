import sys
import os
from Sat_Simulator import const
import time

const.ONLY_UPLINK = False
const.ONLY_DOWNLINK = False
iotMax = 100

if True:
    if sys.argv[1] == "1":
        arg2 = const.INITIAL_ALPHA = 1
        arg3 = const.ALPHA_HIGHER_THRESHOLD = .26
        arg4 = const.ALPHA_DOWN_THRESHOLD = .3
        arg5 = const.ALPHA_INCREASE = .005
        # const.INITIAL_ALPHA = float(sys.argv[2])
        # const.ALPHA_HIGHER_THRESHOLD = float(sys.argv[3])
        # const.ALPHA_DOWN_THRESHOLD = float(sys.argv[4])
        # const.ALPHA_INCREASE = float(sys.argv[5])
        # const.ROUTING_MECHANISM = const.RoutingMechanism.probability_with_hyperparameter  # 原来的，真烦，一堆错误
        const.ROUTING_MECHANISM = const.RoutingMechanism.assign_by_datarate_and_available_memory
        # const.LOGGING_FILE = "/home/ochabra2/logs/ours" + sys.argv[2] + "-" + sys.argv[3] + "-" + sys.argv[4] + "-" + sys.argv[5] + ".log"
        const.LOGGING_FILE = "/home/ochabra2/logs/ours" + f"{arg2}" + "-" + f"{arg3}" + "-" + f"{arg4}" + "-" + f"{arg5}" + ".log"

from typing import List
from datetime import datetime
import random

import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'Sat_Simulator')))

from Sat_Simulator.src.utils import Time, Print
from Sat_Simulator.src.routing import Routing
from Sat_Simulator.src.satellite import Satellite
from Sat_Simulator.src.iotSatellite import IoTSatellite
from Sat_Simulator.src.station import Station
from Sat_Simulator.src.links import Link
from Sat_Simulator.src.data import Data
from Sat_Simulator.src.packet import Packet
from Sat_Simulator.src.topology import Topology
from Sat_Simulator.src.node import Node
from Sat_Simulator.src.transmission import Transmission
from Sat_Simulator.src.groundTransmission import GroundTransmission
from Sat_Simulator.src.dataCenter import DataCenter
from Sat_Simulator.src import log
from Sat_Simulator.src.iotDevice import IotDevice

# =================================================通信
import socket
import json
from typing import List

if __name__ == "__main__":

    # 卫星（接收-发送卫星、拍照卫星？）
    satellites: 'List[Satellite]' = Satellite.load_from_tle("Sat_Simulator/referenceData/swarm.txt")
    satellites = [IoTSatellite(i) for i in satellites]
    print("number of satellites:", len(satellites))
    
    startTime = Time().from_str("2022-07-09 00:00:00")
    endTime = Time().from_str("2022-07-10 00:00:00")


# =========================================================仿真过程=================================================================
    # cd /root/nfs/project/satellite_model/Serval/
    # python launchSat.py --config_file orin_config/rank0_config.yaml
    
    from orin_config.orinConfig import SimulatorConfig
    simConfig = SimulatorConfig()
    
    from MSCO_distModel.initialize.initialize_simulator import initialize_sim
    initialize_sim(simConfig)
    
    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.bind((simConfig.local_ip, simConfig.local_port))
    # server_socket.listen(5)
    # print(f"I'm: {simConfig.local_ip}:{simConfig.local_port}, listening")
    
    # conn, address = server_socket.accept()  # 接受一个新的连接
    # print(f"Connection from: {address}")
    
    # data = conn.recv(1024).decode()  # 接收数据\
    # print(f"Received from client: {data}")
    # conn.close()  # 断开连接
    
    # ======================================================
    '''
        1. sat接受gs的静态filter：
            - {questionid: ,location: ,time:}
            - {questionid: ,location: ,time:}
            - ....
        2. 
    '''
    # time.sleep(3)
    # print("sleep 3s")
    geochat_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vision_model/GeoChat'))
    if geochat_path not in sys.path:
        sys.path.append(geochat_path)
    # print(sys.path)
    
    import mutiSateChatInOrbit

    def receive_jsonl_file(sock, output_path):
        with open(output_path, 'w') as f:
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                f.write(data.decode('utf - 8'))
            
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((simConfig.local_ip, simConfig.local_port))
    server_socket.listen(5)
    print(f"I'm: {simConfig.local_ip}:{simConfig.local_port}, listening")
    
    conn, address = server_socket.accept()  # 接受一个新的连接
    print(f"Connection from: {address}")
    
    received_file_content = server_socket.recv(1024 * 1024).decode('utf - 8')  # 假设文件不会太大，接受

    # 读取并解析临时文件中的JSONL数据
    staticFilter_file_path = "/root/nfs/project/vision_model/GeoChat/tables/sat/rec_staticfilter.jsonl"
    with open(staticFilter_file_path, 'w') as f:
        data = conn.recv(1024).decode()  # 接收数据
        f.write(data.decode('utf-8'))
        print(f"Received from client: {data}")
        # jsonl_objs = [json.loads(line) for line in f.readlines() if line]    #————this读取文件，
        #                                                         #  geochat里面的，并且可以在这里做BS调度
        # print("Received JSONL file data:", jsonl_objs)
    conn.close()  # 断开连接
        
    static_filter = [json.loads(q) for q in open(os.path.expanduser(staticFilter_file_path), "r")]  
    static_filter = _get_chunk(static_filter, self.config.num_chunks, self.config.chunk_idx)                    
    
    questionid = static_filter[j]['questionid']
    location = static_filter[j]['location']
    image_time = static_filter[j]['time']
    
    
    


    
    
    # ===========================================================
    
    conn, address = server_socket.accept()  # 接受新的连接
    
    print(f"Sending data to {address}")
    conn.send("Hello from B".encode())  # 发送数据
    conn.close()  # 断开连接
    server_socket.close()   # 套接字关闭
    





    # sim = Simulator(60, startTime, endTime, satellites, groundStations)
    # # sim.calculate_topologys()
    # # sim.save_topology("tmp.txt")
    # # sim.load_topology("/scratch/ochabra2/maps/2022-07-10-20:00:00.txt")
    # # sim.calcuate_and_save_topologys(iotMax)  # 先计算保存，之后直接加载load
    # sim.run()  # 好像不用加载，他run的过程中会自动加载

    
    
    
    
    