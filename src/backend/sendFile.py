import json
import socket
from rdt_socket import *
import utilities
from client_config import *

class Peer(object):
    def __init__(self, domain, port):
        self.am_interested = INIT_AM_INTERESTED
        self.am_chocked = INIT_AM_CHOCKED
        self.peer_interested = INIT_PEER_INTERESTED
        self.peer_chocked = INIT_PEER_CHOCKED
        self.domain = domain
        self.port = port

class Client(object):
    def openTorrent(self, file_name):
        with open(file_name, 'rb') as file:
            self.torrent = json.load(file)

    def requestServer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = socket.gethostbyname(self.torrent['announce'])
        print(ip)
        s.connect((ip, self.torrent['port']))
        rdt_s = rdt_socket(s)
        self.ip = s.getsockname()[0]
        self.listen_port = 6666
        self.id = "hhl"
        rdt_s.sendBytes(utilities.objEncode(
            {
                'ip': self.ip,
                'port': self.listen_port,
                'peer_id': self.id,
                'event': 'started'
            }
        ))
        server_resp = utilities.objDecode(rdt_s.recvBytes())
        print(server_resp)

    def connectPeer(self, peer : Peer):
        peer.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            peer.ip = socket.gethostbyname(peer.domain)
            print("Connected to tracker server")
        except socket.error as e:
            print(e)
client = Client()
client.openTorrent("1.json")
while True:
    client.requestServer()
