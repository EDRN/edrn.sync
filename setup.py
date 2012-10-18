#!/usr/bin/env python
# encoding: utf-8
# Copyright 2010–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

import os.path
from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

version = '1.0.2'

_descr = u'''**********
edrn.sync
**********

.. contents::

EDRN Sync provides an API for slurping up DMCC RDF representing
EDRN users and groups and registering those users into our EDRN 
IC LDAP server.

'''
_keywords = 'edrn sync ldap dmcc informatics center'
_classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Science/Research',
    'License :: Other/Proprietary License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Database :: Front-Ends',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = _descr + read('docs', 'INSTALL.txt') + '\n' + read('docs', 'USE.txt') + '\n' + read('docs', 'HISTORY.txt') + '\n'
open('doc.txt', 'w').write(long_description)

setup(
    name='edrn.sync',
    version=version,
    description='EDRN Sync Services',
    long_description=long_description,
    classifiers=_classifiers,
    keywords=_keywords,
    author='Chris Mattmann',
    author_email='chris.a.mattmann@jpl.nasa.gov',
    url='http://cancer.jpl.nasa.gov/',
    download_url='http://oodt.jpl.nasa.gov/dist/edrn-sync',
    license=read('docs', 'LICENSE.txt'),
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['edrn'],
    include_package_data=True,
    zip_safe=True,
    test_suite='edrn.sync.tests',
    extras_require={'test': ['unittest2']},
    entry_points={
        'console_scripts': [
            'dmccsync = edrn.sync.dmccsync:main',
            'dmccgroupsync = edrn.sync.dmccmakegroups:main',
        ],
    }, 
    package_data = {
        # And include any *.conf files found in the 'conf' subdirectory
        # for the edrn.sync package
        'edrn.sync.conf': ['*.conf'],
        'edrn.sync': ['*.files'],
    },
    install_requires=[
        'setuptools',
        'oodt',
        'python-ldap',
        'rdflib',
    ],
)
