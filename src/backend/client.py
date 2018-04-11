'''
client side
'''
import threading
import json
import socket
import bitarray
import server_config
import rdt_socket as rdts
import utilities
import random
import time
import queue
import rdt_socket
import torrent
from message import Message
from piecemanager import pieceManager

CLIENT_PORT = 5555
CLIENT_LISTEN_MAX = 8
FILE_HEADER_SIZE = 8

# 这些是常量，不会变动，不需要放到配置文件中
INIT_AM_INTERESTED = False
INIT_AM_CHOCKED = False
INIT_PEER_INTERESTED = False
INIT_PEER_CHOCKED = False
START_EVENT = 'started'
COMPLETED_EVENT = 'completed'

# 全局变量
left_piece = queue.Queue(300)
msg = Message()
pieces_manager = 0

class PeerConnection(threading.Thread):
    '''
    not finished
    client
    '''
    def __init__(self, sock, pieces_num):
        threading.Thread.__init__(self)
        self.socket = rdt_socket.rdt_socket(sock)
        self.peer_bitfield = 0
        self.pieces_num = pieces_num
        self.wait_respone = 0
        self.my_choking = 1
        self.my_interested = 0
        self.peer_choking = 1
        self.peer_interested = 0


    def run(self):
        """ 连接 线程主函数 """
        # TODO:这里是需要读全局的bitfield的，发送一个全局的bitfield

        self.send_message(msg.bitfield(pieces_manager.get_bitfield().to01()))
        # print(utilities.obj_to_beautiful_json(bitfield_ret))
        # print('exchange the bitfield completed!')
        # self.peer_bitfield = bitfield_ret['bitfield']

        self.time_keeper = 0
        while True:
            # TODO:下面为示例代码，不一定能够正确运行
            # 一旦发送消息，wait_respoine = 1,就不再发送消息，等待回应
            # 防止同一个状态下重复发送多条消息
            if self.wait_respone == 0:
                # 开始一个定时器
                self.time_keeper = time.clock()
                # 封装一个发送消息函数，里面能够修改self.wait_respone为1

                # 请求数据块部分
                if self.my_interested == 0 and self.peer_choking == 0:
                    self.send_message(msg.no_interested())
                elif self.my_interested == 0 and self.peer_choking == 1:
                    # TODO:等待态
                    pass
                elif self.my_interested == 1 and self.peer_choking == 0:
                    # 从队列中取出一个数据块索引并发送
                    self.socket.sendbytes(msg.request(piece_index))
                elif self.my_interested == 1 and self.peer_choking == 1:
                    self.socket.sendbytes(msg.interested())
                
                # 接受数据块部分
                if self.my_choking == 0 and self.peer_interested == 0:
                    # 应该是没有机会到达这样的状态的
                    pass
                elif self.my_choking == 0 and self.peer_interested == 1:
                    self.send_message(msg.no_choke())
                elif self.my_choking == 1 and self.peer_interested == 0:
                    # TODO:等待态,需要想想怎么处理
                    pass
                elif self.my_choking == 1 and self.peer_interested == 1:
                    self.send_message(msg.choke())

            recv_msg = self.recv_message()
            # 如果没有收到消息，就继续循环,否则就处理消息
            if not recv_msg:
                # 如果超时还没有收到消息，就将wait_respone置为0，重新发送消息
                if self.wait_respone == 1 and (time.clock()-self.time_keeper > 1):
                    self.wait_respone = 0
                continue
            else:
                # 收到了消息，就处理消息，并且修改状态位
                self.wait_respone = 0
            
            if recv_msg['type'] == 'bitfield':
                self.peer_bitfield = bitarray.bitarray(recv_msg['bitfield'])
                print(self.peer_bitfield)


            # if recv_msg['type'] == 'no_choking':
            #     # 修改状态位
            #     peer_choking = 1
            
            # if recv_msg['type'] == 'interested':
            #     peer_interested = 1
                
    def send_message(self, msg):
        """ 传入message字典，并转成二进制发送，并将wait_respone置为1 """
        self.socket.sendBytes(utilities.objEncode(msg))
        self.wait_respone = 1
    
    def recv_message(self):
        """ 接受消息，并转成字典 """
        data = self.socket.recvBytes()
        return utilities.objDecode(data)

