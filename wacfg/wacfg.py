#!/usr/bin/env python

import sys
from optparse import OptionParser, OptionGroup

from .config import Config
from .helpers import *
from .vercmp import *
from .output import OUT
from .content import Content
from .webapp import *
from .optparsing import waopts

class Env:
    pass


def main():

    parser = waopts()

    (Env.options, Env.args) = parser.parse_args()
    Env.cfg = Config

    # end optparser ---------------------------------------------------

    OUT.debug("Eng.options: %s" % Env.options)
    OUT.debug("Env.args: %s" % Env.args)

    try:
        if Env.args[0] in ["install","upgrade","remove","purge"]:
            if len(Env.args) == 1:
                OUT.error("You need to provide a webapp. Get a list with 'wacfg list'")
                sys.exit(1)

            argx = [x for x in sys.argv[1:] if x != Env.args[1]]
            if len(Env.args) == 2:
                ApplicationList(Env.args[1]).latest_version().install(argx)
            elif len(Env.args) == 3:
                Application(Env.args[1], Env.args[2]).install(argx)
    except IndexError as e:
        parser.print_help()


    if "list" in Env.args:
        if "installed" in Env.args:
            InstalledApps(Env).list()
        elif "available" in Env.args:
            ApplicationList().list()
        else:
            ApplicationList().list()
            print("")
            InstalledApps(Env).list()
            print("")

    if "upgradeall" in Env.args:
        InstalledApps(Env).upgrade()

if __name__ == "__main__":
    sys.exit(main())

