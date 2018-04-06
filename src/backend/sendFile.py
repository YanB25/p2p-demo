import json
import socket
from config import *

class Peer(object):
    def __init__(self):
        self.am_interested = INIT_AM_INTERESTED
        self.am_chocked = INIT_AM_CHOCKED
        self.peer_interested = INIT_PEER_INTERESTED
        self.peer_chocked = INIT_PEER_CHOCKED
        self.domain =
class Client(object):
    def connectPeer(self, Peer):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.ip = socket.gethostbyname(domain)
            self.s.connect((self.ip, self.port))
            print("Connected to tracker server")
        except socket.error as e:
            print(e)

    def send(self, file : bytearray):
        len = len(file)
        self.s.sendall(len.to_bytes(8, byteorder='big'))
        self.s.sendall(file)

    def recv(self):
        pass
