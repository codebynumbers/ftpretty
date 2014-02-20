from ftpretty import ftpretty
import os

class MockFTP(object):
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

    def _set_files(self, files):
        self._files = files

    def _set_dirlist(self, dirlist):
        self._dirlist = dirlist

ftp_conn = MockFTP()
f = ftpretty(None, None, None, ftp_conn=ftp_conn)

f.cwd('photos')
print f.pwd()
print f.cd('photos/nature/mountains')

f._set_files(['a.txt', 'b.txt'])
print f.list()

print f.cd('/')
print f.put('AUTHORS.rst', 'AUTHORS.rst')

f._set_dirlist("""-rw-rw-r-- 1 rharrigan rharrigan   47 Feb 20 11:39 AUTHORS.rst
drwxrwxr-x 4 rharrigan rharrigan 4096 Feb 12 10:00 build
drwxrwxr-x 2 rharrigan rharrigan 4096 Feb 17 17:02 dist
drwxrwxr-x 5 rharrigan rharrigan 4096 Feb 12 10:01 env
drwxrwxr-x 2 rharrigan rharrigan 4096 Feb 12 10:00 ftpretty.egg-info
-rw-rw-r-- 1 rharrigan rharrigan 6019 Feb 20 13:25 ftpretty.py
-rw-rw-r-- 1 rharrigan rharrigan 6306 Feb 20 13:25 ftpretty.pyc
-rw-rw-r-- 1 rharrigan rharrigan  168 Feb 17 16:57 HISTORY.rst
-rw-rw-r-- 1 rharrigan rharrigan 1079 Feb 12 09:38 LICENSE.txt
-rw-rw-r-- 1 rharrigan rharrigan 2708 Feb 20 11:39 README.rst
-rw-rw-r-- 1 rharrigan rharrigan  764 Feb 17 17:01 setup.py
-rw-rw-r-- 1 rharrigan rharrigan 2085 Feb 20 13:27 test.py
-rw-rw-r-- 1 rharrigan rharrigan  195 Feb 20 11:39 TODO.rst""")
print f.list(extra=True)


f.get('AUTHORS.rst', 'local_copy.txt')
