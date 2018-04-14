import sys
sys.path.insert(0, '../../src/backend/')

from piecemanager import *
from torrent import *


file_name = 'vid.mp4'
torrent_file_name = '{}.torrent'.format(file_name)
full_file_name = file_name
save_file_name = 'save_{}'.format(file_name)

# 初始化两个数据块管理器，一个空的，另一个是加载完全的
empty_piece_manager = pieceManager(torrent_file_name)
print(empty_piece_manager.get_bitfield())
full_piece_manager = pieceManager(torrent_file_name)
full_piece_manager.load_download_file_data(full_file_name)
print(full_piece_manager.get_bitfield())

# for i in range(0,empty_piece_manager.piece_num):
#     test_data = full_piece_manager.get_piece(i)
#     empty_piece_manager.update_data_field(i, test_data)
#     print(empty_piece_manager.get_bitfield())


# empty_piece_manager.merge_full_data_to_file(save_file_name)

# print('same?', torrent.same_as_torrent(torrent_file_name, save_file_name))
# print('same?', empty_piece_manager.get_piece(1) == full_piece_manager.get_piece(1))


full_piece_manager.save_current_all_pieces()
empty_piece_manager.load_previous_all_pieces()
empty_piece_manager.merge_full_data_to_file(save_file_name)
print('same?', same_as_torrent(torrent_file_name, save_file_name))