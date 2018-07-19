from collections import deque
from io import BytesIO, IOBase
from os import path, remove, SEEK_END
from sys import getsizeof

class MockFTP(object):

    def __init__(self):
        self._files = None
        self._size = 0
        self._dirlist = None
        self._exists = True
        self._stack = deque()
        self._contents = ''

    def storbinary(self, command, f, blocksize=8192, callback=None):
        if isinstance(f, str):
            with open(command.split(' ')[-1], 'w') as file:
                file.write(f)
        elif not isinstance(f, BytesIO) and isinstance(f, IOBase):
            with open(command.split(' ')[-1], 'wb') as file:
                file.write(f.read())
        elif isinstance(f, BytesIO) and isinstance(f, IOBase) or isinstance(f, BytesIO) and not isinstance(f, IOBase):
            with open(command.split(' ')[-1], 'wb') as file:
                file.write(f.getvalue())

        self._size = self.size(f)

    def retrbinary(self, command, callback, blocksize=8192):
        callback(self._contents)
        return

    def pwd(self):
        return "/".join(self._stack)

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
        if not self._exists:
            raise Exception("Doesn't exist")
        remove(filename)
        return True

    def rename(self, fromname, toname):
        return

    def cwd(self, pathname):
        if not self._exists:
            self._exists = True
            raise Exception("Doesn't exist")
        for dir in pathname.split("/"):
            if dir == '..':
                self._stack.pop()
            else:
                self._stack.append(dir)

    def size(self, filename):
        if isinstance(filename, str):
            self._size = path.getsize(filename)
        elif isinstance(filename, BytesIO) and isinstance(filename, IOBase) or isinstance(filename, BytesIO) and not isinstance(filename, IOBase):
            self._size = getsizeof(filename.getvalue())
        elif not isinstance(filename, BytesIO) and isinstance(filename, IOBase):
            self._size = path.getsize(filename.name)
        return self._size

    def dir(self, dirname, callback):
        for line in self._dirlist.splitlines():
            callback(line)

    def sendcmd(self, command):
        return command

    def set_pasv(self, passive):
        return passive

    def quit(self):
        raise Exception('Fake a problem with quit')

    def close(self):
        return True

    def _set_files(self, files):
        self._files = files

    def _set_dirlist(self, dirlist):
        self._dirlist = dirlist

    def _set_exists(self, exists):
        self._exists = exists

    def _set_contents(self, contents):
        self._contents = contents
