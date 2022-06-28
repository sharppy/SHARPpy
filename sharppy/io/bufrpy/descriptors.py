from .util import int2fxy
from collections import namedtuple
from abc import ABCMeta, abstractproperty
try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

class OperatorConflict(Exception):
    pass

# opcodes for operators
class OpCode:
    # long-term, in effect until cancelled
    CHANGE_DATA_WIDTH = 1
    CHANGE_SCALE = 2
    CHANGE_REFERENCE_VALUES = 3
    ADD_ASSOCIATED_FIELD = 4
    INCREASE_SRW = 7
    CHANGE_CCITTIA5_WIDTH = 8

    # immediate
    SIGNIFY_CHARACTER = 5
    SIGNIFY_DATA_WIDTH = 6


operators = {}

class OperatorMeta(type):
    def __init__(cls, name, bases, dict):
        type.__init__(cls, name, bases, dict)
        if hasattr(cls, 'opcode'):
            operators[cls.opcode] = cls

_Operator = OperatorMeta('_Operator', (object, ), {})

class Operator(_Operator):
    def neutral(self):
        """
        Tell if this operator is "neutral", i.e. one that returns resets stateful operator
        """
        raise NotImplementedError("Implement")

    def check_conflict(self, operators):
        """
        Check if this operator conflicts with given operator map
        :param dict operators: Operator objects indexed by opcode
        """
        raise NotImplementedError("Implement")

    def _check_conflict(self, operators, conflicting_opcodes):
        for opcode in conflicting_opcodes:
            if opcode in operators:
                raise OperatorConflict("Conflict with existing operator %d" %opcode)

    def __eq__(self, other):
        return self.opcode == other.opcode and self.operand == other.operand

    def __ne__(self, other):
        return not self.__eq__(other)

class ChangeDataWidth(Operator):
    opcode = OpCode.CHANGE_DATA_WIDTH
    description = "Change data width"
    immediate = False

    def __init__(self, operand):
        self.operand = operand

    def neutral(self):
        return self.operand == 0

    def bits(self):
        return self.operand-128

    def check_conflict(self, operators):
        self._check_conflict(operators, (self.opcode, OpCode.INCREASE_SRW))

class ChangeScale(Operator):
    opcode = 2
    description = "Change scale"
    immediate = False

    def __init__(self, operand):
        self.operand = operand

    def neutral(self):
        return self.operand == 0

    def scale(self):
        return self.operand-128

    def check_conflict(self, operators):
        self._check_conflict(operators, (self.opcode, OpCode.INCREASE_SRW))

class ChangeReferenceValues(Operator):
    opcode = 3
    description = "Change reference values"
    immediate = False

    def __init__(self, operand):
        self.operand = operand

    def neutral(self):
        return self.operand == 255

    def bits(self):
        return self.operand

    def check_conflict(self, operators):
        self._check_conflict(operators, (OpCode.INCREASE_SRW,))

class AddAssociatedField(Operator):
    opcode = 4
    description = "Add associated field"
    immediate = False

    def __init__(self, operand):
        self.operand = operand

    def neutral(self):
        return self.operand == 0

    def bits(self):
        return self.operand

    def check_conflict(self, operators):
        self._check_conflict(operators, (self.opcode,))

class SignifyCharacter(Operator):
    opcode = 5
    description = "Signify width of CCITT IA5 field"
    immediate = True
        
    def __init__(self, operand):
        self.operand = operand

    def neutral(self):
        # Immediate operator, won't be saved
        return True

    def bits(self):
        return self.operand*8

    def check_conflict(self, operators):
        # Immediate operator, no conflicts
        pass

class SignifyLocalDescriptor(Operator):
    opcode = 6
    description = "Signify data width for the immediately following local descriptor"
    immediate = True

    def __init__(self, operand):
        self.operand = operand

    def netural(self):
        # Immediate operator, won't be saved
        return True

    def check_conflict(self, operators):
        # Immediate operator, no conflicts
        pass

class IncreaseSrw(Operator):
    opcode = 7
    description = "Increase scale, reference value and data width"
    immediate = False

    def __init__(self, operand):
        self.operand = operand

    def neutral(self):
        return self.operand == 0

    def bits(self):
        return int(((self.operand*10)+2)/3)

    def scale(self):
        return self.operand

    def ref(self):
        return self.operand

    def check_conflict(self, operators):
        self._check_conflict(operators, (self.opcode, OpCode.CHANGE_DATA_WIDTH, OpCode.CHANGE_SCALE, OpCode.CHANGE_REFERENCE_VALUES))

class ChangeTextWidth(Operator):
    opcode = 8
    description = "Change width of CCITT IA5 field"
    immediate = False

    def __init__(self, operand):
        self.operand = operand

    def bits(self):
        return self.operand*8

    def neutral(self):
        return self.operand == 0

    def check_conflict(self, operators):
        self._check_conflict(operators, (self.opcode,))

