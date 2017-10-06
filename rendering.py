from struct import unpack
import bmp_reader
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor
from sys import argv
from pixel_extarct import Extractor


class Render(QWidget):

    def __init__(self, file, header, info, palette, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.file = file
        self.header = header
        self.info = info
        self.palette = palette

        self.initUI()

    def initUI(self):
        self.resize(450, 350)
        self.setWindowTitle('BMP image')
        self.show()

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        size =1

        extractor = Extractor(self.file,self.header,self.info, self.palette)
        for pixel in extractor.get_pixel(size):
            (x, y), color = pixel
            painter.fillRect(x, y, size, size, QColor(*color))

        painter.end()

if __name__ == "__main__":
    with open('pal8gs.bmp', 'rb') as f:
        file = f.read()
        reader = bmp_reader.Reader()
        reader.check_file_type(file)
        header = reader.read_header(file)
        info = reader.read_info(file, header.version)

        app = QApplication(argv)

        palette = reader.read_pallete(file, info)
        render = Render(file, header, info, palette)
        render.show()

        app.exec_()
