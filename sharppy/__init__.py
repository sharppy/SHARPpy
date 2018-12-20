#from . import _sharppy_version as version

__all__ = ['version', 'sharptab', 'viz', 'databases', 'io', 'plot']

#__version__ = version.get_version()

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

