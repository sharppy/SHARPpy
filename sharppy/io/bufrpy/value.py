from collections import namedtuple
from .descriptors import OpCode
import codecs

class BufrValue(namedtuple('BufrValue', ['raw_value', 'value', 'descriptor'])):
    """Contains single value

    Contains single value, both in raw and decoded form, plus a link
    to its descriptor.

    :ivar str|int raw_value: Raw value. Either as hex-encoded string for textual values or an unsigned integer for numeric values
    :ivar str|int|float|None value: Decoded value. Value decoded according to its descriptor. Textual values are strings and numeric values floats or ints. Missing value is indicated by :py:data:`None`.
    :ivar ElementDescriptor descriptor: The descriptor of this value
    """
    __slots__ = ()

def _decode_raw_value(raw_value, descriptor, operators={}):
    if descriptor.unit == 'CCITTIA5': # Textual
        value = codecs.decode(raw_value.encode('iso-8859-1'),'hex_codec').decode('iso-8859-1') # CCITT IA5 is pretty close to ASCII, which is a subset of ISO-8859-1
    else:
        bits = _calculate_read_length(descriptor, operators)
        scale = _calculate_scale(descriptor, operators)
        ref = _calculate_ref(descriptor, operators)
        if raw_value ^ ((1 << bits)-1) == 0: # Missing value, all-ones
            value = None
        else:
            value = 10**-scale * (raw_value + ref)
            
    return BufrValue(raw_value, value, descriptor)

def get_op(operators, opcodes):
    """
    Get first operator that is present or None
    """
    for opcode in opcodes:
        if opcode in operators:
            return operators[opcode]
    return None
    
def _calculate_ref(descriptor, operators):
    # change of reference value by Change reference values is built into the descriptor
    if descriptor.code_descriptor():
        return descriptor.ref
    else:
        op = operators.get(OpCode.INCREASE_SRW, None)
        return descriptor.ref * (op.ref() if op else 1)

def _calculate_scale(descriptor, operators):
    if descriptor.code_descriptor():
        return descriptor.scale
    else:
        op = get_op(operators, (OpCode.CHANGE_SCALE, OpCode.INCREASE_SRW))
        return descriptor.scale + (op.scale() if op else 0)

def _calculate_read_length(descriptor, operators):
    if descriptor.unit == 'CCITTIA5':
        op = operators.get(OpCode.CHANGE_CCITTIA5_WIDTH, None)
        if op:
            return op.bits()
        else:
            return descriptor.length
    elif descriptor.code_descriptor():
        return descriptor.length
    else:
        op = get_op(operators, (OpCode.CHANGE_DATA_WIDTH, OpCode.INCREASE_SRW))
        return descriptor.length + (op.bits() if op else 0)

class BufrSubset(namedtuple("_BufrSubset", ["values"])):
    """
    Single BUFR message data subset

    :ivar values: Subset data as a list of BufrValues.
    """
