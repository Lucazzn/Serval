import argparse
from distutils.command.config import config

def initial_args():
    parser = argparse.ArgumentParser(description='Physical simulation')
    parser.add_argument('--config_file',default=None,type=str)
    args = parser.parse_args()
    return args

def initialize_sim(config):
    # 1.初始化命令行参数（设备信息）, 更新到config类中（虚拟仿真）
    argsconfig = initial_args()
    if argsconfig.config_file !=None:
        print("Updating config from file...\n")
        config.load_from_yaml(argsconfig.config_file)
    # 2.初始化设备配置
    
    
# def initialize_device():
    




# def _initialize_distributed(config):
#     args = get_args()
#     if  args.config_file   != None:
#         print("Updating config from file...")
#         config.load_from_json(args.config_file)
#     print("Initializing process group...")


# import argparse

# _GLOBAL_ARGS = None

# def initial_args():
#     global _GLOBAL_ARGS

#     if _GLOBAL_ARGS is None:
#         parser = argparse.ArgumentParser(description='rank: device id')
#         parser.add_argument('--rank', default=0, type=int)
#         parser.add_argument('--world', default=1, type=int)
#         parser.add_argument('--config_file',default=None,type=str)
#         _GLOBAL_ARGS = parser.parse_args()
#         # parser从命令行获取参数，组成一个字典即为args,此处被声明为全局变量_GLOBAL_ARGS

# def get_args():
#     """Return arguments."""
#     assert (
#     _GLOBAL_ARGS is not None
#     ), 'global arguments is not initialized'
    
#     return _GLOBAL_ARGS