class Client(threading.Thread):
    '''
    client side
    '''
    def __init__(self, torrent_file_name, config_file_name):
        """ 对客户端对象，初始化客户端ip，端口，并读取种子文件，将种子元数据存到客户端中 """
        threading.Thread.__init__(self)
        # 初始化种子文件元数据
        self.metadata = torrent.read_torrent_file(torrent_file_name)
        self.pieces_num = len(self.metadata['info']['piece_hash'])
        # TODO:bitfield需要思考如何处理，这个应该能够被各个连接访问
        self.bitfield = bitarray.bitarray([0 for _ in range(1, self.pieces_num+1)])
        # 得到本机ip并且作为客户端的成员变量存进来
        self.client_ip = utilities.get_host_ip()
        self.client_port = 0
        # 从配置文件中读取数据,同时更新client_port
        self.load_config_file(config_file_name)
        # 初始化可用peer列表
        self.peers_list_response = []
        # TODO:没有什么特别好的解决方法
        global pieces_manager
        pieces_manager = pieceManager(torrent_file_name)


    def load_config_file(self, config_file_name):
        """ 从json配置文件中加载进来 """
        with open(config_file_name, 'r') as f:
            config = json.load(f)
        # 初始化几个全局常量TODO:讲道理全局常量不应该变，这么写好像不太好
        global CLIENT_LISTEN_MAX
        global FILE_HEADER_SIZE
        CLIENT_LISTEN_MAX = config['client_listen_max']
        FILE_HEADER_SIZE =  config['file_header_size']
        self.client_port = config['client_port']

    def run(self):
        print('run')
        # 从bitfield中初始化队列，将任务放到队列中等待连接去执行
        self.from_bitfield_setup_queue()
        print('initing the queue ..... finished!')
        # 得到所有的peer列表。存在self.peerListResponse里。
        self.get_peers_list()
        # 监听端口，等待其他peer建立其的链接
        print('ok get list')
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((self.client_ip, self.client_port))
        listen_socket.listen(CLIENT_LISTEN_MAX)

        # 向N个peer主动发起链接
        self.establish_link()

        while True:
            # 阻塞型接受新链接
            (new_socket, addr) = listen_socket.accept()
            print('get new socket from listener port, addr is {}'.format(addr))
            # 开启新线程建立链接
            peer_connection = PeerConnection(new_socket, self.pieces_num)
            peer_connection.start()

    def get_peers_list(self):
        """ 向tracker发起链接，请求peer list """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('connect to tracker : {}:{}'.format(self.metadata['announce'], self.metadata['port']))
        sock.connect((self.metadata['announce'], self.metadata['port']))
        rdt_s = rdt_socket.rdt_socket(sock)
        rdt_s.sendBytes(utilities.objEncode(self.make_resquest(START_EVENT)))
        data = rdt_s.recvBytes()
        print(utilities.binary_to_beautiful_json(data))
        sock.close()
        self.peers_list_response = utilities.objDecode(data)
        print('finish get peer list')

    def establish_link(self):
        """ 主动向peer建立链接 """
        for idx, peer_info in enumerate(self.peers_list_response['peers']):
            if idx >= 4: return # TODO: add constant here
            peer_ip = peer_info['peer-ip']
            peer_port = peer_info['peer-port']
            print('trying to connect to peer {}:{}'.format(peer_ip, peer_port))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer_ip, peer_port))
            # 拉起新的线程管理该tcp
            peer_connection = PeerConnection(sock, self.pieces_num)
            print('connect to {}:{} finish. tcp start'.format(peer_ip, peer_port))
            peer_connection.start()
    
    def from_bitfield_setup_queue(self):
        """ 根据现有的bitfield，将没有的块的（索引，哈希值）二元组push进全局队列中 """
        for i in range(0, self.pieces_num):
            if self.bitfield[i] == 0:
                # print('put the {}:{} into queue !'.format(i,self.metadata['info']['piece_hash'][i]))
                left_piece.put((i,self.metadata['info']['piece_hash'][i]))
    
    def get_id(self):
        """ 使用客户端自己的信息生成自己的id """
        return self.client_ip + ':' + str(self.client_port)

    def make_resquest(self, event):
        """ 制作特定事件的请求，返回对应请求的对象 """
        peer_list_request_obj = {
            'ip': self.client_ip,
            'port': self.client_port,
            'peer_id': self.get_id(),
            'event': event
        }
        return peer_list_request_obj


def init_config_file(config_file_name='client_config.json'):
    """ 如果没有配置文件，先初始化一个 """
    config = {}
    config['client_listen_max'] = 8
    config['client_port'] = 5555
    config['file_header_size'] = 8
    with open(config_file_name, 'w') as config_f:
        json.dump(config, config_f, indent=4)

if __name__ == "__main__":
    init_config_file()
