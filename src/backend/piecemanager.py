import json
import collections
import torrent
import bitarray
import os

class pieceManager():
    """
    这个类维护着
        数据块列表:  TODO:需不需要存哈希表？我暂时没有想到这个需求,所以就用个列表就好,不过还是顺便存一个字典吧
        bitfield : 用于其他进程访问
    这个类有这样的功能：

    对发送文件方而言
        能够从pieceManager中拿到索引号对应的数据块并且发送
        piece_data get_piece(piece_index)

    对接收文件方而言
        能够将正确的数据块放到pieceManager维护的数据里，并更新bitfield【必须保证正确】，如果数据块已存在就不管
        update_data_bitfield(piece_index, piece_data)
        merge_data_to_file()
    
    对所有连接，都需要
        bitfield get_bitfield()
    
    初次打开，必须初始化文件数据块，索引号，哈希表，如何初始化？
    """
    # 初始化文件管理器的时候应该需要用这几个参数初始化：文件名，哈希表，块长度，bitfield可以自己生成
    def __init__(self, torrent_file_name):
        """ 需要传入种子文件文件名，通过种子文件初始化，默认没有文件 """
        metadata = torrent.read_torrent_file(torrent_file_name)
        self.hash_table = metadata['info']['piece_hash'] # 得到了一个哈希列表
        self.piece_length = metadata['info']['piece_length']
        self.file_name = metadata['info']['file_name']
        self.file_length = metadata['info']['file_length']
        self.piece_num = len(self.hash_table)
        self.pieces_data = [None]*self.piece_num # 给列表预初始化大小
        self.bitfield = bitarray.bitarray([0 for _ in range(1, self.piece_num+1)])

        self.load_exist_full_file_data()
        # self.load_previous_data()

    def load_previous_data(self, temp_file_name='temp_piece_data'):
        """ TODO:打算是加载下载到一半的数据进来，放到piece_data成员变量中 """
        return

    def get_bitfield(self):
        """ 返回bitfield """
        return self.bitfield

    def get_piece(self, piece_index):
        """ 从已有的数据块中找到对应的已下载数据返回 """
        # 如果没有数据块，会返回None （在初始化的时候就已经实现了使用None初始化列表）
        return self.pieces_data[piece_index]
    
    def updata_data_field(self, piece_index, piece_data):
        """ 将数据块放入到对应的index的列表中 """
        # 默认认为数据块一定是正确的，并且原来没有这个数据块
        self.pieces_data[piece_index] = piece_data
        self.bitfield[piece_index] = 1
        return
    
    def load_exist_full_file_data(self):
        """ 如果一个文件已经存在，则加载进来，作为已经下载完整的文件 """
        if os.path.isfile(self.file_name):
            print('file {} exist!'.format(self.file_name) )
            self.load_download_file_data(self.file_name)

    def load_download_file_data(self, download_file_name=''):
        """ 将一个已有的文件作为该种子文件对应的文件 """
        # 默认参数为种子文件的文件名
        if not download_file_name:
            download_file_name = self.file_name
        with open(download_file_name, 'rb') as f:
            for i in range(0, self.piece_num):
                self.pieces_data[i] = f.read(self.piece_length)
                self.bitfield[i] = 1
    
    def merge_full_data_to_file(self, save_file_name):
        if 0 in self.bitfield:
            # TODO: 如果文件不完整，不能够运行这个函数，异常处理
            pass
        else:
            with open(save_file_name, 'wb') as f:
                for i in range(0, self.piece_num):
                    f.write(self.pieces_data[i])


if __name__ == '__main__':
    torrent_file_name = './../../test/vid.mp4.torrent'
    full_file_name = './../../test/vid.mp4'
    save_file_name = './../../test/save_void.mp4'
    p = pieceManager(torrent_file_name)
    print(p.get_bitfield())
    q = pieceManager(torrent_file_name)
    q.load_download_file_data(full_file_name)
    print(q.get_bitfield())


    for i in range(0,p.piece_num):
        test_data = q.get_piece(i)
        p.updata_data_field(i, test_data)
        print(p.get_bitfield())
    
    p.merge_full_data_to_file(save_file_name)

    print('same?', torrent.same_as_torrent(torrent_file_name, save_file_name))
    print('same?', p.get_piece(1) == q.get_piece(1))

