""" A simple API wrapper for FTPing files 

    you should be able to this:

    from ftpretty import ftpretty
    f = ftpretty(host, user, pass, secure=False, timeout=10)
    f.get(remote, local)
    f.put(local, remote)
    f.list(remote)
    f.cd(remote)
    f.delete(remote)
    f.close()
    
"""
from ftplib import FTP
try:
    from ftplib import FTP_TLS
except ImportError:
    FTP_TLS = None
import os
import cStringIO
import re
import datetime
from dateutil import parser

class ftpretty(object):
    """ A wrapper for FTP connections """
    conn = None
    tmp_output = None
    relative_paths = set(['.', '..'])

    def __init__(self, host, user, password, 
        secure=False, passive=True, ftp_conn=None, **kwargs):

        if ftp_conn:
            self.conn = ftp_conn
        elif secure and FTP_TLS:
            self.conn = FTP_TLS(host=host, user=user, passwd=password, **kwargs)
            self.conn.prot_p()
        else:
            self.conn = FTP(host=host, user=user, passwd=password, **kwargs)

        if not passive:
            self.conn.set_pasv(False)

    def __getattr__(self, name):
        """ Pass anything we don't know about, to underlying ftp connection """
        def wrapper(*args, **kwargs):
            method = getattr(self.conn, name)
            return method(*args, **kwargs)
        return wrapper

    def get(self, remote, local=None):
        """ Gets the file from FTP server

            local can be:
                a string: path to output file
                a file: opened for writing
                None: contents are returned
        """       
        if isinstance(local, file):
            local_file = local
        elif local is None:
            local_file = cStringIO.StringIO()
        else:   
            local_file = open(local, 'wb')

        self.conn.retrbinary("RETR %s" % remote, local_file.write)

        if isinstance(local, file):
            local_file = local
        elif local is None:
            contents = local_file.getvalue()
            local_file.close()
            return contents
        else:   
            local_file.close()

        return None

    def put(self, local, remote, contents=None):
        """ Puts a local file (or contents) on to the FTP server 

            local can be:
                a string: path to inpit file
                a file: opened for reading
                None: contents are pushed
        """       
        remote_dir = os.path.dirname(remote)
        remote_file = os.path.basename(local)\
            if remote.endswith('/') else os.path.basename(remote)

        if contents:
            # local is ignored if contents is set
            local_file = cStringIO.StringIO(contents)
        elif isinstance(local, file):
            local_file = local
        else:
            local_file = open(local, 'rb')
        current = self.conn.pwd()
        self.descend(remote_dir, force=True)

        size = 0
        try:
            self.conn.storbinary('STOR %s' % remote_file, local_file)
            size = self.conn.size(remote_file)
        except Exception as exc:
            print exc
        finally:
            local_file.close()
            self.conn.cwd(current)
        return size

    def list(self, remote='.', extra=False, remove_relative_paths=False):
        """ Return directory list """
        if extra:
            self.tmp_output = []
            self.conn.dir(remote, self._collector)
            directory_list = split_file_info(self.tmp_output)
        else:
            directory_list = self.conn.nlst(remote)

        if remove_relative_paths:
            return filter(self.is_not_relative_path, directory_list)

        return directory_list

    def is_not_relative_path(self, path):
        if isinstance(path, dict):
            return path.get('name') not in self.relative_paths
        else:
            return path not in self.relative_paths

    def descend(self, remote, force=False):
        """ Descend, possibly creating directories as needed """
        remote_dirs = remote.split('/')
        for directory in remote_dirs:
            try:
                self.conn.cwd(directory)
            except Exception as exc:
                if force:
                    self.conn.mkd(directory)
                    self.conn.cwd(directory)
        return self.conn.pwd()

    def delete(self, remote):
        """ Delete a file from server """
        try:
            self.conn.delete(remote)
        except Exception as exc:
            return False
        else:
            return True        

    def cd(self, remote):
        """ Change working directory on server """
        try:
            self.conn.cwd(remote)
        except Exception as exc:
            return False
        else:
            return self.pwd()

    def pwd(self):
        """ Return the current working directory """
        return self.conn.pwd()

    def close(self):
        """ End the session """
        try:
            self.conn.quit()
        except Exception as exc:
            self.conn.close()

    def _collector(self, line):
        """ Helper for collecting output from dir() """
        self.tmp_output.append(line)

def split_file_info(fileinfo):
    """ Parse sane directory output usually ls -l
        Adapted from https://gist.github.com/tobiasoberrauch/2942716 
    """
    current_year = datetime.datetime.now().strftime('%Y')
    files = []        
    for line in fileinfo:
        parts = re.split(
            '^([\\-dbclps])' +                # Directory flag [1]
            '([\\-rwxs]{9})\\s+' +            # Permissions [2]
            '(\\d+)\\s+' +                    # Number of items [3]
            '(\\w+)\\s+' +                    # File owner [4]
            '(\\w+)\\s+' +                    # File group [5]
            '(\\d+)\\s+' +                    # File size in bytes [6]
            '(\\w{3}\\s+\\d{1,2})\\s+' +       # 3-char month and 1/2-char day of the month [7]
            '(\\d{1,2}:\\d{1,2}|\\d{4})\\s+' + # Time or year (need to check conditions) [+= 7]
            '(.+)$'                       # File/directory name [8]
            , line)

        date = parts[7]
        time = parts[8] if ':' in parts[8] else '00:00'
        year = parts[8] if ':' not in parts[8] else current_year
        dt_obj = parser.parse("%s %s %s" % (date, year, time) )

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