class DescriptorTable(Mapping):
    """
    Descriptor table that provides lookups for replication descriptors.

    Passes non-replication descrtiptor lookups on to a mapping supplied at creation time.
    """

    def __init__(self, table):
        self.table = table

    def __getitem__(self, code):
        f = (code >> 14) & 0x3
        x = (code >> 8) & 0x3f
        y = code & 0xff
        if f == 1:
            # Replication descriptor
            return ReplicationDescriptor(code, 0, x, y, "")
        elif f == 2:
            op = operators[x](y)
            return OperatorDescriptor(code, 0, x, y, op, op.description)
        else:
            return self.table[code]

    def __iter__(self, code):
        return iter(self.table)

    def __len__(self, code):
        return len(self.table)

class ElementDescriptor(namedtuple('_ElementDescriptor', ['code', 'length', 'scale', 'ref', 'significance', 'unit'])):
    """Describes single value

    Data element described with an :class:`ElementDescriptor` is decoded into a
    :class:`.BufrValue`, with either textual or numeric value.

    :ivar int code: Descriptor code
    :ivar int length: Length of data, in bits
    :ivar int scale: Scaling factor applied to value to get scaled value for encoding
    :ivar float ref: Reference value, subtracted from scaled value to get encoded value
    :ivar str significance: Semantics of the element
    :ivar str unit: Unit of the element, affects interpretation of the encoded data in case of e.g. textual vs. numeric values

    """
    __slots__ = ()

    def strong(self):
        return self

    def code_descriptor(self):
        return 'FLAG' in self.unit or 'TABLE' in self.unit

class ReplicationDescriptor(namedtuple('ReplicationDescriptor', ['code', 'length', 'fields', 'count', 'significance'])):
    """Describes a repeating collection of values
    
    Data described with a :class:`ReplicationDescriptor` is decoded
    into a list of lists of values. The outer list has one element per
    replication and the inner lists one element per replicated field.

    :ivar int code: Descriptor code
    :ivar int length: Length of data, always 0
    :ivar int fields: Number of following descriptors to replicate
    :ivar int count: Number of replications
    :ivar str significance: Meaning of the replicated list
    """
    __slots__ = ()

    def strong(self):
        return self

class OperatorDescriptor(namedtuple('OperatorDescriptor', ['code', 'length', 'operation', 'operand', 'operator', 'significance'])):
    """Operators 201-208 are supported.
    
    :ivar int code: Descriptor code, the whole FXY as int
    :ivar int length: Length of data. Always 0.
    :ivar int operation: Opcode, X of FXY
    :ivar int operand: Operand, Y of FXY.
    :ivar Operator operator: Operator object for checking conflicts and parsing operand.
    :ivar str significance: Operator definition.
    """
    __slots__ = ()

    def strong(self):
        return self

class SequenceDescriptor(object):
    """Describes a fixed sequence of elements in compact form

    Similar to a replication with count 1, but the encoded form is
    more compact, since the sequence of fields is implicit. Except
    that at least in NWCSAF Templates the constituent elements of the
    sequence are also present in the template.

    :ivar int code: Descriptor code
    :ivar int length: Length of data, sum of lengths of constituent descriptors
    :ivar int descriptor_codes: Sequence containing constituent descriptor codes
    :ivar str significance: Meaning of the sequence, always empty string
    :ivar descriptors: Sequence containing constituent descriptors.
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def code(self):
        pass

    @abstractproperty
    def length(self):
        pass

    @abstractproperty
    def descriptor_codes(self):
        pass

    @abstractproperty
    def significance(self):
        pass

    @abstractproperty
    def descriptors(self):
        pass

class StrongSequenceDescriptor(namedtuple('_SequenceDescriptor', ['code', 'length', 'descriptor_codes', 'significance', 'descriptors']), SequenceDescriptor):
    """
    SequenceDescriptor with direct references to child descriptors
    """
    __slots__ = ()

    def strong(self):
        return self

class LazySequenceDescriptor(namedtuple('_LazySequenceDescriptor', ['code', 'descriptor_codes', 'significance', 'descriptor_table']), SequenceDescriptor):
    """
    SequenceDescriptor with lazy references to child descriptors though the descriptor table
    """

    @property
    def length(self):
        return sum(x.length for x in self.descriptors)

    @property
    def descriptors(self):
        try:
            return [self.descriptor_table[code] for code in self.descriptor_codes]
        except KeyError as e:
            raise KeyError("No descriptor for code " + int2fxy(e.args[0]))

    def strong(self):
        return StrongSequenceDescriptor(self.code, self.length, self.descriptor_codes, self.significance, tuple(d.strong() for d in self.descriptors))
