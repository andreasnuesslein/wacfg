import os, sys
import tarfile, zipfile
import subprocess
import time
import logging

from .config import Config
from .content import Content
from .helpers import identify_server
from .vercmp import pkgsplit
from . import optparsing
from .output import *

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
            OUT.debug("Source set correctly to: %s" % Env.src)
        else:
            OUT.debug("Guessing sourcefile from packagename...")
            names = [Env.pn, Env.pn+"-"+Env.pv]
            suffixes = ["", ".tar", ".gz", ".bz2", ".tar.gz", ".tgz", ".tar.bz2", ".zip", ".ZIP"]
            try:
                Env.src = [name+suffix for name in names for suffix in suffixes if os.path.isfile(name+suffix)][0]
            except IndexError:
                OUT.error("No sourcefile explicitely set or found in this folder")
                sys.exit(1)

        if zipfile.is_zipfile(Env.src):
            source = zipfile.ZipFile(Env.src)
        elif tarfile.is_tarfile(Env.src):
            source = tarfile.open(Env.src)
        else:
            OUT.error("Not a valid archive")
            sys.exit(1)

        source.extractall(path = Env.sboxpath)

        #----------------------------------------------------------
        # Check whether we extracted a folder into a folder...
        dir = os.listdir(Env.sboxpath)
        if len(dir) == 0:
            OUT.error("No files in sandbox, something went wrong")
            sys.exit(1)
        if len(dir) == 1:
            wd = os.path.dirname(Env.sboxpath)
            tmpdir = "._unzip%s" % (Env.pn)
            tools.mv(os.path.join(Env.sboxpath,dir[0]),tmpdir,wd)
            tools.rm(Env.sboxpath, recursive=True)
            tools.mv(tmpdir, Env.sboxpath, wd)

        return

    @staticmethod
    def archive_install():
        sboxpath_s = os.path.join(Env.sboxpath, '%s')
        destpath_s = os.path.join(Env.destpath, '%s')

        manuallychanged = None

        if os.path.isdir(Env.destpath):
            if os.path.isfile(destpath_s % '.wacfg'):
                content = Content(Env.destpath)
                csventries = content.readCSV()
                manuallychanged = content.setOperation( lambda x,y: y-x )
                manuallychanged = [ file for file in manuallychanged if os.path.exists(file.abspath) ]
                if manuallychanged:
                    OUT.info('The following files have been changed manually:')
                    for file in manuallychanged:
                        OUT.info("\t- %s" % os.path.normpath(file.abspath))
                    OUT.info('\nPlease run:')
                    OUT.info('CONFIG_PROTECT="tmp/installed/localhost/htdocs/wordpress/" etc-update')

            else:
                # XXX Folder exists, but no .wacfg-files...
                OUT.error("Either you installed this manually before or some \
                        goofball erased the .wacfg-files.\nEither way, I'm exiting")
                sys.exit(1)

        # Create a ContentCSV for sandboxdir
        Env.sboxcontent = Content(Env.sboxpath, Env.pn, Env.pv)
        Env.sboxcontent.writeCSV()
        Env.sboxcontent.writeMetaCSV(Env)

        # Move files that have custom changes
        if manuallychanged:
            for entry in manuallychanged:
                if entry.type != "dir":
                    relpth = os.path.relpath(entry.path)
                    ep = sboxpath_s % relpth
                    epntmp = os.path.join(os.path.split(relpth)[0],
                            "._cfg%s_%s" % ("%04d", os.path.split(relpth)[1]) )
                    epn = sboxpath_s % epntmp
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
            OUT.error("Rsync exited abnormally :-(")
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
    def chown(owner, group=None, path=".", recursive=False):
        path = os.path.join(Env.sboxpath, path)
        args = ["/bin/chown", "--silent"]
        if recursive:
            args += ["--recursive"]
        if group:
            args += ["%s:%s" % (owner,group)]
        else:
            args += [owner]
        args += [path]
        OUT.debug("Chown-arguments: %s" % args)
        if subprocess.call(args):
            OUT.warn("chown exited abnormally.")
        return


    @staticmethod
    def server_own(path=".", recursive=False):
        return tools.chown(Env.server, Env.server, path, recursive)


    @staticmethod
    def wget(path):
        try:
            os.mkdir("sources/")
        except:
            pass
        output = os.path.join("sources/",path.split("/")[-1])
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
        Env.src = output
        return output



