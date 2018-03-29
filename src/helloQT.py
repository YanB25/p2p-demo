import sys
from PyQt4 import QtGui
class Window(object):
    def __init__(self):
        self.app = QtGui.QApplication(sys.argv)
        self.w = QtGui.QWidget()
        self.b = QtGui.QLabel(self.w)
        LABEL = "Internet Log"
        self.b.setText(LABEL)
        self.b.move(400, 20)
        self.w.setGeometry(100,100,200,50)
        self.w.setWindowTitle("P2P Demo")

        self.textbox = QtGui.QPlainTextEdit(self.w)
        self.textbox.move(100, 50)
        self.textbox.resize(600, 400)
        self.textbox.setReadOnly(True)
        self.w.resize(800, 500)
        self.w.show()
    def run(self):
        self.w.show()
        self.app.exec_()
    def appendText(self, text):
        print(text)
        self.textbox.setPlainText(self.textbox.toPlainText() +text+ "\n")

if __name__ == '__main__':
    window = Window()
    window.appendText('hello')
    window.appendText('world')
    window.run()
    
