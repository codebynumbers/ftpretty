import os

class MockFTP(object):
    """ Mock FTP lib for testing """
    _current = '.'
    _files = None
    _size = 0
    _dirlist = None

    def storbinary(self, command, f):
        f.seek(0, os.SEEK_END)
        self._size = f.tell()

    def retrbinary(self, command, callback):
        return

    def pwd(self):
        return self._current

    def nlst(self, dirname=None):
        return self._files

    def quit(self):
        return

    def close(self):
        return

    def mkd(self, dirname):
        return

    def rmd(self, dirname):
        return

    def delete(self, filename):
        return "OK"

    def rename(self, fromname, toname):
        return

    def cwd(self, pathname):
        self._current = pathname

    def size(self, filename):
        return self._size

    def dir(self, dirname, callback):
        for line in self._dirlist.splitlines():
            callback(line)

    def sendcmd(self, command):
        return command

    def set_pasv(self, passive):
        return passive

    def _set_files(self, files):
        self._files = files

    def _set_dirlist(self, dirlist):
        self._dirlist = dirlist
