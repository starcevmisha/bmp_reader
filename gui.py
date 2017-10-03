from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QMessageBox, QDialog
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QWidget, QMainWindow
from PyQt5.QtGui import QPainter, QColor
import sys
import bmp_reader


class MainWidget(QMainWindow):

    def __init__(self, filename=None, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.file_name = filename
        self.palette = []
        self.initUI()

        with open(self.file_name, 'rb') as f:
            file = f.read()
            reader = bmp_reader.Reader()
            reader.check_file_type(file)
            header = reader.read_header(file)
            info = reader.read_info(file, header.version)

            self.color_table = reader.read_pallete(file, info)



    def initUI(self):
        palette_action = QtWidgets.QAction("&Show palette", self)
        palette_action.setShortcut('Ctrl+P')
        palette_action.triggered.connect(self.show_palette)

        menu_bar = self.menuBar()
        menu_bar.addAction(palette_action)

        self.resize(450, 350)
        self.center()
        self.setWindowTitle('BMP file opener')
        self.show()

    def show_palette(self):
        palette_widget = PaletteWidget(self.color_table)
        palette_widget.setGeometry(200, 100, 700, 200)
        palette_widget.exec_()


    def center(self): # Отцентровать окно
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class PaletteWidget(QDialog):
    def __init__(self, palette, parent=None):
        QWidget.__init__(self, parent)
        self.palette = palette
        self.setWindowTitle('Palette')

    def paintEvent(self,e):
        painter= QPainter()
        painter.begin(self)
        self.draw_palette(painter, self.palette)
        painter.end()

    def draw_palette(self, painter, palette_arr):
        color_size = 20
        chunks = [palette_arr[x:x + 10] for x in range(0, len(palette_arr), 10)]
        for i in range(len(chunks)):
            for j in range(len(chunks[i])):
                painter.fillRect(i*color_size, j*color_size, color_size, color_size,
                                 QColor(*chunks[i][j]))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWidget('lena.bmp')
    widget.show()
    app.exec_()
# TODO при нажати кнопки выводить следующее изображение из всех в папке