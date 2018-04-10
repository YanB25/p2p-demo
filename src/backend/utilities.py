'''
utilities functions here
'''
import json
import socket
def objEncode(obj):
    return json.dumps(obj,indent=4, sort_keys=True).encode('utf-8')
def objDecode(binary):
    return json.loads(binary.decode('utf-8'))

def get_host_ip():
    """得到本机IP"""
    # try:
    #     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     s.connect(('8.8.8.8', 80))
    #     ip = s.getsockname()[0]
    # finally:
    #     s.close()
    # return ip
    return '127.0.0.1'
