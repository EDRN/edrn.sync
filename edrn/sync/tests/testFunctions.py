# encoding: utf-8
# Copyright 2010–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''EDRN Sync Services - unit tests for functions.'''

import unittest2 as unittest
import ldap
import edrn.sync.syncldap

class LDAPFunctionsTest(unittest.TestCase):
    '''Test the LDAP functions.'''
    def search_s(self, baseDN, searchScope, searchFilter, attrs):
        if searchScope not in (ldap.SCOPE_SUBTREE, ldap.SCOPE_ONELEVEL, ldap.SCOPE_BASE):
            raise ldap.LDAPError(dict(info='Unknown scope'))
        self.lastFilter = searchFilter
        return None
    def testPersonExists(self):
        edrn.sync.syncldap.personExists(self, 'mattmann')
        self.assertEquals('(uid=mattmann)', self.lastFilter)
    def testGroupExists(self):
        edrn.sync.syncldap.groupExists(self, 'erne')
        self.assertEquals('(&(cn=erne)(objectClass=groupOfUniqueNames))', self.lastFilter)
    def testMemberExists(self):
        edrn.sync.syncldap.memberExists(self, 'erne', 'mattmann')
        self.assertEquals('(&(cn=erne)(uniquemember=mattmann,dc=edrn,dc=jpl,dc=nasa,dc=gov))', self.lastFilter)


    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
