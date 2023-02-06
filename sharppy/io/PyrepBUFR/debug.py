from textwrap import wrap

def dump_bin(byte_string, bytes_per_line):
    return '\n'.join(wrap(' '.join(['{0:08b}'.format(x) for x in byte_string]), 9*bytes_per_line))
    
def dump_hex(byte_string, bytes_per_line):
    return '\n'.join(wrap(' '.join(['{0:02X}'.format(x) for x in byte_string]), 3*bytes_per_line))
