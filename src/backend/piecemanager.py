import json
import collections
import torrent
import bitarray
import os

class pieceManager():
    """
    这个类维护着
        数据块列表: index 对应的数据块的binary data
        哈希列表：index对应的数据块的hash值
        bitfield : 用于其他进程访问
        以上都可以使用piece_index直接索引
    这个类有这样的功能：

    对发送文件方而言
        能够从pieceManager中拿到索引号对应的数据块并且发送
        piece_data get_piece(piece_index)

    对接收文件方而言
        能够将正确的数据块放到pieceManager维护的数据里，并更新bitfield【必须保证正确】，如果数据块已存在就不管TODO:似乎函数名字错了，晚点改回来
        update_data_bitfield(piece_index, piece_data)
        
        如果文件已经下载完成，就将已有的数据块存成文件
        merge_data_to_file()

        存一个块到“$(file_name)_data/$(piece_index)"中
        save_piece_data(piece_index, raw_data)

        将当前的所有块存起来
        save_current_all_pieces()
    
        尝试读取以前下载的块，如果有就加载，没有就没有罗，不干活
        load_previous_all_pieces(self, temp_file_name='temp_piece_data'):


    对所有连接，都需要
        bitfield get_bitfield()
    
    """
    # 初始化文件管理器的时候应该需要用这几个参数初始化：文件名，哈希表，块长度，bitfield可以自己生成
    def __init__(self, torrent_file_name):
        """ 需要传入种子文件文件名，通过种子文件初始化，默认没有文件 """
        metadata = torrent.read_torrent_file(torrent_file_name)
        self.torrent_file_name = torrent_file_name
        self.hash_table = metadata['info']['piece_hash'] # 得到了一个哈希列表
        self.piece_length = metadata['info']['piece_length']
        self.file_name = metadata['info']['file_name']
        self.file_length = metadata['info']['file_length']
        self.piece_num = len(self.hash_table)
        self.pieces_data = [None]*self.piece_num # 给列表预初始化大小
        self.bitfield = bitarray.bitarray([0 for _ in range(1, self.piece_num+1)])

        # self.load_exist_full_file_data()
        self.load_previous_all_pieces()

    def save_piece_data(self, piece_index, save_path=''):
        """ 将一个piece数据块存到文件夹save_path中，默认存到$(FILE_NAME)_data/$(piece_number)中，如test.txt的第0块存到test.txt_data/0中 """
        # TODO:文件名中有点‘。’,不太好？？
        if not save_path:
            save_path = self.file_name+'_data/'
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        with open(save_path+str(piece_index), 'wb') as f:
            f.write(self.pieces_data[piece_index])

    def load_piece_data(self, piece_index, load_path=''):
        """
        从指定的路径中找到文件数据并加载进来，
        load_path：文件数据存放路径,末尾默认含有/
        piece_index: 对应数据块索引
        """
        # 动态默认值的实现，默认路径为  test.txt_data/
        if not load_path:
            load_path = self.file_name+'_data/'
        # TODO:文件不存在，异常处理？
        with open(load_path+str(piece_index), 'rb') as f:
            piece_data = f.read()
            self.update_data_field(piece_index, piece_data)

    def save_current_all_pieces(self, save_path=''):
        """ 将当前的所有块存起来 """
        [self.save_piece_data(i,save_path) for i in range(0,self.piece_num) if self.bitfield[i] == 1]
    
    def load_previous_all_pieces(self, load_path=''):
        """ 寻找指定路径下的文件数据，并加载进来 """
        # 动态默认值的实现，默认路径为  test.txt_data/
        if not load_path:
            load_path = self.file_name+'_data/'
        if not os.path.exists(load_path):
            os.mkdir(load_path)
        # 得到路径下的所有文件名的列表
        files_list = os.listdir(load_path)
        for f_name in files_list:
            if f_name.isdigit():
                # 如果文件名是数字
                piece_index = int(f_name)
                if 0 <= piece_index and piece_index <= self.piece_num:
                    self.load_piece_data(piece_index,load_path)
            else:
                pass
    
    def is_completed(self):
        if 0 in self.bitfield:
            return False
        return True

    def get_bitfield(self):
        """ 返回bitfield """
        return self.bitfield

    def get_piece(self, piece_index):
        """ 从已有的数据块中找到对应的已下载数据返回, 返回格式是binary """
        # 如果没有数据块，会返回None （在初始化的时候就已经实现了使用None初始化列表）
        return self.pieces_data[piece_index]
    
    def update_data_field(self, piece_index, piece_data):
        """ 将数据块放入到对应的index的列表中 """
        # 默认认为数据块一定是正确的，并且原来没有这个数据块
        self.pieces_data[piece_index] = piece_data
        self.bitfield[piece_index] = 1
        print(self.bitfield)
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
        print('load the file completed!')
        print('The bitfield is ', self.bitfield)
    
    def merge_full_data_to_file(self, save_file_name=''):
        """ 如果拥有完整的数据块，尝试将数据块整合成一整个文件 """
        if not save_file_name:
            save_file_name = 'download_'+self.file_name
        if not self.is_completed():
            # TODO: 如果文件不完整，不能够运行这个函数，异常处理
            print('The data is not completed')
            return 0
        print('The data is completed')
        with open(save_file_name, 'wb') as f:
            for i in range(0, self.piece_num):
                f.write(self.pieces_data[i])
        print('same ?:',torrent.same_as_torrent(self.torrent_file_name, save_file_name))
        return 1


