---
typora-copy-images-to: ./img
---

[TOC]

# 一.实验要求

- C/S通信实现要求：

1. 两台计算机分别模拟服务器、客户端
2. 通过编程实现服务器端、客户端程序Socket，Client。
3. 服务器端程序监听客户端向服务器端发出的请求， 并返回数据给客户端。
4. 不采用方式，自定义通信协议，传输文件要足够大（例如：一个视频文件）

- P2P通信实验要求

1. 为每个peer开发服务器程序、客户端程序
2. 每个peer上线后，向服务器注册自己的通信信息；
3. 假设peer3要下载文件 （视频），A与peer1，peer2都拥有A，请设计方案使peer3能够同时从peer1、peer2同时下载该文件，例如：从peer1下载A的前50%、同时从peer2下载后50%。
4. 比较与C/S通信方式的性能指标

# 二. 设计摘要

- 本次实验我们使用Python3语言，在Linux操作系统上完成。


- C/S通信部分，我们使用TCP作为传输层协议，使用固定头部+可变数据长度的应用层通信协议，能够解决TCP的分包、黏包问题。
- P2P部分：我们研究并实现了简化版的有tracker服务器的Bittorrent协议。采用消息循环的设计方式，两台对等主机之间建立连接后各自开启一个线程，交换bitfield并初始化自身状态，进入消息循环，根据自身状态和收到的消息决定状态的转换和执行的操作。
- 各台对等主机，以及对等主机和服务器之间的通信基于了C/S通信部分实现的可靠二进制文件传输模块。

# 三. 具体实现

## 1. C/S通信

### (1).  应用层协议

C/S通信中采用TCP作为传输层协议，可以保证传输的文件流是有序且无误的。然而TCP作为一种流传输协议，应用层是无法获知接收缓冲区中一个文件起始和结束的位置。因此我们采用了固定头部+可变数据长度的应用层通信协议，我们将之命名为rdt_socket。

![image-20180428121650380](/Users/lixinrui/QtProject/p2p-demo/report/img/image-20180428121650380.png)

### (2). 服务端

服务端在使用该协议时，首先建立普通的socket连接：

```python
import socket
import utilities					#实用工具库，提供get_host_ip函数
SERVER_IP = utilities.get_host_ip()	#获取本机ip
SERVER_PORT = 6666					#服务器端口固定为6666
#获取socket文件，采用tcp连接 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#设置允许重用地址，防止程序退出后提示端口仍被占用
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#开始监听端口
server_socket.bind((SERVER_IP, SERVER_PORT))
#设置最大连接数为MAX_TCP_LINK
server_socket.listen(MAX_TCP_LINK)
```

然后将该server_socket传入rdt_socket类，获得rdt_socket对象，然后将要发送的二进制文件传入sendBytes方法，该方法将在在其头部加上8字节的文件长度信息

```python
def sendBytes(self, f : bytearray):
    try:
        #获取文件长度
        l = len(f)
        #设置header
        header = struct.pack('!1Q', l)
        send_data = header + f
        #记录日志
        logger.debug('Sending raw tcp data len {}'.format(len(send_data)))
        #使用socket发送该message
        self.s.sendall(send_data)
        #异常处理
    except socket.error as e:
        print(e)
        print(e.filename)
```

### (3). 客户端

客户端在使用该协议时，同样首先建立普通的TCP连接连接到服务器，然后将socket传入rdt_socket类，使用rdt_socket的recvBytes方法获取文件

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, SERVER_PORT))
rdt_s = rdt_socket.rdt_socket(sock)
data = rdt_s.recvBytes()
```

recvBytes的实现如下，其基本思路是：

首先检查缓冲区是否有8个字节的header，若有则检查缓冲区的长度是否有header中指出的文件长，若有则说明有一个文件可以取出了。该函数会首先检查当前TCP缓冲区中是否已经有有一个文件，如果没有，才会阻塞读取缓冲区，之后再检查是否有一个文件。

```python
def recvBytes(self):
    if len(self.databuf) >= FILE_HEADER_SIZE:
        header = struct.unpack("!1Q", self.databuf[:FILE_HEADER_SIZE])
        body_size = header[0]
        if len(self.databuf) >= FILE_HEADER_SIZE + body_size:
            body = self.databuf[FILE_HEADER_SIZE:FILE_HEADER_SIZE + body_size]
            self.databuf = self.databuf[FILE_HEADER_SIZE+body_size:]
            return body
    while True:
        data = self.s.recv(1024)
        logger.debug('Received raw tcp data len {}'.format(len(data)))
        if data:
            self.databuf += data
            while True:
                if len(self.databuf) < FILE_HEADER_SIZE:
                    break
                header = struct.unpack("!1Q", self.databuf[:FILE_HEADER_SIZE])
                body_size = header[0]
                if len(self.databuf) < FILE_HEADER_SIZE + body_size:
                    break
                body = self.databuf[FILE_HEADER_SIZE:FILE_HEADER_SIZE + body_size]
                self.databuf = self.databuf[FILE_HEADER_SIZE+body_size:]
                return body
