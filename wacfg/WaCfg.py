import os, sys
import tarfile, zipfile
import subprocess

from config import Config
from content import Content
from helpers import OUT

class tools:

    def archive_unpack():

        if Env.src and os.path.isfile(Env.src):
            print("src set correctly to: %s" % Env.src)
            srcfile = Env.src
        else:
            print("guessing name")
            names = [Env.pn, Env.pn+"-"+Env.pv, "latest"]
            suffixes = ["", ".tar", ".gz", ".bz2", ".tar.gz", ".tgz", ".tar.bz2", ".zip"]
            try:
                srcfile = [name+suffix for name in names for suffix in suffixes if os.path.isfile(name+suffix)][0]
            except IndexError:
                print("No archive found")
                sys.exit(1)

        if zipfile.is_zipfile(srcfile):
            source = zipfile.ZipFile(srcfile)
        elif tarfile.is_tarfile(srcfile):
            source = tarfile.open(srcfile)
        else:
            raise Exception("Not a valid archive")

        source.extractall(path = Env.sboxpath)

        #----------------------------------------------------------
        # Check whether we extracted a folder into a folder...
        dir = os.listdir(Env.sboxpath)
        if len(dir) == 0:
            raise Exception("no files in sandbox, something went wrong")
        if len(dir) == 1:
            wd = os.path.dirname(Env.sboxpath)
            tmpdir = "._unzip%s" % (Env.pn)
            tools.mv(os.path.join(Env.sboxpath,dir[0]),tmpdir,wd)
            os.rmdir(Env.sboxpath)
            tools.mv(tmpdir, Env.sboxpath, wd)

        return


    def wacfg_global_info_install():
        print("write information to global db, e.g. /var/db/wacfg")
        path = Env.cfg._dbdir
        # ... XXX


    def archive_update():
        print("update archive")
        # ... XXX


    def archive_install():
        csvfile = '.wacfg-%s-%s' % (Env.pn, Env.pv)
        if os.path.isdir(Env.destpath):
            if os.path.isfile(os.path.join(Env.destpath, csvfile)):
                return tools.archive_update()
            else:
                print("Either you installed this manually before or some \
                        goofball erased the .wacfg-files.\nEither way, I'm exiting")
                sys.exit(1)
        else:
            # Create a ContentCSV for sandboxdir
            Env.sboxcontent = Content(Env.sboxpath)
            Env.sboxcontent.writeCSV(os.path.join(Env.sboxpath, csvfile))

            try:
                os.makedirs(os.path.dirname(Env.destpath))
            except:
                pass
            tools.mv(Env.sboxpath, os.path.dirname(Env.destpath))

            return


    def mv(frompath, topath, wd="."):
        args = ["/bin/mv", frompath, topath]
        #if Config.verbosity:
        #    args += ["-v"]
        return subprocess.call(args, cwd=wd)

    def chmod(mode, path="", recursive=False):
        path = os.path.join(Env.sboxpath, path)
        args = ["/bin/chmod"]
        if recursive:
            args += ["-R"]
        args += [mode, path]
        return subprocess.call(args)


    def chown(owner, group=None, path="", recursive=False):
        path = os.path.join(Env.sboxpath, path)
        args = ["/bin/chown"]
        if recursive:
            args += ["-R"]
        if group:
            args += ["%s:%s" % (owner,group)]
        else:
            args += [owner]
        args += [path]
        return subprocess.call(args)


    def server_own(path="", recursive=False):
        suser = 'apache'
        return tools.chown(path, suser, suser, recursive)




class Env:
    pass

class WaCfg:

    def _src_unpack(self):
        tools.archive_unpack()

    def _src_config(self):
        tools.chmod("0755", recursive=True)
        tools.server_own(recursive=True)

    def _src_install(self):
        tools.archive_install()

    def _post_install(self):
        pass


def main(Handler=WaCfg, source=None, vhost="localhost"):

    # --------------------------------------
    # Setting the environment
    Env.cfg = Config()

    Env.vhost = vhost

    Env.pn = os.path.basename(os.path.dirname(os.getcwd()))
    Env.pv = os.path.basename(os.getcwd())
    Env.sboxpath = os.path.join(Env.cfg._sandboxroot, Env.pn)
    Env.destpath = os.path.join(Env.cfg.wwwroot, vhost, "htdocs", Env.pn)

    Env.src = source
    if Env.src:
        Env.src = Env.src % {
                'PN':Env.pn,
                'PV':Env.pv,
                'P' :"%s-%s" % (Env.pn, Env.pv)}
        if Env.src.startswith(("ftp://","http://")):
            Env.src = tools.wget(Env.src)


    App = Handler()


    # --------------------------------------
    # Going through the 4 steps...
    OUT("Unpacking source...")
    App.src_unpack() if "src_unpack" in dir(App) else App._src_unpack()

    OUT("Configuring source...")
    App.src_config() if "src_config" in dir(App) else App._src_config()

    OUT("Installing...")
    App.src_install() if "src_install" in dir(App) else App._src_install()

    OUT("PostInst...")
    App.post_install() if "post_install" in dir(App) else App._post_install()


    OUT("May the source be with you...")

