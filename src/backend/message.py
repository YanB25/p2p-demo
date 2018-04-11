""" create message  object """

import struct
import bitarray
import json
import random

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
        
class Choke():
    """ Choke类消息 """
    def __init__(self):
        self.length = 1
        self.message_id = 0
    def to_bytes(self):
        return struct.pack('!ib', self.length, self.message_id)
    def to_json_string(self):
        msg = {}
        msg['type'] = self.__class__.__name__
        msg['length'] = self.length
        msg['message_id'] = self.message_id
        return json.dumps(msg, indent=4)
class UnChoke():
    """ UnChoke类消息 """
    def __init__(self):
        self.length = 1
        self.message_id = 1
    def to_bytes(self):
        return struct.pack('!ib', self.length, self.message_id)
    def to_json_string(self):
        msg = {}
        msg['type'] = self.__class__.__name__
        msg['length'] = self.length
        msg['message_id'] = self.message_id
        return json.dumps(msg, indent=4)
class Interested():
    """ Interested类消息 """
    def __init__(self):
        self.length = 1
        self.message_id = 2
    def to_bytes(self):
        return struct.pack('!ib', self.length, self.message_id)
    def to_json_string(self):
        msg = {}
        msg['type'] = self.__class__.__name__
        msg['length'] = self.length
        msg['message_id'] = self.message_id
        return json.dumps(msg, indent=4)
class UnInterested():
    """ UnInterested类消息 """
    def __init__(self):
        self.length = 1
        self.message_id = 3
    def to_bytes(self):
        return struct.pack('!ib', self.length, self.message_id)
    def to_json_string(self):
        msg = {}
        msg['type'] = self.__class__.__name__
        msg['length'] = self.length
        msg['message_id'] = self.message_id
        return json.dumps(msg, indent=4)

class Have():
    """ Have类消息 """
    def __init__(self, piece_index : int ):
        """ piece_index为请求对应的数据块的索引 """
        self.length = 1 + 4
        self.message_id = 4
        self.piece_index = piece_index
    def to_bytes(self):
        fmt = '!ibi'
        return struct.pack(fmt, self.length, self.message_id, self.piece_index)
    def to_json_string(self):
        msg = {}
        msg['type'] = self.__class__.__name__
        msg['length'] = self.length
        msg['message_id'] = self.message_id
        msg['piece_index'] = self.piece_index
        return json.dumps(msg, indent=4)
        
        
class Bitfield():
    """ Bitfield类消息 """
    def __init__(self, _bitfield : list ):
        """ _bitfield 为一个只含有0,1的列表 """
        self.bitfield = _bitfield
        self.length = 1 + len(_bitfield)
        self.message_id = 5
    def to_bytes(self):
        fmt = '!ib{}b'.format(str(self.length-1))
        return struct.pack(fmt, self.length, self.message_id, *self.bitfield)
    def to_json_string(self):
        msg = {}
        msg['type'] = self.__class__.__name__
        msg['length'] = self.length
        msg['message_id'] = self.message_id
        msg['bitfield'] = bitarray.bitarray(self.bitfield).to01()
        return json.dumps(msg, indent=4)

class Request():
    """ Request类消息 """
    def __init__(self, piece_index : int ):
        """ piece_index为请求对应的数据块的索引 """
        self.length = 1 + 4
        self.message_id = 6
        self.piece_index = piece_index
    def to_bytes(self):
        fmt = '!ibi'
        return struct.pack(fmt, self.length, self.message_id, self.piece_index)
    def to_json_string(self):
        msg = {}
        msg['type'] = self.__class__.__name__
        msg['length'] = self.length
        msg['message_id'] = self.message_id
        msg['piece_index'] = self.piece_index
        return json.dumps(msg, indent=4)
        
