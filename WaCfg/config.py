import os

try:
    import ConfigParser as configparser
except:
    import configparser

class Config:
    # not user-changeable
    _appdir = "/home/nutz/work/wacfg/apps/"
    _sandboxroot = "/home/nutz/work/wacfg/tmp/sandbox/"
    #_wwwroot = "/home/nutz/work/wacfg/tmp/installed/"
    #_dbroot = "/home/nutz/work/wacfg/tmp/vardbwacfg/"


    # user-changeable
    etcconfig = "/home/nutz/work/wacfg/etc/wacfg/wacfg.conf"


    def __init__(self):
        section = 'general'
        config = configparser.RawConfigParser()
        config.read(self.etcconfig)
        self.wwwroot = config.get(section,'wwwroot')



