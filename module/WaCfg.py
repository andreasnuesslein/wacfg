import os, sys
import tarfile, zipfile
import subprocess

import helpers

""" GLOBAL DEFINITIONS """
_sandboxdir = "/home/nutz/work/tmp/wacfg/sandbox/"
_wwwdir = "/home/nutz/work/tmp/wacfg/installed/"

VERBOSITY = 0

def vprint(str, level = 1):
    if VERBOSITY >= level:
        print(str)

class tools:
    def archive_unpack(src):
        src_path = helpers._find_src(src)
        if zipfile.is_zipfile(src_path):
            source = zipfile.ZipFile(src_path)
        elif tarfile.is_tarfile(src_path):
            source = tarfile.open(src_path)
        else:
            raise Exception("Not a valid archive")

        pkgname = "%s-%s" % (os.path.split(os.path.split(os.getcwd())[0])[1],
                os.path.split(os.getcwd())[1])
        path = os.path.join(_sandboxdir, pkgname)
        source.extractall(path = path)
        dir = os.listdir(path)
        if len(dir) == 0:
            Exception("no files in sandbox, something went wrong")
        if len(dir) == 1:
            """ If the archive created another directory, mv one up """
            wd = os.path.dirname(path)
            tmpdir = "._unzip%s" % (pkgname)
            args = ["/bin/mv", os.path.join(path,dir[0]), tmpdir]
            subprocess.call(args, cwd=wd)
            os.rmdir(path)
            args = ["/bin/mv", tmpdir, path]
            subprocess.call(args, cwd=wd)

        print(pkgname)
        return(pkgname)


    def archive_install():
        pass

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
        args = ["/bin/chmod", mode, path]
        return subprocess.call(args)

    def chmod_r(path, mode):
        for x in os.listdir(path):
            abspath = os.path.join(path, x)
            tools.chmod(abspath, mode)
            if os.path.isdir(abspath):
                tools.chmod_r(abspath, mode)


    ## XXX tool for regex'ing paths and files would be good, so one can easily chmod those.



class WaCfg:
    pkgname = ""
    def _src_unpack(self, src):
        if not src:
            src = os.path.basename(os.path.abspath(os.path.curdir))
        self.pkgname = tools.archive_unpack(src)

    def _src_config(self):
        path = os.path.join(_sandboxdir, self.pkgname)
        tools.chmod_r(path, "0700")
        print(self.pkgname)



    def _src_install(self):
        tools.archive_install()




def main(Handler, source=None):
    App = Handler()

    print("Unpacking source...")
    if "src_unpack" in dir(App):
        App.src_unpack()
    else:
        App._src_unpack(source)

    print("Configuring source...")
    if "src_config" in dir(App):
        App.src_config()
    else:
        App._src_config()

    print("Installing...")
    if "src_install" in dir(App):
        App.src_install()
    else:
        App._src_install()



    print("May the source be with you...")



