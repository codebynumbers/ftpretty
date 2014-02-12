#!/usr/bin/env python
from setuptools import setup
import os

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(name='ftpretty',
      version='0.1.1',
      description='Pretty FTP wrapper',
      long_description=read('README.rst'),
      license='MIT',
      author='Rob Harrigan',
      author_email='harrigan.rob@gmail.com',
      url='https://github.com/codebynumbers/ftpretty/',
      download_url='https://github.com/codebynumbers/ftpretty/tarball/0.1.1',
      py_modules=['ftpretty'],
     )

