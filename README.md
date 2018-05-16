# p2p-demo
a p2p demo, computer network project.
based on Python3

项目主页：

http://wangyf.top/revealjs/pre/p2p-demo

## 瓶颈
QT运行时会阻塞进程。  
需要分离UI线程和任务线程
## Usage
``` sh
$ python src/UI.py
```

or exlicitely

``` sh
$ python3 src/UI.py
```

## backend
define a class and inherit from QThread
``` python
from QtPy5.QtCore import QThread
class Task(QThread):
    pipe = pyqtSignal(str)
    def __init__():
        pass
```
then define function `run`

``` python
class Task(QThread):
    ...
    def run(self, *arg):
        do-your-task()
        self.pipe.emit("hello world")
```
what you send in `self.pipe.emit()`would be sent to UI and shown properly.
