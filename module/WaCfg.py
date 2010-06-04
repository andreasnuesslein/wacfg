import os, sys
import tarfile, zipfile

import helpers

""" GLOBAL DEFINITIONS """
_sandboxdir = "/home/nutz/work/tmp/"

class tools:
    def archive_unpack(src):
        source = helpers._find_src(src)
        return source.extractall(path = _sandboxdir)

    def chown(path, uid=-1, gid=-1, user=None, group=None):
        if type(user) == type(""):
            try:
                uid = _get_uid(user)
            except:
                raise Exception("invalid username")
        if type(group) == type(""):
            try:
                gid = _get_gid(group)
            except:
                raise Exception("invalid groupname")

        return os.lchown(path, uid, gid)

    def chmod(path, mode):
        if len(mode) == 3:
            mode = "0"+mode
        return os.chmod(path, mode)

    ## XXX tool for regex'ing paths and files would be good, so one can easily chmod those.



class WaCfg:
    def _src_unpack(self, src):
        if not src:
            src = os.path.basename(os.path.abspath(os.path.curdir))
        tools.archive_unpack(src)

    def _src_config(self):

        pass






def main(Handler, source=None):
    print("Unpacking source...")
    try:
        Handler().src_unpack()
    except:
        Handler()._src_unpack(source)

    print("Configuring source...")


    print("May the source be with you...")



