import os, sys
import tarfile, zipfile
import subprocess

from . import optparsing
from .output import OUT
from .webapp import ApplicationVersion

class Tools:
    def __init__(self, Env):
        self.Env = Env


    def mv(self, frompath, topath, wd="."):
        args = ["/bin/mv", frompath, topath]
        return subprocess.call(args, cwd=wd)

    def rm(self, rmpath, wd=".", recursive=False):
        # XXX shutil.rmtree() and regular os.remove() can be used here. replace this.
        args = ["/bin/rm"]
        if recursive:
            args += ["--recursive", "--force"]
        args += [rmpath]
        return subprocess.call(args, cwd=wd)


    def rsync(self, frompath, topath, wd="."):
        if not "/" == frompath[-1:]:
            frompath += "/"
        if not "/" == topath[-1:]:
            topath += "/"
        args = ["/usr/bin/rsync", "-a", frompath, topath]
        return subprocess.call(args, cwd=wd)

    def wget(self, path):
        try:
            os.mkdir("sources/")
        except:
            pass
        output = os.path.join("sources/",path.split("/")[-1])
        args = ["/usr/bin/wget", "--continue", "--no-verbose"]
        args += ["--output-document=%s" % output]
        args += [path]
        p1 = subprocess.call(args)
#        #print(p1.poll())
#        i=1
#        while not p1.poll() and p1.poll() != 0:
#            dots = "."*(i%4)
#            i+=1
#            print("\rDownloading %s" % dots),
#            sys.stdout.flush()
#            time.sleep(0.1)
#        print(" done\n")
        self.Env.src = output
        return output


    def chmod(self, mode, path="", recursive=False):
        path = os.path.join(self.Env.sboxpath, path)
        args = ["/bin/chmod"]
        if recursive:
            args += ["-R"]
        args += [mode, path]
        return subprocess.call(args)

    def chown(self, owner, group=None, path=".", recursive=False):
        path = os.path.join(self.Env.sboxpath, path)
        args = ["/bin/chown", "--silent"]
        if recursive:
            args += ["--recursive"]
        if group:
            args += ["%s:%s" % (owner,group)]
        else:
            args += [owner]
        args += [path]
        OUT.debug("Chown-arguments: %s" % args)
        if subprocess.call(args):
            OUT.warn("chown exited abnormally.")
        return

    def server_own(self, path=".", recursive=False):
        return self.chown(self.Env.server, self.Env.server, path, recursive)


    def archive_unpack(self):
        if self.Env.src and os.path.isfile(self.Env.src):
            OUT.debug("Source set correctly to: %s" % self.Env.src)
        else:
            OUT.debug("Guessing sourcefile from packagename...")
            names = [self.Env.pn, self.Env.pn+"-"+self.Env.pv]
            suffixes = ["", ".tar", ".gz", ".bz2", ".tar.gz", ".tgz"]
            suffixes += [".tar.bz2", ".zip", ".ZIP"]
            try:
                self.Env.src = [name+suffix for
                        name in names for suffix in suffixes
                        if os.path.isfile(name+suffix)][0]
            except IndexError:
                OUT.error("No sourcefile explicitely set or found in this folder")
                sys.exit(1)

        if zipfile.is_zipfile(self.Env.src):
            source = zipfile.ZipFile(self.Env.src)
        elif tarfile.is_tarfile(self.Env.src):
            source = tarfile.open(self.Env.src)
        else:
            OUT.error("Not a valid archive")
            sys.exit(1)

        try:
            self.rm(self.Env.sboxpath, recursive=True)
            os.mkdir(self.Env.sboxpath)
        except:
            pass
        source.extractall(path = self.Env.sboxpath)

        #----------------------------------------------------------
        # Check whether we extracted a folder into a folder...
        dir = os.listdir(self.Env.sboxpath)
        if len(dir) == 0:
            OUT.error("No files in sandbox, something went wrong")
            sys.exit(1)
        if len(dir) == 1:
            wd = os.path.dirname(self.Env.sboxpath)
            tmpdir = "._unzip%s" % (self.Env.pn)
            self.mv(os.path.join(self.Env.sboxpath,dir[0]), tmpdir, wd)
            self.rm(self.Env.sboxpath, recursive=True)
            self.mv(tmpdir, self.Env.sboxpath, wd)
        return

    def archive_install(self):

        app = ApplicationVersion(self.Env.pn, self.Env.pv, self.Env.sboxpath)
        app.cur_content.writeCSV(self.Env)
        app.cur_content.writeMetaCSV(self.Env)

        # see if the path exists - it might have content already. -> UPDATE
        if os.path.isdir(self.Env.destpath):
            if os.path.isfile(os.path.join(self.Env.destpath, '.wacfg')):
                old_app = ApplicationVersion(path = self.Env.destpath)
                app.upgrade(old_app.cur_content)

            else:
                # XXX Folder exists, but no .wacfg-files...
                OUT.error("Either you installed this manually before or some \
                        goofball erased the .wacfg-files.\nEither way, I'm exiting")
                sys.exit(1)


        # do the actual "installation" / move
        try:
            os.makedirs(os.path.split(self.Env.destpath)[0])
        except:
            pass
        if self.rsync(self.Env.sboxpath, self.Env.destpath) == 0:
            self.rm(self.Env.sboxpath, recursive=True)
        else:
            OUT.error("Rsync exited abnormally :-(")
            sys.exit(1)
        return
