# Import Numpy functions and supply alternatives if not present
try:
    from numpy import arange, array, ceil, dtype, float64, floor, frombuffer, isnan, log, min_scalar_type, nan, ones, uint8, zeros
except ModuleNotFoundError:
    from math import ceil, floor, log, isnan
    from re import sub

    arange = range
    array = list
    uint8 = int
    float64 = float
    nan = float('nan')
    
    def zeros(size, dtype=int):
        if str(dtype).find('int') > -1:
            dtype = int
        else:
            dtype = float
        return [dtype(0) for i in range(size)]

    def ones(size, dtype=int):
        if str(dtype).find('int') > -1:
            dtype = int
        else:
            dtype = float
        return [dtype(1) for i in range(size)]

    class dtype(object):
        def __init__(self, spec):
            self.type = int
    
    def frombuffer(byte_string, type_spec):
         byte_order = 'big' if sub('[ui\d\s]', '', type_spec) == '>' else 'little'
         byte_width = int(sub('[<>iu\s]', '', type_spec))
         signed     = sub('[<>\d\s]', '', type_spec) == 'i'
         return [int.from_bytes(byte_string[i:i+byte_width], byte_order, signed=signed) for i in range(0, len(byte_string), byte_width)]
    
    class min_scalar_type(object):
        def __init__(self, value):
            self.type = type(value)

# Import Pint functions and supply alternatives if not present
try:
    from metpy.units import units
    Quantity = units.Quantity
except:
    try:
        from pint import Quantity, UnitRegistry

        units = UnitRegistry()
        units.define('percent = 1 / 100 = %')

    except ImportError:
        class UnitRegistry(object):
            def __call__(self, *args, **kwargs):
                raise ImportError("Could not find pint module.")
            def __getattribute__(self, *args, **kwargs):
                self()
            def define(self, *args, **kwargs):
                self()

        class Quantity(object):
            def __init__(self, *args, **kwargs):
                raise ImportError("Could not find pint module.")

        units = UnitRegistry()

# Import Pandas functions and supply alternatives if not present
try:
    from pandas import DataFrame
except ImportError:
    class DataFrame(object):
        def __init__(self, *args, **kwargs):
            raise ImportError("Could not find pandas module.")