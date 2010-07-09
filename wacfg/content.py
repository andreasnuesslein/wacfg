import os, hashlib, csv

class Content:
    def __init__(self, path=None):
        self.entries = []
        if path:
            olddir = os.getcwd()
            os.chdir(path)
            self.addpath()
            os.chdir(olddir)

        else:
            pass

    def addpath(self, path='.'):
            for entry in os.listdir(path):
                x = os.path.join(path, entry)
                if os.path.isdir(x):
                    self.addpath(x)
                self.entries += [Entry(path=x)]


    def writeCSV(self, path):
        f = open(path, 'w')
        w = csv.writer(f, delimiter=' ', quotechar='"')
        for entry in self.entries:
            w.writerow(entry.toArray())
        f.close()

    def readCSV(self, path):
        f = open(path)
        w = csv.reader(f, delimiter=' ', quotechar='"')
        for entry in w:
            print(entry)
            self.entries += [Entry(array=entry)]
        f.close()

    def toList(self):
        return sorted(self.entries, key=lambda x: x.path)


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
            self.md5 = 0
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


    def toArray(self):
        target_or_md5 = self.target if self.type == 'sym' else self.md5
        return [self.type, self.mod, self.uid, self.gid, self.path, target_or_md5]


    def file_md5(self, path):
        #return hashlib.md5(open(path,'rb').read()).hexdigest()
        md5 = hashlib.md5()
        with open(path, 'rb') as file:
            while True:
                data = file.read(8192)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()

