import sys
sys.path.insert(0, '../src/backend/')
from client2 import *
from torrent import *



# make_torrent_file('vid.mp4', )
test_torrent_file = './vid.mp4.torrent'
client = Client(test_torrent_file)
client.start()