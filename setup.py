from __future__ import print_function

from glob import glob

try:
    from setuptools import setup
except ImportError:
    print("Falling back to distutils. Functionality may be limited.")
    from distutils.core import setup

requires = []
long_description = open('README.rst').read() + "\n\n" + open("ChangeLog").read()

config = {
    'name'            : 'hn-saved-stories',
    'description'     : 'Archive saved stores from your Hacker News profile.',
    'long_description': long_description,
    'author'          : 'Brandon Sandrowicz',
    'author_email'    : 'brandon@sandrowicz.org',
    'url'             : 'https://github.com/bsandrow/hn-saved-stories',
    'version'         : '0.1',
    'packages'        : ['hn_saved_stores'],
    'package_data'    : { '': ['LICENSE'] },
    'scripts'         : glob('bin/*'),
    'install_requires': requires,
    'license'         : open('LICENSE').read(),
}

setup(**config)