class Piece():
    """ Piece类消息 """
    def __init__(self, piece_index : int, raw_data : bytes):
        """ piece_index 是该块对应的索引，raw_data 是该块对应的内容，字节对齐 """
        self.piece_index = piece_index
        self.raw_data = raw_data
        self.length = 1 + 4 + len(raw_data)
        self.message_id = 7
    def to_bytes(self):
        fmt = '!ibi'
        return struct.pack(fmt, self.length, self.message_id, self.piece_index)+self.raw_data
    def to_json_string(self):
        msg = {}
        msg['type'] = self.__class__.__name__
        msg['length'] = self.length
        msg['message_id'] = self.message_id
        msg['raw_data'] = str(self.raw_data)
        return json.dumps(msg, indent=4)



def bytes_to_message(binary):
    _msg_length = struct.unpack_from('!i', binary, 0)
    # 因为会返回元组，只能够这样加上索引来访问,下面同理
    msg_length = _msg_length[0]
    if msg_length == 0:
        return KeepAlive()
    else:
        _msg_id = struct.unpack_from('!b', binary, 4)
        msg_id = _msg_id[0]
        if msg_id == 0:
            return Choke()
        elif msg_id == 1:
            return UnChoke()
        elif msg_id == 2:
            return Interested()
        elif msg_id == 3:
            return UnInterested()
        elif msg_id == 4:
            _piece_index = struct.unpack_from('!i', binary, 5)
            return Have(_piece_index[0])
        elif msg_id == 5:
            tuple_bitfield = struct.unpack_from('!'+str(msg_length-1)+'b', binary, 5)
            print(tuple_bitfield)
            list_bitfield = list(tuple_bitfield)
            return Bitfield(list_bitfield)
        elif msg_id == 6:
            _piece_index = struct.unpack_from('!i', binary, 5)
            return Request(_piece_index[0])
        elif msg_id == 7:
            _piece_index = struct.unpack_from('!i', binary, 5)
            piece_index = _piece_index[0]
            raw_data = binary[9:]
            return Piece(piece_index, raw_data)
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
# -----------------Choke--------------------
    msg = Choke()
    print("type(msg) == ", type(msg))
    print('type(msg) == Choke ?', type(msg) == Choke)

    binary_msg = msg.to_bytes()
    print('binary_msg : ', binary_msg)

    ret_msg = bytes_to_message(binary_msg)
    print('type(ret_msg) == Choke ?', type(ret_msg) == Choke)
    print('ret_msg.to_json() : ', ret_msg.to_json_string())


# -----------------Bitfield--------------------
    msg = Bitfield(bitarray.bitarray([1,0,0,0,0,0,1,1,1,0]))
    print("type(msg) == ", type(msg))
    print('type(msg) == Bitfield ?', type(msg) == Bitfield)

    binary_msg = msg.to_bytes()
    print('binary_msg : ', binary_msg)

    ret_msg = bytes_to_message(binary_msg)
    print('type(ret_msg) == Bitfield ?', type(ret_msg) == Bitfield)
    print('ret_msg.to_json() : ', ret_msg.to_json_string())

# -----------------Request--------------------
    msg = Request(3)
    print("type(msg) == ", type(msg))
    print('type(msg) == Request ?', type(msg) == Request)

    binary_msg = msg.to_bytes()
    print('binary_msg : ', binary_msg)

    ret_msg = bytes_to_message(binary_msg)
    print('type(ret_msg) == Request ?', type(ret_msg) == Request)
    print('ret_msg.to_json() : ', ret_msg.to_json_string())

# -----------------Piece--------------------
    msg = Piece(3, b'r129r930jf9023u4234u2394')
    print("type(msg) == ", type(msg))
    print('type(msg) == Piece ?', type(msg) == Piece)

    binary_msg = msg.to_bytes()
    print('binary_msg : ', binary_msg)

    ret_msg = bytes_to_message(binary_msg)
    print('type(ret_msg) == Piece ?', type(ret_msg) == Piece)
    print('ret_msg.to_json() : ', ret_msg.to_json_string())
