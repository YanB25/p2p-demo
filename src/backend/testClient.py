import socket 
import json
import utilities
import rdt_socket
from server_config import *
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', SERVER_PORT))
rdt_s = rdt_socket.rdt_socket(s)

rdt_s.sendBytes(utilities.objEncode({
    'ip': SERVER_IP,
    'port' : 1000,
    'peer_id': 'asddsf',
    'event': 'started'
}))
data = rdt_s.recvBytes()
print(utilities.objDecode(data))
s.close()