from datetime import datetime
try:
    from hashlib import sha3_512 as hashbrown
except ImportError as err:
    from hashlib import sha512 as hashbrown
from io import BytesIO, IOBase

def hash(filename, algorithm=None, blocksize=65536):
    if not algorithm:
        algorithm = hashbrown()
    if isinstance(filename, str):
        try:
            with open(filename, 'rb') as filestream:
                buffer = filestream.read(blocksize)
                while len(buffer) > 0:
                    algorithm.update(buffer)
                    buffer = filestream.read(blocksize)
        except FileNotFoundError:
            algorithm.update(bytes(filename.encode('utf-8')))
    elif isinstance(filename, BytesIO):
        buffer = filename.read1(blocksize)
        while len(buffer) > 0:
            algorithm.update(buffer)
            buffer = filename.read1(blocksize)
    elif isinstance(filename, IOBase):
        buffer = filename.read(blocksize)
        while len(buffer) > 0:
            algorithm.update(buffer)
            buffer = filename.read(blocksize)

    return algorithm.hexdigest()

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
