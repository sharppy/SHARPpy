from collections import namedtuple

class Template(namedtuple("_Template", ["name", "descriptors"])):
    """BUFR message template

    Describes a BUFR message by listing the descriptors that are
    present in the message. The same descriptors must be present in
    the same order in Section 3 of the actual message. The template
    includes descriptions, length, units and other information
    required to interpret the descriptor references in the message.

    Possible descriptor types are :class:`.ElementDescriptor`,
    :class:`.ReplicationDescriptor`, :class:`.SequenceDescriptor` and
    :class:`.OperatorDescriptor`.

    :ivar name: Name of the template
    :ivar descriptors: List of descriptors

    """
    __slots__ = ()

