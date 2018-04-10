""" create message  object """

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
    def resquest(piece_index):
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

if __name__ == '__main__':
    print(Message.keep_alive())
    print(Message.choke())
    print(Message.no_choke())
    print(Message.interested())
    print(Message.no_interested())
    print(Message.have(3))
    print(Message.bitfield(3))
    print(Message.resquest(4))
    data = b'testest'
    print(Message.piece(3, data))