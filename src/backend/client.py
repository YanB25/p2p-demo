'''
client side
'''
import threading
import socket
import bitarray
from client_config import *
import server_config
import rdt_socket as rdts
import utilities
import random
import queue
import rdt_socket
import torrent
import message

queue left_piece

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
    
    def send_message(self, msg):
        



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
    def __init__(self, torrent_file_name):
        threading.Thread.__init__(self)
        self.metadata = torrent.read_torrent_file(torrent_file_name)
        # 计算数据块的数量
        self.pieces_num = len(self.metadata['info']['piece_hash'])
        self.bitfeild = bitarray([0 for _ in range(1, self.pieces_num+1)])
    def run(self):
        print('run')
        # 从bitfield中初始化队列，将任务放到队列中等待连接去执行
        self.fromBitfieldSetUpQueue()
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
        print((self.metadata['announce'], self.metadata['port']))
        sock.connect((self.metadata['announce'], self.metadata['port']))
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
    
    def fromBitfieldSetUpQueue(self):
        for i in range(0, self.pieces_num):
            if self.bitfeild[i] == 0:
                left_piece.push((i,self.metadata['info']['piece_hash'][i]))

if __name__ == "__main__":
    client = Client()
    client.start()

