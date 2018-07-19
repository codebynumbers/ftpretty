from datetime import datetime
from ftplib import FTP, FTP_TLS, error_perm
from hashlib import sha512
from io import BytesIO, IOBase
from logging import basicConfig, DEBUG, debug, ERROR, error, getLogger, INFO, info
from os import listdir, path
from re import split
from sys import getsizeof

basicConfig(level=INFO)
log = getLogger(__name__)

class ftpretty(object):
    conn = None
    tmp_output = None
    relative_paths = set(['.', '..'])

    def __init__(self, host, user, password, ftp_conn=None, passive=True, secure=False, **kwargs):
        if ftp_conn:
            self.conn = ftp_conn
        elif secure and FTP_TLS:
            self.conn = FTP_TLS(host=host, user=user, passwd=password, **kwargs)
            self.conn.prot_p()
            log.info('Creating Secure FTP Session: ' + user + '@' + host + ':' + ' [Credential: ' + sha512(password.encode('utf8')).hexdigest() + ']')
        else:
            self.conn = FTP(host=host, user=user, passwd=password, **kwargs)
            log.info('Creating Insecure FTP Session: ' + user + '@' + host + ':' + ' [Credential: ' + sha512(password.encode('utf8')).hexdigest() + ']')

        if not passive:
            self.conn.set_pasv(False)
            log.info('Passive Mode [DISABLED]')

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            method = getattr(self.conn, name)
            return method(*args, **kwargs)
        return wrapper

    def get(self, remote, local=None):
        if isinstance(local, IOBase):
            local_file = local
            log.debug('Saving download to existing open file: [' + local_file.name + '] using descriptor [' + str(local_file.fileno()) + '] in [' + local_file.mode + '] mode')
        elif local is None:
            local_file = BytesIO(local)
            log.debug('Saving download to binary file stream: [' + str(local_file.getbuffer()) + ']')
        else:
            local_file = open(local, 'wb', buffering=0)
            log.debug('Creating binary file buffer: [' + local_file.name + '] using file descriptor [' + str(local_file.fileno()) + '] in [' + local_file.mode + '] mode for download')

        total_size = self.conn.size(remote)

        progress = transfer(local_file, int(total_size), get=True)
        self.conn.retrbinary('RETR {0}'.format(remote), progress.handle, blocksize=8192)

        if isinstance(local, IOBase):
            pass
        elif local is None:
            contents = local_file.getvalue()
            local_file.close()
            return contents
        else:
            local_file.close()

        return None

    def put(self, local, remote, contents=None):
        remote_dir = path.dirname(remote)
        if remote.endswith('/'): 
            remote_file = path.basename(local)
        else: 
            remote_file = path.basename(remote)

        if contents:
            local_file = BytesIO(contents)
            log.debug('Reading contents from binary stream: [' + str(local_file.getbuffer()) + '] for upload')
            total_size = getsizeof(local_file)
        else:
            if isinstance(local, IOBase):
                local_file = local
                log.debug('Reading contents from open file descriptor: [' + str(local_file.fileno()) + '] in [' + local_file.mode + '] mode for upload')
            elif isinstance(local, str):
                local_file = open(local, 'rb', buffering=0)
                log.debug('Opening file: [' + local_file.name + '] using file descriptor [' + str(local_file.fileno()) + '] in [' + local_file.mode + '] mode for upload')
            total_size = path.getsize(local_file.name)

        current = self.conn.pwd()
        self.descend(remote_dir, force=True)

        size = 0
        try:
            progress = transfer(remote_file, int(total_size))
            self.conn.storbinary('STOR {0}'.format(remote_file), local_file, blocksize=8192, callback=progress.handle)
            size = self.conn.size(remote_file)
        finally:
            local_file.close()
            self.conn.cwd(current)
        return size

    def upload_tree(self, src, dst, ignore=None):
        names = listdir(src)
        if ignore is not None:
            ignored_names = ignore(src, names)
        else:
            ignored_names = set()

        try:
            self.conn.mkd(dst)
        except error_perm:
            pass

        errors = []
        for name in names:
            if name in ignored_names:
                continue
            src_name = path.join(src, name)
            dst_name = path.join(dst, name)
            try:
                if path.islink(src_name):
                    pass
                elif path.isdir(src_name):
                    self.upload_tree(src_name, dst_name, ignore)
                else:
                    self.put(src_name, dst_name)
            except Exception as why:
                errors.append((src_name, dst_name, str(why)))

        return dst

    def list(self, remote='.', extra=False, remove_relative_paths=False):
        if extra:
            self.tmp_output = []
            self.conn.dir(remote, self._collector)
            directory_list = split_file_info(self.tmp_output)
        else:
            directory_list = self.conn.nlst(remote)

        if remove_relative_paths:
            return list(filter(self.is_not_relative_path, directory_list))

        return directory_list

    def is_not_relative_path(self, path):
        if isinstance(path, dict):
            return path.get('name') not in self.relative_paths
        else:
            return path not in self.relative_paths

    def descend(self, remote, force=False):
        remote_dirs = remote.split('/')
        for directory in remote_dirs:
            try:
                self.conn.cwd(directory)
            except Exception:
                if force:
                    self.conn.mkd(directory)
                    self.conn.cwd(directory)
        return self.conn.pwd()

    def delete(self, remote):
        try:
            self.conn.delete(remote)
        except Exception:
            return False
        else:
            return True

    def cd(self, remote):
        try:
            self.conn.cwd(remote)
        except Exception:
            return False
        else:
            return self.pwd()

    def pwd(self):
        return self.conn.pwd()

    def rename(self, remote_from, remote_to):
        return self.conn.rename(remote_from, remote_to)

    def close(self):
        try:
            self.conn.quit()
        except Exception:
            self.conn.close()

    def _collector(self, line):
        self.tmp_output.append(line)


