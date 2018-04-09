import socket
import json
import time
import hashlib

from utilities import *
from rdt_socket import *

SERVER_IP = '127.0.0.1'
SERVER_PORT = 6666



class Client():
    def __init__(self):
        """ 需要维护一个要连接的服务器的列表，一个客户端只接受一个文件 """
        """ 初始化服务器列表（先初始化一个） """
        """ 还有一个数据块字典 """
        self.server_ip = SERVER_IP
        self.server_port = SERVER_PORT

    def make_ack(self):
        msg = {}
        msg['status'] = '200'
        return msg
        
    def make_nak(self):
        msg = {}
        msg['status'] = 'gg'
        return msg

    def make_request(self,file_name):
        msg = {}
        msg['status'] = '100'
        msg['file_name'] = file_name
        return msg

    def main_request_file(self, file_name, save_file_name):
        """ 讲道理，是从服务器列表中请求文件，并存到指定路径，成功或失败， 这是主入口函数 """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.server_port))
        msg = self.make_request(file_name)
        s.send(objEncode(msg))
        print('send the msg: ', msg)
        ret = json.loads(s.recv(1024).decode())
        print('get the msg: ', ret)
        if (ret['status'] == '200'):
            s.send(objEncode(self.make_ack()))    
            with open(save_file_name, 'wb') as f:
                # time.sleep(5)
                rdt_s = rdt_socket(s)
                b = rdt_s.recvBytes()
                print(b)
                f.write(b)
        
        s.close()


def diff_the_file(file1, file2):
    with open(file1, 'rb') as f1:
        data1 = f1.read()
    with open(file2, 'rb') as f2:
        data2 = f2.read()
    if hashlib.sha1(data1).digest() == hashlib.sha1(data2).digest():
        print('{} and {} is same.'.format(file1, file2))
    else:
        print('{} and {} is different.'.format(file1, file2))


if __name__ == '__main__':
    test_file = 'vid.mp4'
    test_download_file = 'my_vid.mp4'
    
    client = Client()
    client.main_request_file('vid.mp4', 'my_vid.mp4')

    diff_the_file(test_file, test_download_file)
