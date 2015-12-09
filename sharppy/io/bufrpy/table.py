from libbufr import read_tables
from os.path import dirname, join
from codecs import open as codec_open

def get_table():
    with codec_open(join(dirname( __file__ ), 'b_table'), 'rb', 'utf-8') as b_file:
        with codec_open(join(dirname( __file__ ), 'd_table'), 'rb', 'utf-8') as d_file:
            return read_tables(b_file, d_file)