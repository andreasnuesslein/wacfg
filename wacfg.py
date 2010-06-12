#!/usr/bin/env python3

import sys, os, subprocess

from vercmp import vercmp

_basedir = os.path.relpath("./apps/")


def help():
    print("help text..")


def get_apps():
    appdirs = [app for app in os.listdir(_basedir) if
            os.path.isdir(os.path.join(_basedir, app)) ]

    return appdirs

class Application:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def __repr__(self):
        return "[%s-%s]" % (self.name, self.version)

    def _vercmp(self, app):
        if type(app) is type(self):
            v = app.version
        else:
            v = app
        return vercmp(self.version, v)

#    def __ne__(self, app):
#        return self._vercmp(app) != 0
    def __lt__(self, app):
        return self._vercmp(app) < 0
#    def __le__(self, app):
#        return self._vercmp(app) <= 0
#    def __eq__(self, app):
#        return self._vercmp(app) == 0
#    def __ge__(self, app):
#        return self._vercmp(app) >= 0
#    def __gt__(self, app):
#        return self._vercmp(app) > 0


def _create_apps(app):
    apps = []
    dir = os.path.join(_basedir, app)
    for v in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, v)):
            a = Application(app, v)
            apps.append(a)
    return sorted(apps)

def createlist(app=None):
    if not app:
        appdirs = [app for app in sorted(os.listdir(_basedir)) if
            os.path.isdir(os.path.join(_basedir, app)) ]
        applications = []
        for app in appdirs:
            applications += _create_apps(app)
        return(applications)
    else:
        return(_create_apps(app))







def exec_app(app):
    args = ["/usr/bin/env", "python3", "wacfg.py"]
    wd = "apps/%s/%s" % (app.name, app.version)
    if os.path.isfile(os.path.join(wd,"wacfg.py")):
        subprocess.call(args,env={'PYTHONPATH':"/home/nutz/work/wacfg2/module/"}, cwd=wd)
    else:
        print("no wacfg.py found in %s" % wd)

def manifiles():
    appl = createlist()
    print(appl)
    
    exec_app(Application('wordpress','2.9.2'))


def main():
    print("MAIN")
    manifiles()

if __name__ == "__main__":
    sys.exit(main())

