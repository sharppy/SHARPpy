from re import search
from textwrap import wrap

from .debug import dump_hex
from .external import array, ceil, zeros, floor
from .operators import Operator
from .replication import Replication, DelayedReplication
from .tables import BUFRDataType, ElementDefinition, parse_int, Table, SequenceDefinition, SequenceElement
from .tables.default import default_table
from .values import BUFRSubset, SubsetCollection, MessageCollection
from .utility import read_integer, read_integers

DEBUG_LEVEL = 0

class InvalidBUFRMessage(Exception):
    pass

class ClosedBUFRFile(Exception):
    pass

class BitMap(object):
    def __init__(self, byte_array):
        self.__byte_array__ = byte_array
        self.cursor = 0
    def seek(self, position):
        self.cursor = position
    def __repr__(self):
        return dump_hex(self.__byte_array__, 1e45)
    def read(self, length):
        start_byte = int(floor( self.cursor / 8 ))
        
        end_byte = int(ceil((self.cursor + length) / 8))

        value_length = int(ceil(length / 8.0))

        bit_mask = sum([2**(((end_byte - start_byte) * 8) - i - 1) for i in range(self.cursor % 8, self.cursor % 8 + length)])
        bit_shift = (((end_byte - start_byte) * 8) - (self.cursor % 8 + int(length)))

        value = ((int.from_bytes(self.__byte_array__[start_byte:end_byte], 'big') & bit_mask) >> bit_shift).to_bytes(value_length, 'big')
        self.cursor += int(length)
        return value

class BUFRFile(object):
    def __init__(self, filename, table_source=default_table):
        self.__table_source__ = table_source
        if type(filename) == str:
            self.__fobj__ = open(filename, 'rb')
        else:
            self.__fobj__ = filename
        self.messages = []
        message_offset = 0
        continue_reading = True
        while continue_reading:
            try:
                message = BUFRMessage(self.__fobj__, table_source=self.__table_source__, file_offset=message_offset)
                message_offset = message.__section_start__[0] + message.__section_start__[6]
                if message.data_category == 11:
                    self.__process_prepbufr_table__(message)
                else:
                    self.messages.append(message)
            except InvalidBUFRMessage:
                continue_reading = False
        if len(self.messages) == 0:
            raise InvalidBUFRMessage('File contains no valid BUFR messages')
    def __str__(self):
        output = ''
        for i, message in enumerate(self.messages):
            output +=  '\n\n' + '*'* 50 + '\n*' + ' ' * 48 + '*\n*' + '{0: ^48s}'.format('Message {0:d}'.format(i)) + '*\n*' + ' ' * 48 + '*\n' + '*' * 50 + '\n\n' + str(message)
        return output

    def __process_prepbufr_table__(self, message):
        table_ax = self.__table_source__.dynamic_table('A')
        table_bx = self.__table_source__.dynamic_table('B')
        table_dx = self.__table_source__.dynamic_table('D')
        message_descriptors = message.expand_descriptors(message.data_descriptors)
        message_bitmap      = message.section_4_data_bytes
        for i in range(len(message_descriptors)):
            value = message_descriptors[i].read_value(message_bitmap)
            for k in range(1, value.group_count):
                if value.groups[k][0].mnemonic == 'TABLAE':
                    table_ax.append(self.__parse_table_a_entry__(*value.groups[k]))
                elif value.groups[k][0].mnemonic == 'FDESC' and value.groups[k][3].mnemonic == 'ELEMNA1':
                    try:
                        table_bx.append(self.__parse_table_b_entry__(*value.groups[k]))
                    except:
                        print(value.groups[k])
                elif value.groups[k][0].mnemonic == 'FDESC' and value.groups[k][3].mnemonic == 'OPER5':
                    table_dx.append(self.__parse_table_d_entry__(*value.groups[k]))

    def __parse_table_a_entry__(self, table_a_entry, table_a_description_1, table_a_description_2):
        return_value = None
        description = table_a_description_1.data_raw + table_a_description_2.data_raw
        match = search(r'([^\s]+)\s+(.*)', description)
        if match is not None:
            return_value = BUFRDataType(table_a_entry.data, match.group(2).strip())
        return return_value

    def __parse_table_b_entry__(self, f_descriptor, x_descriptor, y_descriptor,
                            element_name_1, element_name_2, units_name,
                            scale_sign, scale, reference_sign, reference,
                            element_data_width):
        element = None
        element_information = element_name_1.data + element_name_2.data_raw
        match = search(r'([\w\d]+)(?:[\s\.]+([^\n]+))?', element_information)
        if match is not None:
            element = ElementDefinition(f_descriptor.data, x_descriptor.data, y_descriptor.data,
                                        scale_sign.data.strip() + scale.data.strip(), 
                                        reference_sign.data.strip() + reference.data.strip(),
                                        element_data_width.data, units_name.data.strip(), match.group(1).strip(), match.group(2).strip())
        return element

    def __parse_table_d_entry__(self, f_descriptor, x_descriptor, y_descriptor,
                            sequence_name, *sequence_descriptors):
        element = None
        match = search(r'([\w\d]+)(?:[\s]+([^\n]+))?', sequence_name.data_raw)
        if match is not None:
            element = SequenceDefinition(f_descriptor.data, x_descriptor.data, y_descriptor.data,
                match.group(1).strip(), match.group(2).strip())
            for index, entry in enumerate(sequence_descriptors):
                element.append(SequenceElement(index, entry.data[0],entry.data[1:3],entry.data[3:], ''))
        return element

    @property
    def data(self):
        message_collection = MessageCollection()
        for message_number, message in enumerate(self.messages):
            subsets = message.subsets
            subsets.metadata['message_number'] = message_number
            subsets.metadata['nominal_year'] = message.file_year
            subsets.metadata['nominal_month'] = message.file_month
            subsets.metadata['nominal_day'] = message.file_day
            subsets.metadata['nominal_hour'] = message.file_hour
            subsets.metadata['nominal_minute'] = message.file_minute
            subsets.metadata['nominal_second'] = message.file_second
            message_collection.append(subsets)
        return message_collection

    def close(self):
        self.__fobj__.close()

