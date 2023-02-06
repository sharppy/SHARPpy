from bz2 import BZ2File
from collections import namedtuple
from copy import deepcopy
from re import split
from sys import modules
from typing import Any
from xml.dom.minidom import parseString
from xml.etree import ElementTree as ET, ElementInclude

from ..external import dtype, array
from ..values import *

def parse_int(value, byte_width, big_endian=True, unsigned=True):
    return dtype(('u' if unsigned else 'i') + str(byte_width)).type(value) if value is not None else None

wmo_field_names = {
    'CodeFigure': 'code',
    'Meaning_en': 'meaning'
}

def obj2dict(obj, element_class):
    if obj.__element_name__ not in element_class.__child_types__:
        raise ValueError('Type "{0}" cannot be added to type "{1}"'.format(obj.__element_name__, element_class.__name__))
    return (obj.id, obj)

def xml2class(node: ET.Element) -> Any:
    cls = getattr(modules[__name__], node.tag)
    return cls.from_xml(node)

def read_xml(filename: str, decompress_input:bool=False) -> Any:
    if decompress_input:
        filename = BZ2File(filename, 'r')
    tree = ET.parse(filename)
    root = tree.getroot()
    ElementInclude.include(root)
    return xml2class(root)

def write_xml(xml_tree: Any, filename: str, compress_output:bool=False) -> None:
    if compress_output:
        out_file = BZ2File(filename, 'w')
    else:
        if type(filename) == str:
            out_file = open(filename, 'wb')
        else:
            out_file = filename
    out_file.write(xml_tree.to_xml().encode('utf-8'))
    out_file.close()

class BUFRTableObjectBase(object):
    __slots__ = ()
    __id_class__ = None
    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            if 'id' not in self.__slots__ or __name not in self.id._fields:
                raise
            return self.id.__getattribute__(__name)
    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == 'id':
            raise AttributeError('Cannot set attribute {0:s}'.format(__name))
        return super().__setattr__(__name, __value)
    def __initialize_id__(self, id):
        if type(id) != self.__id_class__:
            raise ValueError('ID must be class {0}'.format(self.__id_class__))
        super().__setattr__('id', id)
    def __repr__(self):
        value_format = lambda a: ('"{0}"' if type(a) == str else '{0}').format(a)
        return super().__repr__() if self.is_container else '{0:s}({1:s})'.format(self.__class__.__name__, ', '.join(['{0:s}={1:s}'.format(x, value_format(getattr(self, x, None))) for x in (list(self.id._fields) + list(self.__slots__[1:]))]))
    @property
    def __element_name__(self):
        return self.__class__.__name__
    @property
    def is_container(self):
        return issubclass(self.__class__, dict)
    @staticmethod
    def __clone_class__(obj, *args, **kwargs):
        class_args = []
        slot_offset = 0
        if 'id' in obj.__slots__:
            class_args.extend(obj.id)
            slot_offset = 1
        if len(obj.__slots__) - slot_offset > 0:
            class_args.extend([getattr(obj, x, None) for x in  obj.__slots__[slot_offset:]])
        class_args.extend(args)
        return obj.__class__(*class_args, **kwargs)
    def to_element(self):
        elm = ET.Element(self.__element_name__)
        slot_offset = 0
        if 'id' in self.__slots__:
            for attribute, value in self.id._asdict().items():
                if value is not None:
                    elm.set(attribute.replace('_', '-'), str(value))
            slot_offset = 1
        if len(self.__slots__) - slot_offset > 0:
            for attribute in self.__slots__[slot_offset:]:
                value = getattr(self, attribute, None)
                if value is not None:
                    elm.set(attribute.replace('_', '-'), str(value))
        if self.is_container:
            for child in sorted(self, key=lambda a: tuple([x for x in a if x is not None])):
                elm.append(self[child].to_element())
        return elm
    def to_xml(self):
        return parseString(ET.tostring(self.to_element())).toprettyxml()
    def diff(self, other):
        if self.__class__ != other.__class__:
            raise TypeError('Types must match for diff')
        if self.is_container:
            self_set = frozenset(self.keys())
            other_set = frozenset(other.keys())
            missing_set = other_set.difference(self_set)
            non_match_set = frozenset([key for key in other_set.intersection(self_set) if other[key] != self[key]])
            content = [(key, other[key]) for key in missing_set]
            content.extend([(key, other[key]) if not other[key].is_container else (key, self[key].diff(other[key])) for key in non_match_set])
            return BUFRTableObjectBase.__clone_class__(other, content)
        else:
            return self == other
    def __eq__(self, other):
        return  self.__class__ == other.__class__
    def __ne__(self, other):
        return not self == other
    def __deepcopy__(self, memo):
        class_args = list(self.id) + [getattr(self, x, None) for x in  self.__slots__[1:]] 
        if self.is_container:
            class_args += [[obj2dict(deepcopy(value), self.__class__) for value in self.values()]]
        return self.__class__(*class_args)

