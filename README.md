ftpretty
========

A wrapper for simple FTP operations: get, put, list etc.

    from ftpretty import ftpretty

    # kwargs are passed to underlying FTP or FTP_TLS connection
    # secure argument switches to an FTP_TLS connection
    f = ftpretty(host, user, pass, secure=False, timeout=10)

    # Get a file, save it locally
    f.get('someremote/file/on/server.txt', '/tmp/localcopy/server.txt')

    # Get a file and write to an open file
    myfile = open('/tmp/localcopy/server.txt', 'wb')
    f.get('someremote/file/on/server.txt', myfile)

    # Get a file and return contents
    contents = f.get('someremote/file/on/server.txt')

    # Put a local file to a remote location
    # non-existent subdirectories will be created automatically
    f.put(local, remote)

    # Return a list the files in a directory
    f.list(remote)

    # Change to remote directory
    f.cd(remote)

    # Delete a remote file 
    f.delete(remote)

    # Close the connection
    f.close()

