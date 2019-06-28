
VERSION = (0, 0, 3)

__version__ = '.'.join(map(str, VERSION))
__author__ = 'https://github.com/Y4hL'
__license__ = 'GNU GPLv3'
__copyright__ = 'Copyright 2019 Y4hL'


from .Gmail import *
from .exceptions import *