class BUFRTableContainerBase(dict):
    __slots__ = ()
    __child_types__ = ()
    def __hash__(self):
        return hash(self.id)
    def __add__(self, b):
        self.extend(b)
        return self
    def extend(self, item):
        if self.__element_name__ == item.__element_name__:
            self.update(item)
        elif item.__element_name__ in self.__child_types__:
            self.append(item)
        else:
            raise ValueError('Type "{0:s}" cannot be added to type "{1:s}"'.format(item.__element_name__, self.__element_name__))
    def append(self, item):
        if item.__element_name__ not in self.__child_types__:
            raise ValueError('Type "{0:s}" cannot be added to type "{1:s}"'.format(item.__element_name__, self.__element_name__))
        self[item.id] = item
    def iloc(self, index):
        return self[sorted(self.keys())[index]]
    def find(self, search_func):
        return BUFRTableObjectBase.__clone_class__(self, [(key, self[key]) for key in self if search_func(key)])
    @property
    def is_empty(self):
        return len(self) == 0

class TableCollection(BUFRTableObjectBase, BUFRTableContainerBase):
    __child_types__ = ('Table', )
    def __eq__(self, other):
        match = super().__eq__(other)
        if match:
            self_keys = set(self.keys())
            other_keys = set(other.keys())
            match = self_keys == other_keys
            if match:
                match = min([self[key] == other[key] for key in self_keys])
        return match
    @staticmethod
    def from_xml(elm):
        return TableCollection(
            [obj2dict(xml2class(child), TableCollection) for child in elm]
        )
    def construct_table_version(self, table_type, table_version, master_table=None, originating_center=None):
        table = Table.create(table_type, master_table, originating_center, table_version)
        for table_content in sorted(self.find(lambda id: id.table_type==table_type and id.master_table==master_table and id.originating_center==originating_center and id.table_version>=table_version).values(), key=lambda a: a.id.table_version, reverse=True):
            for item in table_content.values():
                if item.id in table and item.is_container:
                    table[item.id].extend(item)
                else:
                    table.extend(item)
        return table

    def dynamic_table(self, table_type):
        table_type = '{0:s}X'.format(table_type)
        tables = self.find(lambda id: id.table_type==table_type and id.master_table==None and id.originating_center==None and id.table_version>=0)
        if not tables.is_empty:
            table = tables.iloc(0)
        else:
            table = Table.create(table_type, None, None, 1e3)
            self.append(table)
        return table

