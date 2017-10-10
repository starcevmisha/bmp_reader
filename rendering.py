from struct import unpack

import math
import bmp_reader
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPixmap, QFont
from PyQt5 import QtCore
from sys import argv

from const import Const
from pixel_extarct import Extractor
from pixel_extract_rle import RLEExtractor


class Render(QWidget):

    def __init__(
            self,
            file,
            header,
            info,
            palette,
            progress_bar=None,
            parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.file = file
        self.header = header
        self.info = info
        self.palette = palette
        self.progress_bar = progress_bar
        self.initUI()

        self.pixmap_cache = None
        self.cached = False
        self.min_size = 300
        self.pixel_size = 1
        self.max_size = 1000

        self.last_prefer_size = 0

    def initUI(self):
        self.resize(450, 350)
        self.setWindowTitle('BMP image')
        # self.show()

    def paintEvent(self, e):
        if self.pixmap_cache is not None and self.last_prefer_size == Const.prefer_pixel_size:
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
        if Const.prefer_pixel_size !=0:
            self.pixel_size = Const.prefer_pixel_size
            self.last_prefer_size = Const.prefer_pixel_size
        elif max(self.info.width, self.info.height) < self.min_size:
            self.pixel_size = math.floor(self.min_size / self.info.width)
        elif max(self.info.width, self.info.height) > self.max_size:
            self.pixel_size = 1 / math.ceil(self.info.width / self.max_size)
        self.last_prefer_size = Const.prefer_pixel_size
        self.pixmap_cache = QPixmap(max(self.min_size, self.info.width*self.pixel_size),
                                    max(self.min_size, abs(self.info.height)*self.pixel_size))
        self.pixmap_cache.fill(QtCore.Qt.transparent)

        painter = QPainter()
        painter.begin(self.pixmap_cache)
        try:
            self.render_pic(painter, self.pixel_size)
        except:
            painter.setFont(QFont("times", 22))
            painter.setPen(QColor(*(255, 0, 0)))
            painter.drawText(0, 30, 'ERROR. BAD IMAGE')

        painter.end()

    def render_pic(self, painter, size):
        if self.header.version == "CORE" or self.info.compression in [0, 3, 6]:
            extractor = Extractor(
                self.file,
                self.header,
                self.info,
                self.palette,
                self.progress_bar)
        elif self.info.compression in [1, 2]:
            extractor = RLEExtractor(
                self.file,
                self.header,
                self.info,
                self.palette,
                self.progress_bar)
        if size < 1:
            t = 1
            max_t = round(1 / size)
            for pixel in extractor.get_pixel(size):
                if t == 1:
                    (x, y), color = pixel
                    painter.fillRect(int(x), int(y), 1, 1, QColor(*color))
                elif t == max_t:
                    t = 0
                t += 1
        else:
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
