'''
server side for p2p protocal.
usage:
python3 server.py

dependencies:
config.py
it set ip and port for server
'''
import utilities
import socket
import json
from rdt_socket import *
from server_config import *

SERVER_IP = utilities.get_host_ip()
SERVER_PORT = 6666

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(MAX_TCP_LINK)

#TODO: need validator for ip, port and id
class Peer(object):
    def __init__(self, ip, port, id):
        self.ip = ip
        self.port = port
        self.id = id
    def __str__(self):
        return "{}:{} id:{}".format(self.ip, self.id, self.id)
    def __eq__(self, rhs):
        return self.id == rhs.ip and self.ip == rhs.ip and self.port == rhs.port
        
available_peers = []

# start callback
print('listening to port {} at ip {}'.format(SERVER_PORT, SERVER_IP))
while True:
    (client_socket, address) = server_socket.accept()
    # try:
    while True:
        rdt_s = rdt_socket(client_socket)
        # data = client_socket.recv(BUFFER_SIZE)
        data = rdt_s.recvBytes()
        json_data = utilities.objDecode(data)
        ip, _ = address
        port = json_data['port']
        id = json_data['peer_id']
        event = json_data['event']
        if event == 'started':
            print(available_peers)
            retList = [{
                'peer-id': obj.id,
                'peer-port': obj.port,
                'peer-ip': obj.ip
            } for obj in available_peers]
            rdt_s.sendBytes(utilities.objEncode({
                'error_code': 0,
                'message': 'started ACK',
                'num-of-peer': len(available_peers),
                'peers': retList
            }))
            client_socket.close()
            if id not in [peer.id for peer in available_peers]:
                available_peers.append(Peer(ip, port, id))
            print('connected by ', (ip, port, id))
            break
        elif event == 'completed':
            available_peers.remove(Peer(ip, port, id))
            client_socket.close()
            print("{} disconnect", id)
            print(available_peers)
        else:
            print("warning, known event {}".format(event), json_data)
            client_socket.send(utilities.objEncode({
                'error_code': 1,
                'message': 'no event in request. abort.'
            }))
            client_socket.close()
# except Exception as e:
#     print('exception!')
#     print(e)
#     print(e.args)
#     client_socket.close()
#     continue