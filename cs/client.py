import socket
import rdt_socket
import datetime
SERVER_ADDR = '127.0.0.1'
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_ADDR, 6666))
rdt_s = rdt_socket.rdt_socket(sock)
begin = datetime.datetime.now()
data = rdt_s.recvBytes()
end = datetime.datetime.now()
print(end-begin)
