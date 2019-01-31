#!/usr/bin/env python3

from os import path
from setuptools import setup

__version__ = '0.2.8'


def read(*paths):
    with open(path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='ftpretty',
    version=__version__,

    packages=['ftpretty',],

    author='bornwitbugs',
    author_email='40208858+bornwitbugs@users.noreply.github.com',
    description='Pretty FTP Wrapper',
    download_url='https://github.com/bornwitbugs/ftpretty/tarball/{0}'.format(__version__),
    license='BSD',
    long_description=(
        read('README.rst') + '\n\n' +
        read('HISTORY.rst') + '\n\n' +
        read('AUTHORS.rst')
    ),
    keywords='ftp ftps file transfer protocal',
    platforms=['any'],
    test_suite = 'tests.test_ftpretty.suite',
    url='https://github.com/bornwitbugs/ftpretty/',
    classifiers=[
        "Topic :: Internet :: File Transfer Protocol (FTP)",
        "Topic :: Utilities",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
    ],
)
