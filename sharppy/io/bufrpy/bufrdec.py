from __future__ import print_function

from util import ByteStream, ReadableStream, int2fxy, fxy2int
from descriptors import ElementDescriptor, OperatorDescriptor, ReplicationDescriptor, SequenceDescriptor, OpCode
from template import Template
from value import _decode_raw_value, _calculate_read_length, BufrSubset, BufrValue
import itertools
from collections import namedtuple, defaultdict
import re

FLAG_COMPRESSED=64
FLAG_OBSERVED=128

class Section0(namedtuple("_Section0", ["length", "edition"])):
    """
    Represents Section 0 of a BUFR message.

    :ivar int length: Total message length, in bytes
    :ivar int edition: BUFR edition number
    """
    __slots__ = ()

class Section1v3(namedtuple("_Section1v3", ["length", "master_table_id", "originating_centre", "originating_subcentre", "update_sequence_number", "optional_section", "data_category", "data_subcategory", "master_table_version", "local_table_version", "year", "month", "day", "hour", "minute"])):
    """
    Section 1 of a BUFR edition 3 message.

    :ivar int length: Length of Section 1
    :ivar int master_table_id: Master table identifier
    :ivar int originating_centre: Originating/generating centre
    :ivar int originating_subcentre: Originating/generating subcentre
    :ivar int update_sequence_number: Update sequence number
    :ivar int optional_section: 0 if optional section not present, 1 if present
    :ivar int data_category: Data category (identifies Table A to be used)
    :ivar int data_subcategory: Data subcategory
    :ivar int master_table_version: Master table version
    :ivar int local_table_version: Local table version
    :ivar int year: Year (originally of century, converted to AD by adding 1900)
    :ivar int month: Month
    :ivar int day: Day
    :ivar int hour: Hour
    :ivar int minute: Minute
    """
    __slots__ = ()

class Section1v4(namedtuple("_Section1v4", ["length", "master_table_id", "originating_centre", "originating_subcentre", "update_sequence_number", "optional_section", "data_category", "data_subcategory", "local_subcategory", "master_table_version", "local_table_version", "year", "month", "day", "hour", "minute", "second"])):
    """
    Section 1 of a BUFR edition 4 message.

    :ivar int length: Length of Section 1
    :ivar int master_table_id: Master table identifier
    :ivar int originating_centre: Originating/generating centre
    :ivar int originating_subcentre: Originating/generating subcentre
    :ivar int update_sequence_number: Update sequence number
    :ivar int optional_section: 0 if optional section not present, 1 if present
    :ivar int data_category: Data category (identifies Table A to be used)
    :ivar int data_subcategory: Data subcategory
    :ivar int local_subcategory: Local subcategory
    :ivar int master_table_version: Master table version
    :ivar int local_table_version: Local table version
    :ivar int year: Year (four digits)
    :ivar int month: Month
    :ivar int day: Day
    :ivar int hour: Hour
    :ivar int minute: Minute
    :ivar int second: Second
    """
    __slots__ = ()

class Section2(namedtuple("_Section2", ["length", "data"])):
    """
    Section 2 of a BUFR message.

    :ivar int length: Length of Section 2
    :ivar data: Contents of section 2, as list of integers representing the content bytes
    """
    __slots__ = ()

class Section3(namedtuple("_Section3", ["length", "n_subsets", "flags", "descriptors"])):
    """Section 3 of a BUFR message.

    Section 3 contains descriptors that describe the actual data
    format. Descriptors are instances of one of the descriptor
    classes: :py:class:`.descriptors.ElementDescriptor`,
    :py:class:`.descriptors.ReplicationDescriptor`,
    :py:class:`.descriptors.OperatorDescriptor`,
    :py:class:`.descriptors.SequenceDescriptor`.

    :ivar int length: Length of Section 3
    :ivar int n_subsets: Number of data subsets in the data section
    :ivar int flags: Flags describing the data set. See BUFR specification for details.
    :ivar descriptors: List of descriptors that describe the contents of each data subset.

    """
    __slots__ = ()

class Section4(namedtuple("_Section4", ["length", "subsets"])):
    """
    Section 4 of a BUFR message.

    Section 4 contains the actual message data.

    :ivar int length: Length of Section 4
    :ivar subsets: Message data as a list of BufrSubsets.
    """
    __slots__ = ()


class Section5(namedtuple("_Section5", ["data"])):
    """
    Section 5 of a BUFR message.

    :ivar data: End token.
    """
    __slots__ = ()