def hash(filename, blocksize=65536):
    hasher = sha512()
    if isinstance(filename, str):
        with open(filename, 'rb') as filestream:
            buffer = filestream.read(blocksize)
            while len(buffer) > 0:
                hasher.update(buffer)
                buffer = filestream.read(blocksize)
    elif not isinstance(filename, BytesIO) and isinstance(filename, IOBase):
        buffer = filename.read(blocksize)
        while len(buffer) > 0:
            hasher.update(buffer)
            buffer = filename.read(blocksize)
    elif isinstance(filename, BytesIO) and isinstance(filename, IOBase) or isinstance(filename, BytesIO) and not isinstance(filename, IOBase):
        buffer = filename.read1(blocksize)
        while len(buffer) > 0:
            hasher.update(buffer)
            buffer = filename.read1(blocksize)

    return hasher.hexdigest()

def split_file_info(fileinfo):
    current_year = datetime.now().strftime('%Y')
    files = []
    for line in fileinfo:
        parts = split(
            r'^([\-dbclps])' +                  # Directory flag [1]
            r'([\-rwxs]{9})\s+' +               # Permissions [2]
            r'(\d+)\s+' +                       # Number of items [3]
            r'([a-zA-Z0-9_-]+)\s+' +            # File owner [4]
            r'([a-zA-Z0-9_-]+)\s+' +            # File group [5]
            r'(\d+)\s+' +                       # File size in bytes [6]
            r'(\w{3}\s+\d{1,2})\s+' +           # 3-char month and 1/2-char day of the month [7]
            r'(\d{1,2}:\d{1,2}|\d{4})\s+' +     # Time or year (need to check conditions) [+= 7]
            r'(.+)$',                           # File/directory name [8]
            line
        )

        date = parts[7]
        time = parts[8] if ':' in parts[8] else '00:00'
        year = parts[8] if ':' not in parts[8] else current_year
        dt_obj = datetime.strptime("{1} {0} {2}".format(date, year, time), '%Y %b %d %H:%M')

        files.append({
            'directory': parts[1],
            'perms': parts[2],
            'items': parts[3],
            'owner': parts[4],
            'group': parts[5],
            'size': int(parts[6]),
            'date': date,
            'time': time,
            'year': year,
            'name': parts[9],
            'datetime': dt_obj
        })

    return files


class transfer:
    bytes_written = 0
    total_size = 0
    transfer_progress = 0

    def __init__(self, current_file, total_size, buffer_size=8192, get=False):
        self.buffer = buffer_size
        self.current_file = current_file
        self.get = get
        self.total_size = total_size

    def handle(self, block):
        if self.get:
            if isinstance(block, bytes):
                self.current_file.write(block)
            elif isinstance(block, str):
                self.current_file.write(bytes(block.encode('utf8')))

        if isinstance(self.current_file, str):
            filename = self.current_file.split('/')[-1]
        elif not isinstance(self.current_file, BytesIO) and isinstance(self.current_file, IOBase):
            filename = self.current_file.name.split('/')[-1]
        elif isinstance(self.current_file, BytesIO) and isinstance(self.current_file, IOBase) or isinstance(self.current_file, BytesIO) and not isinstance(self.current_file, IOBase):
            filename = hash(self.current_file)

        self.bytes_written += self.buffer

        if (self.bytes_written / self.total_size) >= 1.0:
            percent_complete = int(100.0)
        else:
            percent_complete = int(100.0 * (self.bytes_written / self.total_size))

        if (self.transfer_progress != percent_complete):
            self.transfer_progress = percent_complete
            print("{0} @ [{1:d}%]".format(filename, percent_complete))
