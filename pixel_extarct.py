from PyQt5.QtCore import QObject, pyqtSignal
from struct import unpack

class Extractor(QObject):
    changedValue = pyqtSignal(int)

    def __init__(self, file, header, info, palette, progress_bar):
        super().__init__()
        self.file = file
        self.header = header
        self.info = info
        self.palette = palette
        if info.bit_count == 16 or info.bit_count == 32:
            self.set_masks()
        self.byte_count = self.info.bit_count / 8
        self.returned_bits = 0
        self.progress_bar = progress_bar

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

    def set_masks(self):
        f_string = '{:032b}' if self.info.bit_count == 32 else '{:016b}'
        red = f_string.format(self.info.red_mask)
        self.red_left, self.red_right = red.find('1'), red.rfind('1')
        green = f_string.format(self.info.green_mask)
        self.green_left, self.green_right = green.find('1'), green.rfind('1')
        blue = f_string.format(self.info.blue_mask)
        self.blue_left, self.blue_right = blue.find('1'), blue.rfind('1')
        alpha = f_string.format(
            self.info.alpha_mask) if self.info.alpha_mask \
            <= 2 ** self.info.bit_count else '0'
        self.alpha_left, self.alpha_right = alpha.find('1'), alpha.rfind('1')

        red_length = len('{:b}'.format(self.info.red_mask).strip('0'))
        green_length = len('{:b}'.format(self.info.green_mask).strip('0'))
        blue_length = len('{:b}'.format(self.info.blue_mask).strip('0'))
        self.alpha_length = len('{:b}'.format(self.info.alpha_mask).strip('0'))

        red_max = 2 ** red_length - 1
        green_max = 2 ** green_length - 1
        blue_max = 2 ** blue_length - 1
        alpha_max = 2 ** self.alpha_length - 1

        self.red_factor = 255 / red_max if red_max != 0 else 1
        self.green_factor = 255 / green_max if green_max != 0 else 1
        self.blue_factor = 255 / blue_max if blue_max != 0 else 1
        self.alpha_factor = 255 / alpha_max if alpha_max != 0 else 1

    def get_pixel(self, size):
        offset = self.header.offset
        pixels_readed_in_line = 0
        self.get_color = self.color_extract_func[self.info.bit_count]

        if self.info.height > 0:
            row_num = self.info.height - 1
            while row_num >= 0:

                color, offset = self.get_color(offset)
                x = pixels_readed_in_line * size
                y = row_num * size
                yield (x, y), color
                pixels_readed_in_line += 1
                if pixels_readed_in_line >= self.info.width:  # Прочиталистрок
                    if row_num%10 == 0:
                        self.changedValue.emit(int(((self.info.height - row_num) /
                                 self.info.height) * 100))
                    while (offset - self.header.offset) % 4 != 0:
                        offset += 1
                    row_num -= 1
                    pixels_readed_in_line = 0
                    self.returned_bits = 0

        else:  # Если перевернуто изображение
            row_num = self.info.height + 1
            while row_num <= 0:
                color, offset = self.get_color(offset)
                pixels_readed_in_line += 1
                x = pixels_readed_in_line * size
                y = (row_num - self.info.height) * size
                yield (x, y), color
                if pixels_readed_in_line >= self.info.width:  # Прочиталистрок
                    if row_num%10 == 0:
                        self.changedValue.emit(row_num)
                    while (offset - self.header.offset) % 4 != 0:
                        offset += 1
                    row_num += 1
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
            offset += 1

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
        bin_string = '{:032b}' if self.info.bit_count == 32 else '{:016b}'

        red_bin = bin_string.format(color)[self.red_left:self.red_right + 1]
        red = int(red_bin, 2) * self.red_factor if red_bin != '' else 0

        green_bin = bin_string.format(color)[
            self.green_left:self.green_right + 1]
        green = int(green_bin, 2) * self.green_factor if green_bin != '' else 0

        blue_bin = bin_string.format(color)[self.blue_left:self.blue_right + 1]
        blue = int(blue_bin, 2) * self.blue_factor if blue_bin != '' else 0

        alpha_bin = bin_string.format(color)[
            self.alpha_left:self.alpha_right + 1]
        if self.alpha_length == 0 or self.alpha_left == - \
                1:  # If alpha mask does not exist
            alpha = 255
        elif alpha_bin.strip('0') == '':  # if alpha does not exist in color
            alpha = 0
        else:
            alpha = int(alpha_bin, 2) * self.alpha_factor
        return (red, green, blue, alpha)
