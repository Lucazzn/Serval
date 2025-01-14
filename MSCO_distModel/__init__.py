import sys
import os
# init 这样可以将 MSCO 文件夹标记为一个 Python 包。
# 动态添加 geochat 模块路径
geochat_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vision_model/GeoChat'))
if geochat_path not in sys.path:
    sys.path.append(geochat_path)
    
sat_simulator_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Sat_Simulator'))  # Sat_Simulator大写
if sat_simulator_path not in sys.path:
    sys.path.append(sat_simulator_path)

# 教训：2025.1.12
# main文件，启动文件最好位于项目的根目录，这样可以避免导入，用到后面工具包问题
# 无法从项目内部的某一部分直接运行，会使得它无法知道自己的父亲包，无法使用相对导入，因为直接从当前的树杈认为是根了
# 当前移动文件所在文件夹/父亲文件夹，被视为项目顶点，我可以直接引用兄弟文件，但是若新的启动文件在父亲文件夹在上一层
# 引用了父亲文件夹的原始启动文件，就无法根据兄弟文件夹的相对路径导入了，因为目前根目录变成原始父亲文件夹的父亲了
# 解决办法就是：添加系统路径，给原始父亲文件夹，以便能看到兄弟文件
# 2025.1.13
# 通常，__init__.py 不是直接运行的。它的作用是在包被导入时执行一些初始化操作，例如设置包级别的变量、导入子模块等。
# 如果 const 模块包含一些初始化代码，你可以在需要使用 Sat_Simulator 包的其他模块中导入该包，这样 __init__.py 就会
# 在正确的包上下文环境中被执行。
# =====================================================
# Python 中的包和模块名是区分大小写的！！！！！！！！！！

# from ..Sat_Simulator import src-------------擦我知道了，sys路径是可以的

# 把sat_simulator当做一个包，使用相对路径导入，  ..表示上级导入


# 进行相对导入，这会将 src 导入到 MSCO 包的命名空间中。
# Q1： MSCO/launch能否直接导入src？
    
# 情况一：launch.py 作为 MSCO 包的一部分被导入
# 如果 launch.py 是作为 MSCO 包的一部分被其他代码（主脚本）导入使用，那么在 launch.py 中可以直接使用 src。因为 __init__.py 中导入的 src 已经在 MSCO 包的命名空间内，launch.py 作为该包内的模块可以访问。例如：
# 在 launch.py 中：     （ 假设launch.py在MSCO包内
# def some_function():
#     result = src.some_function_in_src()
#     return result

# 情况二：launch.py 作为脚本直接运行
# 如果 launch.py 是作为脚本直接运行（例如 python launch.py），则不能直接使用 src。当直接运行脚本时，Python 会将其视为顶级脚本，而不是包内的模块，此时相对导入的上下文会失效。在这种情况下，运行 launch.py 会报错，提示找不到 src 模块。
# 要解决这个问题，可以将 launch.py 所在的 MSCO 包当作一个整体来运行，例如使用 python -m MSCO.launch，这样 launch.py 会在包的环境下运行，能够正确访问 src。或者像前面提到的，通过修改 sys.path 或设置 PYTHONPATH 环境变量等方式，以更通用的方式导入模块。
# 综上所述，只有在 launch.py 作为 MSCO 包的一部分被导入时，才可以直接使用在 __init__.py 中通过相对导入引入的 src；若直接运行 launch.py，则不能直接使用。


# ???
# 当你使用 from..Sat_Simulator import const 这样的相对导入语句时，
# Python 需要知道当前模块所在的包结构，以便正确解析相对路径。
# 错误信息 ImportError: attempted relative import with no known parent package 
# 表明 Python 无法确定当前模块的父包。
# !!!!!  : 这通常发生在你尝试以脚本的方式直接运行一个模块!!!!，而不是将其作为包的一部分导入时。