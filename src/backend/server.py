import utilities
import socket
import json
from server_config import *
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

while True:
    (client_socket, address) = server_socket.accept()
    try:
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data: 
                continue
            json_data = utilities.objDecode(data)
            print(json_data)
            ip = json_data['ip']
            port = json_data['port']
            id = json_data['id']
            event = json_data['event']
            if event == 'started':
                available_peers.append(Peer(ip, port, id))
                print(available_peers)
                client_socket.send(utilities.objEncode({
                    'error_code': 0,
                    'message': 'started ACK'
                }))
                client_socket.close()
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
    except Exception as e:
        print('exception!')
        print(e)
        print(e.args)
        client_socket.close()
        continue

    
