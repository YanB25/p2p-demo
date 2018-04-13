# message的重构

需求：

客户端中：

send_message(message)函数中，可以传一个消息类的对象，然后直接使用Message.to_bytes()就可以得到其二进制数据进行文件传输
recv_message()函数中，可以接受一个二进制数据，并根据其内容返回一个Message对象


每个消息弄一个类
1. 各自的构造函数，构造各种消息
1. to_bytes()函数
1. to_json()函数，方便调试

同时还有一个bytes_to_message(binary)函数，能够使用二进制数据，生成对应的消息类对象
1. 读取二进制文件内的固定偏移量处的参数，得知message类型，然后使用相应的解析字符串，构造，返回对应的对象
