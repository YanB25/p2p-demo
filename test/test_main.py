""" 兼顾做种，以及运行server文件 """

import os
import sys
sys.path.insert(0, '../src/backend/')
from torrent import *

# 做种客户端
make_torrent_file('./client1/test.txt')
# 运行server端
os.system("python ../src/backend/server.py")