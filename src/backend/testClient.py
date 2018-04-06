import socket 
import json
import utilities
from server_config import *
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', SERVER_PORT))
s.send(utilities.objEncode({
    'ip': SERVER_IP,
    'port' : 1000,
    'id': 'asddsf',
    'event': 'started'
}))
data = s.recv(1000)
print(utilities.objDecode(data))
for i in range(1000):
    continue
print('finish')
s.send(utilities.objEncode({
    'event': 'completed',
    'ip': SERVER_IP,
    'port': 1000,
    'id': 'asddsf'
}))
s.close()