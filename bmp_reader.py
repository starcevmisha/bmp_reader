from struct import unpack, pack

versions = {
    12: 'CORE',
    40: 3,
    108: 4,
    124: 5
}


class FileHeader:

    def __init__(self, size, reserved1, reserved2, offset, version):
        self.size = size
        self.reserved1 = reserved1
        self.reserved2 = reserved2
        self.offset = offset
        self.version = version

    def __iter__(self):
        yield "bfSize: {} byte".format(self.size)
        yield "bfReserved1: {}".format(self.reserved1)
        yield "bfReserved2: {}".format(self.reserved2)
        yield "bfOffBits: {} byte".format(self.offset)
        # yield "Version: {}".format(self.version)


class BitmapCoreHeader:

    def __init__(self):
        self.version = ''
        self.size = 0
        self.width = 0
        self.height = 0
        self.planes_count = 0
        self.bit_count = 0

    def __iter__(self):
        yield "Version: {}".format(self.version)
        yield "biSize: {} byte".format(self.size)
        yield "Width: {} px".format(self.width)
        yield "Height: {} px".format(self.height)
        yield "Planes count: {}".format(self.planes_count)
        yield "Bit per pixel: {}".format(self.bit_count)


class BitmapV3Header(BitmapCoreHeader):

    def __init__(self):
        super().__init__()
        self.offset = 0x36
        self.bit_count = 0
        self.compression = 0
        self.size_image = 0
        self.x_pels_per_meter = 0
        self.y_pels_per_meter = 0
        self.clr_used = 0
        self.clr_important = 0
        self.red_mask = None
        self.green_mask = None
        self.blue_mask = None
        self.alpha_mask = None

    @property
    def clr_used(self):
        return self._clr_used

    @clr_used.setter
    def clr_used(self, value):
        self._clr_used = value if value != 0 or self.bit_count > 8 else 2 ** self.bit_count

    def set_default_masks(self):
        if self.bit_count == 16:
            self.red_mask = 31744
            self.green_mask = 992
            self.blue_mask = 31
            self.alpha_mask = 0
        elif self.bit_count == 32:
            self.red_mask = 0x00ff0000
            self.green_mask = 0x0000ff00
            self.blue_mask = 0x000000ff
            self.alpha_mask = 0x00000000

    def __iter__(self):
        for i in super().__iter__():
            yield i
        yield "Compression: {}".format(self.compression)
        yield "Image Size: {} byte".format(self.size_image)
        yield "X pixels per meter: {}".format(self.x_pels_per_meter)
        yield "Y pixels per meter: {}".format(self.y_pels_per_meter)
        yield "Colors in BitMap: {}".format(self.clr_used)
        yield "Used Colors: {}".format(self.clr_important)
        if self.bit_count == 16 or self.bit_count == 32:
            yield "RedMask:   {}".format(pack('>I', self.red_mask).hex())
            yield "GreenMask: {}".format(pack('>I', self.green_mask).hex())
            yield "BlueMask:  {}".format(pack('>I', self.blue_mask).hex())
            yield "AlphaMask: {}".format(pack('>I', self.alpha_mask).hex())


class BitmapV4Header(BitmapV3Header):

    def __init__(self):
        super().__init__()
        self.cs_type = 0
        self.endpoints = 0
        self.gamma_red = 0
        self.gamma_green = 0
        self.gamma_blue = 0

    def __iter__(self):
        for i in super().__iter__():
            yield i
        yield "CS Type:   {}".format(self.cs_type)


class BitmapV5Header(BitmapV4Header):

    def __init__(self):
        super().__init__()
        self.intent = 0
        self.profile_data = 0
        self.profile_size = 0

    def __iter__(self):
        for i in super().__iter__():
            yield i
        yield "Intent: {}".format(self.intent)
        yield "Profile data: {}".format(self.profile_data)
        yield "Profile size: {}".format(self.profile_size)


