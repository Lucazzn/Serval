from typing import TYPE_CHECKING
from itertools import chain
import random # type: ignore
from time import time as timeNow
import numpy as np

from src.links import Link
from src.log import Log
from src.utils import Print
import const

if TYPE_CHECKING:
    from src.satellite import Satellite
    from src.station import Station
    from src.node import Node
    from src.packet import Packet
    from typing import List, Dict, Optional

class CurrentTransmission:
    def __init__(self, sending: 'Node', receivingNodes: 'List[Node]', channel: 'int') -> None:
        self.sending = sending
        self.receivingNodes = receivingNodes
        self.receivingChannel = channel

        self.packets: 'List[Packet]' = []
        self.packetsTime: 'List[tuple(float, float)]' = [] #List of startTimes and endTimes for each packet relevative to the start of the timestep
        self.PER: 'Dict[Node, float]' = {} #the PER for each node. Should be set to 1 if the node isn't scheduled to receive the packet
        self.SNR: 'Dict[Node, float]' = {}
        
class Transmission:
    """
    This class is what sends the data between nodes
    """
    def __init__(self, links: 'Dict[Node, Dict[Node, Link]]', topology: 'Topology', satList: 'List[Satellite]', gsList: 'List[Station]', timeStep: 'int') -> None:
        self.links = links ##links should be a case of Dict[Satellite][Station] = links
        self.linkList = list( chain( *(list(d.values()) for d in self.links.values()) ))
        self.nodes = [i for i in chain(satList, gsList)]
        self.topology = topology
        self.timeStep = timeStep
        self.satList = satList
        self.gsList = gsList

        transmissions = self.get_new_transmissions()
        self.transmit(transmissions)
        
    def transmit(self, transmissions: 'List[CurrentTransmission]'):
        '''
            执行传输动作
        '''
        #so here's how this works 
        #we have each device which has been scheduled from x time to y time
        #so let's do this, for each reception device's channel, we store a list of each packet's (startTime, endTime)
        #we then find any collisions in the startTime and endTime

        #receiving is a dict[node][channel] = List[ (packet, (startTime, endTime), PER, SNR) ]
        
        receiving = {}              
        # 遍历所有发送节点 0 
        # {1 所有接收节点 node：{2所有发送/接收通道 transmission.receivingChannel: [3发送的数据包info (packet, (startTime, endTime), PER, SNR)，(),() ……]}}
    
        #s = timeNow()
        for transmission in transmissions:  # 遍历所有传输动作
            for node in transmission.receivingNodes:
                for i in range(len(transmission.packets)):  # node不变，遍历所有发送的数据包；通道不变
                    lst = receiving.setdefault(node, {})
                    # 用 setdefault 方法确保 receiving 字典中存在当前接收节点 node 的条目，如果不存在则创建一个空字典{}。
                    chanList = lst.setdefault(transmission.receivingChannel, [])
                    # 使用 setdefault 方法确保 lst=receiving 的字典中存在当前接收通道 receivingChannel 的条目，如果不存在则创建一个空列表。
                    chanList.append((transmission.packets[i], transmission.packetsTime[i], transmission.PER[node], transmission.SNR[node], str(transmission.sending), str(transmission.packets[i])))
                    # 将当前数据包的信息添加到通道列表 chanList 中。每个条目是一个元组，包含数据包、数据包时间、包错误率（PER）、信噪比（SNR）、发送节点和数据包的字符串表示。
                    
                    #receiving[node][transmission.receivingChannel].append((transmission.packets[i], transmission.packetsTime[i], transmission.PER[node], str(transmission.sending), str(transmission.packets[i])))
        # transmission：
        # {发送节点，接收节点，通道，数据包，数据包时间，PER，SNR}
        # 它将传输信息组织到一个字典中，以便后续处理。
        
        #print("Time to create receiving dict", timeNow() - s)
        
        #print receiving but call the repr function for each object
        #now let's go through each receiving and find any overlapping times 
        #TODO: double check if I need to consider the -6 difference - seems kinda unimportant
        #t = timeNow()
        
        
        # 信息聚合到一起，不管sendingNode，包放在一张大表里，只完成包接受动作
        # {receivingNode：{channel：[block=包1，包2，包3，……]}}
        for receiver in receiving.keys():           # 遍历所有接收node
            # k，v
            for channel, blocks in receiving[receiver].items():   # 遍历所有通道
                if len(blocks) == 0:
                    continue
                #now for each block, we have a list of tuples where the 0th element is the packet and the 1st element is (startTime, endTime) and 2nd is the sendingNode
                #we need to find out if any of the times overlap, and if so drop them from list
                
                times = [i[1] for i in blocks]
                collidedInds = set() # set of indicies of collided packets
                # 检查每颗卫星上：每个通道上的数据包时间 times，找出时间重叠的包。
                for i in range(len(times)):
                    for j in range(len(times)):
                        if i == j:
                            continue
                        #there is overlap if the second start time is between the first start & end
                        firstTime = times[i]
                        secondTime = times[j]
                        if firstTime[0] <= secondTime[0] and secondTime[0] < firstTime[1]:   # sec start time在first start 和end时间之间=>重叠；不重：后一个数据包的start时间在上一个数据包end time之后
                            # 重叠=>比较 信噪比 SNR
                            snrOne = blocks[i][3]
                            snrTwo = blocks[j][3]
                            #if snrOne is greater than snrTwo by 6 db, then we can drop the second packet
                            #if snrTwo is greater than snrOne by 6 db, then we can drop the first packet
                            #if they are within 6 db, then we have a collision
                            ''' 如果一个包的信噪比比另一个包高 6 dB 以上，则丢弃 信噪比低的包。
                                如果两个包的信噪比相差不大，则认为发生了冲突，丢弃两个包。
                            '''
                            if snrOne - snrTwo > 6:
                                print("Collision between", blocks[i][0], "and", blocks[j][0], "Dropping ", blocks[j][0])
                                collidedInds.add(j)
                            elif snrTwo - snrOne > 6:
                                print("Collision between", blocks[i][0], "and", blocks[j][0], "Dropping ", blocks[i][0])
                                collidedInds.add(i)
                            else:
                                print("Collision between", blocks[i][0], "and", blocks[j][0])
                                collidedInds.add(i)
                                collidedInds.add(j)
                
                #now that we have this info, let's send
                collidedPackets = [blocks[i][0] for i in collidedInds]  # 将冲突的数据包记录到日志中
                if len(collidedPackets) > 0:
                    Log("Packets in collision:", *collidedPackets, receiver)
                
                # 对于没有冲突的数据包，检查包容错率PER
                #now receive the successful packets
                successfulInds = [i for i in range(len(blocks)) if i not in collidedInds]
                succesfulBlocks = [blocks[i] for i in successfulInds]
                for block in succesfulBlocks:
                    packet = block[0]
                    PER = block[2]
                    
                    #let's check if this packet gets dropped by PER
                    
                    if random.random() <= PER:
                        #print("Packet dropped", packet, receiver)
                        pass
                        #Log("Packet dropped", packet)
                    else:
                        #print("Packet recieved", packet, receiver)
                        '''
                            如果随机数小于等于 PER，则丢弃该包。
                            否则，检查接收节点是否有足够的接收能力，如果有，则接收该包。
                        '''
                        time = block[1][1] - block[1][0]
                        if receiver.has_power_to_recieve(time):
                            receiver.use_receive_power(time)
                            receiver.recieve_packet(packet)

    def get_new_transmissions(self) -> 'Dict[int, List[currentTransmission]]':
        '''
            # 这个函数是整个传输过程的核心，它将所有的传输信息整合到一起，然后进行传输
            配置每个传输动作
            Arguments: 这是known  and unknown，只涉及sat->地面站之间的下行传输，不涉及sat和sat之间的连接
            sat (Satellite)
            gs (Station)
            time (Time)
            **kwargs (dict) - optional arguments. If you pass this, it will override the default values
                snr (float)
                distance (float)
                uplinkDatarate (float)
                downlinkDatarate (float)
                BER (float)
                PER (float)
        # linklist: 
        # - {send1:[starTime:[…按idx对应的………],nodesend：[……],channel：[……],endtime：[……]], 
        # -  send2,
        # -  send3
        # - ……}
        '''
        
        devicesTransmitting = {}
        currentTransmissions = []
        
        for link in self.linkList:
            #print("Link has {} start times".format(len(link.startTimes)), *link.nodeSending)
            for idx in range(len(link.startTimes)):   # 处理一个sendnode的一个时间段的数据包信息
                sending = link.nodeSending[idx]
                startTime = link.startTimes[idx]
                channel = link.channels[idx]
                endTime = min(link.endTimes[idx], self.timeStep)
                
                #let's do this to avoid duplicate sending - maybe think of a better way to handle this??
                if sending in devicesTransmitting:
                    #check if this is from the same  or another, if its in another - raise an exception
                    if link is devicesTransmitting[sending]:
                        pass  # 当前sending确实在发送，但如果是同一个link，不做处理
                    else:
                        raise Exception("{} is transmitting on two links at the same time".format(sending))
                devicesTransmitting[sending] = link # 第一次记录当前发送节点在发送数据
                
                receiving = []
                datarate = 0
                if sending.beamForming:
                    receiving = [link.get_other_object(sending)]
                    per = {receiving[0]: link.PER}
                    snr = {receiving[0]: link.snr}
                    datarate = link.get_relevant_datarate(sending)
                else:
                    listOfLinks = self.topology.nodeLinks[sending]
                    receiving = [i.get_other_object(sending) for i in listOfLinks]
                    per = {i.get_other_object(sending): i.PER for i in listOfLinks}
                    snr = {i.get_other_object(sending): i.snr for i in listOfLinks}
                    receiving = [i for i in receiving if i.recieveAble]
                    
                    #lst = [i.get_relevant_datarate(sending) for i in listOfLinks if i.get_other_object(sending).recieveAble]
                    #datarate = min(lst)
                    datarate = link.get_relevant_datarate(sending)
                    for i in listOfLinks:
                        if i.get_relevant_datarate(sending) < datarate or not i.is_listening():
                            per[i.get_other_object(sending)] = 1
                    #Log("Sending", sending, "receiving", *receiving, "channel", channel, "datarate", datarate, "PER", per, "SNR", snr, "totalPackets")
                
                trns = CurrentTransmission(sending, receiving, channel)
                # 建一个 CurrentTransmission 对象，表示当前传输，一个动作
                
                #now let's assign the packets within this transmission
                currentTime = startTime
                while currentTime < endTime and len(sending.transmitPacketQueue) > 0:
                    lengthOfNextPacket = sending.transmitPacketQueue[-1].size
                    timeForNext = lengthOfNextPacket / datarate
                    
                    if currentTime + timeForNext <= endTime and sending.has_power_to_transmit(timeForNext):
                        # 检查当前要发送的包可以在时间步结束前发送完，并且发送节点有足够能量发送数据包
                        sending.use_transmit_power(timeForNext)
                        pck = sending.send_data()  # 发送的包
                        trns.packets.append(pck)
                        trns.packetsTime.append((currentTime, currentTime + timeForNext))
                        currentTime = currentTime + timeForNext
                        # 完成一个传输动作的信息配置
                    else:
                        break  
                # Log("Sending", sending, "receiving", *receiving, "channel", channel, "datarate", datarate, "PER", per, "SNR", snr, "totalPackets", len(trns.packets))
                assert len(trns.packets) == len(trns.packetsTime)
                trns.PER = per
                trns.SNR = snr
                currentTransmissions.append(trns)
                
                # 完成一个传输动作的信息配置
                # (sendingNode，接收结点，通道，pck,(curtime,endtime),per,snr) 实际部署这个时间没法计算？实际跑，还是需要提前profiler，但我又不需要优化这个per啥的
                        
        return currentTransmissions
        
        