class Message(namedtuple("_Message", ["section0", "section1", "section2", "section3", "section4", "section5"])):
    """
    Represents a complete BUFR message, of either edition 3 or edition 4.

    :ivar Section0 section0: Section 0, start token and length
    :ivar Section1v3|Section1v4 section1: Section 1, time and source metadata
    :ivar Section2 section2: Section 2, optional metadata, not processed
    :ivar Section3 section3: Section 3, message structure
    :ivar Section4 section4: Section 4, message contents
    :ivar Section5 section5: Section 5, end token
    """
    __slots__ = ()

def decode_section0(stream):
    """
    Decode Section 0 of a BUFR message into :class:`.Section0` object.

    :param ReadableStream stream: Stream to decode from
    :return: Decoded Section 0
    :rtype: Section0
    :raises ValueError: if the message does not start with BUFR
    """
    bufr = stream.readstr(4)
    if bufr != 'BUFR':
        raise ValueError("BUFR message must start with bytes BUFR, got: " + repr(bufr))
    total_length = stream.readint(3)
    edition = stream.readint(1)
    return Section0(total_length, edition)

def decode_section1_v3(stream):
    """
    Decode Section 1 of version 3 BUFR message into :class:`.Section1v3` object.

    :param ReadableStream stream: Stream to decode from
    :return: Decoded Section 1
    :rtype: Section1v3
    :raises ValueError: if master table id is not 0
    """
    length = stream.readint(3)
    master_table_id = stream.readint(1)
    if master_table_id != 0:
        raise ValueError("Found master table value %d, only 0 supported" %master_table_id)
    originating_subcentre = stream.readint(1)
    originating_centre = stream.readint(1)
    update_sequence_number = stream.readint(1)
    optional_section = stream.readint(1)
    data_category = stream.readint(1)
    data_subcategory = stream.readint(1)
    master_table_version = stream.readint(1)
    local_table_version = stream.readint(1)
    year = stream.readint(1) + 1900
    month = stream.readint(1)
    day = stream.readint(1)
    hour = stream.readint(1)
    minute = stream.readint(1)
    # Total bytes read this far is 17, read length-17 to complete the section
    rest = stream.readbytes(length-17)
    return Section1v3(length, master_table_id, originating_centre, originating_subcentre, update_sequence_number, optional_section, data_category, data_subcategory, master_table_version, local_table_version, year, month, day, hour, minute)

def decode_section1_v4(stream):
    """
    Decode Section 1 of version 4 BUFR message into :class:`.Section1v4` object.

    :param ReadableStream stream: Stream to decode from
    :return: Decoded Section 1
    :rtype: Section1v4
    :raises ValueError: if master table id is not 0
    """
    length = stream.readint(3)
    master_table_id = stream.readint(1)
    if master_table_id != 0:
        raise ValueError("Found master table value %d, only 0 supported" %master_table_id)
    originating_centre = stream.readint(2)
    originating_subcentre = stream.readint(2)
    update_sequence_number = stream.readint(1)
    optional_section = stream.readint(1)
    data_category = stream.readint(1)
    data_subcategory = stream.readint(1)
    local_subcategory = stream.readint(1)
    master_table_version = stream.readint(1)
    local_table_version = stream.readint(1)
    year = stream.readint(2)
    month = stream.readint(1)
    day = stream.readint(1)
    hour = stream.readint(1)
    minute = stream.readint(1)
    second = stream.readint(1)
    # Total bytes read this far is 22, read length-22 to complete the section
    rest = stream.readbytes(length-22)
    return Section1v4(length, master_table_id, originating_centre, originating_subcentre, update_sequence_number, optional_section, data_category, data_subcategory, local_subcategory, master_table_version, local_table_version, year, month, day, hour, minute, second)

def decode_section2(stream):
    """
    Decode Section 2 of a BUFR message into :class:`.Section2` object.

    :param ReadableStream stream: Stream to decode from
    :return: Decoded Section 2
    :rtype: Section2
    """
    length = stream.readint(3)
    data = list(stream.readbytes(length-3))
    return Section2(length, data)

def _decode_descriptors_table(length, stream, descriptor_table):
    # length is remaining length of descriptor field in bytes
    n_read = 0
    codes = []
    while n_read + 2 <= length:
        codes.append(stream.readint(2))
        n_read += 2

    descriptors = []
    for code in codes:
        try:
            descriptors.append(descriptor_table[code])
        except KeyError as e:
            raise KeyError("Missing definition for descriptor " + int2fxy(code))

    # read final byte, since length of the section should be even and
    # descriptors start at odd offset
    stream.readbytes(length-n_read)
    return descriptors

