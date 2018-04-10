"""
本文件函数列表：
make_torrent_file(upload_file_name) 会在当前目录下生成upload_file_name.torrent文件
read_torrent_file(torrent_file_name) 读取torrent文件，返回一个dict
same_as_torrent(torrent_file_name, download_file) 检测种子文件元数据与下载的文件是否相符合，符合返回1，不符合返回0
"""


import json
import socket
import bitarray
import hashlib
import os
from  utilities import *
# from collection import OrderedDict

DEFAULT_PIECE_SIZE = 512
DEFAULT_CLIENT_PORT = 6666


def make_torrent_file(file_name):
    """使用本机ip及文件制作torrent文件"""
    
    torrent = {}
    torrent['announce'] = get_host_ip() # 获取本机IP
    torrent['port'] = DEFAULT_CLIENT_PORT # 默认本机监听端口号
    torrent['comment'] = 'test'
    torrent['info'] = {}
    torrent['info']['piece_length'] = DEFAULT_PIECE_SIZE # 默认块大小
    torrent['info']['piece_hash'] = []
    # 使用系统调用获取去除路径后的文件名
    torrent['info']['file_name'] = os.path.basename(file_name)
    # 使用系统调用获取文件大小
    torrent['info']['file_length'] = os.path.getsize(file_name)
    piece_length = torrent['info']['piece_length']
    with open(file_name,'rb') as file:
        while 1:
            piece_contents = file.read(piece_length)
            if not piece_contents:
                break
            else:
                torrent['info']['piece_hash'].append(str(hashlib.sha1(piece_contents).digest()))
    with open(file_name+'.torrent', 'w') as file:
        json.dump(torrent, file)

def read_torrent_file(torrent_file_name):
    """读取指定的torrent文件，返回一个dict"""

    with open(torrent_file_name, 'r') as file:
        torrent = json.load(file)
    return torrent

def same_as_torrent(torrent_file_name, download_file):
    """将下载的指定文件进行解析，与种子文件元数据进行对比
        若相同则返回1，出现差错则返回0"""

    torrent = read_torrent_file(torrent_file_name)
    piece_length = torrent['info']['piece_length']
    download_length = os.path.getsize(download_file)
    if torrent['info']['file_length'] != download_length:
        print('The file size not match!')
        return 0
    piece_numbers = len(torrent['info']['piece_hash'])
    diff_show_status = bitarray.bitarray([0 for _ in range(1, piece_numbers+1)])
    diff_status = 1
    piece_index = 0
    with open(download_file, 'rb') as file:
        while 1:
            # 读取一个piece
            piece_contents = file.read(piece_length)
            if not piece_contents:
                break
            # 如果读完，则结束，否则进行加密，计算sha1值
            hash_piece = str(hashlib.sha1(piece_contents).digest())
            # 如果不相等，则输出
            if hash_piece != torrent['info']['piece_hash'][piece_index]:
                diff_status = 0
                diff_show_status[piece_index] = 1
                # 去掉注释，可以看到是第几块数据块出现了问题
                # print(piece_index,'： -----------------------------------------')
                # print(hash_piece)
                # print(torrent['info']['piece_hash'][piece_index])
            # 无论如何，都要+1，去读下一个包
            piece_index += 1
    # print(diff_show_status)
    return diff_status


if __name__ == '__main__':
    test_file_name = '../../test/vid.mp4'
    # 那个currupted文件，第一行改了一点东西
    test_currupted_file_name = '../../test/vid_currupted.mp4'
    test_torrent_name = '../../test/vid.mp4.torrent'
    make_torrent_file(test_file_name)
    t = read_torrent_file(test_torrent_name)
    print(t)
    print(type(t))
    # 通过自己修改了torrent文件，测试了一下
    d = same_as_torrent(test_torrent_name,test_currupted_file_name)
    print(d)
    d = same_as_torrent(test_torrent_name,test_file_name)
    print(d)

    
