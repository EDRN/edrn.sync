# encoding: utf-8
# Copyright 2010–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''EDRN Sync Services - unit tests for functions.'''

import unittest2 as unittest
import ldap
import edrn.sync.syncldap
from edrn.sync.utils import generatePassword


class LDAPFunctionsTest(unittest.TestCase):
    '''Test the LDAP functions.'''
    def search_s(self, baseDN, searchScope, searchFilter, attrs):
        if searchScope not in (ldap.SCOPE_SUBTREE, ldap.SCOPE_ONELEVEL, ldap.SCOPE_BASE):
            raise ldap.LDAPError(dict(info='Unknown scope'))
        self.lastFilter = searchFilter
        return None
    def testPersonExists(self):
        edrn.sync.syncldap.personExists(self, 'mattmann')
        self.assertEqual('(uid=mattmann)', self.lastFilter)
    def testGroupExists(self):
        edrn.sync.syncldap.groupExists(self, 'erne')
        self.assertEqual('(&(cn=erne)(objectClass=groupOfUniqueNames))', self.lastFilter)
    def testMemberExists(self):
        edrn.sync.syncldap.memberExists(self, 'erne', 'mattmann')
        self.assertEqual('(&(cn=erne)(uniquemember=mattmann,dc=edrn,dc=jpl,dc=nasa,dc=gov))', self.lastFilter)


class PasswordFunctionsTest(unittest.TestCase):
    u'''Test password generation'''
    def testPasswordGeneration(self):
        pwd1, pwd2 = generatePassword(), generatePassword()
        self.assertTrue(pwd1 != pwd2, u'Got identical passwords "{}" and "{}"'.format(pwd1, pwd2))
        self.assertTrue(pwd1 != 'changeme', u'Got a breakable password "changeme"')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
