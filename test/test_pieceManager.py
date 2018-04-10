import sys
sys.path.insert(0, '../src/backend/')

from piecemanager import *

torrent_file_name = 'vid.mp4.torrent'
full_file_name = 'vid.mp4'
save_file_name = 'save_void.mp4'
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

