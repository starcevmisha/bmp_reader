from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QMessageBox, QDialog
from PyQt5.QtWidgets import QApplication
from sys import argv
import sys


class MainWidget(QtWidgets.QMainWindow):

    def __init__(self, filename=None, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.file_name = filename
        self.color_table = None
        self.dock_widget = QtWidgets.QDockWidget(self)
        self.dock_widget.hide()
        self.init_ui()
        if self.file_name is not None and self.file_name != '':
            self.open_file(self.file_name)

    def init_ui(self):

        self.setWindowTitle('BMP file opener')
        self.show()

if __name__ == "__main__":
    app = QApplication(argv)
    widget = MainWidget('lena.bmp')
