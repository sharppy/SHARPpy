from collections import namedtuple
from copy import deepcopy
from sys import modules

from .tables import ElementDefinition, parse_int
from .values import BUFRString

class Operator(ElementDefinition):
    __slots__ = ('id',)
    __id_class__ = namedtuple('OperatorID', ('f', 'x', 'y'))
    mnemonic = "OPER"
    name = 'Operator'
    def __init__(self, f, x, y):
        super().__initialize_id__(self.__id_class__(
            f=parse_int(f, 1), 
            x=parse_int(x, 1), 
            y=parse_int(y, 1)
        ))
    @staticmethod
    def create(f, x, y):
        cls = getattr(modules[__name__], 'Operator{0:02d}'.format(x), Operator)
        return cls(f, x, y)

class Operator05(Operator):
    mnemonic = "OPER5"
    name = 'Operator05'
    unit = "CCITT IA5"

    @property
    def bit_width(self):
        return self.id.y * 8

class Operator06(Operator):
    mnemonic = "OPER6"
    name = 'Operator06'
    
    def apply(self, element):
        element = deepcopy(element)
        element.bit_width *= self.y
        return element
