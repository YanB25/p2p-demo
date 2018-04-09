'''
client side
'''
#TODO: 不是很能理解rdt_socket接口。希望 @新锐帮我检查一下
import threading
import socket
from client_config import *
import server_config
import rdt_socket as rdts
import utilities
import random
import rdt_socket
def GenerateRnId():
    #TODO: should be put into another module
    return str(random.randint(0, 1e10))
class PeerConnection(threading.Thread):
    '''
    not finished
    client
    '''
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.socket = sock
    def run(self):
        pass

PEER_LIST_REQUEST_OBJ = {
    'ip': CLIENT_IP,
    'port': CLIENT_PORT,
    'peer_id': GenerateRnId(),
    'event': 'started'
}
class Client(threading.Thread):
    ''' 
    client side 
    '''
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print('run')
        self.getPeersList()
        print('ok get list')
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((CLIENT_IP, CLIENT_PORT))
        listen_socket.listen(CLIENT_LISTEN_MAX)
        while True:
            (s, _) = listen_socket.accept()
            print('get new socket from listener port')
            rdt_socket = rdts.rdt_socket(s)
            peer_connection = PeerConnection(rdt_socket)
            peer_connection.start()
    def getPeersList(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print((server_config.SERVER_IP, server_config.SERVER_PORT))
        sock.connect((server_config.SERVER_IP, server_config.SERVER_PORT))
        rdt_s = rdt_socket.rdt_socket(sock)
        rdt_s.sendBytes(utilities.objEncode(PEER_LIST_REQUEST_OBJ))
        data = rdt_s.recvBytes()
        print(utilities.objDecode(data))
        sock.close()
        self.peersListResponse = utilities.objDecode(data)
        print('finish get peer list')

if __name__ == "__main__":
    client = Client()
    client.start()

