import sys
import os
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
from fastapi import FastAPI, File, UploadFile
import json
import io
from typing import List
import asyncio
import uvicorn
import multiprocessing as mp

app = FastAPI()

import torch
@app.post("/send_tensor")
async def send_tensor(tensor_data: List[float]):
    tensor = torch.tensor(tensor_data)
    # 这里可以对接收的张量进行处理
    print(tensor)
    return {"message": "Tensor received successfully"}

# @app.post("/send_json")
# async def send_json(json_data: dict):
#     # 这里可以对接收的JSON数据进行处理
#     return {"message": "JSON received successfully"}

@app.post("/send_jsonl_file")
async def send_jsonl_file(file: UploadFile = File(...)):
    contents = await file.read()
    jsonl_data = [json.loads(line) for line in contents.decode('utf - 8').splitlines() if line]
    # 这里可以对接收的JSONL文件数据进行处理
    return {"message": "JSONL file received successfully"}

# import uvicorn
# import asyncio
def receiver_server(postGS):
    uvicorn.run(app, host="0.0.0.0", port=portGS)


if __name__ == "__main__":

    # 卫星（接收-发送卫星、拍照卫星？）
    satellites: 'List[Satellite]' = Satellite.load_from_tle("referenceData/swarm.txt")
    satellites = [IoTSatellite(i) for i in satellites]
    print("number of satellites:", len(satellites))
    
    startTime = Time().from_str("2022-07-09 00:00:00")
    endTime = Time().from_str("2022-07-10 00:00:00")


# =========================================================仿真过程=================================================================
    # cd /root/nfs/project/satellite_model/Serval/
    # python launchSatellite.py --config_file orin_config/rank0_config.yaml
    
    from orin_config.orinConfig import SimulatorConfig
    simConfig = SimulatorConfig()
    
    from MSCO_distModel.initialize.initialize_simulator import initialize_sim
    initialize_sim(simConfig)

    # import threading   # 1. 多线程，以为内在python的GIL全局解释器锁，降低了cpu多核的利用率
    # server_thread = threading.Thread(target=receiver_server, args=(simConfig.local_port,))  
    # # receiver_server(simConfig.local_port)
    # server_thread.start()  
    
    # 2. 异步，同时执行，gather等待所有完成，相当于同级，也没必要
    
    '''
        多进程时，进程间的通信和数据共享需要特别小心，因为每个进程有 !!独立的内存空间 。
         - 可以使用 multiprocessing 提供的 Queue、Pipe 等工具来实现进程间通信。
        而在异步编程中，要注意处理好异步任务之间的依赖关系和资源竞争问题。
        2. HTTP 协议通常是单向的，即客户端发送请求，服务器返回响应后连接关闭。
            而 WebSocket 协议允许在客户端和服务器之间建立持久连接，实现双向通信。
            在 FastAPI 中，可以使用 fastapi - websockets 库来实现 WebSocket 功能。
    '''
    # 3. 多进程
    server_multiprocess = mp.Process(target=receiver_server, args=(simConfig.local_port,))
    server_multiprocess.start()  # 启动进程
    
    print("test")
    
    server_multiprocess.join()   # 等待进程结束
    
    





    # sim = Simulator(60, startTime, endTime, satellites, groundStations)
    # # sim.calculate_topologys()
    # # sim.save_topology("tmp.txt")
    # # sim.load_topology("/scratch/ochabra2/maps/2022-07-10-20:00:00.txt")
    # # sim.calcuate_and_save_topologys(iotMax)  # 先计算保存，之后直接加载load
    # sim.run()  # 好像不用加载，他run的过程中会自动加载

    
    
    
    
    