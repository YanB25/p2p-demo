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

### 启动做种客户端，含有完整数据
```sh
cd p2p-demo/seed
python3 seed_client.py
```

### 启动其他客户端

```sh
cd p2p-demo/c2
python3 test_client2.py
```

