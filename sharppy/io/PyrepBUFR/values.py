from collections.abc import Sequence

from .external import DataFrame, Quantity, units
from .utility import byte_integer, ceil, dict_merge, get_min_type

unit_substituions = {
    'Hour': 'hour',
    'Minute': 'minute',
    'Year': 'year',
    'Month': 'month',
    'Day': 'day',
    'Degree': 'degree',
    'Degree true': 'degree',
    'gpm': 'meter',
    '%': 'percent',
    'PA': 'Pa'
}

class BUFRValueBase(object):
    __slots__ = ()
    @property
    def data(self):
        return None

class BUFRValue(BUFRValueBase):
    __slots__ = ('element', '__bytes__')
    @classmethod
    def create(cls, element):
        return cls(element, None)
    @classmethod
    def create_from_table(cls, table, f, x, y):
        element = table.find(lambda id: id == (f, x, y))
        if element.is_empty:
            raise IndexError('Element f={0}, x={1}, y={2} not found in table.'.format(f,x,y))
        return cls(element.iloc(0), None)
    def __init__(self, element, byte_string):
        self.element = element
        if byte_string is None:
            self.set_missing()
        else:
            self.__bytes__ = byte_string
    @property
    def f(self):
        return self.element.f
    @property
    def x(self):
        return self.element.x
    @property
    def y(self):
        return self.element.y
    @property
    def mnemonic(self):
        return self.element.mnemonic
    @property
    def is_missing(self):
        return sum([2**i for i in range(self.element.bit_width)]).to_bytes(len(self.__bytes__), 'big') == self.__bytes__
    def set_missing(self):
        self.__bytes__ = sum([2**i for i in range(self.element.bit_width)]).to_bytes( int(ceil(self.element.bit_width / 8)) , 'big')
    def __repr__(self):
        return '{0:s} {1:s} {2}'.format(self.__class__.__name__, self.mnemonic, str(self.data).replace('\n', '\\n'))
    @property
    def unit(self):
        return self.element.unit

class BUFRNumeric(BUFRValue):
    @property
    def data(self):
        return_value = None
        if not self.is_missing:
            if self.element.scale == 0:
                return_value = get_min_type(self.element.reference_value + int.from_bytes(self.__bytes__, 'big'))
            else:
                return_value = get_min_type((self.element.reference_value + int.from_bytes(self.__bytes__, 'big')) * 10.0**(-1 * self.element.scale))
        return return_value
    @data.setter
    def data(self, value):
        if self.element.scale == 0:
            value = value - self.element.reference_value
        else:
            value = int(round(value * 10.0**self.element.scale - self.element.reference_value))
        self.__bytes__ = byte_integer(get_min_type(value), self.element.bit_width)
    @property
    def unit(self):
        unit = super().unit
        return units(unit_substituions.get(unit, unit))

