import sys
import os
import socket
# if __name__ == "__main__":
#     main()
#     ''' 
#         其实就是那个main的仿真过程，只是需要在生成数据之后………………生成传输队列之前，
#         添加计算模块，得到文本的结果，放入传输队列，按照路由传输，保存确定传输路径
#     '''
# # ==================================================================================================

from Sat_Simulator import const

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

# # -=======================================
# sat_simulator_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Sat_Simulator'))
# if sat_simulator_path not in sys.path:
#     sys.path.append(sat_simulator_path)
# from Sat_Simulator import src 
# # import Sat_Simulator.src as src
# # from ..Sat_Simulator.src import src
# # -=======================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'Sat_Simulator')))

from Sat_Simulator.src.utils import Time, Print, Location
from Sat_Simulator.src.routing import Routing
from Sat_Simulator.src.satellite import Satellite
from Sat_Simulator.src.station import Station
from Sat_Simulator.src.recieveGS import RecieveGS
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

if __name__ == "__main__":
    # process flags etc
    # maybe check dependencies - I have skyfield 1.42
    # set up simulator class with info from config fil

    stations = pd.read_json("Sat_Simulator/referenceData/stations.json")
    groundStations: 'List[Station]' = []
    for id, row in stations.iterrows():
        s = Station(row["name"], id, Location().from_lat_long(row["location"][0], row["location"][1]))
        groundStations.append(RecieveGS(s))

    print("number of recieve stations:" , len(groundStations))    # cnt：只接收大型地面站，，从station的json文件中读取

    startTime = Time().from_str("2022-07-09 00:00:00")
    endTime = Time().from_str("2022-07-10 00:00:00")

# =========================================================仿真过程=================================================================

    '''
    # 1. 计算gs和sat的连接拓扑，map
    # 2. 创建每个拓扑的link信息，不只包含0-1连接，SBR等链路信息
    # 3. 计算路由：根据link，创建最优的唯一link-best，
    # 4. 创建传输动作：按照路由信息传输包，包括容错性等检查
    
    # 个性化配置文件：    - 先写config类
    main(): 
    1. 实例化config类，类中存公共的参数，作为类的属性，参数改变为了不同的对比实验配置
    - - 1.2. 类中有一个方法，可以加载yaml文件，更新类的属性，实现不同设备上(or对比实验其实也可以)的不同的参数配置
    2. 初始化实验配置：分成 
                        - 初始化虚拟仿真模块、
                        - 初始化设备信息ip，端口、
                        - \\ 初始化分布式部分、
                        - \\ 初始化模型部分
    - - 3. 用parser参数字典获取命令行参数，config路径， config类根据yaml更新参数
    - 总结：因为参数可以：- 放在config类中，
                        - 也可以放在yaml中供config加载更新（需要从终端获取yaml路径），
                        - 也可以不放在yaml，直接从终端加载，但参数太多就用yaml存
    '''
    # cd /root/nfs/project/satellite_model/Serval/
    # python launchGs.py --config_file orin_config/gs_config.yaml
    
    from orin_config.orinConfig import SimulatorConfig
    simConfig = SimulatorConfig()
    
    from MSCO_distModel.initialize.initialize_simulator import initialize_sim
    initialize_sim(simConfig)
    
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # host = simConfig.master_satellite_ipPort.split(':')[0]
    # port = int(simConfig.master_satellite_ipPort.split(':')[1])
    # client_socket.connect((host, port))  # 连接到服务器
    
    # message = "Hello from A"
    # client_socket.send(message.encode())  # 发送数据
    # client_socket.close()  # 断开连接
    
    # ================================================
    '''
        1. gs发送静态filter给sat
            1.2. sat接收filter
        2. 完成1-gs，2-sat的仿真模拟： map，link，route，transmission
        
        
        3. gs本地算token，embed
    '''
    print("# 执行其他操作...")
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = simConfig.master_satellite_ipPort.split(':')[0]
    port = int(simConfig.master_satellite_ipPort.split(':')[1])
    client_socket.connect((host, port))  # 连接到服务器
    
    jsonl_path = "/root/nfs/project/vision_model/GeoChat/tables/gs/staticfilter.jsonl"
    with open(jsonl_path, 'r') as f:
        for jsonl_file_content in f.readlines():
            print(jsonl_file_content)
            
            client_socket.send(jsonl_file_content.encode('utf-8'))  # 发送数据
        # jsonl_file_content = f.read()   
    
    client_socket.close()  # 断开连接

    
    
    
    
    
    # ===============================================
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 新建套接字
    client_socket.connect((host, port))  # 再次连接到服务器
    
    data = client_socket.recv(1024).decode()  # 接收数据
    print(f"Received from server: {data}")
    client_socket.close()  # 断开连接 套接字关闭
    




    # sim = Simulator(60, startTime, endTime, satellites, groundStations)
    # # sim.calculate_topologys()
    # # sim.save_topology("tmp.txt")
    # # sim.load_topology("/scratch/ochabra2/maps/2022-07-10-20:00:00.txt")
    # # sim.calcuate_and_save_topologys(iotMax)  # 先计算保存，之后直接加载load
    # sim.run()  # 好像不用加载，他run的过程中会自动加载

    
    
    
    
    