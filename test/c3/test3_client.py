import sys
sys.path.insert(0, '../../src/backend/')
from client import *
from torrent import *

# make_torrent_file('vid.mp4')
file_name = 'test.txt'
test_torrent_file = '../{}.torrent'.format(file_name)
test_config_file = './client3_config.json'
client = Client(test_torrent_file,test_config_file)
client.start()