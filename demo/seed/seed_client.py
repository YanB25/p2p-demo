import sys
sys.path.insert(0, '../../src/backend/')
from client import *
from torrent import *

file_name = '../vid.mp4'
test_torrent_file = file_name+'.torrent'
test_config_file = './client_config.json'
client = Client(test_torrent_file,test_config_file)
client.start()