
from qtpy.QtGui import *
from qtpy.QtCore import *

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
import os

class Config(QObject):
    """
    The Config class keeps track of the configuration in a QObject, so that it 
    can be passed via signals and slots.
    """
    def __init__(self, file_name):
        """
        Construct a Config object.
        file_name:  The name of the file to store configuration information in.
        """
        super(Config, self).__init__()

        self._file_name = file_name
        self._cfg = ConfigParser.RawConfigParser()
        if os.path.exists(file_name):
            self._cfg.read(file_name)

    def __getitem__(self, item):
        """
        Get an item from the configuration. The call should look like this:
        value = config['section', 'field']
        """
        section, field = item
        return self._cfg.get(section, field)

    def __setitem__(self, item, value):
        """
        Set an item in the configuration, overwriting what's already there. The call should look like this:
        config['section', 'field'] = value
        """
        section, field = item
        if not self._cfg.has_section(section):
            self._cfg.add_section(section)

        self._cfg.set(section, field, value)

    def __contains__(self, item):
        """
        Check to see if an item is in the configuration. The call should look like this:
        ('field', 'section') in config
        """
        section, field = item
        return self._cfg.has_option(section, field)

    def __iter__(self):
        """
        Iterate over all the fields in the configuration. The call might look like this:
        for (section, field), value in config: # ...
        """
        for section in self._cfg.sections():
            for field in self._cfg.options(section):
                yield (section, field), self[section, field]

    def initialize(self, cfg_dict):
        """
        Add items in the configuration. This function doesn't modify items that already exist.
        cfg_dict:   A dictionary of configuration items. Keys are (section, field) tuples, and the values
                    are the configuration values.
        """
        for item, value in cfg_dict.items():
            if item not in self:
                self[item] = value

    def toFile(self):
        """
        Write the configuration to the file.
        """
        self._cfg.write(open(self._file_name, 'w'))
