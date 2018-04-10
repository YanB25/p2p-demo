import sys
sys.path.insert(0, '../../src/backend/')
from client import *
from torrent import *

make_torrent_file('vid.mp4')
test_torrent_file = './vid.mp4.torrent'
test_config_file = './client_config.json'
client = Client(test_torrent_file,test_config_file)
client.start()