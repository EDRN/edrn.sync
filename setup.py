#!/usr/bin/env python
# encoding: utf-8
# Copyright 2010–2015 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

import os.path
from setuptools import setup, find_packages

version = '1.0.4'

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
    return unicode(open(os.path.join(os.path.dirname(__file__), *rnames), 'rb').read(), 'utf-8')

long_description = _descr + read('docs', 'INSTALL.txt') + u'\n' + read('docs', 'USE.txt') + u'\n' + read('docs', 'HISTORY.txt')
open('doc.txt', 'wb').write(long_description.encode('utf-8'))

setup(
    name='edrn.sync',
    version=version,
    description='EDRN Sync Services',
    long_description=long_description,
    classifiers=_classifiers,
    keywords=_keywords,
    author='Chris Mattmann',
    author_email='chris.a.mattmann@jpl.nasa.gov',
    url='https://github.com/EDRN/edrn.sync',
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
        'oodt==0.9', # 0.10 doesn't include ez_setup.py and fails to install
        'python-ldap',
        'rdflib',
    ],
)
