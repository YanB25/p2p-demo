import sys
from PyQt4 import QtGui
from config import *
#TODO: self.logTextBox should offer API to append information
class Window(object):
    def __init__(self):
        self.app = QtGui.QApplication(sys.argv)
        w = QtGui.QWidget()
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
        self.app.exec_()
    def submitOnClick(self):
        print('success', self.ip, self.port)
        self.IPValidator(self.ip)
        self.PortValidator(self.port)
        # TODO: server begin here

    def initIP(self, window):
        self.initIPAddressTextbox(window)
        self.initIPLabel(window)
    def initPort(self, window):
        self.initPortTexbox(window)
        self.initPortLabel(window)
    def initLog(self, window):
        self.initLogTexbox(window)
        self.initLogLabel(window)
    def initSubmit(self, window):
        self.submitButton = QtGui.QPushButton(window)
        self.submitButton.setText("submit")
        self.submitButton.move(SUBMIT_LEFT_MARGIN, SUBMIT_BUTTON_TOP_MARGIN)
        self.submitButton.clicked.connect(self.submitOnClick)

    def initLogTexbox(self, window):
        self.LogTextbox = QtGui.QPlainTextEdit(window)
        self.LogTextbox.move(LOG_LEFT_MARGIN, MARGIN)
        self.LogTextbox.resize(LOG_WIDTH, LOG_HEIGH)
        self.LogTextbox.setReadOnly(True)
    def initLogLabel(self, window):
        self.LogLabel = QtGui.QLabel(window)
        self.LogLabel.setText("Log")
        self.LogLabel.move(LOG_LABEL_LEFT_MARGIN, 10)

    def initIPAddressTextbox(self, window):
        self.IPTextbox = QtGui.QLineEdit(window) 
        self.IPTextbox.move(LEFT_MARGIN + LABEL_WIDTH, MARGIN)
        self.IPTextbox.textChanged.connect(self.editIP)
    def initPortTexbox(self, window):
        self.portTexbox = QtGui.QLineEdit(window)
        self.portTexbox.move(LEFT_MARGIN + LABEL_WIDTH, MARGIN + LABEL_HEIGHT)
        self.portTexbox.textChanged.connect(self.editPort)
    def initIPLabel(self,window):
        self.IPLabel = QtGui.QLabel(window)
        self.IPLabel.setText('IP')
        self.IPLabel.move(LEFT_MARGIN, MARGIN + WORD_OFFSET)
    def initPortLabel(self,window):
        self.IPLabel = QtGui.QLabel(window)
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

if __name__ == '__main__':
    window = Window()
    window.run()
    
