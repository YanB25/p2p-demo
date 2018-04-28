import socket
import rdt_socket
import socket
import utilities			#实用工具库，提供get_host_ip函数
import server_config
SERVER_IP = utilities.get_host_ip()	#获取本机ip
SERVER_PORT = 6666			#服务器端口固定为6666
#获取socket文件，采用tcp连接 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#设置允许重用地址，防止程序退出后提示端口仍被占用
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#开始监听端口
server_socket.bind((SERVER_IP, SERVER_PORT))
#设置最大连接数为MAX_TCP_LINK
server_socket.listen(1)
(client_socket, address) = server_socket.accept()
rdt_s = rdt_socket.rdt_socket(client_socket)
f =open('Untitled.mov', 'rb').read()
rdt_s.sendBytes(f)
