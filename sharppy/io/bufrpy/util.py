from itertools import islice

class ByteStream(object):
    """
    Stream of bytes, represented as length-1 (byte) strings
    """
    def __init__(self, filelike):
        self.f = filelike

    def __iter__(self):
        return self

    def next(self):
        d = self.f.read(1)
        if len(d):
            return d
        else:
            raise StopIteration

    __next__ = next

class ReadableStream(object):
    """Wrapper for ByteStream with additional operations for reading
    structures such as strings and variable-width integers.
    """
    def __init__(self, stream):
        self.stream = stream

    def readstr(self, n):
        """ Read n bytes as CCITT IA5 String """
        # TODO CCITT IA5 rather than ISO-8859-1
        res = b"".join(islice(self.stream, n)).decode('iso-8859-1')
        if len(res) == n:
            return res
        else:
            raise IOError("Premature end of stream")

    def readbytes(self, n):
        """ Read n bytes as list of ints """
        res = list(ord(x) for x in islice(self.stream, n))
        if len(res) == n:
            return res
        else:
            raise IOError("Premature end of stream")

    def readint(self, n):
        """ Read n-byte big-endian integer """
        bytes = list(islice(self.stream, n))
        if len(bytes) == n:
            return sum([ord(x) << 8*i for (i,x) in enumerate(reversed(bytes))])
        else:
            raise IOError("Premature end of stream")

def slices(s, slicing):
    """
    Slice object into segments of given length.

    e.g. slices("001007",[1,2,3]) => ["0","01","007"]
    """
    position = 0
    out = []
    for length in slicing:
        out.append(s[position:position + length])
        position += length
    return out

def fxy(fxy_code):
    """
    Convert FXY code to FXY triplet.

    "fxxyyy" -> int(f),int(xx),int(yyy)
    e.g. fxy("001007") == 0,1,7

    :param str fxy_code: FXY code as string
    :return: F,X,Y triplet
    :rtype: tuple
    """
    return map(int, slices(fxy_code, [1,2,3]))

def fxy2int(fxy_code):
    """
    Convert FXY code to FXY integer.

    "fxxyyy" -> int(f),int(xx),int(yyy) -> (f << 14 + xx << 8 + yyy)
    e.g. "001007" -> 0,1,7 -> (0 << 14 + 1 << 6 + 7) = 263
   
    :param str fxy_code: FXY code as string
    :return: FXY integer
    :rtype: int
    """
    f,x,y = fxy(fxy_code)
    return (f << 14) + (x << 8) + y

def int2fxy(code):
    """
    Convert FXY integer to FXY code.

    Inverse of fxy2int.
    :param int code: FXY integer
    :return: FXY code
    :rtype: int
    """
    f = code >> 14 & 0x3
    x = code >> 8 & 0x3f
    y = code & 0xff
    return "%d%02d%03d" %(f,x,y)
