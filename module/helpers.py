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

    ## XXX currently trying to find the file.. is this smart?
    if not src_path:
        raise Exception("No archive found")

    return src_path

