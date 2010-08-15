import os, sys

from .output import *
from .vercmp import pkgsplit
from .helpers import identify_server
from .tools import Tools
from .webapp import ApplicationVersion


VERSION = (0, 1, 0, 'final', 0)

def __version__():
    version = '%d.%d.%d' % VERSION[0:3]
    if VERSION[3] != 'final':
        version += '_%s%d' % VERSION[3:]
    return version


class Env:
    pass
tools = Tools(Env)


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
    ApplicationVersion(path = Env.destpath).cur_content.removeFiles()

def purge():
    if not os.path.isfile(os.path.join(Env.destpath, '.wacfg')):
        OUT.error("The given path does not contain a wacfg-installation.. aborting")
        sys.exit(1)
    else:
        OUT.warn("The directory '%s' will be completely deleted with all its contents." % Env.destpath)
        try:
            x = raw_input("Are you sure? (y/N) ") # PY2
        except NameError:
            x = input("Are you sure? (y/N) ") # PY3
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

    Env.sboxroot = "/var/tmp/webapps/"
    Env.vhost = Env.options.vhost or vhost or "localhost"
    Env.installdir = Env.options.installdir or installdir or Env.pn
    Env.server = Env.options.server or server or identify_server()
    Env.wwwroot = Env.options.wwwroot or wwwroot or "/var/www"
    OUT.debug("Server: %s" % Env.server)
    OUT.debug("Wwwroot: %s" % Env.wwwroot)
    Env.sboxpath = os.path.join(Env.sboxroot, Env.pn)
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

