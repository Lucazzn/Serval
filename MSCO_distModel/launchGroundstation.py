import sys
import os

# # 动态添加 MSCO_distModel 模块路径
# msco_distmodel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if msco_distmodel_path not in sys.path:
#     sys.path.append(msco_distmodel_path)

# # 相当与我有GeoChat的路径了，可以像在GeoChat中一样import geochat
# import MSCO_distModel  # 这将执行 __init__.py 中的路径设置（init将MSCO标记为一个包，这里导入，就可以使用msco里导入的）
# import GeoChat # 确保 geochat 模块路径正确

# def main():
#     print("Geochat module imported successfully")

# if __name__ == "__main__":
#     main()
#     ''' 
#         其实就是那个main的仿真过程，只是需要在生成数据之后………………生成传输队列之前，
#         添加计算模块，得到文本的结果，放入传输队列，按照路由传输，保存确定传输路径
#     '''
# # ==================================================================================================
''' 可能因为还没运行过init文件，确实，直接就python launch、或许py MSCO/launch。py
    现在先：动态添加 Sat_Simulator 模块路径
'''
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

    stations = pd.read_json("referenceData/stations.json")
    groundStations: 'List[Station]' = []
    cnt = 0
    # 只接收地面站
    for id, row in stations.iterrows():
        s = Station(row["name"], id, Location().from_lat_long(row["location"][0], row["location"][1]))
        groundStations.append(RecieveGS(s))
        cnt += 1
    
    print("Number of recieve:", cnt)     # cnt：只接收大型地面站，，从station的json文件中读取
    print("Sanity")
    iotStationsPath = "/root/nfs/project/satellite_model/Serval/Sat_Simulator/unrelated/"
    if iotMax == 1000000:
        print("1000000")
        locs = open(iotStationsPath + "stationsLocsMillion.txt", "r").readlines()
    if iotMax == 100000:
        print("100000")
        locs = open(iotStationsPath + "stationsLocs100000.txt", "r").readlines()
    elif iotMax == 10000:
        print("10000")
        locs = open(iotStationsPath + "stationsLocs10000.txt", "r").readlines()
    else:
        #no iot devices √
        locs = []
        
    print("number of iot devices:", len(locs))
    latLst = []
    lonLst = []
    altLst = []
    for line in locs:
        line = line.replace('\n', '')
        line = line.split(',')
        latLst.append(float(line[0]))              # longitude and latitude  经度  纬度
        lonLst.append(float(line[1]))                
        altLst.append(float(0))                   # altitude高度

    if len(locs) == 0:                        #            this
        print("Generating random iot devices")
        latLst = list(np.random.uniform(-90, 90, iotMax))
        lonLst = list(np.random.uniform(-180, 180, iotMax))
        altLst = [0] * iotMax
    print("number of iot devices:", len(latLst))    
    locs = Location.multiple_from_lat_long(latLst, lonLst, altLst)
    # 只发送地面设备
    # groundstation 包含2种地面站：RecieveGS、IotSDevice，他们都属于station
    iotCount = 0
    for loc in locs:
        gs = Station("IotDevice" + str(cnt), cnt, loc)
        cnt += 1
        groundStations.append(IotDevice(gs, latLst[iotCount], lonLst[iotCount]))
        iotCount += 1
        
    print("number of stations:" , len(groundStations))

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
    # python launchGroundstation.py orin_config/gs_config.yaml
    
    from orin_config.orinConfig import SimulatorConfig
    simConfig = SimulatorConfig()
    
    from MSCO_distModel.initialize.initialize_simulator import initialize_sim
    initialize_sim(simConfig)
    
    import requests
    import torch
    import json
    import asyncio
    # import requests_async as requests

    # 发送张量数据
    tensor_to_send = torch.tensor([1.0, 2.0, 3.0])
    tensor_data = tensor_to_send.tolist()
    response = requests.post("http://"+ simConfig.master_satellite_ipPort + "/send_tensor", json=tensor_data)
    print(response.json())
    # print("test")

    # # 发送JSON数据
    # json_data = {
    #     "key1": "value1",
    #     "key2": 2
    # }
    # response = requests.post("http://192.168.1.100:8000/send_json", json=json_data)
    # print(response.json())

    # 发送JSONL文件数据
    # with open('example.jsonl', 'r') as f:
    #     files = {'file': f}
    #     response = requests.post("http://192.168.1.100:8000/send_jsonl_file", files=files)
    # print(response.json())


    




    # sim = Simulator(60, startTime, endTime, satellites, groundStations)
    # # sim.calculate_topologys()
    # # sim.save_topology("tmp.txt")
    # # sim.load_topology("/scratch/ochabra2/maps/2022-07-10-20:00:00.txt")
    # # sim.calcuate_and_save_topologys(iotMax)  # 先计算保存，之后直接加载load
    # sim.run()  # 好像不用加载，他run的过程中会自动加载

    
    
    
    
    