from struct import unpack


class RLEExtractor:

    def __init__(self, file, header, info, palette):
        self.file = file
        self.header = header
        self.info = info
        self.palette = palette
        self.cases = {
            0: self.next_row,
            1: self.end_of_image,
            2: self.shift
        }

    def get_pixel(self, size):
        offset = self.header.offset
        local_offset = 0
        row_num = self.info.height-1

        while row_num >= 0:
            if offset % 2 != 0:
                offset += 1

            first = unpack('B', self.file[offset:offset + 1])[0]
            if first == 0:
                second = unpack('B', self.file[offset + 1:offset + 2])[0]
                if second in self.cases.keys():
                    offset, local_offset, row_num = self.cases[
                        second](offset, local_offset, row_num)

                else:
                    pixels_count = 0
                    for i in range(second):
                        if pixels_count >= second or local_offset > self.info.width:
                            break
                        raw_color = unpack('B', self.file[offset + 2:offset + 3])[0]
                        colors = self.extract_colors(raw_color)
                        for color in colors:
                            if pixels_count >= second:
                                break
                            x = local_offset * size
                            y = row_num * size
                            yield (x, y), self.palette[color]
                            local_offset += 1
                            pixels_count += 1
                        offset += 1
                    offset += 2

            else:

                pixels_count = 0
                raw_color = unpack('B', self.file[offset + 1:offset + 2])[0]
                colors = self.extract_colors(raw_color)
                flag = False
                for i in range(first):
                    if flag == False:
                        for color in colors:
                            if pixels_count >= first or local_offset > self.info.width:
                                flag= True
                                break
                            x = local_offset * size
                            y = row_num * size
                            yield (x, y), self.palette[color]
                            pixels_count += 1
                            local_offset += 1
                offset += 2

    def next_row(self, offset, local_offset, row_num):
        offset += 2
        local_offset = 0
        row_num -= 1
        return offset, local_offset, row_num

    def end_of_image(self,offset, local_offset, row_num):
        raise StopIteration

    def shift(self, offset, local_offset, row_num):
        x_offset = unpack('B', self.file[offset + 2:offset + 3])[0]
        y_offset = unpack('B', self.file[offset + 3:offset + 4])[0]
        local_offset += x_offset
        row_num -= y_offset
        offset += 4
        return offset, local_offset, row_num

    def extract_colors(self, raw_color):
        if self.info.bit_count == 4:
            first_color = raw_color >> 4
            second_color = raw_color & 0x0f
            return [first_color, second_color]
        return [raw_color]