class BUFRMessage(object):
    def __init__(self, filename, table_source=default_table, file_offset=0):
        self.__table_source__ = table_source
        if type(filename) == str:
            self.__fobj__ = open(filename, 'rb')
        else:
            self.__fobj__ = filename
        self.__table_a__ = Table.create('A', None, None, None)
        self.__table_b__ = Table.create('B', None, None, None)
        self.__table_d__ = Table.create('D', None, None, None)
        self.__table_f__ = Table.create('F', None, None, None)
        self.__section_start__ = zeros(7, dtype='uint32')
        self.__section_start__[0] = file_offset
        start_word = self.__fobj__.read(4)
        file_start = start_word == b'BUFR'
        while not file_start:
            if DEBUG_LEVEL > 2:
                print('Seeking ahead')
            self.__section_start__[0] += 1
            self.__fobj__.seek(self.__section_start__[0])
            start_word = self.__fobj__.read(4)
            file_start = start_word == b'BUFR'
            if start_word == b'':
                break

        if not file_start:
            raise InvalidBUFRMessage('File contains no valid BUFR messages')
    
        if DEBUG_LEVEL > 1:
            print('Found start')
        self.__fobj__.seek(self.__section_start__[0] + 4)
        self.__section_start__[6] = read_integer(b'\x00' + self.__fobj__.read(3))
        self.bufr_edition = read_integer(self.__fobj__.read(1))
        self.__section_start__[1] = self.__section_start__[0] + 8
        self.__fobj__.seek(self.__section_start__[1] + (9 if self.bufr_edition == 4 else 7))
        self.section_2_present = read_integer(self.__fobj__.read(1))
        if self.section_2_present:
            self.__fobj__.seek(self.__section_start__[1])
            self.__section_start__[2] = self.__section_start__[1] + read_integer(b'\x00' + self.__fobj__.read(3))
            self.__fobj__.seek(self.__section_start__[2])
            self.__section_start__[3] = self.__section_start__[2] + read_integer(b'\x00' + self.__fobj__.read(3))
        else:
            self.__fobj__.seek(self.__section_start__[1])
            self.__section_start__[3] = self.__section_start__[1] + read_integer(b'\x00' + self.__fobj__.read(3))
        self.__fobj__.seek(self.__section_start__[3])
        self.__section_start__[4] = self.__section_start__[3] + read_integer(b'\x00' + self.__fobj__.read(3))
        self.__fobj__.seek(self.__section_start__[4])
        self.__section_start__[5] = self.__section_start__[4] + read_integer(b'\x00' + self.__fobj__.read(3)) - 4
        if DEBUG_LEVEL > 1:
            print('Initializing Table A')
        for table in (self.__table_source__.construct_table_version('A', 0, master_table=self.bufr_master_table)
                    + self.__table_source__.construct_table_version('A', self.local_table_version, master_table=self.bufr_master_table, originating_center=self.originating_center)
                    + self.__table_source__.construct_table_version('AX', 0)).values():
            self.__table_a__.append(table)
        if DEBUG_LEVEL > 1:
            print('Initializing Table B')
        for table in (self.__table_source__.construct_table_version('B', self.master_table_version, master_table=self.bufr_master_table, originating_center=None)
                    + self.__table_source__.construct_table_version('B', self.local_table_version,  master_table=self.bufr_master_table, originating_center=self.originating_center)
                    + self.__table_source__.construct_table_version('BX', 0)).values():
            self.__table_b__.append(table)
        if DEBUG_LEVEL > 1:
           print('Initializing Table D')
        for table in (self.__table_source__.construct_table_version('D', self.master_table_version, master_table=self.bufr_master_table, originating_center=None)
                    + self.__table_source__.construct_table_version('D', self.local_table_version,  master_table=self.bufr_master_table, originating_center=self.originating_center)
                    + self.__table_source__.construct_table_version('DX', 0)).values():
            self.__table_d__.append(table)
        if DEBUG_LEVEL > 1:
           print('Initializing Table F')
        for table in (self.__table_source__.construct_table_version('F', self.master_table_version, master_table=self.bufr_master_table, originating_center=None)
                    + self.__table_source__.construct_table_version('F', self.local_table_version,  master_table=self.bufr_master_table, originating_center=self.originating_center)
                    + self.__table_source__.construct_table_version('FX', 0)).values():
            self.__table_f__.append(table)
        
    def close(self):
        self.__fobj__.close()

    # Section 1 - Identification
    
    @property
    def bufr_master_table(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        self.__fobj__.seek(self.__section_start__[1] + 3)
        return read_integer(self.__fobj__.read(1))
    @property
    def originating_center(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        if self.bufr_edition == 3:
            offset = 5
        elif self.bufr_edition == 4:
            offset = 4
        self.__fobj__.seek(self.__section_start__[1] + offset)
        value = 0
        if self.bufr_edition == 3:
            value = read_integer(self.__fobj__.read(1))
        elif self.bufr_edition == 4:
            value = read_integer(self.__fobj__.read(2))
        return value
    @property
    def originating_subcenter(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        if self.bufr_edition == 3:
            offset = 4
        elif self.bufr_edition == 4:
            offset = 6
        self.__fobj__.seek(self.__section_start__[1] + offset)
        value = 0
        if self.bufr_edition == 3:
            value = read_integer(self.__fobj__.read(1))
        elif self.bufr_edition == 4:
            value = read_integer(self.__fobj__.read(2))
        return value
    @property
    def update_sequence_number(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        offset = 6
        if self.bufr_edition == 4:
            offset += 2
        self.__fobj__.seek(self.__section_start__[1] + offset)
        return read_integer(self.__fobj__.read(2))
    @property
    def data_category(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        offset = 8
        if self.bufr_edition == 4:
            offset += 2
        self.__fobj__.seek(self.__section_start__[1] + offset)
        return read_integer(self.__fobj__.read(1))
    @property
    def data_category_description(self):
        description = ''
        codes = self.__table_a__.find(lambda id: id.code==self.data_category)
        if codes is not None:
            description = codes.iloc(0).description
        return description
    @property
    def international_data_sub_category(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        value = None
        if self.bufr_edition == 4:
            offset = 11
            self.__fobj__.seek(self.__section_start__[1] + offset)
            value = read_integer(self.__fobj__.read(1))
        return value
    @property
    def local_sub_category(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        if self.bufr_edition == 3:
            offset = 9
        if self.bufr_edition == 4:
            offset = 12
        
        self.__fobj__.seek(self.__section_start__[1] + offset)
        return read_integer(self.__fobj__.read(1))
    @property
    def master_table_version(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        offset = 10
        if self.bufr_edition == 4:
            offset += 3
        self.__fobj__.seek(self.__section_start__[1] + offset)
        return read_integer(self.__fobj__.read(1))
    @property
    def local_table_version(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        offset = 11
        if self.bufr_edition == 4:
            offset += 3
        self.__fobj__.seek(self.__section_start__[1] + offset)
        return read_integer(self.__fobj__.read(1))
    @property
    def file_date(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        offset = 12
        if self.bufr_edition == 4:
            offset += 3
        self.__fobj__.seek(self.__section_start__[1] + offset)
        if self.bufr_edition == 3:
            year = read_integer(self.__fobj__.read(1))
            month, day, hour, minute = read_integers(self.__fobj__.read(4), 1)
            second = 0
        elif self.bufr_edition == 4:
            year = read_integer(self.__fobj__.read(2))
            month, day, hour, minute, second = read_integers(self.__fobj__.read(5), 1)
        return (year, month, day, hour, minute, second)
    
    @property
    def file_year(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        offset = 12
        if self.bufr_edition == 4:
            offset += 3
        self.__fobj__.seek(self.__section_start__[1] + offset)
        year = parse_int(0, 2)
        if self.bufr_edition == 3:
            year = read_integer(self.__fobj__.read(1))
        elif self.bufr_edition == 4:
            year = read_integer(self.__fobj__.read(2))
        return year if year > 1500 else (2000 + year if year < 70 else 1900 + year)

    @property
    def file_month(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        offset = 13
        if self.bufr_edition == 4:
            offset += 4
        self.__fobj__.seek(self.__section_start__[1] + offset)
        return read_integer(self.__fobj__.read(1))
    @property
    def file_day(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        offset = 14
        if self.bufr_edition == 4:
            offset += 4
        self.__fobj__.seek(self.__section_start__[1] + offset)
        return read_integer(self.__fobj__.read(1))
    @property
    def file_hour(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        offset = 15
        if self.bufr_edition == 4:
            offset += 4
        self.__fobj__.seek(self.__section_start__[1] + offset)
        return read_integer(self.__fobj__.read(1))
    @property
    def file_minute(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        offset = 16
        if self.bufr_edition == 4:
            offset += 4
        self.__fobj__.seek(self.__section_start__[1] + offset)
        return read_integer(self.__fobj__.read(1))
    @property
    def file_second(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        value = parse_int(0, 1)
        if self.bufr_edition == 4:
            offset = 21
            self.__fobj__.seek(self.__section_start__[1] + offset)
            value = read_integer(self.__fobj__.read(1))
        return value
    @property
    def section_1_local_data(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        offset = 17
        if self.bufr_edition == 4:
            offset += 5
        self.__fobj__.seek(self.__section_start__[1] + offset)
        if self.section_2_present:
            end = self.__section_start__[2] - self.__section_start__[1] - offset
        else:
            end = self.__section_start__[3] - self.__section_start__[1] - offset
        return self.__fobj__.read(end)

    # Section 2 - Optional

    @property
    def section_2_local_data(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        data = b''
        if self.section_2_present:
            self.__fobj__.seek(self.__section_start__[2])
            end = self.__section_start__[3] - self.__section_start__[2] - 4
            data = self.__fobj__.read(end)
        return data
    
    # Section 3 - Data Description

    @property
    def number_of_subsets(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        self.__fobj__.seek(self.__section_start__[3] + 4)
        return read_integer(self.__fobj__.read(2))
    @property
    def observed_data(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        self.__fobj__.seek(self.__section_start__[3] + 6)
        return read_integer(self.__fobj__.read(1)) & 128 > 0
    @property
    def compressed(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        self.__fobj__.seek(self.__section_start__[3] + 6)
        return read_integer(self.__fobj__.read(1)) & 64 > 0
    @property
    def data_descriptors(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        self.__fobj__.seek(self.__section_start__[3] + 7)
        end = self.__section_start__[4] - self.__section_start__[3] - 7
        end -= end % 2
        data = read_integers(self.__fobj__.read(end), 2)
        return array([array([(x & ( 3 << 14)) >> 14,
                             (x & (63 <<  8)) >>  8,
                             (x &        255)      ]) for x in data])
    @property
    def section_4_data_bytes(self):
        if self.__fobj__.closed:
            raise ClosedBUFRFile('File already closed.')
        self.__fobj__.seek(self.__section_start__[4] + 4)
        end = self.__section_start__[5] - self.__section_start__[4]
        return BitMap(self.__fobj__.read(end))

    def expand_descriptors(self, file_descriptors):
        expanded_descriptors = []
        number_of_descriptors = len(file_descriptors)
        i = 0
        
        while i < number_of_descriptors:
            file_descriptor = file_descriptors[i]
            if file_descriptor[0] == 0:
                element = self.__table_b__.find(lambda id: id.f==file_descriptor[0] and id.x==file_descriptor[1] and id.y==file_descriptor[2])
                if not element.is_empty:
                    element = element.iloc(0)
                    expanded_descriptors.append(element)
            elif file_descriptor[0] == 1:
                if file_descriptor[2] == 0:
                    expanded_descriptors.append(DelayedReplication(file_descriptor[0], file_descriptor[1], file_descriptor[2], self.expand_descriptors(file_descriptors[i+2:i+file_descriptor[1]+2]), self.expand_descriptors(file_descriptors[i+1:i+2])[0]))
                    i += file_descriptor[1]+1
                else:
                    expanded_descriptors.append(Replication(file_descriptor[0], file_descriptor[1], file_descriptor[2], data_elements=self.expand_descriptors(file_descriptors[i+1:i+file_descriptor[1]+1])))
                    i += file_descriptor[1]
            elif file_descriptor[0] == 2:
                if file_descriptor[1] == 5:
                    expanded_descriptors.append(Operator.create(file_descriptor[0], file_descriptor[1], file_descriptor[2]))
                elif file_descriptor[1] == 6:
                    operator = Operator.create(file_descriptor[0], file_descriptor[1], file_descriptor[2])
                    expanded_descriptors.append(operator.apply(self.expand_descriptors(file_descriptors[i+1:i+2])[0]))
                    i += 1
            elif file_descriptor[0] == 3:
                sequence = self.__table_d__.find(lambda id: id.f==file_descriptor[0] and id.x==file_descriptor[1] and id.y==file_descriptor[2])
                if not sequence.is_empty:
                    if sequence.iloc(0).mnemonic in ['DRP16BIT', 'DRP8BIT', 'DRP1BIT', 'DRPSTAK']:
                        delayed_replication_sequence = sequence.iloc(0).get_descriptors()
                        expanded_descriptors.append(DelayedReplication(delayed_replication_sequence[0][0], delayed_replication_sequence[0][1], delayed_replication_sequence[0][2], self.expand_descriptors(file_descriptors[i+1:i+delayed_replication_sequence[0][1]+1]), self.expand_descriptors(delayed_replication_sequence[1:2])[0]))
                        i += delayed_replication_sequence[0][1]
                    else:
                        sequence = self.expand_descriptors(sequence.iloc(0).get_descriptors())
                        expanded_descriptors.extend(sequence)
            i += 1
        return expanded_descriptors

    @property
    def subsets(self):
        message_bitmap = self.section_4_data_bytes
        descriptors = self.expand_descriptors(self.data_descriptors)
        
        subsets_collection = SubsetCollection()

        for subset_number in range(self.number_of_subsets):
            subset = BUFRSubset(self.__table_f__)
            subset.metadata['subset_number'] = subset_number
            for i in range(len(descriptors)):
                value = descriptors[i].read_value(message_bitmap)
                subset.append(value)
            subsets_collection.append(subset)
        return subsets_collection

    def __str__(self):
        description = [
            {
                'Length of Section 0 (bytes)': lambda : '8',
                'Total Length of BUFR Message (bytes)': lambda : str(self.__section_start__[6]),
                'BUFR Edition Number': 'bufr_edition'
            },
            {
                'Length of Section 1 (bytes)': lambda : str(self.__section_start__[2] - self.__section_start__[1] if self.section_2_present else self.__section_start__[3] - self.__section_start__[1]),
                'BUFR Master Table': 'bufr_master_table',
                'Originating Center': 'originating_center',
                'Originating Sub-Center': 'originating_subcenter',
                'Update Sequence Number': 'update_sequence_number',
                'Flag (Presence of Section 2)': 'section_2_present',
                'BUFR Data Category': 'data_category' if DEBUG_LEVEL == 0 else 'data_category_description',
                'International Sub-Category': 'international_data_sub_category',
                'Local Sub-Category': 'local_sub_category',
                'Version Number of Master Table': 'master_table_version',
                'Version Number of Local Table': 'local_table_version',
                'Year': 'file_year',
                'Month': 'file_month',
                'Day': 'file_day',
                'Hour': 'file_hour',
                'Minute': 'file_minute',
                'Second': 'file_second',
                '': lambda :  '' if len(self.section_1_local_data) == 0 else '\n{0:=^50s}\n'.format(' Begin Additional Section 1 Data ') + '\n'.join(wrap(''.join(['%02x ' % b for b in self.section_1_local_data]), width=48)) + '\n' + '{0:=^50s}\n'.format(' End Additional Section 1 Data ')
            },
            {
                'Length of Section 1 (bytes)': lambda : str(self.__section_start__[3] - self.__section_start__[2] if self.section_2_present else 0),
                '': lambda :  '' if not self.section_2_present else '\n{0:=^50s}\n'.format(' Begin Optional Section 2 Data ') + '\n'.join(wrap(''.join(['%02x ' % b for b in self.section_2_local_data]), width=48)) + '\n' + '{0:=^50s}\n'.format(' End Optional Section 2 Data ')
            },
            {
                'Length of Section 3 (bytes)': lambda : str(self.__section_start__[4] - self.__section_start__[3]),
                'Number of Data Subsets': 'number_of_subsets',
                'Flag (Observed Data)': 'observed_data',
                'Flag (Compressed Data)': 'compressed',
                'Data Descriptors': lambda : '\n\n' + '\n'.join(wrap('  '.join(['{0:01d}-{1:02d}-{2:03d}'.format(*x) for x in self.data_descriptors]), width=50)) + '\n',
                'Expanded Descriptors': lambda : (('\n\n' + '\n'.join(wrap(', '.join([y.strip() for y in ('\n'.join([str(x) for x in self.expand_descriptors(self.data_descriptors)]).split('\n') )]), width=50))) if DEBUG_LEVEL == 0 else
                                                  ('\n\n' + '\n'.join([repr(x) for x in self.expand_descriptors(self.data_descriptors)])))
            },
            {
                'Length of Section 4 (bytes)': lambda : str(self.__section_start__[5] - self.__section_start__[4]),
                '': lambda :  '\n{0:=^50s}\n'.format(' Begin Section 4 Data ') + '\n'.join(wrap(str(self.section_4_data_bytes), width=51)) + '\n' + '{0:=^50s}\n'.format(' End Section 4 Data ')
            }
        ]



        output = ''

        for section in range(len(description)):
            output += '\n{0:^50s}\n\n'.format('BUFR Section {0:1d}'.format(section))
            for label, property_name in description[section].items():
                if type(property_name) == str:
                    output += '{0:<36s}{1:>14s}\n'.format(label, str(getattr(self, property_name)))
                else:
                    output += '{0:<36s}{1:>14s}\n'.format(label, property_name())
        return output