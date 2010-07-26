#!/usr/bin/env python

import sys
import os
import subprocess
import logging

from WaCfg.config import Config
from WaCfg.helpers import *
from WaCfg.vercmp import vercmp


class Env:
    pass


class Application:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.file = "%s-%s.py" % (name, version)

    def __repr__(self):
        return "[%s-%s]" % (self.name, self.version)

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

    #
    def valid_exec(self):
        path = os.path.join(Config._appdir, self.name, self.file)
        return(os.path.isfile(path))

    def install(self):
        if self.valid_exec():
            wd = os.path.join(Config._appdir, self.name)
            args = [os.path.join(wd, self.file)]
            logging.debug("RUNNING: %s wd(%s)" %(args, wd))
            subprocess.call(args, cwd=wd)
        else:
            print("no wacfg.py found")


class ApplicationList:
    def __init__(self, app=None):
        if not app:
            apps = [app for app in sorted(os.listdir(Config._appdir)) if
                os.path.isdir(os.path.join(Config._appdir, app)) ]
        else:
            apps = [app]

        self.apps = [Application(app, v)
                for app in apps
                for v in os.listdir(os.path.join(Config._appdir, app))
                if os.path.isdir(os.path.join(Config._appdir, app, v))]

    def dict(self):
        appdict = {}
        for app in self.apps:
            if app.name in appdict:
                appdict[app.name] += [app.version]
            else:
                appdict[app.name] = [app.version]
        return(appdict)

    def list(self):
        print("List of currently installed webapps:\n")
        if Env.options.verbose:
            for k, v in self.dict().items():
                print("- "+k)
                for version in v:
                    string = "\t- %s" if Application(k,version).valid_exec() \
                            else "\t- %s (no wacfg.py)"
                    print(string % version)
                print("")
        else:
            for app in uniq([x.name for x in self.apps]):
                print("- "+app)
        print("")
        return()



def main():
    from WaCfg import optparsing
    from optparse import OptionParser, OptionGroup

    parser = optparsing.waopts()

    default_group = OptionGroup(parser, "General Options")
    default_group.add_option("-l", "--list", action="store_true", dest="list",
            default=False, help="list all available applications")
    default_group.add_option("-v", "--verbose", action="count", dest="verbose",
            help="increase verbosity")

    parser.add_option_group(default_group)

    (Env.options, Env.args) = parser.parse_args()

    # end optparser ---------------------------------------------------

    OUT(Env.options, 2)
    OUT(Env.args, 2)

    Config.verbosity = Env.options.verbose

    try:
        function = {'install': 'install',
         'upgrade': 'upgrade',
         'remove': 'remove',
         'purge': 'purge',
         }[Env.args[0]]
    except:
        parser.print_help()
        sys.exit(1)


    print(function)
    sys.exit(1)

    # Evaluate Options
    if Env.options.install:
        if len(Env.args) < 3:
            # XXX maybe just use the latest version here...
            return "Please specify a correct package and version"
        Application(Env.args[1], Env.args[2]).install()

    if Env.options.list:
        if len(Env.args) == 0:
            Env.args += [None]
        ApplicationList(Env.args[0]).list()


if __name__ == "__main__":
    sys.exit(main())

