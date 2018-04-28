'''
Reliably send a file (bytes)
Usage : suppose you have a byte array f to send / recv
        On sender side :
            s = connect(ip, port)
            rdt_s = rdt_socket(s)
            rdt_s.sendBytes(f)
        On receiver side :
            s, addr = accept()
            rdt_s = rdt_socket(s)
            rdt_s.recvBytes()
'''
import socket
import struct
import logging
logging.basicConfig(
    # filename='../../log/client.{}.log'.format(__name__),
    format='[%(asctime)s - %(name)s - %(levelname)s] : \n%(message)s\n',
    # datefmt='%M:%S',
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
logger.disabled = True

# from client_config import *
FILE_HEADER_SIZE = 8
class rdt_socket(object):
    def __init__(self, s : socket):
        self.s = s
        self.databuf = bytes()

    def sendBytes(self, f : bytearray):
        try:
            l = len(f)
            header = struct.pack('!1Q', l)
            send_data = header + f
            logger.debug('Sending raw tcp data len {}'.format(len(send_data)))
            self.s.sendall(send_data)
        except socket.error as e:
            print(e)
            print(e.filename)

    def recvBytes(self):
        if len(self.databuf) >= FILE_HEADER_SIZE:
            header = struct.unpack("!1Q", self.databuf[:FILE_HEADER_SIZE])
            body_size = header[0]
            if len(self.databuf) >= FILE_HEADER_SIZE + body_size:
                body = self.databuf[FILE_HEADER_SIZE:FILE_HEADER_SIZE + body_size]
                self.databuf = self.databuf[FILE_HEADER_SIZE+body_size:]
                return body
        while True:
            data = self.s.recv(1024)
            logger.debug('Received raw tcp data len {}'.format(len(data)))
            if data:
                self.databuf += data
                while True:
                    if len(self.databuf) < FILE_HEADER_SIZE:
                        break
                    header = struct.unpack("!1Q", self.databuf[:FILE_HEADER_SIZE])
                    body_size = header[0]
                    if len(self.databuf) < FILE_HEADER_SIZE + body_size:
                        break
                    body = self.databuf[FILE_HEADER_SIZE:FILE_HEADER_SIZE + body_size]
                    self.databuf = self.databuf[FILE_HEADER_SIZE+body_size:]
                    return body
