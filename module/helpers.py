import os, sys
import tarfile, zipfile

def _get_uid(username):
    from pwd import getpwnam
    return getpwnam(username)[2]
def _get_gid(groupname):
    from grp import getgrnam
    return getgrnam(groupname)[2]


def _find_src(src):
    certain = False
    sources = None
    src = os.path.relpath(src)

    src_path = None
    tries = [src, src+".tar", src+".gz", src+".bz2", src+".tar.gz", src+".tar.bz2"]
    tries += [src+".zip"]

    for i in tries:
        if os.path.isfile(i):
            src_path = i
            certain = True
            break

    ## XXX currently trying to find the file.. is this smart?
    if not src_path:
        count = 0
        for i in os.listdir("."):
            if "zip" in i or ".tar" in i:
                count = count + 1
                src_path = i
        if count > 1:
            raise Exception("More than one possible archive found.")


    if zipfile.is_zipfile(src_path):
        sources = zipfile.ZipFile(i)
    elif tarfile.is_tarfile(src_path):
        sources = tarfile.open(i)
    else:
        raise Exception("Not a valid archive")

    return sources

