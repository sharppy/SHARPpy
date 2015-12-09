from util import slices, fxy2int, fxy, int2fxy
from descriptors import ElementDescriptor, ReplicationDescriptor, OperatorDescriptor, LazySequenceDescriptor, DescriptorTable

def read_tables(b_line_stream, d_line_stream=None):
    """
    Read BUFR table(s) in from libbufr text file(s).

    The return value is a dict that combines the tables read.

    :param b_line_stream: Iterable of lines, contents of the B-table file
    :param d_line_stream: Iterable of lines, contents of the D-table file
    :return: Mapping from FXY integers to descriptors
    :rtype: dict
    :raises NotImplementedError: if the table contains sequence descriptors
    :raises ValueError: if the table contains descriptors with illegal class (outside range [0,3])
    """
    descriptors = {}
    for line in b_line_stream:
        # Format from btable.F:146 in libbufr version 000400
        parts = slices(line, [1,6,1,64,1,24,1,3,1,12,1,3])
        if not parts[11]:
            # Geo::BUFR skips lines without bit width definition,
            # libbufr defaults bit width to 0
            # choosing to skip here
            continue
        raw_descriptor = parts[1]
        descriptor_code = fxy2int(raw_descriptor)
        significance = parts[3].strip()
        unit = parts[5].strip()
        scale = int(parts[7])
        reference = int(parts[9])
        bits = int(parts[11])

        descr_class = raw_descriptor[0]
        if descr_class == '0':
            descriptors[descriptor_code] = ElementDescriptor(descriptor_code, bits, scale, reference, significance, unit)
        elif descr_class == '1':
            f,x,y = fxy(raw_descriptor)
            descriptors[descriptor_code] = ReplicationDescriptor(descriptor_code, 0, x, y, significance)
        elif descr_class == '2':
            f,x,y = fxy(raw_descriptor)
            descriptors[descriptor_code] = OperatorDescriptor(descriptor_code, 0, x, y, significance)
        elif descr_class == '3':
            raise ValueError("B-table file should not contain descriptors of class 3: %s" %descr_class)
        else:
            raise ValueError("Encountered unknown descriptor class: %s" %descr_class)

    def group_d_lines(ls):
        buf = None
        for line in ls:
            if line.startswith(' 3'):
                if buf:
                    yield buf
                buf = [line]
            else:
                buf.append(line)
        yield buf

    table = DescriptorTable(descriptors) # descriptors is not copied, just referenced 

    if d_line_stream:
        for lines in group_d_lines(d_line_stream):
            # Format inferred
            parts = slices(lines[0], [1,6,1,2,1,6])
            raw_d_descriptor = parts[1]
            d_descriptor_code = fxy2int(raw_d_descriptor)
            n_elements = int(parts[3])
            actual_elements = len(lines)
            if n_elements != actual_elements:
                raise ValueError("Expected %d elements, found %d" %(n_elements, actual_elements))
            constituent_codes = []
            for line in lines:
                l_parts = slices(line, [1,6,1,2,1,6])
                constituent_codes.append(fxy2int(l_parts[5]))

            descriptors[d_descriptor_code] = LazySequenceDescriptor(d_descriptor_code, constituent_codes, '', table)
    return table

