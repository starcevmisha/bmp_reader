import sys
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QFrame,
    QTextEdit,
    QPlainTextEdit,
    QSplitter,
    QStyleFactory,
    QApplication,
    QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QPixmap, QBrush


class Example(QWidget):

    def __init__(self, name, tags, text):
        self.app = QApplication(sys.argv)
        super().__init__()

        self.title = name

        self.initUI(name, tags, text)

    def initUI(self, name, tags, text):
        hbox = QHBoxLayout(self)

        top = QLabel()
        pixmap = QPixmap("123.jpg")
        top.setPixmap(pixmap)
        top.show()

        bottom = QPlainTextEdit(text)
        bottom.setFrameShape(QFrame.StyledPanel)

        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(top)
        splitter1.addWidget(bottom)

        hbox.addWidget(splitter1)
        self.setLayout(hbox)

        self.setGeometry(200, 200, 500, 600)
        self.setWindowTitle(self.title)
        self.show()

    def onChanged(self, text):

        self.lbl.setText(text)
        self.lbl.adjustSize()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
