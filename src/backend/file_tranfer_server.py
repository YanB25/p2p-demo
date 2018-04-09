import socket
import json
import time
from rdt_socket import *
from utilities import *

SERVER_IP = '127.0.0.1'
CLIENT_IP = '127.0.0.1'
SERVER_PORT = 6666
# CLIENT_PORT

class Server():
    def __init__(self):
        self.files = []
        self.files.append('vid.mp4')
    
    def send_file(self, conn, file_name):
        s = rdt_socket(conn)
        print(file_name)
        with open(file_name, 'rb') as f:
            data = f.read()
        print(data)
        s.sendBytes(data)

    def make_ack(self):
        msg = {}
        msg['status'] = '200'
        return msg

    def make_nak(self):
        msg = {}
        msg['status'] = 'gg'
        return msg

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((SERVER_IP, SERVER_PORT))
        s.listen()
        print(s.getsockname(),  ' is listening.!')
        while True:
            conn, addr = s.accept()
            print('connected by ', addr[0], ':', addr[1])
            time.sleep(2.5)
            msg = json.loads(conn.recv(1024).decode())
            print('get the msg : ', msg)
            if msg['file_name'] in self.files:
                conn.send(objEncode(self.make_ack()))
                ret = objDecode(conn.recv(1024))
                if ret['status'] == '200':
                    self.send_file(conn, msg['file_name'])
            else:
                conn.send(objEncode(self.make_nak()))
                conn.close()



if __name__ == '__main__':
    server = Server()
    server.run()