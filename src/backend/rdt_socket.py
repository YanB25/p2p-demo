import socket
import struct
from client_config import *

class rdt_socket(object):
    def __init__(self, s : socket):
        self.s = s
        self.databuf = bytes()

    def sendBytes(self, f : bytearray):
        l = len(f)
        header = struct.pack('!1Q', l)
        send_data = header + f
        self.s.sendall(send_data)

    def recvBytes(self):
        while True:
            data = self.s.recv(1024)
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
