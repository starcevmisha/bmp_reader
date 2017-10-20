import bmp_reader
import argparse
import sys
from PyQt5.QtWidgets import QApplication
import gui

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, help='file name')
parser.add_argument('-d', '--dir', help='view all files in directory')
parser.add_argument('--gui', action='store_true', help='GUI')
args = parser.parse_args()

if (args.gui):
    app = QApplication(sys.argv)
    widget = gui.MainWidget(args)
    widget.show()
    app.exec_()
elif args.file:
    try:
        with open(args.file, 'rb') as f:
            file = f.read()
    except FileNotFoundError:
        print("No such file")
        sys.exit(85)

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


elif args.dir:
    print("Open directory only in gui mod")
