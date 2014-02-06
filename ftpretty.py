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

class ftpretty(object):
    conn = None

    def __init__(self, host, user, password, secure=False, **kwargs): 
        if secure:
            self.conn = FTP_TLS(host=host, user=user, passwd=password, **kwargs)
            self.conn.prot_p()
        else:
            self.conn = FTP(host=host, user=user, passwd=password, **kwargs)
        

    def get(self, remote, local):
        """ Gets the file from FTP server """       
        local_file = open(local, 'wb')
        self.conn.retrbinary("RETR %s" % remote, local_file.write)
        local_file.close()
        return os.path.getsize(local)
       
    def put(self, local, remote):
        """ Puts a local file on the FTP server """       
        remote_dir = os.path.dirname(remote)
        remote_file = os.path.basename(remote)
        local_file = open(local, 'rb')
        self.cd(remote_dir, force=True)
        self.conn.storbinary('STOR %s' % remote_file, local_file)
        local_file.close()
        # assumes an initial stright downward descent, 
        # no dot paths, make more robust later
        self.cd("../" * len(remote_dir.split('/')))
        return self.conn.size(remote)

    def list(self, remote='.'):
        """ Return directory list """
        files = self.conn.nlst(remote)
        return files

    def cd(self, remote, force=False):
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

    def close(self):
        try:
            self.conn.quit()
        except:
            self.conn.close()