```

## 2.P2P通信

下面我们将从三个方面分别介绍我们设计的P2P通信协议

1. Torrent文件格式
2. Tracker — Peer协议
3. Peer — Peer 协议

### (1). Torrent文件格式

Torrent文件的作用是：

- 声明了一个P2P网络的tracker服务器地址和端口。
- 声明了在该P2P网路上共享的一个文件的文件名、长度、区块数、各区块哈希值，唯一确定了一个文件。

一个Peer在获取一个Torrent文件后，便可加入该P2P网络并获取该文件。

使用(类)Json的语法描述Torrent文件如下：

```json
{
  announce: <str>, #domain name
  port: <int>
  comment: <str>
  info: <dict> {
    piece_length: <int>
    piece_hash: <list<str>>
    file_name: <str> 
    file_length: <int>
  }
}
```

### (2).Tracker — Peer协议 

这部分协议提供了加入和退出P2P的机制。特别是使得加入P2P的Peer能够获取目前的Peer列表。

#### Peer发送的Request格式：

包含：

- Peer的IP
- port，Peer的本地监听端口
- peer_id，由peer的ip和port组成
- event，可能值包括started（用于请求加入网络），stoped（未使用），completed（用于请求退出网络）。

```json
{
  port: <int> (validator: 1~65536)
  ip (opt): <str>, (validator: 点分十进制表示法)
  peer_id: <str>, (peer ip + ':' + peer port)
  event: <str>, [(started) | (stopped) | (completed)]
}
```

#### Traker发送的Response格式：

包含：

- error_code，收到的请求有效时为0，非法请求则为1
- message，包括started ACK和disconnect ACK两种
- num-of-peer，请求前的peer数
- 请求前P2P网络中的peer的id、端口、地址

```python
{
  error_code: <int>
  message: <str> 
  num-of-peer: <int>
  peers: <list> [
    {
      peer-id: <str> (peer ip + ':' + peer port)
      peer-port: <int> <validator: 1 - 65536>
      peer-ip: <str> <validator: 点分十进制表示法>
    }
  ]
}
```

该Response仅会向刚刚发送请求的peer发送。这样已经加入的peer不会收到新peer加入的消息，然而由于我们的设计是peer1向peer2主动建立一个peer connection连接时，peer2会同样会（被动地）和peer1建立一个peer connection，因此之前已经加入网络的Peer依旧能够与新Peer建立连接。

### (3).Peer — Peer 协议

如摘要部分提到的，每个Peer是以消息循环的方式进行工作。



## 五、设计心得

过去三周，我从零开始，学习了Qt，QML，JavaScript，SQL，设计模式，成功写出了本Project，取得了较大收获。这段学习过程中遇到的困难，主要是面对一些全新的，又没有好的教程用来形成一个基础的知识体系，以及足够大的社区帮你在StackOverflow上问好各种问题，一个很简单的问题都会卡很久。例如学习QML时，官方的tutorial就是讲了一个简单的例子，并没有讲清每一句话的含义，大概是“你看，这里写个TextField{}，就会有个文本框”这种感觉。但，TextField及它里面的property、它的id作用域是什么呢，跨文件怎么办呢？（我大概有几天时间都在纠结各种"property xxx is not bound in this Context"）？

直到一周后去图书馆找参考书，在广图没有找到，还好学校图书馆有一本，帮助我建立了知识体系，对我起了很大帮助。

 