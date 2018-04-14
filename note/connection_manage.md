# 连接的调度如何弄？

## 全局变量修改的加锁

1. queue修改的加锁
    1. 从队列里取一个块与放回去的过程需要加锁
**UPDATE:不需要加锁。Python的Queue是线程安全的。但Queue不保证empty()和qsize()能返回准确的值。不排除发生RC的可能**

1. piece_manager
    1. update_data_field函数的调用是线程不安全的
        1. 若我先将数据存到数组中，还来不及更新bitfield，线程突然切换，另一个线程也请求从bitfield中拿到刚刚其实已经下好的但是还没有更新到bitfield的数据，就出问题了。


## 修改方案

1. client传入一个lock

```py

    lock = threading.lock()

    def __init__(self, sock, pieces_num, lock):

        self.lock = lock


    def get_available_piece_request(self):

        self.lock().acquire()

        self.lock().release()    
```

## 谁，什么时候，保存数据？