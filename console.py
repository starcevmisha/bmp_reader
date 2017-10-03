import bmp_reader
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('name', type=str, help='file name')
args = parser.parse_args()


with open(args.name, 'rb') as f:
    file = f.read()
    reader = bmp_reader.Reader()
    reader.check_file_type(file)
    header = reader.read_header(file)
    print('BitmapFileHeader')
    for i in header:
        print(' '*4 + i)
    info = reader.read_info(file, header.version)
    print("\nBitmapInfoHeader")
    for i in info:
        print(' '*4 + i)