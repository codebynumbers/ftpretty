#!/usr/bin/env python
from setuptools import setup
import os

__version__ = '0.4.0'


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='ftpretty',
    version=__version__,
    description='Pretty FTP wrapper',
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
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
    ],
    license='MIT',
    author='Rob Harrigan',
    author_email='harrigan.rob@gmail.com',
    url='https://github.com/codebynumbers/ftpretty/',
    download_url='https://github.com/codebynumbers/ftpretty/tarball/%s' % __version__,
    py_modules=['ftpretty','compat'],
    install_requires = [
        'python-dateutil',
    ],
    tests_require = [
        'libfaketime',
        'fs'
    ],
    test_suite = 'tests.test_ftpretty.suite',
)
