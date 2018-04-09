from rdt_socket import *

class Client():
    def __init__(self):
        """ 需要维护一个要连接的服务器的列表，一个客户端只接受一个文件 """
        """ 初始化服务器列表（先初始化一个） """
        """ 还有一个数据块字典 """

    def main_request_file(file_name, save_path):
        """ 讲道理，是从服务器列表中请求文件，并存到指定路径，成功或失败， 这是主入口函数 """


    def request_file(file_name):
        """ 向服务器列表发送request请求，请求一个文件，并返回已成功连接的socket列表 """

    def receive_file(sockets, file_name):
        """ 从已成功连接的socket列表中接受数据块，并且维护数据块的完整性，直到文件传输完成 """
        with open(file_name, 'wb') as file:
            for s in sockets:
                rdt_s = rdt_socket(s)
                file.write(rdt_s.recvBytes())




        