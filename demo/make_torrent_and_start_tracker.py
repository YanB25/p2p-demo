""" 兼顾做种，以及运行server文件 """

import os
import sys
# 这里是源代码的路径，可自行修改为对应的相对路径或绝对路径。
SRC_PATH = '../src/backend/'
sys.path.insert(0, SRC_PATH)
from torrent import *

full_file = './seed/test.mp4'
# 制作种子文件，默认存到当前目录下
make_torrent_file(full_file)
# 运行server端
os.system("python3 "+SRC_PATH+"server.py")