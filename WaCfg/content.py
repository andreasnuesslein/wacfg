import os
import hashlib
import csv
from time import strftime

try:
    import ConfigParser as configparser
except:
    import configparser


class Content:
    def __init__(self, path):
        self.path = path
        self.entries = set()

        olddir = os.getcwd()
        os.chdir(path)
        self.createEntries()
        os.chdir(olddir)


    def createEntries(self, path='.'):
            for entry in os.listdir(path):
                x = os.path.join(path, entry)
                if os.path.isdir(x):
                    self.createEntries(x)
                if not "./.wacfg" in x:
                    self.entries.add(Entry(path=x))


    def writeCSV(self, path):
        f = open(path, 'w')
        w = csv.writer(f, delimiter=' ', quotechar='"')
        for entry in self.entries:
            w.writerow(entry.toArray())
        f.close()


    def checkCSV(self, path):
        oldentries = set()
        f = open(path, 'r')
        w = csv.reader(f, delimiter=' ', quotechar='"')
        for entry in w:
            oldentries.add(Entry(array=entry))
        f.close()
        if len(self.entries) == 0:
            self.entries = oldentries
            return
        else:
            self.diff = self.entries - oldentries
            self.entries = oldentries
            return self.diff


    def writeMetaCSV(self, Env, path=None):
        if not path:
            path = os.path.join(self.path, '.wacfg')
        section = 'general'
        config = configparser.RawConfigParser()
        config.add_section(section)
        config.set(section, 'pn', Env.pn)
        config.set(section, 'pv', Env.pv)
        config.set(section, 'installdate', strftime('%Y-%m-%d %H:%M:%S'))
        config.set(section, 'installdir', Env.installdir)
        config.set(section, 'vhost', Env.vhost)
        with open(path, 'w') as file:
            config.write(file)

    def readMetaCSV(self, path=None):
        if not path:
                path = os.path.join(self.path, '.wacfg')
        section = 'general'
        config = configparser.RawConfigParser()
        config.read(path)
        ret = {}
        ret['pn'] = config.get(section, 'pn')
        ret['pv'] = config.get(section, 'pv')
        ret['vhost'] = config.get(section, 'vhost')
        ret['installdir'] = config.get(section, 'installdir')
        ret['installdate'] = config.get(section, 'installdate')
        return ret


class Entry:
    def __init__(self, path=None, array=None):
        if path:
            self._init_by_path(path)
        elif array:
            self._init_by_array(array)

    def _init_by_path(self, path):
        self.path = path

        stat = os.lstat(path)
        self.mtime = stat.st_mtime
        self.mod = stat.st_mode
        self.uid = stat.st_uid
        self.gid = stat.st_gid

        if os.path.islink(path):
            self.type = 'sym'
            #self.target = os.path.relpath(os.path.realpath(path))
            self.target = os.path.realpath(path)
        elif os.path.isfile(path):
            self.type = 'obj'
            self.md5 = self.file_md5(path)
        elif os.path.isdir(path):
            self.type = 'dir'
            self.md5 = '0'
        else:
            raise Exception("unknown filetype")

    def _init_by_array(self, array):
        (self.type, self.mod, self.uid, self.gid, self.path, target_or_md5) = array
        if self.type == 'sym':
            self.target = target_or_md5
        else:
            self.md5 = target_or_md5


    def __repr__(self):
        if self.type == 'sym':
            ret = '%s %s %s %s %s -> %s'
        else:
            ret = '%s %s %s %s %s %s'
        return ret % tuple(self.toArray())


    def __hash__(self):
        if self.type == 'sym':
            return hash((self.type, self.path, self.target))
        if self.type == 'dir':
            return hash((self.type, self.path))
        return hash((self.type, self.path, self.md5))


    def __lt__(self, other):
        return self.path < other.path


    def __eq__(self, other):
        if self.path == other.path:
            if self.type == 'sym':
                return self.target == other.target
            else:
                return self.md5 == other.md5
        return False


    def toArray(self):
        target_or_md5 = self.target if self.type == 'sym' else self.md5
        return [self.type, self.mod, self.uid, self.gid, self.path, target_or_md5]


    def file_md5(self, path):
        md5 = hashlib.md5()
        with open(path, 'rb') as file:
            while True:
                data = file.read(8192)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()