def _decode_descriptors_template(length, stream, descriptor_template):
    # length is remaining length of descriptor field in bytes
    n_read = 0
    codes = []
    while n_read + 2 <= length:
        code = stream.readint(2)
        codes.append(code)
        n_read += 2

    # read final byte, since length of the section should be even and
    # descriptors start at odd offset
    stream.readbytes(length-n_read)

    # check descriptor codes
    if len(codes) == len(descriptor_template.descriptors):
        for i, (code, descriptor) in enumerate(zip(codes, descriptor_template.descriptors)):
            if code != descriptor.code:
                raise ValueError("Invalid template, mismatch at index %d, template code: %d, message code: %d" %(i, descriptor.code, code))
        return descriptor_template.descriptors

    raise ValueError("Invalid template, length does not match message: template: %d, message: %d" %(len(descriptor_template.descriptors), len(codes)))

def decode_section3(stream, descriptor_table):
    """
    Decode Section 3, the descriptor section, of a BUFR message into a :class:`.Section3` object.

    If descriptor_table is a Template, it must match the structure of the message.

    :param ReadableStream stream: BUFR message, starting at section 3
    :param Mapping|Template descriptor_table: either a mapping from BUFR descriptor codes to descriptors or a Template describing the message
    """
    length = stream.readint(3)
    reserved = stream.readint(1)
    n_subsets = stream.readint(2)
    flags = stream.readint(1)
    # 7 bytes of headers so far

    if isinstance(descriptor_table, Template):
        descriptors = _decode_descriptors_template(length-7, stream, descriptor_table)
    else:
        descriptors = _decode_descriptors_table(length-7, stream, descriptor_table)

    # Strongify the descriptors, lazy sequence descriptors would be difficult to handle otherwise
    descriptors = [descriptor.strong() for descriptor in descriptors]

    return Section3(length, n_subsets, flags, descriptors)


def skip_section4(stream):
    """
    Skip Section 4
    :return: None
    """

    from bitstring import ConstBitStream, Bits
    length = stream.readint(3)
    pad = stream.readint(1)
    data = stream.readbytes(length-4)
    return

