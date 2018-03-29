import sys
from PyQt5 import QtGui, QtWidgets
from config import *
from PyQt5.QtCore import *
import time
#TODO: self.logTextBox should offer API to append information
class WorkingDemo(QThread):
    #TODO: what this syntax it is!? I can't put sinOut into __init__
    sinOut = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.m = 0

    def run(self):
        while True:
            self.m+=1
            print(self.m)
            self.sinOut.emit(str(self.m))
            time.sleep(0.1)

class Window(object):
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        w = QtWidgets.QWidget()
        w.setGeometry(100,100,200,50)
        w.setWindowTitle("P2P Demo")
        self.window = w

        self.initIP(w)
        self.initPort(w)
        self.initLog(w)
        self.initSubmit(w)

        w.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        w.show()
    def run(self):
        self.window.show()
        return self.app.exec_()
    def submitOnClick(self):
        if self.IPValidator(self.ip) and self.PortValidator(self.port):
            print('success', self.ip, self.port)
            self.task = WorkingDemo()
            self.task.sinOut.connect(self.append)
            self.task.start()

    def initIP(self, window):
        self.initIPAddressTextbox(window)
        self.initIPLabel(window)
    def initPort(self, window):
        self.initPortTexbox(window)
        self.initPortLabel(window)
    def initLog(self, window):
        self.initLogTexbox(window)
        self.initLogLabel(window)
        self.logIndex = 0
    def initSubmit(self, window):
        self.submitButton = QtWidgets.QPushButton(window)
        self.submitButton.setText("submit")
        self.submitButton.move(SUBMIT_LEFT_MARGIN, SUBMIT_BUTTON_TOP_MARGIN)
        self.submitButton.clicked.connect(self.submitOnClick)

    def initLogTexbox(self, window):
        self.LogTextbox = QtWidgets.QPlainTextEdit(window)
        self.LogTextbox.move(LOG_LEFT_MARGIN, MARGIN)
        self.LogTextbox.resize(LOG_WIDTH, LOG_HEIGH)
        self.LogTextbox.setReadOnly(True)
    def initLogLabel(self, window):
        self.LogLabel = QtWidgets.QLabel(window)
        self.LogLabel.setText("Log")
        self.LogLabel.move(LOG_LABEL_LEFT_MARGIN, 10)

    def initIPAddressTextbox(self, window):
        self.IPTextbox = QtWidgets.QLineEdit(window) 
        self.IPTextbox.move(LEFT_MARGIN + LABEL_WIDTH, MARGIN)
        self.IPTextbox.textChanged.connect(self.editIP)
    def initPortTexbox(self, window):
        self.portTexbox = QtWidgets.QLineEdit(window)
        self.portTexbox.move(LEFT_MARGIN + LABEL_WIDTH, MARGIN + LABEL_HEIGHT)
        self.portTexbox.textChanged.connect(self.editPort)
    def initIPLabel(self,window):
        self.IPLabel = QtWidgets.QLabel(window)
        self.IPLabel.setText('IP')
        self.IPLabel.move(LEFT_MARGIN, MARGIN + WORD_OFFSET)
    def initPortLabel(self,window):
        self.IPLabel = QtWidgets.QLabel(window)
        self.IPLabel.move(LEFT_MARGIN, MARGIN + WORD_OFFSET + LABEL_HEIGHT)
        self.IPLabel.setText('Port')

    def editIP(self, newIP):
        self.ip = newIP
    def editPort(self, newPort):
        self.port = newPort

    def IPValidator(self, ip):
        ips = ip.split('.')
        if (len(ips) != 4):
            print("Error '.' in IP")
            return False
        try:
            for part in ips:
                ipart = int(part)
                if (ipart <= 0 or ipart >= 256):
                    return False
        except:
            print("Error in parcing IP")
            return False
        return True
    def PortValidator(self, port):
        try:
            iport = int(port)
            if (iport <= 1024 or iport >= 65536):
                print("port {} not in range(1024, 65535)".format(iport))
                return False
        except:
            print("Port {} not int".format(port))
            return False
        return True
    def append(self, txt):
        self.logIndex += 1
        self.LogTextbox.setPlainText(self.LogTextbox.toPlainText()  + txt + "\n")
        self.LogTextbox.verticalScrollBar().setValue(self.logIndex)
if __name__ == '__main__':
    window = Window()
    # Should return the exit code of QApplication
    sys.exit(window.run())
