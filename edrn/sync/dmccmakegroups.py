#!/usr/bin/env python
# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''EDRN RDF Group Sync tool dmccgroupsync - parse user and site RDF from DMCC and build groups in EDRN IC cancer LDAPS server.
'''

import sys, getopt
import warnings
import ldap
import ldap.modlist as modlist
from rdf import RDFPersonList, RDFSiteList

warnings.filterwarnings("ignore")
_verbose = False
_helpMessage = '''
Usage: dmccgroupsync [-v] [-u LDAP DN] [-p password] [-l LDAP URL] user RDF file site RDF file...

Options:
-v, --verbose
    Work verbosely rather than silently.
-u, --user
    An LDAP DN identifying the user who has permission to add 
    entries to the LDAP server. This will likely be e.g., uid=admin, ou=system.
-p, --password
    The password for the user who has permission to add entries to the LDAP server.
-l  --ldapUrl
    The LDAP URL pointing to the server to synchronize with.

Environment:
None'''

def verboseLog(message):
    if _verbose:
        print >>sys.stderr, message

class _Usage(Exception):
    '''An error for problems with arguments on the command line.'''
    def __init__(self, msg):
        self.msg = msg
        
def makeGroups(rdfUsersFile, rdfSiteFile, ldapUrl, adminUser, adminPass):
    rdfPersons = RDFPersonList(rdfUsersFile)
    rdfSites = RDFSiteList(rdfSiteFile, rdfPersons.persons)
    
    for site in rdfSites.sites:
        print "Processing group: ["+site.abbrevName+"]\n"
        
        # first need to create group name
        groupName = str(site.pi.lastname+" "+site.title).strip()
        
        # now add group only if it doesn't exist yet
        _addGroup(ldapUrl, adminUser, adminPass, groupName, site.staffList)

def _addGroup(ldapUrl, adminUser, adminPass, groupName, staffList):
    ldapConn = ldap.initialize(ldapUrl)
    ldapConn.simple_bind_s(adminUser, adminPass)

    if not _groupExists(ldapConn, groupName):
        # construct DN
        dn = u"cn="+groupName+",dc=edrn,dc=jpl,dc=nasa,dc=gov"
        attrs={}
        attrs['objectclass'] = ['top', 'groupOfUniqueNames']
        attrs['cn'] = str(groupName)
        attrs['description'] = str(groupName)
        
        memberuidList = []
        for staff in staffList:
            memberuidList.append(str("uid="+staff.uid+",dc=edrn,dc=jpl,dc=nasa,gov"))
        
        attrs['uniquemember'] = memberuidList
        ldif = modlist.addModlist(attrs)
        success=False
        verboseLog("Creating group: ["+str(ldif)+"]")
        try:
            ldapConn.add_s(dn,ldif)
            success=True
        except ldap.LDAPError, e:
            print e.message['info']        
    else:
        # try to add the new members to it
        verboseLog("Group: ["+groupName+"] already exists: attempting to add new members")
        
    
    ldapConn.unbind_s()            


def _groupExists(ldapConn, groupcn):
    baseDn = "dc=edrn,dc=jpl,dc=nasa,dc=gov"
    filter = "(&(cn="+groupcn+")(objectClass=groupOfUniqueNames))"
    attrs=[]
    try:
        results = ldapConn.search_s(baseDn, ldap.SCOPE_SUBTREE, filter, attrs)
        if results <> None and len(results) > 0:
            return True
        else:
            return False
    except ldap.LDAPError, e:
        print e.message['info']


def _memberExists(ldapConn, groupcn, uid):
    baseDn = "dc=edrn,dc=jpl,dc=nasa,dc=gov"
    filter = "(&(cn="+groupcn+")(uniquemember="+uid+",dc=edrn,dc=jpl,dc=nasa,dc=gov))"
    attrs=[]
    try:
        results = ldapConn.search_s(baseDn, ldap.SCOPE_SUBTREE, filter, attrs)
        if results <> None and len(results) > 0:
            return True
        else:
            return False
    except ldap.LDAPError, e:
        print e.message['info']
    
    
    
def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'hvu:p:l:', ['help', 'verbose', 'user=', 'password=', 'ldapUrl='])
        except getopt.error, msg:
            raise _Usage(msg)
        if len(args) == 0:
            raise _Usage(_helpMessage)
        
        ldapUser = None
        ldapPass = None
        ldapUrl = None
        
        # Process options
        for option, value in opts:
            if option in ('-v', '--verbose'):
                global _verbose
                _verbose = True
            elif option in ('-h', '--help'):
                raise _Usage(_helpMessage)
            elif option in ('-u', '--user'):
                ldapUser = value
            elif option in ('-p', '--password'):
                ldapPass = value
            elif option in ('-l', '--ldapUrl'):
                ldapUrl = value
        
        if ldapUser == None or ldapPass == None or ldapUrl == None:
            raise _Usage(_helpMessage)
            
        rdfUsersFile = args[0]
        rdfSiteFile = args[1]
        makeGroups(rdfUsersFile, rdfSiteFile, ldapUrl, ldapUser, ldapPass)

    except _Usage, err:
        print >>sys.stderr, sys.argv[0].split('/')[-1] + ': ' + str(err.msg)
        return 2
    

if __name__ == '__main__':
    sys.exit(main())