def decode_section4(stream, descriptors, n_subsets=1, compressed=False):
    """
    Decode Section 4, the data section, of a BUFR message into a :class:`.Section4` object.

    :param ReadableStream stream: BUFR message, starting at section 4
    :param descriptors: List of descriptors specifying message structure
    :param int n_subsets: Number of data subsets, from section 3
    :param bool compressed: Whether message data is compressed or not, from section 3
    :raises NotImplementedError: if the message contains operator descriptors
    :raises NotImplementedError: if the message contains sequence descriptors
    """

    REPLICATION_DESCRIPTORS = set([fxy2int("031000"), fxy2int("031001"), fxy2int("031002")])
    REPETITION_DESCRIPTORS = set([fxy2int("031011"), fxy2int("031012")])

    from bitstring import ConstBitStream, Bits
    length = stream.readint(3)
    pad = stream.readint(1)
    data = stream.readbytes(length-4)
    bits = ConstBitStream(bytes=data)


    def decode(bits, descriptors, operators, descriptor_overlay):
        """
        :param bits: Bit stream to decode from
        :param descriptors: Descriptor iterator
        :param dict operators: Operators in effect, indexed by opcode
        :param dict descriptor_overlay: Overlay descriptors affected by CHANGE_REFERENCE_VALUES operator
        """
        values = []
        for descriptor in descriptors:
            descriptor = descriptor_overlay.get(descriptor.code, descriptor)
            if isinstance(descriptor, ElementDescriptor):
                op_crf = operators.get(OpCode.CHANGE_REFERENCE_VALUES, None)
                if op_crf is not None:
                    ref_value = Bits._readuint(bits, op_crf.bits(), bits.pos)
                    bits.pos += op_crf.bits()
                    top_bit_mask = (1 << op_crf.bits()-1)
                    if ref_value & top_bit_mask:
                        ref_value = -(ref_value & ~top_bit_mask)
                    overlay_descriptor = ElementDescriptor(descriptor.code, descriptor.length, descriptor.scale, ref_value, descriptor.significance, descriptor.unit)
                    descriptor_overlay[descriptor.code] = overlay_descriptor
                    continue
                
                op_aaf = operators.get(OpCode.ADD_ASSOCIATED_FIELD, None)
                if op_aaf is not None and descriptor.code != fxy2int("031021"):
                    # Don't apply to ASSOCIATED FIELD SIGNIFICANCE
                    associated_value = Bits._readuint(bits, op_aaf.bits(), bits.pos)
                    bits.pos += op_aaf.bits()
                    # Use dummy descriptor 999999 for associated field, like Geo::BUFR and libbufr
                    dummy_descriptor = ElementDescriptor(fxy2int("999999"), op_aaf.bits(), 0, 0, "ASSOCIATED FIELD", "NUMERIC")
                    values.append(BufrValue(associated_value, associated_value, dummy_descriptor))

                read_length = _calculate_read_length(descriptor, operators)
                if descriptor.unit == 'CCITTIA5':
                    raw_value = Bits._readhex(bits, read_length, bits.pos)
                else:
                    raw_value = Bits._readuint(bits, read_length, bits.pos)
                bits.pos += read_length
                values.append(_decode_raw_value(raw_value, descriptor, operators))
            elif isinstance(descriptor, ReplicationDescriptor):
                aggregation = []
                if descriptor.count:
                    bval = None
                    count = descriptor.count
                else:
                    bval = decode(bits, itertools.islice(descriptors, 1), {}, {})[0]
                    count = bval.value
                n_fields = descriptor.fields
                field_descriptors = list(itertools.islice(descriptors, n_fields))
                if bval is None or bval.descriptor.code in REPLICATION_DESCRIPTORS:
                    # Regular replication, X elements repeated Y or <element value> times in the file
                    for _ in range(count):
                        aggregation.append(decode(bits, iter(field_descriptors), operators, descriptor_overlay))
                elif bval.descriptor.code in REPETITION_DESCRIPTORS:
                    # Repeated replication, X elements present once in the file, output <element value> times
                    repeated_values = decode(bits, iter(field_descriptors), operators, descriptor_overlay)
                    for _ in range(count):
                        aggregation.append(repeated_values)
                else:
                    raise ValueError("Unexpected delayed replication element %s" %bval)
                values.append(aggregation)
            elif isinstance(descriptor, OperatorDescriptor):
                op = descriptor.operator
                if op.immediate:
                    if op.opcode == OpCode.SIGNIFY_CHARACTER:
                        raw_value = Bits._readhex(bits, op.bits(), bits.pos)
                        bits.pos += op.bits()
                        char_descriptor = ElementDescriptor(fxy2int(op.code), op.bits(), 0, 0, "CHARACTER INFORMATION", "CCITTIA5")
                        value = _decode_raw_value(raw_value, char_descriptor, {})
                        values.append(value)
                    elif op.opcode == OpCode.SIGNIFY_LOCAL_DESCRIPTOR:
                        base_descriptor = itertools.islice(descriptors, 1)[0]
                        mod_descriptor = ElementDescriptor(base_descriptor.code, op.bits(), base_descriptor.scale, base_descriptor.ref, base_descriptor.significance, base_descriptor.unit)
                        values.add(decode(bits, descriptors, {}, {})[0].value)
                        
                    else:
                        raise NotImplementedError("Unknown immediate operator: %s" % str(descriptor))
                else:
                    if op.neutral():
                        del operators[op.opcode]
                    else:
                        op.check_conflict(operators)
                        operators[op.opcode] = op
            elif isinstance(descriptor, SequenceDescriptor):
                seq = decode(bits, iter(descriptor.descriptors), operators, descriptor_overlay)
                values.extend(seq)
            else:
                raise NotImplementedError("Unknown descriptor type: %s" % descriptor)
        return values

    def decode_compressed(bits, descriptors, n_subsets, operators, descriptor_overlay):
        """
        :param bits: Bit stream to decode from
        :param descriptors: Descriptor iterator
        :param n_subsets: Number of subsets to decode
        :param dict operators: Operators in effect, indexed by opcode
        :param dict descriptor_overlay: Overlay descriptors affected by CHANGE_REFERENCE_VALUES operator
        """
        subsets = [[] for x in range(n_subsets)]
        for descriptor in descriptors:
            descriptor = descriptor_overlay.get(descriptor.code, descriptor)

            if isinstance(descriptor, ElementDescriptor):
                op_crf = operators.get(OpCode.CHANGE_REFERENCE_VALUES, None)
                if op_crf is not None:
                    dummy_descriptors = iter([ElementDescriptor(fxy2int("999999"), op_crf.bits(), 0, 0, "ASSOCIATED FIELD", "NUMERIC")])
                    _subsets = decode_compressed(bits, dummy_descriptors, n_subsets, {}, {})
                    raw_vals = [subset[0].raw_value for subset in _subsets]

                    if len(set(raw_vals)) != 1:
                        raise ValueError("Encountered different reference values for different subsets: %s", raw_vals)

                    ref_value = raw_vals[0]
                    top_bit_mask = (1 << op_crf.bits()-1)
                    if ref_value & top_bit_mask:
                        ref_value = -(ref_value & ~top_bit_mask)

                    overlay_descriptor = ElementDescriptor(descriptor.code, descriptor.length, descriptor.scale, ref_value, descriptor.significance, descriptor.unit)
                    descriptor_overlay[descriptor.code] = overlay_descriptor
                    continue

                op_aaf = operators.get(OpCode.ADD_ASSOCIATED_FIELD, None)
                if op_aaf is not None and descriptor.code != fxy2int("031021"):
                    # Don't apply to ASSOCIATED FIELD SIGNIFICANCE
                    # Use dummy descriptor 999999 for associated field, like Geo::BUFR and libbufr
                    dummy_descriptors = iter([ElementDescriptor(fxy2int("999999"), op_aaf.bits(), 0, 0, "ASSOCIATED FIELD", "NUMERIC")])
                    vals = decode_compressed(bits, dummy_descriptors, n_subsets, {}, {})
                    for i,ss in enumerate(vals):
                        subsets[i].extend(ss)

                read_length = _calculate_read_length(descriptor, operators)
                if descriptor.unit == 'CCITTIA5':
                    ref_value = Bits._readhex(bits, read_length, bits.pos)
                else:
                    ref_value = Bits._readuint(bits, read_length, bits.pos)
                bits.pos += read_length

                n_bits = Bits._readuint(bits, 6, bits.pos)
                bits.pos += 6
                
                for i in range(n_subsets):
                    if descriptor.unit == 'CCITTIA5':
                        n_chars = n_bits
                        if n_chars:
                            raw_value = Bits._readhex(bits, n_chars*8, bits.pos)
                            bits.pos += n_chars*8
                            value = _decode_raw_value(raw_value, descriptor, operators)
                        else:
                            value = _decode_raw_value(ref_value, descriptor, operators)
                    else:
                        if n_bits:
                            increment = Bits._readuint(bits, n_bits, bits.pos)
                            bits.pos += n_bits
                            if increment ^ ((1 << n_bits)-1) == 0: # Missing value, all-ones
                                value = _decode_raw_value((1 << descriptor.length)-1, descriptor, operators)
                            else:
                                value = _decode_raw_value(ref_value + increment, descriptor, operators)
                        else:
                            value = _decode_raw_value(ref_value, descriptor, operators)
                    subsets[i].append(value)
            elif isinstance(descriptor, ReplicationDescriptor):
                aggregations = [[] for x in range(n_subsets)]
                if descriptor.count:
                    bval = None
                    count = descriptor.count
                else:
                    bval = decode_compressed(bits, itertools.islice(descriptors, 1), n_subsets, {}, {})[0][0]
                    count = bval.value
                n_fields = descriptor.fields
                field_descriptors = list(itertools.islice(descriptors, n_fields))

                if bval is None or bval.descriptor.code in REPLICATION_DESCRIPTORS:
                    # Regular replication, X elements repeated Y or <element value> times in the file
                    for _ in range(count):
                        replication = decode_compressed(bits, iter(field_descriptors), n_subsets, operators, descriptor_overlay)
                        for subset_idx in range(n_subsets):
                            aggregations[subset_idx].append(replication[subset_idx])
                elif bval.descriptor.code in REPETITION_DESCRIPTORS:
                    # Repeated replication, X elements present once in the file, output <element value> times
                    replication = decode_compressed(bits, iter(field_descriptors), n_subsets, operators, descriptor_overlay)
                    for _ in range(count):
                        for subset_idx in range(n_subsets):
                            aggregations[subset_idx].append(replication[subset_idx])
                else:
                    raise ValueError("Unexpected delayed replication element %s" %bval)

                for subset_idx in range(n_subsets):
                    subsets[subset_idx].append(aggregations[subset_idx])
            elif isinstance(descriptor, OperatorDescriptor):
                op = descriptor.operator
                if op.opcode in (1,2,3,4,7):
                    if op.neutral():
                        del operators[op.opcode]
                    else:
                        op.check_conflict(operators)
                        operators[op.opcode] = op
                else:
                    raise NotImplementedError("Can only decode operators 201-204 and 207 for compressed BUFR data at the moment, please file an issue on GitHub, found operator: 2%02d" %op.opcode)
            elif isinstance(descriptor, SequenceDescriptor):
                comp = decode_compressed(bits, iter(descriptor.descriptors), n_subsets, operators, descriptor_overlay)
                for i,subset in enumerate(comp):
                    subsets[i].extend(subset)
            else:
                raise NotImplementedError("Unknown descriptor type: %s" % descriptor)
        return subsets

    if compressed:
        subsets = [BufrSubset(x) for x in decode_compressed(bits, iter(descriptors), n_subsets, {}, {})]
    else:
        subsets = [BufrSubset(decode(bits, iter(descriptors), {}, {})) for _ in range(n_subsets)]
    return Section4(length, subsets)

