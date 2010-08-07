import os
import hashlib
import csv
from time import strftime

try:
    import ConfigParser as configparser
except:
    import configparser



cfile = '.wacfg-%s-%s'

class Content:
    def __init__(self, path, pn=None, pv=None):
        self.path = path
        self.pn = pn
        self.pv = pv
        self.entries = set()

        olddir = os.getcwd()
        os.chdir(path)
        self.createEntries()
        os.chdir(olddir)

    def __repr__(self):
        try:
            ret = self.readMetaCSV()
            return "%-10s %s\t@ %s" % (ret['pn'], ret['pv'], self.path)
        except:
            return"Webapp @ %s" % (self.path)

    def createEntries(self, path='.'):
            for entry in os.listdir(path):
                x = os.path.join(path, entry)
                if os.path.isdir(x):
                    self.createEntries(x)
                if not "./.wacfg" in x:
                    self.entries.add(Entry(wd=os.path.abspath(path),path=x))

    def setOperation(self, operation):
        if not self.csventries:
            return self.entries
        return( operation(self.entries, self.csventries) )

    def removeFiles(self):
        self.readCSV()
        entries = self.setOperation( lambda x,y: x & y )
        for entry in sorted(entries, key=lambda x:x.type, reverse=True):
            entry.remove()


    def writeCSV(self, pn=None, pv=None):
        pn = pn or self.pn
        pv = pv or self.pv
        file = os.path.join(self.path, cfile % (pn, pv))
        f = open(file, 'w')
        w = csv.writer(f, delimiter=' ', quotechar='"')
        for entry in self.entries:
            w.writerow(entry.toArray())
        f.close()

    def readCSV(self, pn=None, pv=None):
        pn = pn or self.pn or self.readMetaCSV()['pn']
        pv = pv or self.pv or self.readMetaCSV()['pv']
        file = os.path.join(self.path, cfile % (pn, pv))
        f = open(file, 'r')
        w = csv.reader(f, delimiter=' ', quotechar='"')

        self.csventries = set()
        for entry in w:
            self.csventries.add(Entry(wd=os.path.abspath(self.path),array=entry))
        f.close()
        return self.csventries


    def writeMetaCSV(self, Env):
        metafile = os.path.join(self.path, '.wacfg')
        section = 'general'
        config = configparser.RawConfigParser()
        config.add_section(section)
        config.set(section, 'pn', Env.pn)
        config.set(section, 'pv', Env.pv)
        config.set(section, 'installdate', strftime('%Y-%m-%d %H:%M:%S'))
        config.set(section, 'installdir', Env.installdir)
        config.set(section, 'vhost', Env.vhost)
        with open(metafile, 'w') as file:
            config.write(file)

    def readMetaCSV(self):
        metafile = os.path.join(self.path, '.wacfg')
        section = 'general'
        config = configparser.RawConfigParser()
        config.read(metafile)
        ret = {}
        ret['pn'] = config.get(section, 'pn')
        ret['pv'] = config.get(section, 'pv')
        ret['vhost'] = config.get(section, 'vhost')
        ret['installdir'] = config.get(section, 'installdir')
        ret['installdate'] = config.get(section, 'installdate')
        return ret


class Entry:
    def __init__(self, wd, path=None, array=None):
        self.wd = wd
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

    def remove(self):
        # XXX This is not yet working perfectly
        abspath = os.path.join(self.wd, self.path)
        if self.type == 'dir':
            try:
                os.removedirs(abspath)
            except:
                pass
        else:
            os.remove(abspath)

