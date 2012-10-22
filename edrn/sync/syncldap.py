#!/usr/bin/env python
# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN generic LDAP functions.
'''

import ldap

def personExists(ldapConn, uid):
    baseDn = "dc=edrn,dc=jpl,dc=nasa,dc=gov"
    searchFilter = "(uid="+uid+")"
    attrs = []
    try:
        results = ldapConn.search_s(baseDn, ldap.SCOPE_ONELEVEL, searchFilter, attrs)
        if results != None and len(results) > 0:
            return True
        else:
            return False
    except ldap.LDAPError, e:
        print e.message['info']
        


def groupExists(ldapConn, groupcn):
    baseDn = "dc=edrn,dc=jpl,dc=nasa,dc=gov"
    searchFilter = "(&(cn="+groupcn+")(objectClass=groupOfUniqueNames))"
    attrs = []
    try:
        results = ldapConn.search_s(baseDn, ldap.SCOPE_ONELEVEL, searchFilter, attrs)
        if results != None and len(results) > 0:
            return True
        else:
            return False
    except ldap.LDAPError, e:
        print e.message['info']


def memberExists(ldapConn, groupcn, uid):
    baseDn = "dc=edrn,dc=jpl,dc=nasa,dc=gov"
    searchFilter = "(&(cn="+groupcn+")(uniquemember="+uid+",dc=edrn,dc=jpl,dc=nasa,dc=gov))"
    attrs = []
    try:
        results = ldapConn.search_s(baseDn, ldap.SCOPE_ONELEVEL, searchFilter, attrs)
        if results != None and len(results) > 0:
            return True
        else:
            return False
    except ldap.LDAPError, e:
        print e.message['info']