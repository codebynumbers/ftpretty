========
ftpretty
========

.. image:: https://travis-ci.com/codebynumbers/ftpretty.svg?branch=master
   :target: https://travis-ci.com/codebynumbers/ftpretty

.. image:: https://coveralls.io/repos/codebynumbers/ftpretty/badge.png?branch=master
   :target: https://coveralls.io/r/codebynumbers/ftpretty?branch=master

.. image:: https://img.shields.io/pypi/v/ftpretty.svg
   :target: https://pypi.python.org/pypi/ftpretty

.. image:: https://img.shields.io/pypi/dm/ftpretty.svg
   :target: https://pypi.python.org/pypi/ftpretty

A wrapper for simple FTP operations: get, put, list etc.

The goal of this library is to provide a frictionless experience to FTPing files
in way similar to Amazon's s3cmd command line tool. The API should be intuitive
with the order of arguments reflecting the transfer direction of bytes.

Transfers are assumed to be binary. 

Unrecognized commands fall through to the underlying FTP or FTP_TLS connection object

Supports python 2 & 3, tested on 2.7 & 3.5, 3.6, & 3.7

Examples
--------

.. code-block:: python

    from ftpretty import ftpretty

    # Minimal
    f = ftpretty(host, port)

    # Advanced
    # There are 3 more possible arguments that can be passed to the __init__ function:
    # Passive - You can choose to specify whether the FTP client is in active mode or passive mode (defaults to passive)
    # Secure - Uses TLS encryption (advised if the server supports it)
    # FTP_CONN - Define another ftp library:

   f = ftpretty(host, port, passive, secure, ftp_conn)

    # Get a file, save it locally
    f.get('someremote/file/on/server.txt', '/tmp/localcopy/server.txt')

    # Check whether something is a file or a folder:
    f.is_file('someremote/file/on/server.txt')

    # Get a file and write to an open file
    myfile = open('/tmp/localcopy/server.txt', 'wb')
    f.get('someremote/file/on/server.txt', myfile)

    # Get a file and return contents (in python 3 contents is bytes)
    contents = f.get('someremote/file/on/server.txt')

    # Get a tree on a remote directory (similar to shutil.copytree, without following symlinks
    f.get_tree("/remote/tree/on/server", "/tmp/local/tree")

    # Put a local file to a remote location
    # non-existent subdirectories will be created automatically
    f.put('/tmp/localcopy/data.txt', 'someremote/file/on/server.txt')

    # Put a local file into a remote directory, denoted by trailing slash on remote
    f.put('/tmp/localcopy/data.txt', 'someremote/dir/')

    # Put using an open file desciptor
    myfile = open('/tmp/localcopy/data.txt', 'r')
    f.put(myfile,  'someremote/file/on/server.txt')

    # Put using string data (in python 3 contents should be bytes)
    f.put(None,  'someremote/file/greeting.txt', contents='blah blah blah')

    # Put a tree on a remote directory (similar to shutil.copytree, without following symlinks
    f.put_tree("Local/tree", "/remote/files/server")

    # Return a list the files in a directory
    f.list('someremote/folder')
    ['a.txt', 'b.txt']

    f.list('someremote/folder', extra=True)
    [{'date': 'Feb 11',
      'datetime': datetime.datetime(2014, 2, 11, 2, 3),
      'directory': 'd',
      'group': '1006',
      'items': '3',
      'name': 'a.txt',
      'owner': '1005',
      'perms': 'rwxr-xr-x',
      'size': '4096',
      'time': '02:03',
      'year': '2014'},
     {'date': 'Feb 11',
      'datetime': datetime.datetime(2014, 2, 11, 2, 35),
      'directory': 'd',
      'group': '1006',
      'items': '3',
      'name': 'b.txt',
      'owner': '1005',
      'perms': 'rwxr-xr-x',
      'size': '4096',
      'time': '02:35',
      'year': '2014'}]

    # Change to remote directory
    f.cd('someremote/folder')

    # This can be made easier with descend and ascend 
    f.descend('on') # Changes directory to 'someremote/folder/on'
    f.ascend() # Changes directory back to 'someremote/folder'
    # Create directory
    f.mkdir('new_folder')
    # Create a file
    f.touch('new_file.txt')

    # Delete a remote file
    f.delete('someremote/folder/file.txt')

    # Close the connection
    f.close()

