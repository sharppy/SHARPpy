from collections import namedtuple
from re import sub

from .tables import ElementDefinition, parse_int
from .values import ReplicationGroup, ReplicationSequence

class Replication(ElementDefinition):
    __slots__ = ('id', 'data_elements')
    __id_class__ = namedtuple('ReplicationID', ('f', 'x', 'y'))
    mnemonic = "REPL"
    name = 'Replication'
    def __init__(self, f, x, y, data_elements):
        super().__initialize_id__(self.__id_class__(
            f=parse_int(f, 1), 
            x=parse_int(x, 1), 
            y=parse_int(y, 1)
        ))
        self.data_elements = data_elements
    def __repr__(self):
        base = super().__repr__()
        return base[:base.find(', data_elements')] + ', \n    replication_count={0}, \n    data_elements=[\n        {1}\n    ]\n)'.format(self.x, ',\n        '.join([repr(x) for x in self.data_elements]))
    def __str__(self):
        return super().__str__() + '\n ' + '\n '.join([str(x) for x in self.data_elements])
    def read_replication(self, bit_map, count):
        output = ReplicationGroup(self)
        for i in range(count):
            values = ReplicationSequence()
            for element in self.data_elements:
                values.append(element.read_value(bit_map))
            output.append(values)
        return output
    def read_value(self, bit_map):
        return self.read_replication(bit_map, self.x)
    
class DelayedReplication(Replication):
    __slots__ = ('id', 'data_elements', 'replication_element', )
    __id_class__ = namedtuple('DelayedReplicationID', ('f', 'x', 'y'))
    mnemonic = "DREPL"
    name = 'Delayed Replication'
    def __init__(self, f, x, y, data_elements, replication_element):
        super().__init__(f, x, y, data_elements)
        self.replication_element = replication_element
    def __repr__(self):
        base = super().__repr__()
        return sub(r'replication_count=[^\s]*', 'replication_element={0}'.format(repr(self.replication_element)), base)
    def read_value(self, bit_map):
        n = self.replication_element.read_value(bit_map)
        return self.read_replication(bit_map, n.data)