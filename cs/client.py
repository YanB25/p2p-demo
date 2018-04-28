import socket
import rdt_socket
SERVER_ADDR = '127.0.0.1'
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_ADDR, 6666))
rdt_s = rdt_socket.rdt_socket(sock)
data = rdt_s.recvBytes()