class Reader:

    def check_file_type(self, file):
        if file[:2] != b'\x42\x4d':
            raise TypeError("It is not a BMP file")

    def read_header(self, file):
        size = unpack('<I', file[0x2:0x6])[0]
        reserved1 = unpack('<H', file[0x6:0x8])[0]
        reserved2 = unpack('<H', file[0x8:0xa])[0]
        offset = unpack('<I', file[0xa:0xa + 4])[0]
        version_size = unpack('<I', file[0xe:0xe + 4])[0]
        version = versions.get(version_size, 'Invalid Type')
        return FileHeader(size, reserved1, reserved2, offset, version)

    def read_info(self, file, version):
        read_version = {
            "CORE": self.read_core,
            3: self.read_v3,
            4: self.read_v4,
            5: self.read_v5
        }
        return read_version[version](file)

    def read_core(self, file):
        info = BitmapCoreHeader()
        info.version = 'Core'
        info.size = unpack('<I', file[0xe:0xe + 4])[0]
        info.width = unpack('<H', file[0x12:0x12 + 2])[0]
        info.height = unpack('<H', file[0x14:0x14 + 2])[0]
        info.planes_count = unpack('<H', file[0x16:0x16 + 2])[0]
        info.bit_count = unpack('<H', file[0x18:0x18 + 2])[0]
        return info

    def read_v3(self, file, info=None):
        if info is None:
            info = BitmapV3Header()
            info.version = 3
        info.size = unpack('<I', file[0xe:0xe + 4])[0]
        info.width = unpack('<i', file[0x12:0x12 + 4])[0]
        info.height = unpack('<i', file[0x16:0x16 + 4])[0]
        info.planes = unpack('<H', file[0x1a:0x1a + 2])[0]
        info.bit_count = unpack('<H', file[0x1c:0x1c + 2])[0]
        info.set_default_masks()
        info.compression = unpack('<I', file[0x1e:0x1e + 4])[0]
        info.size_image = unpack('<I', file[0x22:0x22 + 4])[0]
        info.x_pels_per_meter = unpack('<i', file[0x26:0x26 + 4])[0]
        info.y_pels_per_meter = unpack('<i', file[0x2a:0x2a + 4])[0]
        info.clr_used = unpack('<I', file[0x2e:0x2e + 4])[0]
        info.clr_important = unpack('<I', file[0x32:0x32 + 4])[0]
        if (info.compression == 3 or info.compression == 6):
            info.red_mask = unpack('<I', file[0x36:0x36 + 4])[0]
            info.green_mask = unpack('<I', file[0x3a:0x3a + 4])[0]
            info.blue_mask = unpack('<I', file[0x3e:0x3e + 4])[0]
            info.alpha_mask = unpack('<I', file[0x42:0x42 + 4])[0]
        return info

    def read_v4(self, file, info=None):
        if info is None:
            info = BitmapV4Header()
            info.version = 4
        info = self.read_v3(file, info)
        info.red_mask = unpack('<I', file[0x36:0x36 + 4])[0]
        info.green_mask = unpack('<I', file[0x3a:0x3a + 4])[0]
        info.blue_mask = unpack('<I', file[0x3e:0x3e + 4])[0]
        info.alpha_mask = unpack('<I', file[0x42:0x42 + 4])[0]
        info.cs_type = pack('>I', unpack('<I', file[0x46:0x46 + 4])[0])
        if info.cs_type == b'\x00\x00\x00\x00':
            info.endpoints = file[0x4a:0x4a + 36]
            info.gamma_red = unpack('<I', file[0x6e:0x6e + 4])[0]
            info.gamma_green = unpack('<I', file[0x72:0x72 + 4])[0]
            info.gamma_blue = unpack('<I', file[0x76:0x76 + 4])[0]
        return info

    def read_v5(self, file):
        info = BitmapV5Header()
        info = self.read_v4(file, info)
        info.version = 5
        info.intent = unpack('<I', file[0x7a:0x7a + 4])[0]
        info.profile_data = unpack('<I', file[0x7e:0x7e + 4])[0]
        info.profile_size = unpack('<I', file[0x82:0x82 + 4])[0]
        info.reserved = unpack('<I', file[0x86:0x86 + 4])[0]
        return info

    def read_pallete(self, file, info):
        start_pos = 0
        if (info.version == 'CORE'):
            start_pos = 0x1a
        if(info.version == 3):
            if info.compression == 3:
                start_pos = 0x42
            elif info.compression == 6:
                start_pos = 0x46
            else:
                start_pos = 0x36
        elif info.version == 4:
            start_pos = 0x7a
        elif info.version == 5:
            start_pos = 0x8a

        # TODO сделать таблицу цветов и потом считывать Массив
        palette = []
        for index in range(info.clr_used):
            start_pos = start_pos + index * 4
            color = file[start_pos:start_pos + 4][::-1]
            red = color[1]
            green = color[2]
            blue = color[3]
            palette.append((red, green, blue))
        return palette

