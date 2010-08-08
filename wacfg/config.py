import os

try:
    import ConfigParser as configparser
except:
    import configparser

class Config:
    # not user-changeable
    _appdir = "/var/lib/webapps/"
    _sandboxroot = "/var/tmp/webapps//"
    #_dbroot = "/home/nutz/work/wacfg/tmp/vardbwacfg/"


