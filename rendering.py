from struct import unpack

import math
import time
import bmp_reader
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPixmap
from PyQt5 import QtCore
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

        self.pixmap_cache = None
        self.cached = False
        self.min_size = 300
        self.pixel_size = 1

    def initUI(self):
        self.resize(450, 350)
        self.setWindowTitle('BMP image')
        # self.show()

    def paintEvent(self, e):
        if self.pixmap_cache is not None:
            self.draw_cached()
            return

        self.draw_to_cache()

        if not self.cached:
            self.draw_cached()
            self.cached = True

    def draw_cached(self):
        qp = QPainter()
        geom = self.geometry()
        qp.begin(self)
        qp.resetTransform()
        qp.drawPixmap((geom.width() -
                       self.info.width *
                       self.pixel_size) /
                      2, (geom.height() -
                          abs(self.info.height) *
                          self.pixel_size) /
                      2, self.pixmap_cache)
        qp.end()

    def draw_to_cache(self):

        self.pixmap_cache = QPixmap(max(self.min_size, self.info.width),
                                    max(self.min_size, self.info.height))
        self.pixmap_cache.fill(QtCore.Qt.transparent)

        painter = QPainter()
        painter.begin(self.pixmap_cache)
        if max(self.info.width, self.info.height) < self.min_size:
            self.pixel_size = math.floor(self.min_size / self.info.width)
        self.render_pic(painter, self.pixel_size)
        painter.end()

    def render_pic(self, painter, size):
        extractor = Extractor(self.file, self.header, self.info, self.palette)
        for pixel in extractor.get_pixel(size):
            (x, y), color = pixel
            painter.fillRect(x, y, size, size, QColor(*color))

    def new_file(self, file, header, info, palette):
        self.file = file
        self.header = header
        self.info = info
        self.palette = palette
        self.pixmap_cache = None
        self.cached = False
        self.repaint()


if __name__ == "__main__":
    app = QApplication(argv)
    with open('pal8gs.bmp', 'rb') as f:
        file = f.read()
    reader = bmp_reader.Reader()
    reader.check_file_type(file)
    header = reader.read_header(file)
    info = reader.read_info(file, header.version)

    palette = reader.read_pallete(file, info)
    render = Render(file, header, info, palette)
    render.show()

    app.exec_()
