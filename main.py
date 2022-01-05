import sys
from logging import getLogger, Logger
from platform import system

PY3K: bool = False
USER_HOME: str = 'HOME'

if sys.version_info.major > 2:
    PY3K = True

if PY3K is True:
    pass
else:
    pass

logger: Logger = getLogger('pyhue')

if system() == 'Windows':
    USER_HOME = 'USERPROFILE'
