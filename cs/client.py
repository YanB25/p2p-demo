import socket
import rdt_socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 6666))
rdt_s = rdt_socket.rdt_socket(sock)
data = rdt_s.recvBytes()
