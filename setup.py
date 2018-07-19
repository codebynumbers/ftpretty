#!/usr/bin/env python3.6

from os import path
from setuptools import setup

__version__ = '0.2.7'


def read(*paths):
    with open(path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='ftpretty',
    version=__version__,
    description='Pretty FTP Wrapper',
    long_description=(
        read('README.rst') + '\n\n' +
        read('HISTORY.rst') + '\n\n' +
        read('AUTHORS.rst')
    ),
    classifiers=[
        "Topic :: Internet :: File Transfer Protocol (FTP)",
        "Topic :: Utilities",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
    ],
    license='BSD',
    author='Antonio Jordan',
    author_email='antonio.jordan+ftpretty@dean.com',
    url='https://github.com/bornwitbugs/ftpretty/',
    download_url='https://github.com/bornwitbugs/ftpretty/tarball/%s' % __version__,
    py_modules=['ftpretty'],
    test_suite = 'tests.test_ftpretty.suite',
)
