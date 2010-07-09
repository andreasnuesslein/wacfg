import os, sys
import tarfile, zipfile


def OUT(str, verbosity=1):
    print(str)

def _get_uid(username):
    from pwd import getpwnam
    return getpwnam(username)[2]
def _get_gid(groupname):
    from grp import getgrnam
    return getgrnam(groupname)[2]

def _find_distro():
    distros = [
            ('gentoo', '/etc/gentoo-release'),
            ('debian', '/etc/debian_version'),
            ]
    for (distro, file) in distros:
        if os.path.isfile(file):
            return distro
    raise Exception("distribution unknown")

def _find_server():
    (distro, path) = _find_distro()
    if distro == 'gentoo':
        path = '/var/db/pkg/www-servers/'
        dirs = os.listdir(path)
        if len(dirs) != 1:
            pass
        pass
    pass



#def vprint(str, level = 1):
#    if VERBOSITY >= level:
#        print(str)


def uniq(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]

