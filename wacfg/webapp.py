import os
import subprocess

from .helpers import *
from .vercmp import *
from .output import OUT
from .content import Content


#import ipdb;ipdb.set_trace()

class Env:
    appdir = "/var/lib/webapps/"



class ApplicationVersion:
    '''
    An Application instance with a specific Version

    ApplicationVersion also has cur_content and new_content,
    for convenient updating.
    '''

    def __init__(self, name=None, version=None, path=None):
        '''
        Initialize either with name,version or path.

        @param name: application Name
        @type name: String
        @param version: and corresponding Version
        @type version: String
        @param path: Path to folder with current Contents
        @type path: String
        '''

        if name and version:
            self._init_by_nv(name, version)
        if path:
            self._init_by_path(path)
        if not name and not version and not path:
            raise Exception()

        self.wacfgfile = os.path.join(Env.appdir,
                self.name, "%s-%s.wa" % (self.name, self.version))

    def _init_by_nv(self, name, version):
        self.name = name
        self.version = version

    def _init_by_path(self, path):
        self.cur_content = Content(path)
        try:
            self.cur_content.mcsv = self.cur_content.readMetaCSV()
            self.name = self.cur_content.mcsv['pn']
            self.version = self.cur_content.mcsv['pv']
        except:
            pass


    def __repr__(self):
        return "%s-%s" % (self.name, self.version)

    def __lt__(self, app):
        return self._vercmp(app) < 0
    def __le__(self, app):
        return self._vercmp(app) <= 0
    def __eq__(self, app):
        return self._vercmp(app) == 0

    def _vercmp(self, app):
        if type(app) is type(self):
            v = app.version
        else:
            v = app
        return vercmp(self.version, v)


    def install(self, sysargs=[]):
        '''
        Install, location given via @sysargs

        @param sysargs: Things like vhost, installdir, ...
        @type sysargs: List
        '''

        wd = os.path.join(Env.appdir, self.name)
        args = [self.wacfgfile] + sysargs
        OUT.debug("RUNNING: %s (wd: %s)" % (args, wd))
        subprocess.call(args, cwd=wd)

    def check_for_update(self):
        try:
            lv = Application(self.name).latest_version()
            if self < lv:
                self.update = lv.version
            else:
                self.update = False
        except:
            self.update = False

    def upgrade(self, old_content):
        old_content.readCSV()
        manuallychanged = old_content.doSetOperation( lambda x,y: y-x )
        manuallychanged = [ file for
                file in manuallychanged if os.path.exists(file.abspath) ]

        if manuallychanged:
            OUT.info('The following files have been changed manually:')

            curconpath_s = os.path.join(self.cur_content.path, "%s")
            for file in manuallychanged:
                OUT.info("\t- %s" % os.path.normpath(file.abspath))

                if file.type != "dir":
                    relpth = os.path.relpath(file.path)
                    ep = curconpath_s % relpth
                    epntmp = os.path.join(os.path.split(relpth)[0],
                            "._cfg%s_%s" % ("%04d", os.path.split(relpth)[1]) )
                    epn = curconpath_s % epntmp
                    i = 0
                    while True:
                        epntmp = epn % i
                        if not os.path.isfile(epntmp):
                            epn = epntmp
                            break
                        i+=1
                    from shutil import move
                    move(ep, epn)


            OUT.info('\nPlease run:')
            OUT.info('CONFIG_PROTECT="%s" etc-update' % old_content.path)



class Application:
    '''
    List of ApplicationVersions with the same name

    '''

    def __init__(self, name):
        self.name = name
        self.src_dir = os.path.join(Env.appdir, self.name)
        self.versions = []
        self.get_versions()

    def get_versions(self):
        for file in os.listdir(self.src_dir):
            if self.name in file and ".wa" in file and \
                    os.path.isfile(os.path.join(self.src_dir, file )):
                        version = pkgsplit( file[:-3] )[1]
                        self.versions += [ ApplicationVersion(self.name, version ) ]

    def latest_version(self):
        return sorted(self.versions)[-1]


class AvailableApps:
    def __init__(self, app=None):
        if app and os.path.isdir(os.path.join(Env.appdir, app)):
            self.apps = [Application(app)]
        elif os.path.isdir(Env.appdir):
            self.apps = [ Application(app)
                    for app in sorted(os.listdir(Env.appdir))
                    if os.path.isdir(os.path.join(Env.appdir, app)) ]
        else:
            self.apps = []

    def list(self):
        if len(self.apps) == 0:
            OUT.info("No webapps available")
        else:
            OUT.info("AVAILABLE webapps:")
            OUT.info("")
            for app in sorted(self.apps):
                OUT.info("- "+app.name)
                if True: # Env.options.verbose XXX
                    for version in sorted(app.versions):
                        OUT.info("\t- "+version.version)
            OUT.info("")


class InstalledApps:
    def __init__(self, Env):
        self.Env = Env
        self.dir = Env.options.wwwroot

    def _list(self):
        hits = []
        for r,d,f in os.walk(self.dir):
            if '.wacfg' in f:
                hits += [os.path.join(r, '.wacfg')]
        result = []

        for hit in hits:
            app = ApplicationVersion(path = hit.replace(".wacfg",""))
            app.check_for_update()
            result += [app]
        return result

    def upgrade(self):
        apps = self._list()
        for app in apps:
            if app.update:
                mcsv = app.cur_content.mcsv
                argx = ["upgrade", "-d", mcsv['installdir'], "-H", mcsv['vhost']]
                ApplicationVersion(mcsv['pn'], app.update).install(argx)


    def list(self):
        apps = self._list()
        if apps == []:
            OUT.info("No webapps installed")
            return
        OUT.debug("Found .wacfgs: %s:" % apps)
        OUT.info("INSTALLED webapps:")
        OUT.info("")
        outdated = False
        for app in sorted(apps, key=lambda x: x.cur_content.path):
            if app.update:
                OUT.warn("- %s (outdated)" % app)
                outdated = True
            else:
                OUT.info("- %s" % app)
        if outdated:
            OUT.warn("")
            OUT.warn("There are outdated instances of webapps on your system!")
            OUT.warn('Run "wacfg upgradeall" - your custom changes will not be overwritten')
        OUT.info("")


