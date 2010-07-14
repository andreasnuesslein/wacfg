import os, sys
import tarfile, zipfile
import subprocess

from config import Config
from content import Content
from helpers import OUT

class tools:

    @staticmethod
    def archive_unpack():
        if Env.src and os.path.isfile(Env.src):
            OUT("src set correctly to: %s" % Env.src)
            srcfile = Env.src
        else:
            OUT("guessing name")
            names = [Env.pn, Env.pn+"-"+Env.pv, "latest"]
            suffixes = ["", ".tar", ".gz", ".bz2", ".tar.gz", ".tgz", ".tar.bz2", ".zip"]
            try:
                srcfile = [name+suffix for name in names for suffix in suffixes if os.path.isfile(name+suffix)][0]
            except IndexError:
                OUT("No archive found")
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


#    def wacfg_global_info_install():
#        OUT("write information to global db, e.g. /var/db/wacfg")
#        path = Env.cfg._dbdir
#        # ... XXX


    @staticmethod
    def archive_install():
        sboxpath_s = os.path.join(Env.sboxpath, '%s')
        destpath_s = os.path.join(Env.destpath, '%s')
        infofile = '.wacfg'
        contentfile = '.wacfg-%s-%s'

        manuallychanged = None

        if os.path.isdir(Env.destpath):
            if os.path.isfile(destpath_s % infofile):
                ex_content = Content(Env.destpath)
                metacsv = ex_content.readMetaCSV()
                manuallychanged = ex_content.checkCSV(
                        destpath_s % contentfile %
                        (metacsv['pn'], metacsv['pv'])
                        )

                OUT(manuallychanged)

                #act_content = Content(Env.)

                # update process
                # ex_info = Content().readMetaCSV(infofile)
                # ex_info[


            else:
                # XXX Folder exists, but no .wacfg-files...
                OUT("Either you installed this manually before or some \
                        goofball erased the .wacfg-files.\nEither way, I'm exiting")
                sys.exit(1)

        # Create a ContentCSV for sandboxdir
        Env.sboxcontent = Content(Env.sboxpath)
        Env.sboxcontent.writeCSV(sboxpath_s % contentfile % (Env.pn, Env.pv))
        Env.sboxcontent.writeMetaCSV(Env)

        # mv files that have been changed manually.
        if manuallychanged:
            for entry in manuallychanged:
                relpth = os.path.relpath(entry.path)
                ep = sboxpath_s % relpth
                epn = sboxpath_s % "._cfg%s_%s" % ("%04d", relpth)
                i = 0
                while True:
                    epntmp = epn % i
                    if not os.path.isfile(epntmp):
                        epn = epntmp
                        break
                    i+=1
                tools.mv(ep, epn)


        # do the actual "installation" / move
        try:
            os.makedirs(os.path.split(Env.destpath)[0])
        except:
            pass
        tools.rsync(Env.sboxpath, Env.destpath)
        return


    @staticmethod
    def mv(frompath, topath, wd="."):
        args = ["/bin/mv", frompath, topath]
        return subprocess.call(args, cwd=wd)


    @staticmethod
    def rsync(frompath, topath, wd="."):
        if not "/" == frompath[-1:]:
            frompath += "/"
        if not "/" == topath[-1:]:
            topath += "/"
        args = ["/usr/bin/rsync", "-a", frompath, topath]
        return subprocess.call(args, cwd=wd)


    @staticmethod
    def chmod(mode, path="", recursive=False):
        path = os.path.join(Env.sboxpath, path)
        args = ["/bin/chmod"]
        if recursive:
            args += ["-R"]
        args += [mode, path]
        return subprocess.call(args)


    @staticmethod
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


    @staticmethod
    def server_own(path="", recursive=False):
        suser = 'apache' # XXX set server-uid/gid here
        return tools.chown(path, suser, suser, recursive)


    @staticmethod
    def wget(path):
        output = path.split("/")[-1]
        args = ["/usr/bin/wget", "--continue"]
        args += ["--output-document=%s" % output]
        args += [path]
        subprocess.call(args)
        return output



class Env:
    pass


class WaCfg:

    def _src_unpack(self):
        tools.archive_unpack()

    def _src_config(self):
        pass

    def _src_install(self):
        tools.archive_install()

    def _post_install(self):
        pass


def main(Handler=WaCfg, source=None, vhost="localhost", installdir=None):

    # --------------------------------------
    # Setting the environment
    Env.cfg = Config()

    Env.vhost = vhost

    Env.pn = os.path.basename(os.path.dirname(os.getcwd()))
    Env.pv = os.path.basename(os.getcwd())
    Env.installdir = installdir or Env.pn
    Env.sboxpath = os.path.join(Env.cfg._sandboxroot, Env.pn)
    Env.destpath = os.path.join(Env.cfg.wwwroot, vhost, "htdocs", Env.installdir)

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

