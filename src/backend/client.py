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
        self.socket = rdt_socket.rdt_socket(sock)
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
        # 得到所有的peer列表。存在self.peerListResponse里。
        self.getPeersList()

        # 监听端口，等待其他peer建立其的链接
        print('ok get list')
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((CLIENT_IP, CLIENT_PORT))
        listen_socket.listen(CLIENT_LISTEN_MAX)

        # 向N个peer主动发起链接
        self.establishLink()

        while True:
            # 阻塞型接受新链接
            (s, addr) = listen_socket.accept()
            print('get new socket from listener port, addr is {}'.format(addr))
            # 开启新线程建立链接
            peer_connection = PeerConnection(s)
            peer_connection.start()

    def getPeersList(self):
        # 向tracker发起链接，请求peer list
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_config.SERVER_IP, server_config.SERVER_PORT))
        rdt_s = rdt_socket.rdt_socket(sock)
        rdt_s.sendBytes(utilities.objEncode(PEER_LIST_REQUEST_OBJ))
        data = rdt_s.recvBytes()

        print(utilities.objDecode(data))
        sock.close()
        self.peersListResponse = utilities.objDecode(data)
        print('finish get peer list')

    def establishLink(self):
        #主动向peer建立链接
        for idx, peerInfo in enumerate(self.peersListResponse['peers']):
            if idx >= 4: return # TODO: add constant here
            peerIP = peerInfo['peer-ip']
            peerPORT = peerInfo['peer-port']
            print('trying to connect to peer {}:{}'.format(peerIP, peerPORT))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peerIP, peerPORT))

            # 拉起新的线程管理该tcp
            peer_connection = PeerConnection(sock)
            print('connect to {}:{} finish. tcp start'.format(peerIP, peerPORT))
            peer_connection.start()

if __name__ == "__main__":
    client = Client()
    client.start()

