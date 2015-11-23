
from PySide.QtGui import *
from PySide.QtCore import *

import ConfigParser
import os

class Config(QObject):
    def __init__(self, file_name):
        super(Config, self).__init__()

        self._file_name = file_name
        self._cfg = ConfigParser.RawConfigParser()
        if os.path.exists(file_name):
            self._cfg.read(file_name)

    def __getitem__(self, item):
        section, field = item
        return self._cfg.get(section, field)

    def __setitem__(self, item, value):
        section, field = item
        if not self._cfg.has_section(section):
            self._cfg.add_section(section)

        self._cfg.set(section, field, value)

    def __contains__(self, item):
        section, field = item
        return self._cfg.has_option(section, field)

    def initialize(self, cfg_dict):
        for item, value in cfg_dict.iteritems():
            if item not in self:
                self[item] = value

    def toFile(self):
        self._cfg.write(open(self._file_name, 'w'))
