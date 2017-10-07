import bmp_reader
import argparse
import sys
from PyQt5.QtWidgets import QApplication
import gui

parser = argparse.ArgumentParser()
parser.add_argument('name', type=str, help='file name')
parser.add_argument('--gui', action='store_true', help='GUI')
args = parser.parse_args()

if (args.gui):
    app = QApplication(sys.argv)
    widget = gui.MainWidget(args.name)
    widget.show()
    app.exec_()
else:
    with open(args.name, 'rb') as f:
        file = f.read()
        reader = bmp_reader.Reader()
        reader.check_file_type(file)
        header = reader.read_header(file)
        print('BitmapFileHeader')
        for i in header:
            print(' ' * 4 + i)
        info = reader.read_info(file, header.version)
        print("\nBitmapInfoHeader")
        for i in info:
            print(' ' * 4 + i)

    a = reader.read_pallete(file, info)
