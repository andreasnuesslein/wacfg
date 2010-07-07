VERSION = (0, 1, 0, 'final', 0)

def __version__():
    version = '%d.%d.%d' % VERSION[0:3]
    if VERSION[3] != 'final':
        version += '_%s%d' % VERSION[3:]
    return version

