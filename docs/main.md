# p2p-demo 

主要进行了bit-torrent客户端的实现，顺便实现了tracker服务器。
具有的功能有：
1. 上传文件
1. 下载文件
1. 通过‘块差机制’维护p2p网络正常生态。

注意的是，目前的实现仅仅能够做到单文件分享（tracker仅维护一个文件的可用peer列表）

[toc]

## 请求通用格式

对每一个客户端之间的请求，都会加上这样的首部。
### header
```
<body-length> : 32bits
<body> : body-length
```
### body

body can be any format. In this project, it is always a `json`.

## 种子文件格式

在bittorrent官方协议中，种子文件以及很多的消息都使用了特殊的bencode进行编码，本项目出于以主要实现协议核心的目的，将bencode简化成json。

种子文件含有以下参数：
|参数名|作用|
|-|-|
|announce|tracker服务器的ip或者url|
|port|tracker服务器监听的端口|
|comment: (optional)|一些对该种子文件的描述|
|piece length|块长|
|piece SHA1|<list> 每一个块的sha1值|
|file name|文件名|
|file length|文件的字节大小|

用json文件描述如下：
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

## tracker 服务器端
官方bittorrent协议中，tracker服务器使用http协议，客户端通过向服务器发送`GET`请求获取可用peer列表。
我们实现的协议做了一些改动，首先，这一个tracker不再是一个http服务器，而是能够响应我们发送的request包的专用服务器。

### 接受request请求

tracker接受具有以下参数的request请求。

|Parameters|作用|
|-|-|
|Metainfo file hash|种子文件的哈希值（TODO:如何说明？好像是一部分）|
|peer_id|客户端的id|
|event|请求事件|
```json
{
  port: <int> (validator: 1~65536)
  ip (opt): <str>, (validator: ip-validator)
  peer_id: <str>, <20 bytes>
  event: <str>, [(started) | (stopped) | (completed)]
}
```

### 对request请求返回值
```json
{
  error_code: <int>
  message: <str> 
  tracker-id(not support): <str>, <20 bytes>
  num-of-peer: <int>
  peers: <list> [
    {
      peer-id: <str> <20 bytes>
      peer-port: <int> <validator: 1 - 65536>
      peer-ip: <str> <validator: 点分十进制表示法>
    }
  ]
}
```
## 用户间协议

```py
伪代码
url = Torrent.parseUrl(torrent)
peers = Client.getPeers(url)
for peer in peers:
  #线程
  alive = client.shakehand(peer)
  if(alive):
    peer.bitfield = client.ex_bitfield(peer) # xchg bitfield
    if (hasMyNeed(peer.bitfield)):
      Message msg(type = 0);
      msg.interested = True
      peer.send(msg)
      peer.am_interested = True        
    msg = client.wait_message(peer) # blocked
    
    if msg is interested:
      # 若unchoked 对等方大于4个,则无法对该peer提供服务
      # 把peer存进队列，并以块差为key
      # 若unchoked 对等方小于4个，则还有空闲的流量可以为其服务
      if unchoked peer less then 4:
        peer.send(UNCHOKED)
      else:
        peer.send(choked)
        queue.push({peer, deltaBlock})
        
    
    if msg is no-interested:
      # 若对方不对我感兴趣，且对方choked我，则没有任何数据可交换了
      # 直接断开链接
      # 若对方不choked我，我还可以继续向对方请求block，链接保持
      if peer.choked:
        break-connection(peer)
        build-new-connection()
      
    if msg is choked:
      # 若对方choked我，继续保持链接
      # 我还能向对方提供服务，让对方unchoked 我
      pass
      
    if msg is no-choked:
      # 对方unchoked我，向它请求block
      if peer.hasMyNeed()
        peer.send(block-request)
      else
        peer.send(no-interested)
    
    if msg is block-request:
      if delta-block > 10:
          peer.send(choked)
      else:
      


          peer.send(required-block)
    
    if msg is required-block:
      # 如果peer还有我需要的block，就继续请求
      # 如果块差变小了，可以解除对对面的choked
      if peer.hasMyNeed():
          peer.send(block-request)
      if delta-block < 10 and peer.my-choked == True:
          peer.send(no-choked)
      
```   

    
对peer:
choked && interested: 等待对方的block request, 并向对方回传消息
choked && no-interested:
peer需要维护的量
可用peer列表（从tracker中获取）
已建立连接的peer列表（通过keep-alive消息来维持）
peer对自己的状态列表(key 为peer_id)
所有peer对自己的状态（choked）
所有peer对自己的状态（interested）
自己对peer的状态字典(key 为peer_id)
自己对所有peer的状态（choked）
自己对所有peer的状态（interested）
状态
对每一个与peer的连接，都有以下四个值来指示该连接的状态。
am_choking
am_interested
peer_choking
peer_interested
Handshake
{
  info_hash <str> : <20 bytes>
  peer_id <str> : <20 bytes>
}

