import os, sys
import tarfile, zipfile

def _get_uid(username):
    from pwd import getpwnam
    return getpwnam(username)[2]
def _get_gid(groupname):
    from grp import getgrnam
    return getgrnam(groupname)[2]


def _find_src(src):
    sources = None
    if not src:
        src = os.path.relpath(src)

    src_path = None
    tries = [src, src+".tar", src+".gz", src+".bz2", src+".tar.gz", src+".tar.bz2"]
    tries += [src+".zip"]

    for i in tries:
        if os.path.isfile(i):
            src_path = i
            break

    if not src_path:
        raise Exception("No archive found")

    return src_path

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

