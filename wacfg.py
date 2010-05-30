#!/usr/bin/env python3

import sys, os

class TestClass:
    def index(self):
        print("fooobazz")


def execfile(file, globals=globals(), locals=locals()):
    with open(file, "r") as fh:
        exec(fh.read()+"\n", globals, locals)

def help():
    print("help text..")


def manifiles():
    src = os.path.relpath("apps/")

    rootdir = os.path.join(os.path.curdir,src)
    appdirs = [app for app in os.listdir(src) if os.path.isdir(os.path.join(rootdir,app)) ]
    sys.path = [rootdir] + sys.path
    for app in ['app1','app2','app3']: #appdirs:
        x = __import__("%s.manifest" % app)
        try:
            print(x.manifest.foo())
        except AttributeError as err:
            print(err)





def main():
    print("MAIN")
    manifiles()


if __name__ == "__main__":
    sys.exit(main())

