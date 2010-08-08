import os

try:
    import ConfigParser as configparser
except:
    import configparser

class Config:
    # not user-changeable
    _appdir = "/home/nutz/work/wacfg/apps/"
    _sandboxroot = "/home/nutz/work/wacfg/tmp/sandbox/"
    wwwroot = "/home/nutz/work/wacfg/tmp/installed/"
    #_dbroot = "/home/nutz/work/wacfg/tmp/vardbwacfg/"


