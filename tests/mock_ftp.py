import os
from fs.memoryfs import MemoryFS
from compat import stringtype

class MockFTP(object):
    """ Mock FTP lib for testing """

    def __init__(self):
        self.mfs = MemoryFS()
        self._stack = []

    def _getpath(self, path):
        path = stringtype(path)
        return os.path.join(self.pwd(), path)

    def storbinary(self, command, f):
        cmd, path = command.split(' ')
        path = self._getpath(path)
        with self.mfs.openbin(path, 'w') as fh:
            fh.write(f.read())
        return self.mfs.getinfo(path, namespaces='details').size

    def retrbinary(self, command, callback):
        cmd, path = command.split(' ')
        path = self._getpath(path)
        with self.mfs.openbin(path) as fh:
            callback(fh.read())
        return

    def pwd(self):
        return "/".join(self._stack)

    def nlst(self, dirname=None):
        dirname = dirname or '.'
        dirname = self._getpath(dirname)
        return self.mfs.listdir(dirname)

    def quit(self):
        self.mfs.close()

    def close(self):
        self.mfs.close()

    def mkd(self, dirname):
        if dirname:
            dirname = self._getpath(dirname)
            self.mfs.makedir(dirname)

    def rmd(self, dirname):
        dirname = self._getpath(dirname)
        self.mfs.makedir(dirname)

    def delete(self, filename):
        filename = self._getpath(filename)
        self.mfs.remove(filename)

    def rename(self, fromname, toname):
        fromname = self._getpath(fromname)
        toname = self._getpath(toname)
        self.mfs.move(fromname, toname)

    def cwd(self, pathname):
        if not pathname:
            return
        for dir in pathname.split("/"):
            if dir == '..' and self._stack:
                self._stack.pop()
            elif dir not in self.mfs.listdir(stringtype(self.pwd())):
                raise Exception("{} doesn't exist".format(dir))
            else:
                self._stack.append(dir)

    def size(self, filename):
        filename = self._getpath(filename)
        return self.mfs.getinfo(filename, namespaces='details').size

    def dir(self, dirname, callback):
        dirname = self._getpath(dirname)
        for file in self.mfs.scandir(dirname, namespaces=['details', 'access']):
            line = '{flag}{permissions} 1 {user} {group} {size} {modified} {name}'.format(
                flag='d' if file.is_dir else '-',
                size=file.size,
                name=file.name,
                modified=file.modified.strftime("%b %-d %H:%M"),
                user='fake_user',
                group='fake_group',
                permissions='rw-rw-rw-',
            )
            callback(line)

    def sendcmd(self, command):
        return command

    def set_pasv(self, passive):
        return passive

