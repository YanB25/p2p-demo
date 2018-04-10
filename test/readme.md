# 测试方法说明

1. 在/src/backend/中打开server.py，运行tracker服务器
1. 在/test/client1目录下运行test_client.py
    1. 注意，客户端的逻辑为先在当前目录下寻找与种子元数据内文件名同名的文件，若找到则加载进来，当做已经下载完了，还会将bitfield更新为全是1
1. 在/test/运行test_client2.py
    1. 注意，这个客户端目录下因为没有测试文件，所以bitfield就为0
1. 然后就可以看到效果了

如果要修改客户端的端口，请修改test_client.py 对应的json文件