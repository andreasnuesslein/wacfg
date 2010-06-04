#!/usr/bin/env python3

import sys, os, subprocess


_basedir = os.path.relpath("apps/")


def help():
    print("help text..")


def get_apps():
    app_basedir = os.path.join(os.path.curdir,_basedir)

    appdirs = [app for app in os.listdir(app_basedir) if
            os.path.isdir(os.path.join(app_basedir, app)) ]

    return appdirs
    #return ["wordpress-2.9.2/"]


def install_apps(applist=get_apps()):

    args = ["/usr/bin/env", "python3", "wacfg.py"]

    for app in applist:
        wd = os.path.join(_basedir,app)
        if os.path.isfile(os.path.join(wd,"wacfg.py")):
            subprocess.call(args, cwd=os.path.join(_basedir,app),
                env={'PYTHONPATH':"/home/nutz/work/wacfg2/module/"})
        else:
            print("no wacfg.py found in %s" % wd)




def main():
    print("MAIN")
    print(get_apps())
    install_apps()


if __name__ == "__main__":
    sys.exit(main())