Message
1. keep-alive
{
  // 空包，客户端通过首部长度字段为0来判断。这个peer还活着
}
choke
{
  type <str> : 'choke'
}
not choke
{
  type <str> : 'no_choke'
}
interested
{
  type <str> : 'no_choke'
}
no_interested
{
  type <str> : 'no_interested'
}
have
{
  type <str> : 'have'
  piece_index <int> : <4 bytes> // 块的序列号，表示有第I个块
}
bitfield
{
  type <str> : 'bitfield'
  bit_field <int> : <variable-length> // 使用bitArray
}
request
{
  type <str> : 'request'
  piece_index <int> : <4 bytes> // 请求第I个块
  // 默认piece与block大小相等
}
piece
{
  type <str> : 'piece'
  piece_index <int> : <4 bytes> // 发送第I个块
  raw_data <int> : <variable-length> // 发送的第I个块的数据
  // piece的大小应该是固定的，只是最后一个包可能会变小
}
以上消息都使用json方式来包装
转成二进制格式，加上定长的数据块长度作为文件首部，发送
summary
每个peer会被很多其他的对等方interested。用以下的方法决定，给予哪几个对等方服务：
定义块差为「发送给peer的块」减去「从peer接受的块」
从intereted的peer中，选择块差最小的一个发送No-choked.

如果块差大于某一个常数k，则说明对面的peer是leecher。向对面发送choked消息。
设置对面为interested
时序
更新interested
向拥有自己所需block的peer发送interested 信息
向不再需要block的peer发送not interested 信息
扫描interested列表，找到unchoked的peer，向其发送block request
死循环，查看socket的接收队列
收到block：向所有peer发送have。向特定的peer发送no instersted. （向特定的peer 发送 insterest）。向特定的「多个」peer发送block request。
收到interested：检查当前my-no-choked的个数。若小于k个，则将其设为my-no-choked,并向其发送no choked.若大于等于k个，则将其加入interest队列，（并发送choked)。
收到no interested：将其设置为choked，并对其发送choked信息。随后，从interested队列中选择一个加入到my-no-choked中，向其发送no-choked.
收到choked：若其仍有我想要的block，则维持interested不变，否则将其设置为no-interested，并向其发送no-interested信息。
收到 no choked：向其发送block request信息。
收到 block request： 定义「块差」为「发送给它的block」-「从它接收到的block」
若块差很大（大于10），说明对方是leecher,向其发送choked。
若它的手中有我需要的block（就可以给它一次机会），置其为Interested，向其发送interested 信息，并向其block request.
若它手中没有我需要的block，或拒绝向我发送block，（说明它是leecher），则结束。
若块差不大（不大于10），则以「负块差」为权重，把block request加入一个队列中。即，优先服务块差比较少的block request
收到have：
四、数据包传输协议
用于将p2p协议中产生的数据包，加上固定长度的首部信息（如数据块的字节数）
然后将这个数据包发送到指定主机。
主机可用url：port  或  ip:port 标识
