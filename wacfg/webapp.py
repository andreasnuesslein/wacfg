import os
import subprocess
import logging

from .config import Config
from .helpers import *
from .vercmp import *
from .output import OUT
from .content import Content

class Env:
    pass

class Application:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.file = "%s-%s.py" % (name, version)

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


    def valid_exec(self):
        path = os.path.join(Config._appdir, self.name, self.file)
        return(os.path.isfile(path))

    def install(self, sysargs=[]):
        if self.valid_exec():
            wd = os.path.join(Config._appdir, self.name)
            args = [os.path.join(wd, self.file)] + sysargs
            OUT.debug("RUNNING: %s wd(%s)" %(args, wd))
            subprocess.call(args, cwd=wd)
        else:
            OUT.error("No wacfg.py found")


class ApplicationList:
    def __init__(self, app=None):
        if not app:
            apps = [app for app in sorted(os.listdir(Config._appdir)) if
                os.path.isdir(os.path.join(Config._appdir, app)) ]
        else:
            apps = [app]
        self.apps = []
        for app in apps:
            for files in sorted(os.listdir(os.path.join(Config._appdir, app))):
                if app in files and ".py" in files and \
                        os.path.isfile(os.path.join(Config._appdir, app, files )):
                    version = pkgsplit( files[:-3] )[1]
                    self.apps += [ Application(app, version ) ]


    def dict(self):
        appdict = {}
        for app in self.apps:
            if app.name in appdict:
                appdict[app.name] += [app.version]
            else:
                appdict[app.name] = [app.version]
        return(appdict)

    def list(self):
        OUT.info("AVAILABLE webapps:")
        OUT.info("")
        if True: # Env.options.verbose: XXX
            for k, v in self.dict().items():
                OUT.info("- "+k)
                for version in v:
                    string = "\t- %s" if Application(k,version).valid_exec() \
                            else "\t- %s (no wacfg.py)"
                    OUT.info(string % version)
                OUT.info("")
        else:
            for app in uniq([x.name for x in self.apps]):
                OUT.info("- "+app)
            OUT.info("")
        return

    def latest_version(self):
        return sorted(self.apps)[-1]



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
            content = Content(hit.replace(".wacfg",""))
            metacsv = content.readMetaCSV()
            cv = Application(metacsv['pn'],metacsv['pv'])
            lv = ApplicationList(metacsv['pn']).latest_version()
            if cv < lv:
                content.update = lv.version
            else:
                content.update = False
            result += [content]
        return result

    def upgrade(self):
        apps = self._list()
        for app in apps:
            if app.update:
                mcsv = app.readMetaCSV()
                argx = ["upgrade", "-d", mcsv['installdir'], "-H", mcsv['vhost']]
                Application(mcsv['pn'], app.update).install(argx)
                #app.install()



    def list(self):
        apps = self._list()
        OUT.debug("Found .wacfgs: %s:" % apps)
        OUT.info("INSTALLED webapps:")
        OUT.info("")
        outdated = False
        for app in sorted(apps, key=lambda x: x.path):
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


