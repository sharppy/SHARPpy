# Import Numpy functions and supply alternatives if not present
try:
    from numpy import arange, arctan2, array, ceil, diff, dtype, exp, float64, floor, frombuffer, hypot, isfinite, isnan, log, min_scalar_type, nan, ones, pi, uint8, zeros

    numpy_found = True

    def compare(values, condition, compare_value):
        condition = condition.strip()
        if condition == '==':
            output = values == compare_value
        elif condition == '!=':
            output = values != compare_value
        elif condition == '<':
            output = values < compare_value
        elif condition == '<=':
            output = values <= compare_value
        elif condition == '>':
            output = values > compare_value
        elif condition == '>=':
            output = values >= compare_value
        else:
            raise ValueError('Condition \'{0:s}\' is not a comparison operator'.format(condition))
        return output

    def logical_and(a, b):
        return a & b
    
    def fill_array(shape, value, dtype=uint8):
        return ones(shape) * value

except ModuleNotFoundError:
    from math import atan2 as arctan2, ceil, exp, floor, hypot, log, isfinite, isnan, pi
    from re import sub

    numpy_found = False

    arange = range
    
    uint8 = int
    float64 = float
    nan = float('nan')
    
    def array(values, dtype=None):
        return values

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
    
    def compare(values, condition, compare_value):
        condition = condition.strip()
        if condition == '==':
            output = [value == compare_value for value in values]
        elif condition == '!=':
            output = [value != compare_value for value in values]
        elif condition == '<':
            output = [value < compare_value for value in values]
        elif condition == '<=':
            output = [value <= compare_value for value in values]
        elif condition == '>':
            output = [value > compare_value for value in values]
        elif condition == '>=':
            output = [value >= compare_value for value in values]
        else:
            raise ValueError('Condition \'{0:s}\' is not a comparison operator'.format(condition))
        return output

    def diff(values, n=1, prepend=None):
        if prepend is not None:
            if type(prepend) not in [list, tuple, set]:
                values = [prepend] + values
            else:
                values = prepend + values
        while n > 0:
            values = [values[i] - values[i-1] for i in range(1, len(values))]
            n -= 1
        return values

    def logical_and(a, b):
        return a and b

    def fill_array(shape, value, dtype=None):
        return [value for i in range(shape)]

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