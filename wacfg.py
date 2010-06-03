#!/usr/bin/env python3

import sys, os, subprocess


def help():
    print("help text..")


def get_apps():
    _basedir = os.path.relpath("apps/")
    app_basedir = os.path.join(os.path.curdir,_basedir)

    appdirs = [app for app in os.listdir(app_basedir) if
            os.path.isdir(os.path.join(app_basedir, app)) ]

    return appdirs
    #return ["wordpress-2.9.2/"]


def exec_apps(applist=get_apps()):
    for app in applist:
        args = ["/usr/bin/env", "python3", "wacfg.py"]
        subprocess.call(args,env={'PYTHONPATH':"/home/nutz/work/wacfg2/module/"},cwd="apps/%s/" %app)




def manifiles():
    exec_apps()



def main():
    print("MAIN")
    manifiles()


if __name__ == "__main__":
    sys.exit(main())

