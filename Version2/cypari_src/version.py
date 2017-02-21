from collections import namedtuple
class Version(namedtuple('Version', ['major', 'minor', 'micro', 'tag'])):
    def __str__(self):
        return '%s.%s.%s%s'%self
    
version_info = Version(2, 1, 0, '')
__version__ = str(version_info)
        
