
import os
try:
    import ConfigParser as configparser
except:
    import configparser

class Config:
    
    # not user-changeable
    _basedir = os.path.relpath("/home/nutz/work/wacfg/apps/")
    _sandboxdir = "/home/nutz/work/tmp/wacfg/sandbox/"
    _wwwdir = "/home/nutz/work/tmp/wacfg/installed/"


    # user-changeable
    etcconfig = "/home/nutz/wacfg/etc/wacfg/wacfg.conf"


    def __init__(self):
        section = 'general'
        config = configparser.RawConfigParser()
        config.read(self.etcconfig)
        self.wwwroot = config.get('general','wwwroot')