def decode_section5(stream):
    """
    Decode Section 5 of a BUFR message into a :class:`.Section5` object.

    Section 5 is just a trailer to allow verifying that the message has been read completely.

    :param ReadableStream stream: BUFR message, starting at section 5
    :raises ValueError: if message end token is not 7777 as specified
    """
    data = stream.readstr(4)
    END_TOKEN = "7777"
    if data != END_TOKEN:
        raise ValueError("Invalid end token: %s, expected: %s" %(data, END_TOKEN))
    return Section5(data)

def decode_file(f, b_table):
    """
    Decode BUFR message from a file into a :class:`.Message` object.

    :param file f: File that contains the bufr message
    :param Mapping|Template b_table: Either a mapping from BUFR descriptor codes to descriptors or a Template describing the message
    """
    return decode(ByteStream(f), b_table)

READ_VERSIONS=(3,4)

def decode_all(stream, b_table):
    """
    Decode all BUFR messages from stream into a list of :class:`.Message` objects and a list of decoding errors.
    

    Reads through the stream, decoding well-formed BUFR messages. BUFR
    messages must start with BUFR and end with 7777. Data between
    messages is skipped.

    :param ByteStream stream: Stream that contains the bufr message
    :param Mapping|Template b_table: Either a mapping from BUFR descriptor codes to descriptors or a Template describing the message
    """
    def seek_past_bufr(stream):
        """ Seek stream until BUFR is encountered. Returns True if BUFR found and False if not """
        try:
            c = None
            while True:
                if c != b'B':
                    c = stream.next()
                    continue
                if c == b'B':
                    c = stream.next()
                    if c == b'U':
                        c = stream.next()
                        if c == b'F':
                            c = stream.next()
                            if c == b'R':
                                return True
                        
        except StopIteration:
            return False

    messages = []
    errors = []
    while seek_past_bufr(stream):
        try:
            msg = decode(itertools.chain([b'B',b'U',b'F',b'R'], stream), b_table)
            messages.append(msg)
        except Exception as e:
            errors.append(e)
            pass
    return messages, errors