class Env:
    pass


class WaCfg:

    def _src_unpack(self):
        tools.archive_unpack()

    def _src_config(self):
        tools.server_own(recursive=True)

    def _src_install(self):
        tools.archive_install()

    def _post_install(self):
        pass


def install():
    if os.path.isfile(os.path.join(Env.destpath, '.wacfg')):
        OUT.warn("Directory alread exists at %s" % Env.destpath)
        OUT.warn('Use upgrade instead of install.')
    else:
        upgrade()

def upgrade():
    OUT.debug("Unpacking source...")
    Env.App.src_unpack() if "src_unpack" in dir(Env.App) else Env.App._src_unpack()

    OUT.debug("Configuring source...")
    Env.App.src_config() if "src_config" in dir(Env.App) else Env.App._src_config()

    OUT.debug("Installing...")
    Env.App.src_install() if "src_install" in dir(Env.App) else Env.App._src_install()

    OUT.debug("PostInst...")
    Env.App.post_install() if "post_install" in dir(Env.App) else Env.App._post_install()

    OUT.info("Successfully installed webapp to %s" % (Env.destpath))

def remove():
    destpath_s = os.path.join(Env.destpath, '%s')

    if os.path.isfile(destpath_s % '.wacfg'):
        content = Content(Env.destpath)
        content.readCSV()
        content.removeFiles()

def purge():
    if not os.path.isfile(os.path.join(Env.destpath, '.wacfg')):
        OUT.error("The given path does not contain a wacfg-installation.. aborting")
        sys.exit(1)
    else:
        OUT.warn("The directory '%s' will be completely deleted with all its contents." % Env.destpath)
        x = raw_input("Are you sure? (y/N) ")
        if x in "yYjJ":
            tools.rm(Env.destpath, recursive=True)


def main(Handler=WaCfg, source=None, vhost=None, installdir=None, server=None, wwwroot=None):

    # ------------------------------------------------------------------------
    # Optionparser
    parser = optparsing.waopts()
    (Env.options, Env.args) = parser.parse_args()
    if Env.options.verbosity:
        OUT.setLevel(logging.DEBUG)

    OUT.debug("Optparse Options: %s" % Env.options)
    OUT.debug("Optparse Arguments: %s" % Env.args)

    # ------------------------------------------------------------------------
    # Setting the environment
    Env.p = os.path.basename(sys.argv[0])[:-3]
    Env.pn, Env.pv, Env.rev = pkgsplit(Env.p)

    Env.cfg = Config
    Env.vhost = Env.options.vhost or vhost or "localhost"
    Env.installdir = Env.options.installdir or installdir or Env.pn
    Env.server = Env.options.server or server or identify_server()
    Env.wwwroot = Env.options.wwwroot or wwwroot or "/var/www"
    OUT.debug("Server: %s" % Env.server)
    OUT.debug("Wwwroot: %s" % Env.wwwroot)
    Env.sboxpath = os.path.join(Env.cfg._sandboxroot, Env.pn)
    Env.destpath = os.path.join(Env.wwwroot,
            Env.vhost, "htdocs", Env.installdir)

    if source:
        source = source % {
                'PN':Env.pn,
                'PV':Env.pv,
                'P' :"%s-%s" % (Env.pn, Env.pv)}
        if source.startswith(("ftp://","http://")):
            Env.src = tools.wget(source)
        else:
            Env.src = os.path.join("sources",source)

    Env.App = Handler()

    # ------------------------------------------------------------------------
    try:
        {'install': install,
        'upgrade': upgrade,
        'remove': remove,
        'purge': purge,
        }[Env.args[0]]()
    except KeyError as e:
        OUT.error("You've entered an invalid command: %s" % e)
    except IndexError as e:
        OUT.warn("No command given, doing upgrade")
        upgrade()

