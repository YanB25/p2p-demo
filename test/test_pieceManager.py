import sys
sys.path.insert(0, '../src/backend/')

from piecemanager import *

p = pieceManager('vid.mp4.torrent')
print(p.get_bitfield())
q = pieceManager('vid.mp4.torrent')
q.load_download_file_data()
print(q.get_bitfield())

test_index = 1
test_data = q.get_piece(test_index)
p.updata_data_field(test_index, test_data)
print(p.get_bitfield())
print(q.get_piece(test_index))
print(p.get_piece(test_index))
print('same?', p.get_piece(1) == q.get_piece(1))