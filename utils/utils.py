
import sys

def is_py3():
    return sys.version_info[0] == 3

def total_seconds(td):
    return td.days * 3600 * 24 + td.seconds + td.microseconds * 1e-6
