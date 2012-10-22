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
from rdf import RDFPersonList, RDFSiteList, RDFCollaborativeGroupList
from syncldap import groupExists

warnings.filterwarnings("ignore")
_verbose = False
_helpMessage = '''
Usage: dmccgroupsync [-v] [-u LDAP DN] [-p password] [-l LDAP URL] RDF-USER-URL RDF-SITE-URL RDF-COMMITTEE-URL

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
        
def makePIGroups(rdfUsersFile, rdfSiteFile, ldapUrl, adminUser, adminPass):
    rdfPersons = RDFPersonList(rdfUsersFile)
    rdfSites = RDFSiteList(rdfSiteFile, rdfPersons.persons)
    
    for site in rdfSites.sites:
        # first need to create group name
        if site.pi == None:
            print "Skipping ingestion of site: ["+site.title+"]: was not able to link to PI.\n"
            continue
        
        groupName = site.pi.lastname+" "+site.title
        groupName = groupName.strip().replace(","," ")
        
        print "Processing PI group: ["+groupName+"]\n"
        # now add group only if it doesn't exist yet
        _addGroup(ldapUrl, adminUser, adminPass, groupName, site.staffList)
        
def makeCollabGroups(rdfUsersFile, rdfCommitteesFile, ldapUrl, adminUser, adminPass):
    rdfPersons = RDFPersonList(rdfUsersFile)
    rdfCommittees = RDFCollaborativeGroupList(rdfCommitteesFile, rdfPersons.persons)
    
    for committee in rdfCommittees.groups:
        if committee.groupType != None and committee.groupType == "Collaborative Group":
            groupName = committee.title[0:committee.title.rfind("Cancers Research Group")].strip()
            
            print "Processing collaborative group: ["+groupName+"]\n"
            # now add group only if it doesn't exist yet
            _addGroup(ldapUrl, adminUser, adminPass, groupName, committee.staffList)
            

def _addGroup(ldapUrl, adminUser, adminPass, groupName, staffList):
    ldapConn = ldap.initialize(ldapUrl)
    ldapConn.simple_bind_s(adminUser, adminPass)

    if not groupExists(ldapConn, groupName):
        # construct DN
        dn = u"cn="+groupName+",dc=edrn,dc=jpl,dc=nasa,dc=gov"
        attrs={}
        attrs['objectclass'] = ['top', 'groupOfUniqueNames']
        attrs['cn'] = str(groupName)
        attrs['description'] = str(groupName)
        
        memberuidList = []
        for staff in staffList:
            if staff != None:
                memberuidList.append(str("uid="+staff.uid+",dc=edrn,dc=jpl,dc=nasa,dc=gov"))
        
        attrs['uniquemember'] = memberuidList
        ldif = modlist.addModlist(attrs)
        verboseLog("Creating group: ["+str(ldif)+"]\n")
        try:
            ldapConn.add_s(dn,ldif)
        except ldap.LDAPError, e:
            print e.message['info']        
    else:
        # try to add the new members to it
        verboseLog("Group: ["+groupName+"] already exists: attempting to update members")
        dn = u"cn="+groupName+",dc=edrn,dc=jpl,dc=nasa,dc=gov"
        results = ldapConn.search_ext_s('dc=edrn,dc=jpl,dc=nasa,dc=gov', ldap.SCOPE_ONELEVEL, '(cn=%s)' % groupName,
            ['uniquemember'])
        members = set()
        for resultDN, attrs in results:
            if dn != resultDN: continue
            members = members.union(attrs['uniquemember'])
        for staff in staffList:
            members.add('uid=' + str(staff.uid) + ',dc=edrn,dc=jpl,dc=nasa,dc=gov')
        mod_attrs = [(ldap.MOD_REPLACE, 'uniquemember', list(members))]
        verboseLog("Replace group members for ["+groupName+"] with ["+str(members)+"]\n")
        try:
            ldapConn.modify_s(dn, mod_attrs)
        except ldap.LDAPError, e:
            print e.message['info']
    ldapConn.unbind_s()            


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
        rdfCommitteesFile = args[2]
        makePIGroups(rdfUsersFile, rdfSiteFile, ldapUrl, ldapUser, ldapPass)
        makeCollabGroups(rdfUsersFile, rdfCommitteesFile, ldapUrl, ldapUser, ldapPass)

    except _Usage, err:
        print >>sys.stderr, sys.argv[0].split('/')[-1] + ': ' + str(err.msg)
        return 2
    

if __name__ == '__main__':
    sys.exit(main())