class BUFRString(BUFRValue):
    @property
    def data(self):
        return_value = None
        if not self.is_missing:
            return_value = self.__bytes__.decode('utf-8').split('\x00')[0].strip()
        return return_value
    @data.setter
    def data(self, value):
        value = value.encode('ascii') + b'\x00'
        value += ((self.element.bit_width // 8) - len(value)) * b' '
        self.__bytes__ = value
    @property
    def data_raw(self):
        return_value = None
        if not self.is_missing:
            return_value = self.__bytes__.decode('utf-8').split('\x00')[0]
        return return_value

class BUFRLookupTable(BUFRValue):
    __slots__ = ('element', '__bytes__', '__lookup_table__')
    def __init__(self, element, byte_string):
        super().__init__(element, byte_string)
        self.__lookup_table__ = None
    def set_lookup_table(self, codes):
        self.__lookup_table__ = dict([(x.code, x.meaning) for x in codes.values()])
    @property
    def data_raw(self):
        return_value = None
        if not self.is_missing:
            return_value = get_min_type(self.element.reference_value + int.from_bytes(self.__bytes__, 'big'))
        return return_value
    @data_raw.setter
    def data_raw(self, value):
        self.__bytes__ = byte_integer(get_min_type(value - self.element.reference_value), self.element.bit_width)

class BUFRCodeTable(BUFRLookupTable):
    @property
    def data(self):
        meaning = None
        if not self.is_missing and self.__lookup_table__ is not None:
            meaning = self.__lookup_table__.get(self.data_raw, meaning)
        return meaning
    @data.setter
    def data(self, value):
        code_switch = dict([(v, k) for k, v in self.__lookup_table__.items()])
        self.data_raw = code_switch.get(value, sum([2**i for i in range(self.element.bit_width)]))

class BUFRFlagTable(BUFRLookupTable):
    def set_lookup_table(self, codes):
        self.__lookup_table__ = dict([(1 << (self.element.bit_width - x.code), x.meaning) for x in codes.values()])
    @property
    def data(self):
        return_value = None
        if not self.is_missing and self.__lookup_table__ is not None:
            value = self.data_raw
            return_value = [v for k, v in self.__lookup_table__.items() if k & value > 0]
        return return_value
    @data.setter
    def data(self, value):
        flag_switch = dict([(v, k) for k, v in self.__lookup_table__.items()])
        self.data_raw = sum([flag_switch.get(x, 0) for x in value])

class BUFRSequence(list):
    __slots__ = ()

    def __len__(self):
        return sum([len(x) if issubclass(x.__class__, Sequence) else 1 for x in self])

    def __iter__(self):
        for x in super().__iter__():
            if issubclass(x.__class__, BUFRSequence):
                for y in x:
                    yield y
            else:
                yield x

    def __list_iter__(self):
        for x in super().__iter__():
            yield x

    def __list_len__(self):
        return super().__len__()

    def value_record(self, key, filter_keys, use_pint, convert_units):
        for item in self.__list_iter__():
            key_value = key(item.element)
            if filter_keys is None or key_value in filter_keys:
                item_value = item.data
                if not item.is_missing:
                    if item.__class__ == BUFRNumeric and (use_pint or key_value in convert_units):
                        item_value = Quantity(item_value, item.unit)
                    if key_value in convert_units:
                        item_value = item_value.to(convert_units[key_value])
                    if item_value.__class__ == Quantity and not use_pint:
                        item_value = item_value.magnitude
                yield (key_value, item_value)

    def to_dict(self, key=lambda element: element.mnemonic, filter_keys=None, use_pint=False, convert_units={}):
        return dict(self.value_record(key, filter_keys, use_pint, convert_units))

    def to_dataframe(self, key=lambda element: element.mnemonic, filter_keys=None, convert_units={}):
        return DataFrame(self.to_dict(key=key, filter_keys=filter_keys, use_pint=False, convert_units=convert_units))

class BUFRSequenceCollection(BUFRSequence):
    def __group_0__(self, key=lambda element: element.mnemonic, filter_keys=None, use_pint=False, convert_units={}):
        return {}

    def __parts__(self):
        return []

    def to_dict(self, key=lambda element: element.mnemonic, filter_keys=None, use_pint=False, convert_units={}):
        output = []
        group_0 = self.__group_0__(key=key, filter_keys=filter_keys, use_pint=use_pint, convert_units=convert_units)
        for y in self.__parts__():
            if issubclass(y.__class__, BUFRSequenceCollection):
                output.extend([dict_merge(group_0, x) for x in y.to_dict(key=key, filter_keys=filter_keys, use_pint=use_pint, convert_units=convert_units)])
            else:
                output.append(dict_merge(group_0, y.to_dict(key=key, filter_keys=filter_keys, use_pint=use_pint, convert_units=convert_units)))
        if len(output) == 0:
            output.append(group_0)
        return output

class BUFRGroup(BUFRSequenceCollection):
    def __init__(self, *args):
        if len(args) == 0:
            args = [BUFRSequence()]
        super().__init__(args)

    def append(self, value):
        if issubclass(value.__class__, BUFRSequence):
            super().append(value)
        else:
            super().__getitem__(0).append(value)

    @property
    def groups(self):
        return [x for x in super().__list_iter__()]

    @property
    def group_count(self):
        return super().__list_len__()

    def __group_0__(self, key=lambda element: element.mnemonic, filter_keys=None, use_pint=False, convert_units={}):
        return self.groups[0].to_dict(key=key, filter_keys=filter_keys, use_pint=use_pint, convert_units=convert_units)

    def __parts__(self):
        return self.groups[1:]

class BUFRSubset(BUFRGroup):
    __slots__ = ('__conditional_values__', '__table_f__', 'metadata')

    def __init__(self, table_f):
        super().__init__()
        self.__table_f__ = table_f
        self.__conditional_values__ = dict([(id, None) for id in self.__table_f__.conditional_code_flags])
        self.metadata = {}

    def process_value(self, value):
        if issubclass(value.__class__, BUFRSequence):
            for value_part in value:
                self.process_value(value_part)
        else:
            value_id = (value.f, value.x, value.y)
            if issubclass(value.__class__, BUFRLookupTable):
                if value_id in self.__conditional_values__:
                    self.__conditional_values__[value_id] = value.data_raw
                code_flag = self.__table_f__.find(lambda id: id[0:3] == value_id and self.__conditional_values__.get((id.condition_f, id.condition_x, id.condition_y), None) == id.condition_value)
                if len(code_flag) > 0:
                    value.set_lookup_table(code_flag.iloc(0))
            elif value_id in self.__conditional_values__:
                self.__conditional_values__[value_id] = value.data

    def append(self, value):
        self.process_value(value)
        super().append(value)

    def __group_0__(self, key=lambda element: element.mnemonic, filter_keys=None, use_pint=False, convert_units={}):
        return dict([(k, v) for k, v in self.metadata.items() if filter_keys is None or k in filter_keys] + list(super().__group_0__(key, filter_keys, use_pint, convert_units).items()))

class ReplicationGroup(BUFRValueBase, BUFRGroup):
    __slots__ = ('element')
    def __init__(self, element):
        super().__init__()
        self.element = element

class ReplicationSequence(BUFRSequence):
    pass

class MetadataCollection(BUFRSequenceCollection):
    __slots__ = ('metadata')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata = {}

    def __group_0__(self, key=lambda element: element.mnemonic, filter_keys=None, use_pint=False, convert_units={}):
        return dict([(k, v) for k, v in self.metadata.items() if filter_keys is None or k in filter_keys])

    def __parts__(self):
        return self.__list_iter__()

class SubsetCollection(MetadataCollection):
    pass

class MessageCollection(MetadataCollection):
    pass