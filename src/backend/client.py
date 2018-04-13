'''
client side
'''
import threading
import json
import socket
import bitarray
import server_config
import hashlib
import rdt_socket as rdts
import utilities
import random
import time
import queue
import rdt_socket
import torrent
from piecemanager import pieceManager
from message import *
from state import *
import logging
logging.basicConfig(
    # filename='../../log/client.{}.log'.format(__name__),
    format='[%(asctime)s - %(name)s - %(levelname)s] : \n%(message)s\n',
    datefmt='%M:%S',
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
left_pieces = queue.Queue(300)
pieces_manager = 0

class PeerConnection(threading.Thread):
    '''
    not finished
    client
    '''
    def __init__(self, sock, pieces_num):
        threading.Thread.__init__(self)
        self.socket = rdt_socket.rdt_socket(sock)
        # self.peer_bitfield = 0
        self.pieces_num = pieces_num
        
        self.request_piece_index = 0
        self.request_piece_hash = 0

        logger.info('peer init connection %s', self.socket.s.getsockname())

    def run(self):
        """ 连接 线程主函数 """
        # TODO:这里是需要读全局的bitfield的，发送一个全局的bitfield
        self.send_message(Bitfield(pieces_manager.get_bitfield().tolist()))
        self.initial_flag = 1
        self.send_file_state = sendFileState('10')
        self.recv_file_state = recvFileState('10')

        logger.info('peer connection %s begin to listen', self.socket.s.getsockname())
        while True:
            recv_msg = self.recv_message()
            # 由于这个是阻塞接受消息，不需要读取不到就循环
            
            # 第一次连接必须交换bitfield
            if self.initial_flag == 1:
                if type(recv_msg) == Bitfield:
                # TODO:从队列中取出一个可下载数据块
                # TODO: 如果有可下载数据块，则改变状态,并发送interest包
                self.send_file_state.to_11()
                self.initial_flag = 0
                continue

            
            # 不是第一次连接，开始检查发送文件部分的状态
            if self.send_file_state.is_10() and type(recv_msg) == Interested:
                # TODO:这里可以决定我到底是choking 还是 no_choke
                # 这里是直接设置我不choke，对方interested
                send_available = 1
                
                logger.debug('I know you are interested with me. ')
                if send_available == 1:
                    self.send_file_state.to_01()
                    self.send_message(UnChoke())    
                # else : #  吸血鬼的话是需要 发Choke的，不过这里不考虑
                #     self.send_file_state.to_11()
                #     self.send_message(Choke())
            elif self.send_file_state.is_01() and type(recv_msg) == Request:
                # 当我Un choke并且对方 interested，发送数据包
                cur_piece_index = recv_msg.piece_index
                cur_piece_binary_data = pieces_manager.get_piece(cur_piece_index)
                self.send_message(Piece(cur_piece_index, cur* _piece_binary_data))
            elif self.send_file_state.is_01() and type(recv_msg) == UnInterested:
                # 当我处于可以发送文件的状态，但是peer收完了，不感兴趣
                self.send_file_state.to_10()
            

            # 开始检查接受文件部分的状态
            if self.recv_file_state.is_11() and type(recv_msg) == UnChoke:
                self.recv_file_state.to_01()
                # TODO:从队列中取一个来发Request
                self.send_message(Request())
            elif self.recv_file_state.is_01() and type(recv_msg) == Piece:
                # TODO:将Piece放到pieces_manager中，如果
                piece_available = 1

                if piece_available == 1:
                    # TODO:如果收到，可用，从队列中取一个新的，并发送新的Request
                    # TODO: 如果队列已经空了，就发送Un interested,并且表明文件已经收完，改变状态
                else :
                    # TODO: 如果不可用，重发Request


            if self.recv_file_state.is_01() and self.send_file_state.is_01():
            # 检查连接是否应该断开
                # TODO:连接断开



            # 请求数据块部分的状态转移
            if self.request_piece_wait_response == 0:
                # 开始一个定时器
                self.request_piece_time_keeper = time.clock()
                if self.my_interested == 0 and self.peer_choking == 0:
                    self.send_message(UnInterested())
                    pieces_manager.merge_full_data_to_file(str(self.socket.s.getsockname())+pieces_manager.file_name)
                    self.request_piece_wait_response = 1
                elif self.my_interested == 0 and self.peer_choking == 1:
                    # TODO:等待态,不需等待回应
                    logger.debug('waiting!')
                    # 然后就会在self.recv_message()阻塞住
                    self.request_piece_wait_response = 1
                elif self.my_interested == 1 and self.peer_choking == 0:
                    logger.debug('I am accepted by remote host!')
                    self.send_message(Request(self.request_piece_index))
                    self.request_piece_wait_response = 1
                elif self.my_interested == 1 and self.peer_choking == 1:
                    self.send_message(Interested())
                    logger.debug('I want you know I am interested with you!')
                    self.request_piece_wait_response = 1
                
            # 发送数据块部分的状态转移
            if self.send_piece_wait_response == 0:
                self.send_piece_time_keeper = time.clock()
                if self.my_choking == 0 and self.peer_interested == 0:
                    # self.send_message(Choke())
                    # TODO:似乎永远不会到达该状态
                    self.send_piece_wait_response = 0
                elif self.my_choking == 0 and self.peer_interested == 1:
                    self.send_message(UnChoke())
                    self.send_piece_wait_response = 1
                elif self.my_choking == 1 and self.peer_interested == 0:
                    # TODO:等待态,需要想想怎么处理
                    logger.debug('waiting!')
                    # 然后就会在self.recv_message()阻塞住
                    self.send_piece_wait_response = 1
                elif self.my_choking == 1 and self.peer_interested == 1:
                    self.send_message(Choke())
                    self.send_piece_wait_response = 1

            recv_msg = self.recv_message()
            # 如果没有收到消息，就继续循环,否则就处理消息
            if not recv_msg:
                # 如果超时还没有收到消息，就将wait_response置为0，重新发送消息
                logger.warning('[ warning ] no message')
                if self.send_piece_wait_response == 1 and (time.clock()-self.send_piece_time_keeper > 1):
                    logger.warning('send_piece time out!')
                    self.send_piece_wait_response = 0
                
                if self.request_piece_wait_response == 1 and (time.clock()-self.request_piece_time_keeper > 1):
                    logger.warning('request_piece time out!')
                    self.request_piece_wait_response = 0
                continue

            # 发送数据块部分的状态转移
            if self.send_piece_wait_response == 1:
                if type(recv_msg) == Interested:
                    self.peer_interested = 1
                    # TODO:这里可以决定我到底是choking 还是 no_choke
                    self.my_choking = 0
                    logger.debug('I know you are interested with me. ')
                    self.send_piece_wait_response = 0
                if type(recv_msg) == Request:
                    # TODO: 需要发送东西， 而且一般发完之后紧接着的是request请求
                    cur_piece_index = recv_msg.piece_index
                    cur_piece_binary_data = pieces_manager.get_piece(cur_piece_index)
                    print(cur_piece_binary_data)
                    self.send_message(Piece(cur_piece_index, cur_piece_binary_data))
                    self.send_piece_wait_response = 1
                if type(recv_msg) == UnInterested:
                    self.peer_interested = 0
                    self.my_choking = 1
                    self.send_message(Choke())
                    self.send_piece_wait_response = 0
            # 请求数据块部分的状态转移
            if self.request_piece_wait_response == 1:
                if type(recv_msg) == Piece:
                    # 得到字符串,原数据块的二进制数据
                    recv_raw_data = recv_msg.raw_data
                    recv_piece_index = recv_msg.piece_index
                    print(recv_raw_data)
                    recv_data_available = 0
                    # 得到的数据块，经过哈希检验后若无误，放入pieceManager中，同时从队列中更新待下载数据块
                    if str(hashlib.sha1(recv_raw_data).digest()) == pieces_manager.hash_table[recv_piece_index]:
                        logger.debug('{} data received without error'.format(recv_piece_index))
                        recv_data_available = 1

                    # 如果数据可用
                    if recv_data_available == 1:
                        pieces_manager.update_data_field(recv_piece_index, recv_raw_data)
                        # self.send_message(Have(recv_piece_index))
                        # 如果下载完成，队列中没有元素，就不感兴趣，否则从队列中继续取
                        queue_top_available = 0
                        # 如果队列元素可用，则退出循环
                        # 退出循环的时候，一定有一个可用元素，或者队列为空
                        while(not queue_top_available):
                            # 在不断从队列中寻找可下载数据块的时候队列可能会变成空的
                            if left_pieces.empty():
                                self.my_interested = 0
                                self.request_piece_wait_response = 0
                                break
                            # 如果队列不空，则在队列中取一个元素
                            self.request_piece_index, self.request_piece_hash = left_pieces.get()
                            # 如果对面有这个数据块，就interest，否则就放回队列中
                            if self.peer_bitfield[self.request_piece_index] == 1:
                                self.my_interested = 1
                                queue_top_available = 1
                                logger.debug("I am interested!")
                            else:
                                left_pieces.put((self.request_piece_index, self.request_piece_hash))
                        self.request_piece_wait_response = 0
                    else:
                        # 如果数据不可用，传输出现损坏,重发
                        self.request_piece_wait_response = 0
                if type(recv_msg) == Choke:
                    self.peer_choking = 1
                    self.request_piece_wait_response = 0
                if type(recv_msg) == UnChoke:
                    self.peer_choking = 0
                    self.request_piece_wait_response = 0
                if type(recv_msg) == Bitfield:
                    self.peer_bitfield = bitarray.bitarray(recv_msg.bitfield)
                    print(self.peer_bitfield)
                    queue_top_available = 0
                    # 如果队列元素可用，则退出循环
                    # 退出循环的时候，一定有一个可用元素，或者队列为空
                    while(not queue_top_available):
                        # 在不断从队列中寻找可下载数据块的时候队列可能会变成空的
                        # print('try to get an item in queue.')
                        # print('queue is empty?{}'.format(str(left_pieces.empty())))
                        if left_pieces.empty():
                            self.my_interested = 0
                            self.request_piece_wait_response = 0
                            logger.debug('The queue is empty.')
                            break
                        # 如果队列不空，则在队列中取一个元素
                        (self.request_piece_index, self.request_piece_hash) = left_pieces.get()
                        # 如果对面有这个数据块，就interest，否则就放回队列中
                        if self.peer_bitfield[self.request_piece_index] == 1:
                            self.my_interested = 1
                            queue_top_available = 1
                            logger.debug("I am interested!")
                        else:
                            left_pieces.put((self.request_piece_index, self.request_piece_hash))
                    self.request_piece_wait_response = 0

            if type(recv_msg) == KeepAlive:
                pass
            # if type(recv_msg) == Have:
            #     # TODO:应该是向已连接的所有peer发送have消息
            #     piece_index = recv_msg.piece_index
            #     self.peer_bitfield[piece_index] = 1

    def send_message(self, msg):
        """ 传入message对象，并转成二进制发送 """
        self.socket.sendBytes(msg.to_bytes())
        logger.info('--------------------------------------------------')
        logger.debug('[ send from {} to {}] : '.format(self.socket.s.getsockname(), self.socket.s.getpeername())+ msg.to_json_string())
        logger.info('--------------------------------------------------')

    def recv_message(self):
        """ 接受消息，并转成对应消息的对象 """
        logger.debug('begin recvive message')
        msg = bytes_to_message(self.socket.recvBytes())
        logger.debug('end receive message')
        logger.info('--------------------------------------------------')
        logger.debug('[ recv ] from {} to {} : '.format(self.socket.s.getpeername(), self.socket.s.getsockname()) +  msg.to_json_string())
        logger.info('--------------------------------------------------')
        return msg

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
        logger.info('client side run...')
        # 从bitfield中初始化队列，将任务放到队列中等待连接去执行
        self.from_bitfield_setup_queue()
        logger.info('initing the queue ..... finished!')
        # 得到所有的peer列表。存在self.peerListResponse里。
        self.get_peers_list()
        # 监听端口，等待其他peer建立其的链接
        logger.info('ok get list')
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((self.client_ip, self.client_port))
        listen_socket.listen(CLIENT_LISTEN_MAX)

        # 向N个peer主动发起链接
        self.establish_link()

        while True:
            # 阻塞型接受新链接
            (new_socket, addr) = listen_socket.accept()
            logger.debug('get new socket from listener port, addr is {}'.format(addr))
            # 开启新线程建立链接
            peer_connection = PeerConnection(new_socket, self.pieces_num)
            peer_connection.start()

    def get_peers_list(self):
        """ 向tracker发起链接，请求peer list """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug('connect to tracker : {}:{} '.format(self.metadata['announce'],str(self.metadata['port'])))
        sock.connect((self.metadata['announce'], self.metadata['port']))
        rdt_s = rdt_socket.rdt_socket(sock)
        rdt_s.sendBytes(utilities.objEncode(self.make_resquest(START_EVENT)))
        data = rdt_s.recvBytes()
        logger.debug(utilities.binary_to_beautiful_json(data))
        sock.close()
        self.peers_list_response = utilities.objDecode(data)
        logger.debug('finish get peer list')

    def establish_link(self):
        """ 主动向peer建立链接 """
        for idx, peer_info in enumerate(self.peers_list_response['peers']):
            if idx >= 4: return # TODO: add constant here
            peer_ip = peer_info['peer-ip']
            peer_port = peer_info['peer-port']
            logger.debug('trying to connect to peer {}:{}'.format(peer_ip, peer_port))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer_ip, peer_port))
            # 拉起新的线程管理该tcp
            peer_connection = PeerConnection(sock, self.pieces_num)
            logger.debug('connect to {}:{} finish. tcp start'.format(peer_ip, peer_port))
            peer_connection.start()
    
    def from_bitfield_setup_queue(self):
        """ 根据现有的bitfield，将没有的块的（索引，哈希值）二元组push进全局队列中 """
        for i in range(0, self.pieces_num):
            if pieces_manager.bitfield[i] == 0:
                logger.info('put the {}:{} into queue !'.format(i,self.metadata['info']['piece_hash'][i]))
                left_pieces.put((i,self.metadata['info']['piece_hash'][i]))
    
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
    logger.info('in file client.py')
    logger.debug('test case (NULL) running...')
    logger.debug('test case finish')
