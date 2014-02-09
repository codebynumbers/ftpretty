ftpretty
========

A wrapper for simple FTP operations: get, put, list etc.

    from ftpretty import ftpretty

    # kwargs are passed to underlying FTP or FTP_TLS connection
    # secure argument switches to an FTP_TLS connection
    f = ftpretty(host, user, pass, secure=False, timeout=10)

    # Get a file, save it locally
    f.get(remote, local)

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

