import os, sys
import tarfile, zipfile
import subprocess
import time

from .config import Config
from .content import Content
from .helpers import OUT
from .vercmp import pkgsplit
from WaCfg import optparsing

VERSION = (0, 1, 0, 'final', 0)

def __version__():
    version = '%d.%d.%d' % VERSION[0:3]
    if VERSION[3] != 'final':
        version += '_%s%d' % VERSION[3:]
    return version


class tools:

    @staticmethod
    def archive_unpack():
        if Env.src and os.path.isfile(Env.src):
            OUT("Source set correctly to: %s" % Env.src, 2)
        else:
            OUT("Guessing sourcefile from packagename...", 2)
            names = [Env.pn, Env.pn+"-"+Env.pv]
            suffixes = ["", ".tar", ".gz", ".bz2", ".tar.gz", ".tgz", ".tar.bz2", ".zip", ".ZIP"]
            try:
                Env.src = [name+suffix for name in names for suffix in suffixes if os.path.isfile(name+suffix)][0]
            except IndexError:
                OUT("No sourcefile explicitely set or found in this folder", 0)
                sys.exit(1)

        if zipfile.is_zipfile(Env.src):
            source = zipfile.ZipFile(Env.src)
        elif tarfile.is_tarfile(Env.src):
            source = tarfile.open(Env.src)
        else:
            OUT("Not a valid archive", 0)
            sys.exit(1)

        source.extractall(path = Env.sboxpath)

        #----------------------------------------------------------
        # Check whether we extracted a folder into a folder...
        dir = os.listdir(Env.sboxpath)
        if len(dir) == 0:
            OUT("No files in sandbox, something went wrong", 0)
            sys.exit(1)
        if len(dir) == 1:
            wd = os.path.dirname(Env.sboxpath)
            tmpdir = "._unzip%s" % (Env.pn)
            tools.mv(os.path.join(Env.sboxpath,dir[0]),tmpdir,wd)
            tools.rm(Env.sboxpath, recursive=True)
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
                infocsv = destpath_s % contentfile % (metacsv['pn'], metacsv['pv'])
                manuallychanged = ex_content.checkCSV(infocsv)
                tools.rm(infocsv)

                if manuallychanged:
                    OUT('The following files have been manually changed:')
                    for file in manuallychanged:
                        OUT("\t- %s" % file.path)
                    OUT('\nPlease run:')
                    OUT('CONFIG_PROTECT="tmp/installed/localhost/htdocs/wordpress/" etc-update')

            else:
                # XXX Folder exists, but no .wacfg-files...
                OUT("Either you installed this manually before or some \
                        goofball erased the .wacfg-files.\nEither way, I'm exiting", 0)
                sys.exit(1)

        # Create a ContentCSV for sandboxdir
        Env.sboxcontent = Content(Env.sboxpath)
        Env.sboxcontent.writeCSV(sboxpath_s % contentfile % (Env.pn, Env.pv))
        Env.sboxcontent.writeMetaCSV(Env)

        # Move files that have been changed manually
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
        if tools.rsync(Env.sboxpath, Env.destpath) == 0:
            tools.rm(Env.sboxpath, recursive=True)
        else:
            OUT("Rsync exited abnormally :-(", 0)
            sys.exit(1)
        return


    @staticmethod
    def rm(rmpath, wd=".", recursive=False):
        args = ["/bin/rm"]
        if recursive:
            args += ["-r"]
        args += [rmpath]
        return subprocess.call(args, cwd=wd)

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
        suser = Env.server # XXX set server-uid/gid here
        return tools.chown(path, suser, suser, recursive)


    @staticmethod
    def wget(path):
        output = path.split("/")[-1]
        args = ["/usr/bin/wget", "--continue", "--no-verbose"]
        args += ["--output-document=%s" % output]
        args += [path]
        p1 = subprocess.call(args)
#        #print(p1.poll())
#        i=1
#        while not p1.poll() and p1.poll() != 0:
#            dots = "."*(i%4)
#            i+=1
#            print("\rDownloading %s" % dots),
#            sys.stdout.flush()
#            time.sleep(0.1)
#        print(" done\n")
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


def main(Handler=WaCfg, source=None, vhost=None, installdir=None, server=None):
    parser = optparsing.waopts()

    (Env.options, Env.args) = parser.parse_args()
    print(Env.options)
    print(Env.args)

    # ------------------------------------------------------------------------
    # Setting the environment
    Env.p = os.path.basename(sys.argv[0])[:-3]
    Env.pn, Env.pv, Env.rev = pkgsplit(Env.p)
    #sys.exit(1)

    Env.cfg = Config()
    Env.vhost = Env.options.vhost or vhost or "localhost"
    Env.installdir = Env.options.installdir or installdir or Env.pn
    Env.server = Env.options.server or server or "apache"
    Env.sboxpath = os.path.join(Env.cfg._sandboxroot, Env.pn)
    Env.destpath = os.path.join(Env.cfg.wwwroot,
            Env.vhost, "htdocs", Env.installdir)

    Env.src = source
    if Env.src:
        Env.src = Env.src % {
                'PN':Env.pn,
                'PV':Env.pv,
                'P' :"%s-%s" % (Env.pn, Env.pv)}
        if Env.src.startswith(("ftp://","http://")):
            Env.src = tools.wget(Env.src)

    Env.App = Handler()

    try:
        {'install': install,
        'upgrade': upgrade,
        'remove': remove,
        'purge': purge,
        }[Env.args[0]]()
    except:
        upgrade()



def install():
    destpath_s = os.path.join(Env.destpath, '%s')
    if os.path.isfile(destpath_s % '.wacfg'):
        print("Directory alread exists at %s\n Please use upgrade instead." % Env.destpath)
    else:
        upgrade()

def upgrade():

    # --------------------------------------
    # Going through the 4 steps...
    OUT("Unpacking source...", 2)
    Env.App.src_unpack() if "src_unpack" in dir(Env.App) else Env.App._src_unpack()

    OUT("Configuring source...", 2)
    Env.App.src_config() if "src_config" in dir(Env.App) else Env.App._src_config()

    OUT("Installing...", 2)
    Env.App.src_install() if "src_install" in dir(Env.App) else Env.App._src_install()

    OUT("PostInst...", 2)
    Env.App.post_install() if "post_install" in dir(Env.App) else Env.App._post_install()


def remove():
    sboxpath_s = os.path.join(Env.sboxpath, '%s')
    destpath_s = os.path.join(Env.destpath, '%s')
    infofile = '.wacfg'
    contentfile = '.wacfg-%s-%s'

    if os.path.isfile(destpath_s % '.wacfg'):
        print("fooo")
        ex_content = Content(Env.destpath)
        metacsv = ex_content.readMetaCSV()
        infocsv = destpath_s % contentfile % (metacsv['pn'], metacsv['pv'])
        entries = ex_content.readCSV(infocsv)
        for entry in entries:
            print(entry)
            entry.delete()



def purge():
    if not os.path.isfile(os.path.join(Env.destpath, '.wacfg')):
        print("The given path does not contain a wacfg-installation.. aborting")
        sys.exit(1)
    else:
        print("The directory '%s' will be completely deleted with all its contents." % Env.destpath)
        x = raw_input("Are you sure? (y/N) ")
        if x in "yYjJ":
            tools.rm(Env.destpath, recursive=True)
