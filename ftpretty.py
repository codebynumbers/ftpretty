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
from ftplib import FTP, FTP_TLS
import os
import cStringIO

class ftpretty(object):
    conn = None

    def __init__(self, host, user, password, secure=False, **kwargs): 
        if secure:
            self.conn = FTP_TLS(host=host, user=user, passwd=password, **kwargs)
            self.conn.prot_p()
        else:
            self.conn = FTP(host=host, user=user, passwd=password, **kwargs)
        

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

    def put(self, local, remote):
        """ Puts a local file on the FTP server """       
        remote_dir = os.path.dirname(remote)
        remote_file = os.path.basename(remote)
        local_file = open(local, 'rb')
        current = self.conn.pwd()
        self.descend(remote_dir, force=True)
        self.conn.storbinary('STOR %s' % remote_file, local_file)
        local_file.close()
        self.conn.cwd(current)
        return self.conn.size(remote)

    def list(self, remote='.'):
        """ Return directory list """
        files = self.conn.nlst(remote)
        return files

    def descend(self, remote, force=False):
        """ Descend, possibly creating directories as needed """
        remote_dirs = remote.split('/')
        for dir in remote_dirs:
            try:
                self.conn.cwd(dir)
            except:
                if force:
                    self.conn.mkd(dir)
                    self.conn.cwd(dir)
        return self.conn.pwd()

    def delete(self, remote):
        return self.conn.delete(remote)

    def cd(self, remote):
        return self.conn.cwd(remote)

    def pwd(self):
        return self.conn.pwd()

    def close(self):
        try:
            self.conn.quit()
        except:
            self.conn.close()
