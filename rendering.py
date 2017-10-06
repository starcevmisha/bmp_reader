from struct import unpack
import bmp_reader
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor
from sys import argv


class Render(QWidget):

    def __init__(self, file, header, info, palette, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.file = file
        self.header = header
        self.info = info
        self.palette = palette
        if info.bit_count == 16 or info.bit_count == 32:
            self.set_masks()
        self.byte_count = self.info.bit_count / 8
        self.initUI()
        self.returned_bits = 0

        self.color_extract_func = {
            1: self.get_less_8_bit_color,
            2: self.get_less_8_bit_color,
            3: self.get_less_8_bit_color,
            4: self.get_less_8_bit_color,
            8: self.get_8_bit_color,
            16: self.get_16_bit_color,
            24: self.get_24_bit_color,
            32: self.get_32_bit_color
        }

    def initUI(self):
        self.resize(450, 350)
        self.setWindowTitle('BMP image')
        self.show()

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        size =1
        for pixel in self.get_pixel(self.file, size):
            (x, y), color = pixel
            painter.fillRect(x, y, size, size, QColor(*color))

        painter.end()

    def set_masks(self):
        f_string = '{:032b}' if self.info.bit_count == 32 else '{:016b}'
        red = f_string.format(self.info.red_mask)
        self.red_left, self.red_right = red.find('1'), red.rfind('1')
        green = f_string.format(self.info.green_mask)
        self.green_left, self.green_right = green.find('1'), green.rfind('1')
        blue = f_string.format(self.info.blue_mask)
        self.blue_left, self.blue_right = blue.find('1'), blue.rfind('1')
        alpha = f_string.format(
            self.info.alpha_mask) if self.info.alpha_mask <= 2 ** self.info.bit_count else '0'
        self.alpha_left, self.alpha_right = alpha.find('1'), alpha.rfind('1')

    def get_pixel(self, file, size):
        offset = self.header.offset
        pixels_readed_in_line = 0
        row_num = self.info.height - 1

        self.get_color = self.color_extract_func[self.info.bit_count]

        while row_num >= 0:
            color, offset = self.get_color(offset)
            pixels_readed_in_line += 1
            x = pixels_readed_in_line*size
            y = row_num*size
            yield (x, y), color
            if pixels_readed_in_line >= self.info.width:  # Прочитали строку
                while (offset - self.header.offset) % 4 != 0:
                    offset += 1
                row_num -= 1
                pixels_readed_in_line = 0
                self.returned_bits = 0

    def get_32_bit_color(self, offset):
        color = self.int_to_rgb(unpack('<I', self.file[offset:offset + 4])[0])
        offset += 4
        return color, offset

    def get_24_bit_color(self, offset):
        blue = unpack('B', self.file[offset:offset + 1])[0]
        green = unpack('B', self.file[offset + 1:offset + 2])[0]
        red = unpack('B', self.file[offset + 2:offset + 3])[0]
        offset += 3
        return (red, green, blue), offset

    def get_16_bit_color(self, offset):
        color = self.int_to_rgb(unpack('<H', self.file[offset:offset + 2])[0])
        offset += 2
        return color, offset

    def get_8_bit_color(self, offset):
        color_num = unpack('B', self.file[offset:offset + 1])[0]
        color = self.palette[color_num]
        offset += 1
        return color, offset

    def get_less_8_bit_color(self, offset):
        if self.returned_bits == 0:
            self.color_bits = \
                '{:08b}'.format(unpack('B', self.file[offset:offset + 1])[0])
            offset+=1

        color_num = int(
            self.color_bits[
                self.returned_bits:self.returned_bits +
                self.info.bit_count],
            2)

        self.returned_bits += self.info.bit_count
        if self.returned_bits == 8:
            self.returned_bits = 0
        return self.palette[color_num], offset


    def int_to_rgb(self, color):
        f_string = '{:032b}' if self.info.bit_count == 32 else '{:016b}'
        red = int(f_string.format(color)[self.red_left:self.red_right + 1], 2)
        green = int(
            f_string.format(color)[
                self.green_left:self.green_right + 1], 2)
        blue = int(
            f_string.format(color)[
                self.blue_left:self.blue_right + 1], 2)
        # int(f_string.format(color)[self.alpha_left:self.alpha_right + 1],2)
        alpha = 255
        return (red, green, blue, alpha)


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
