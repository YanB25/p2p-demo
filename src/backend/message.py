""" create message  object """

import struct
import json
class Message():
    @staticmethod
    def keep_alive():
        return ''

    @staticmethod
    def choke():
        msg = create_message('choke')
        return msg
    
    @staticmethod
    def no_choke():
        msg = create_message('no_choke')
        return msg

    @staticmethod
    def interested():
        msg = create_message('interested')
        return msg
    
    @staticmethod
    def no_interested():
        msg = create_message('no_interested')
        return msg
    
    @staticmethod
    def have(piece_index):
        msg = create_message('have')
        msg['piece_index'] = piece_index
        return msg
    
    @staticmethod
    def bitfield(_bitfield):
        msg = create_message('bitfield')
        msg['bitfield'] = _bitfield
        return msg
    
    @staticmethod
    def request(piece_index):
        msg = create_message('resquest')
        msg['piece_index'] = piece_index
        return msg
    
    @staticmethod
    def piece(piece_index, raw_data):
        msg = create_message('piece')
        msg['piece_index'] = piece_index
        msg['raw_data'] = raw_data
        return msg

def create_message(type):
    msg = {}
    msg['type'] = type
    return msg

class KeepAlive():
    def __init__(self):
        self.length = 0
    def to_bytes(self):
        return struct.pack('!i',self.length)
    def to_json_string(self):
        msg = {}
        msg['type'] = self.__class__.__name__
        msg['length'] = self.length
        return json.dumps(msg, indent=4)
        

def bytes_to_message(binary):
    msg_length = struct.unpack('!i', binary)
    print(msg_length)
    # 因为会返回元组，只能够这样加上索引来访问
    if msg_length[0] == 0:
        return KeepAlive()
    else:
        return None
        

if __name__ == '__main__':
    # print(Message.keep_alive())
    # print(Message.choke())
    # print(Message.no_choke())
    # print(Message.interested())
    # print(Message.no_interested())
    # print(Message.have(3))
    # print(Message.bitfield(3))
    # print(Message.request(4))
    # data = b'testest'
    # print(Message.piece(3, data))

    msg = KeepAlive()
    print("type(msg) == ", type(msg))
    print('type(msg) == KeepAlive ?', type(msg) == KeepAlive)

    binary_msg = msg.to_bytes()
    print('binary_msg : ', binary_msg)

    ret_msg = bytes_to_message(binary_msg)
    print('type(ret_msg) == KeepAlive ?', type(ret_msg) == KeepAlive)
    print('ret_msg.to_json()', ret_msg.to_json_string())

