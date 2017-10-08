from PyQt5 import QtWidgets

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QPushButton
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QWidget, QMainWindow
from PyQt5.QtGui import QPainter, QColor
import sys
import bmp_reader
from rendering import Render
import os


class MainWidget(QMainWindow):

    def __init__(self, args, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.palette = []
        self.initUI()

        if args.file:
            self.file_name = os.path.realpath(args.file)

            directory = os.path.dirname(os.path.realpath(self.file_name))
            self.list_of_bmp_files = [
                directory +
                '\\' +
                f for f in os.listdir(directory) if f.endswith('.bmp')]
            self.list_index = self.list_of_bmp_files.index(self.file_name)
        if args.dir:
            directory = os.path.dirname(
                os.path.realpath(
                    args.dir)) + '\\' + args.dir
            self.list_of_bmp_files = [
                directory +
                '\\' +
                f for f in os.listdir(directory) if f.endswith('.bmp')]
            self.file_name = self.list_of_bmp_files[0]
            self.list_index = self.list_of_bmp_files.index(self.file_name)
        self.set_image(self.file_name)

    def initUI(self):
        palette_action = QtWidgets.QAction("&Show palette", self)
        palette_action.setShortcut('Ctrl+P')
        palette_action.triggered.connect(self.show_palette)

        next_button = QtWidgets.QAction("&NextImage", self)
        next_button.triggered.connect(self.on_click_next)
        prev_button = QtWidgets.QAction("&PrevImage", self)
        prev_button.triggered.connect(self.on_click_prev)

        menu_bar = self.menuBar()
        menu_bar.addAction(palette_action)
        menu_bar.addAction(prev_button)
        menu_bar.addAction(next_button)

        self.resize(600, 600)
        self.center()
        self.setWindowTitle('BMP file opener')

        self.show()

    def show_palette(self):
        palette_widget = PaletteWidget(self.palette)
        palette_widget.setGeometry(300, 300, 600, 200)
        palette_widget.exec_()

    def center(self):  # Отцентровать окно
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @pyqtSlot()
    def on_click_next(self):  # x = +1
        self.next_prev_image(1)

    @pyqtSlot()
    def on_click_prev(self):  # x =  -1
        self.next_prev_image(-1)

    def next_prev_image(self, x):
        self.list_index += x
        if self.list_index == len(self.list_of_bmp_files):
            self.list_index = 0
        if self.list_index == -1:
            self.list_index = len(self.list_of_bmp_files) - 1
        self.set_image(self.list_of_bmp_files[self.list_index])

    def set_image(self, name):
        self.setWindowTitle(os.path.basename(name))
        with open(name, 'rb') as f:
            self.file = f.read()
        reader = bmp_reader.Reader()
        reader.check_file_type(self.file)
        self.header = reader.read_header(self.file)
        self.info = reader.read_info(self.file, self.header.version)

        self.palette = reader.read_pallete(self.file, self.info)
        self.renderer = Render(
            self.file, self.header, self.info, self.palette)
        self.setCentralWidget(self.renderer)


class PaletteWidget(QDialog):

    def __init__(self, palette, parent=None):
        QWidget.__init__(self, parent)
        self.palette = palette
        self.setWindowTitle('Palette')

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        self.draw_palette(painter, self.palette)
        painter.end()

    def draw_palette(self, painter, palette_arr):
        color_size = 20
        count = self.height() // color_size
        chunks = [palette_arr[x:x + count]
                  for x in range(0, len(palette_arr), count)]
        for i in range(len(chunks)):
            for j in range(len(chunks[i])):
                painter.fillRect(
                    i * color_size,
                    j * color_size,
                    color_size,
                    color_size,
                    QColor(
                        *chunks[i][j]))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWidget('pal1.bmp')
    widget.show()
    app.exec_()