class Table(BUFRTableObjectBase, BUFRTableContainerBase):
    __slots__ = ('id',)
    __id_class__ = namedtuple('TableID', 
                              ('table_type', 'master_table', 'originating_center', 'table_version'),
                              defaults=(None, None, None, None))
    __child_types__ = ('BUFRDataType', 'CodeFlagDefinition', 'ElementDefinition', 'SequenceDefinition')
    @staticmethod
    def create(table_type, master_table, originating_center, table_version, *args, **kwargs):
        cls = getattr(modules[__name__], 'Table' + table_type.upper(), Table)
        return cls(table_type, master_table, originating_center, table_version, *args, **kwargs)
    def __init__(self, table_type, master_table, originating_center, table_version, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().__initialize_id__(self.__id_class__(
            table_type=table_type,
            master_table=parse_int(master_table, 1),
            originating_center=parse_int(originating_center, 2),
            table_version=parse_int(table_version, 1)
        ))
    @property
    def __element_name__(self):
        return 'Table'
    @staticmethod
    def from_xml(elm):
        return Table.create(
            elm.attrib.get('table-type', None),
            elm.attrib.get('master-table', None),
            elm.attrib.get('originating-center', None),
            elm.attrib.get('table-version', None),
            [obj2dict(xml2class(child), Table) for child in elm]
        )
    def __eq__(self, other):
        match = super().__eq__(other)
        if match:
            self_keys = set(self.keys())
            other_keys = set(other.keys())
            match = self_keys == other_keys
            if match:
                match = min([self[key] == other[key] for key in self_keys]) and other.id == self.id
        return match

class TableF(Table):
    @property
    def conditional_code_flags(self):
        output_set = set()
        for id in self:
            if id.condition_f is not None and id.condition_x is not None and id.condition_y is not None and id.condition_value is not None:
                output_set.update((ElementDefinition.__id_class__(id.condition_f, id.condition_x, id.condition_y),))
        return list(sorted(output_set))

class BUFRDataType(BUFRTableObjectBase):
    __slots__ = ('id', 'description')
    __id_class__ = namedtuple('BUFRDataTypeID', ('code'))
    def __init__(self, code, description):
        super().__initialize_id__(self.__id_class__(parse_int(code, 1)))
        self.description = description
    @staticmethod
    def from_xml(elm):
        return BUFRDataType(
            elm.attrib.get('code', None),
            elm.attrib.get('description', None)
        )
    def __eq__(self, other):
        match = super().__eq__(other)
        if match:
            match = (self.id == other.id
                 and self.description == other.description)
        return match

class ElementDefinition(BUFRTableObjectBase):
    __slots__ = ('id', 'scale', 'reference_value', 'bit_width', 'unit', 'mnemonic', 'name')
    __id_class__ = namedtuple('ElementDefinitionID', ('f', 'x', 'y'))

    def __init__(self, f, x, y, scale, reference_value, bit_width, unit, mnemonic, name):
        super().__initialize_id__(self.__id_class__(
            f=parse_int(f, 1), 
            x=parse_int(x, 1), 
            y=parse_int(y, 1)
        ))
        self.scale = parse_int(scale, 1, unsigned=False)
        self.reference_value = parse_int(reference_value, 4, unsigned=False)
        self.bit_width = parse_int(bit_width, 2)
        self.unit = unit
        self.mnemonic = mnemonic
        self.name = name
    def __eq__(self, other):
        match = super().__eq__(other)
        if match:
            match = (self.id == other.id
                 and self.scale == other.scale
                 and self.reference_value == other.reference_value
                 and self.bit_width == other.bit_width
                 and self.unit == other.unit
                 and self.mnemonic == other.mnemonic)
        return match
    @staticmethod
    def from_xml(elm):
        return ElementDefinition(
            elm.attrib.get('f', None),
            elm.attrib.get('x', None),
            elm.attrib.get('y', None),
            elm.attrib.get('scale', None),
            elm.attrib.get('reference-value', None),
            elm.attrib.get('bit-width', None),
            elm.attrib.get('unit', None),
            elm.attrib.get('mnemonic', None),
            elm.attrib.get('name', None)
        )
    def __str__(self):
        return '{0:01d}-{1:02d}-{2:03d}'.format(*self.id)
    def read_value(self, bit_map):
        data_bytes = bit_map.read(self.bit_width)
        if self.unit == "CCITT IA5":
            data_value = BUFRString(self, data_bytes)
        elif self.unit == "Code table":
            data_value = BUFRCodeTable(self, data_bytes)
        elif self.unit == "Flag table":
            data_value = BUFRFlagTable(self, data_bytes)
        else:
            data_value = BUFRNumeric(self, data_bytes)
        return data_value

class SequenceDefinition(BUFRTableObjectBase, BUFRTableContainerBase):
    __slots__ = ('id', 'mnemonic', 'name')
    __id_class__ = namedtuple('SequenceDefinitionID', ('f', 'x', 'y'))
    __child_types__ = ('SequenceElement', )
    def __init__(self, f, x, y, mnemonic, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().__initialize_id__(self.__id_class__(
            f=parse_int(f, 1),
            x=parse_int(x, 1),
            y=parse_int(y, 1)
        ))
        self.mnemonic = mnemonic
        self.name = name
    @staticmethod
    def from_xml(elm):
        return SequenceDefinition(
            elm.attrib.get('f', None),
            elm.attrib.get('x', None),
            elm.attrib.get('y', None),
            elm.attrib.get('mnemonic', None),
            elm.attrib.get('name', None),
            [obj2dict(xml2class(child), SequenceDefinition) for child in elm]
        )
    def __eq__(self, other):
        match = super().__eq__(other)
        if match:
            self_keys = set(self.keys())
            other_keys = set(other.keys())
            match = self_keys == other_keys
            if match:
                match = min([self[key] == other[key] for key in self_keys]) and other.id == self.id
        return match
    def get_descriptors(self):
        return array([array((item.f, item.x, item.y)) for item in self.values()])

class SequenceElement(BUFRTableObjectBase):
    __slots__ = ('id', 'f', 'x', 'y', 'name')
    __id_class__ = namedtuple('SequenceElementID', ('index'))
    def __init__(self, index, f, x, y, name):
        super().__initialize_id__(self.__id_class__(parse_int(index, 2)))
        self.f = parse_int(f, 1)
        self.x = parse_int(x, 1)
        self.y = parse_int(y, 1)
        self.name = name
    def __eq__(self, other):
        match = super().__eq__(other)
        if match:
            match = (self.id == other.id
                 and self.f == other.f
                 and self.x == other.x
                 and self.y == other.y)
        return match
    @staticmethod
    def from_xml(elm):
        return SequenceElement(
            elm.attrib.get('index', None),
            elm.attrib.get('f', None),
            elm.attrib.get('x', None),
            elm.attrib.get('y', None),
            elm.attrib.get('name', None)
        )

class CodeFlagDefinition(BUFRTableObjectBase, BUFRTableContainerBase):
    __slots__ = ('id','mnemonic')
    __id_class__ = namedtuple('CodeFlagDefinitionID', ('f', 'x', 'y', 'is_flag', 'condition_f', 'condition_x', 'condition_y', 'condition_value'))
    __child_types__ = ('CodeFlagElement', )
    def __init__(self, f, x, y, is_flag, condition_f, condition_x, condition_y, condition_value, mnemonic, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().__initialize_id__(self.__id_class__(
            f=parse_int(f, 1),
            x=parse_int(x, 1),
            y=parse_int(y, 1),
            is_flag=bool(is_flag) if is_flag is not None else None,
            condition_f=parse_int(condition_f, 1),
            condition_x=parse_int(condition_x, 1),
            condition_y=parse_int(condition_y, 1),
            condition_value=parse_int(condition_value, 4)
        ))
        self.mnemonic = mnemonic
    @staticmethod
    def from_xml(elm):
        return CodeFlagDefinition(
            elm.attrib.get('f', None),
            elm.attrib.get('x', None),
            elm.attrib.get('y', None),
            elm.attrib.get('is-flag', None),
            elm.attrib.get('condition-f', None),
            elm.attrib.get('condition-x', None),
            elm.attrib.get('condition-y', None),
            elm.attrib.get('condition-value', None),
            elm.attrib.get('mnemonic', None),
            [obj2dict(xml2class(child), CodeFlagDefinition) for child in elm]
        )
    def __eq__(self, other):
        match = super().__eq__(other)
        if match:
            self_keys = set(self.keys())
            other_keys = set(other.keys())
            match = self_keys <= other_keys and other.id == self.id
            if match:
                match = min([self[key] == other[key] for key in self_keys]) 
        return match

class CodeFlagElement(BUFRTableObjectBase):
    __slots__ = ('id', 'meaning')
    __id_class__ = namedtuple('CodeFlagElementID', ('code'))
    def __init__(self, code, meaning):
        super().__initialize_id__(self.__id_class__(
            parse_int(code, 4)
        ))
        self.meaning = meaning
    def __eq__(self, other):
        match = super().__eq__(other)
        if match:
            match = (self.id == other.id
                 and self.meaning.lower().strip() == other.meaning.lower().strip())
        return match
    @staticmethod
    def from_xml(elm):
        return CodeFlagElement(
            elm.attrib.get('code', None),
            elm.attrib.get('meaning', None)
        )

def convert_wmo_table(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    table = Table.create('A', 0, None, 0)
    for child in root:
        if child.tag == 'BUFR_TableA_en':
            kwargs = dict([(wmo_field_names[field.tag], field.text) for field in child if field.tag in wmo_field_names])
            if kwargs['code'].find('-') < 0:
                kwargs['code'] = [int(kwargs['code']), int(kwargs['code'])]
            else:
                kwargs['code'] = [int(x) for x in kwargs['code'].split('-')]
            for i in range(int(kwargs['code'][0]), int(kwargs['code'][1])+1):
                kwargs['code'] = i
                table.append(BUFRDataType(
                    kwargs['code'],
                    kwargs['meaning']
                ))
    return table

def convert_ncep_table(filename):
    table = None
    with open(filename, 'r') as in_file:
        line = in_file.readline().strip()
        while line != 'END':
            if line != '' and line[0] != '#':
                if len(line) > 5 and line[0:5] == 'Table':
                    table_type = line[6]
                    id = [int(x) for x in  split(r'\s*\|\s*', line[line.find('|')+1:].strip())]
                    if len(id) == 2:
                        master_table, table_version = id
                        originating_center = None
                    elif len(id) == 3:
                        master_table, originating_center, table_version = id
                    table = Table.create(table_type=table_type, master_table=master_table, originating_center=originating_center, table_version=table_version)
                    if table.table_type == 'B':
                        convert_ncep_B_table(in_file, table)
                        break
                    elif table.table_type == 'D':
                        convert_ncep_D_table(in_file, table)
                        break
                    elif table.table_type == 'F':
                        convert_ncep_F_table(in_file, table)
                        break
            line = in_file.readline().strip()
    return table

def convert_ncep_B_table(in_file, table):
    line = in_file.readline().strip()
    while line != 'END':
        if line != '' and line[0] != '#':
            parts = split(r'\s*\|\s*', line.strip())
            parts[0] = [int(x) for x in parts[0].strip().split('-')]
            parts[1:4] = [int(x.strip()) for x in parts[1:4]]
            parts[4] = parts[4].strip()
            parts[5] = [x.strip() for x in parts[5].strip().split(';')]
            table.append(ElementDefinition(
                parts[0][0],
                parts[0][1],
                parts[0][2],
                parts[1],
                parts[2],
                parts[3],
                parts[4],
                parts[5][0],
                parts[5][2]
            ))
        line = in_file.readline().strip()

def convert_ncep_D_table(in_file, table):
    index = 0
    line = in_file.readline().strip()
    sequence = None
    while line != 'END':
        if line != '' and line[0] != '#':
            parts = split(r'\s*\|\s*', line.strip())
            if len(parts[0]) > 0:
                parts[0] = [int(x) for x in parts[0].strip().split('-')]
                parts[1] = [x.strip() for x in parts[1].strip().split(';')]
                if sequence is not None:
                    table.append(sequence)
                sequence = SequenceDefinition(
                    parts[0][0],
                    parts[0][1],
                    parts[0][2],
                    parts[1][0],
                    parts[1][2],
                )
                index = 0
            else:
                parts[1] = [int(x) for x in parts[1].replace('>','').strip().split('-')]
                index += 1
                sequence.append(SequenceElement(index,
                                                parts[1][0],
                                                parts[1][1],
                                                parts[1][2],
                                                parts[2].strip()))
        line = in_file.readline().strip()
    table.append(sequence)

def convert_ncep_F_table(in_file, table):
    line = in_file.readline().strip()
    f = x = y =  None
    conditional_ids = []
    conditional_values = []
    codes = []
    while line != 'END':
        if line != '' and line[0] != '#':
            parts = split(r'\s*\|\s*', line.strip())
            if len(parts[0]) > 0:
                f, x, y = [int(x) for x in parts[0].strip().split('-')]
                mnemonic, code_type = [x.strip() for x in parts[1].strip().split(';')]
            elif len(parts) == 2:
                if len(codes) > 0:
                    if len(conditional_ids) > 0:
                        for conditional_id in conditional_ids:
                            for conditional_value in conditional_values:
                                table.append(CodeFlagDefinition(
                                    f, x, y, code_type == 'FLAG',
                                    conditional_id[0], conditional_id[1], conditional_id[2],
                                    conditional_value, mnemonic, codes
                                ))
                    else:
                        table.append(CodeFlagDefinition(
                            f, x, y, code_type == 'FLAG',
                            None, None, None,
                            None, mnemonic, codes
                        ))
                conditional_ids = []
                conditional_values = []
                codes = []
                parts = parts[1].split('=')
                conditional_ids = [[int(x) for x in y.strip().split('-')] for y in parts[0].split(',')]
                conditional_values = [int(x) for x in parts[1].split(',')]
            else:                    
                code = CodeFlagElement(parts[1].replace('>', '').strip(), parts[2].strip())
                codes.append((code.id, code))
                if parts[1].find('>') == -1:
                    if len(codes) > 0:
                        if len(conditional_ids) > 0:
                            for conditional_id in conditional_ids:
                                for conditional_value in conditional_values:
                                    table.append(CodeFlagDefinition(
                                        f, x, y, code_type == 'FLAG',
                                        conditional_id[0], conditional_id[1], conditional_id[2],
                                        conditional_value, mnemonic, codes
                                    ))
                        else:
                            table.append(CodeFlagDefinition(
                                f, x, y, code_type == 'FLAG',
                                None, None, None,
                                None, mnemonic, codes
                            ))
                    conditional_ids = []
                    conditional_values = []
                    codes = []
        line = in_file.readline().strip()