def decode(stream, b_table, skip_data=False):
    """ 
    Decode BUFR message from stream into a :class:`.Message` object.

    See WMO306_vl2_BUFR3_Spec_en.pdf for BUFR format specification.

    :param ByteStream stream: Stream that contains the bufr message
    :param Mapping|Template b_table: Either a mapping from BUFR descriptor codes to descriptors or a Template describing the message
    :param bool skip_data: Skip decoding data? Can be used to get only extract metadata of a file to e.g. analysis of decoding errors.
    """

    rs = ReadableStream(stream)
    section0 = decode_section0(rs)
    if section0.edition not in READ_VERSIONS:
        raise ValueError("Encountered BUFR edition %d, only support %s" %(section0.edition, READ_VERSIONS))
    if section0.edition == 3:
        section1 = decode_section1_v3(rs)
    elif section0.edition == 4:
        section1 = decode_section1_v4(rs)
    if section1.optional_section != 0:
        section2 = decode_section2(rs)
    else:
        section2 = None
    section3 = decode_section3(rs, b_table)
    if skip_data:
        section4 = skip_section4(rs)
    else:
        section4 = decode_section4(rs, section3.descriptors, section3.n_subsets, section3.flags & FLAG_COMPRESSED)
    section5 = decode_section5(rs)
    return Message(section0, section1, section2, section3, section4, section5)


    
