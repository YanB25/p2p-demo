'''
server side for p2p protocal.
usage:
python3 server.py

dependencies:
config.py
it set ip and port for server
'''
import os
import utilities
import threading
import socket
import json
from rdt_socket import *
from server_config import *
import logging 

logging.basicConfig(
    # filename='../../log/client.log',
    format='[%(asctime)s - %(levelname)s ]: \n%(message)s\n',
    datefmt='%M:%S',
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

SERVER_IP = utilities.get_host_ip()
SERVER_PORT = 6666

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(MAX_TCP_LINK)

#TODO: need validator for ip, port and id
class ServerMonitor(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server
    def run(self):
        logger.info('server monitor running')
        while True:
            enter = input('(you can quit if enter q)...\n')
            if enter == 'q':
                logger.warning('server quit. all tcp link WILL NOT SAVE')
                # self.server.fouceQuit() 
                # #TODO: should send quit msg to all tcp link
                # unknown bug. maybe it is becaz not check msg type in all place in client.py
                # talk with WYF
                os._exit(0)

class Peer(object):
    """
    Peer Object storing ip, port and a unique id.
    """
    def __init__(self, ip, port, id):
        self.ip = ip
        self.port = port
        self.id = id
    def __str__(self):
        return "{}:{} id:{}".format(self.ip, self.id, self.id)
    def __eq__(self, rhs):
        return self.id == rhs.id and self.ip == rhs.ip and self.port == rhs.port
        
available_peers = []

# start callback
class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        logger.info('listening to port {} at ip {}'.format(SERVER_PORT, SERVER_IP))
    def run(self):
        ## init server monitor
        self.server_monitor = ServerMonitor(self)
        self.server_monitor.start()

        while True:
            logger.info('server being running')
            (client_socket, address) = server_socket.accept()

            rdt_s = rdt_socket(client_socket)
            data = rdt_s.recvBytes()
            json_data = utilities.objDecode(data)

            ip, _ = address
            port = json_data['port']
            id = json_data['peer_id']
            event = json_data['event']

            if event == 'started':
                logger.debug(available_peers)
                rdt_s.sendBytes(utilities.objEncode(self.START_ACK()))
                client_socket.close()

                if id not in [peer.id for peer in available_peers]:
                    available_peers.append(Peer(ip, port, id))
                    logger.debug('connected by %s', (ip, port, id))
                else:
                    logger.warning('peer already in list, ip %s port %d id %s', 
                        ip, 
                        port, 
                        id)

            elif event == 'completed':
                logger.debug('get disconnect request')
                logger.info('ip:%s, port:%d, id:%s', ip, port, id)
                try:
                    available_peers.remove(Peer(ip, port, id))
                except ValueError as e:
                    logger.exception(e, exc_info=True)
                    logger.critical('no this peer. ignore.')
                    rdt_s.sendBytes(utilities.objEncode({
                        'error_code': 1,
                        'message': 'NOT a peer for this server',
                    }))
                rdt_s.sendBytes(utilities.objEncode(self.COMPLETE_ACK()))
                client_socket.close()
                logger.debug("disconnect finished, id:%s", id)
                logger.debug(available_peers)
            else:
                logger.critical("warning, known event {}".format(event), json_data)
                client_socket.send(utilities.objEncode({
                    'error_code': 1,
                    'message': 'no event in request. abort.'
                }))
                client_socket.close()

    def available_peers_list(self):
        return [{
            'peer-id': obj.id,
            'peer-port': obj.port,
            'peer-ip': obj.ip
            } for obj in available_peers if obj.id != id
        ]
    def START_ACK(self):
        return {
            'error_code': 0,
            'message': 'started ACK',
            'num-of-peer': len(available_peers),
            'peers': self.available_peers_list()
        }
    def COMPLETE_ACK(self):
        return {
            'error_code': 0,
            'message': 'disconnect ACK'
        }
    def fouceQuit(self):
        for peer in available_peers:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.debug('trying to connect to peer id:%s, quit.', peer.id)
            sock.connect((peer.ip, peer.port))
            rdt_s = rdt_socket(sock)
            rdt_s.sendBytes(utilities.objEncode({
                'type': 10,
                'message': 'server not going to keep working'
            }))
            logger.debug('disconnect msg has sent to peer %s', peer.id)
            sock.close()
if __name__ == "__main__":
    server = Server()
    server.start()