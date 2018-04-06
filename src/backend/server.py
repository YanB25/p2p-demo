import utilities
import socket
import json
from server_config import *
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(MAX_TCP_LINK)
while True:
    (client_socket, address) = server_socket.accept()
    while True:
        data = client_socket.recv(BUFFER_SIZE)
        if not data: 
            continue
        else:
            print(utilities.objDecode(data))
            client_socket.send("ack".encode("utf-8"))
            client_socket.close()
            break
    
