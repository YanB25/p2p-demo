# 测试方法说明

1. 为了方便测试，原有get_host_ip函数我改成了直接返回127.0.0.1

1. 以下指令，运行的python需要某相对地址处的文件，在运行前需要先cd到指定目录，不然找不到文件。

## 做种，启动服务端
```sh
cd p2p-demo/test
python3 test_main.py
# 该文件的作用是更新种子文件，并启动客户端 
```

## 启动客户端

注意！客户端一旦启动，会先在“文件名_data"下加载历史数据，数据块以索引号命名
因此若想使用部分数据来调试，可以往里面放几个块

目前每一个测试客户端都有完整的文件数据块，可删掉一些再测试。
客户端运行完之后会把数据块存下来，可通过注释client.py:line 268取消这种行为

### 启动做种客户端，含有完整数据
```sh
cd p2p-demo/test/seed
python3 seed_client.py
```

### 启动其他客户端，不含有或只含有部分数据

```sh
cd p2p-demo/test/c2
python3 test_client2.py
```

