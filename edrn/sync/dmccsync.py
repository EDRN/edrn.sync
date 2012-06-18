#!/usr/bin/env python
# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''EDRN RDF User Sync tool dmccsync - parse user RDF from DMCC and sync to EDRN IC cancer LDAPS server.
'''

import sys, getopt
import xml.dom.minidom
import warnings
import ldap
import re
import time
import ldap.modlist as modlist
from xml.dom.minidom import Node
from syncldap import personExists
from rdf import RDFPersonList

warnings.filterwarnings("ignore")
_verbose = False
_defaultPwd = 'changeme'
_defaultEmail = 'unknown@example.com'
_defaultDesc = 'imported via EDRN dmccsync at '
_defaultPhone = '555-555-5555'
_helpMessage = '''
Usage: dmccsync [-v] [-u LDAP DN] [-p password] [-l LDAP URL] RDF-URL...

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

def sync(rdfUsersFile, ldapUrl, adminUser, adminPass):
    pList = RDFPersonList(rdfUsersFile)
    processed=0
    for person in pList.persons:
        if _addUserToLDAP(ldapUrl, adminUser, adminPass, person):
            processed=processed+1
    
    print "Added "+str(processed)+" entries to the LDAP server at: ["+ldapUrl+"]"

def _addUserToLDAP(ldapUrl, adminUser, adminPass, rdfPerson):
    ldapConn = ldap.initialize(ldapUrl)
    ldapConn.simple_bind_s(adminUser, adminPass)

    # construct DN
    dn = "uid="+rdfPerson.uid+",dc=edrn,dc=jpl,dc=nasa,dc=gov"
    attrs = {}
    attrs['objectclass'] = ['top', 'person', 'organizationalPerson', 'edrnPerson', 'inetOrgPerson']
    attrs['cn'] = str(rdfPerson.firstname + " " +rdfPerson.lastname)
    attrs['userPassword'] = str(_defaultPwd)
    attrs['uid'] = str(rdfPerson.uid)
    attrs['mail'] = str(rdfPerson.email)
    attrs['telephoneNumber'] = str(rdfPerson.phone)
    attrs['sn'] = str(rdfPerson.lastname)
    attrs['description'] = str(_defaultDesc+time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))
    
    ldif = modlist.addModlist(attrs)
    success=False
    
    if(not personExists(ldapConn, rdfPerson.uid)):
        verboseLog("Syncing record: ["+str(ldif)+"]")
        try:
            ldapConn.add_s(dn,ldif)
            success=True
        except ldap.LDAPError, e:
            print e.message['info']
    else:
        verboseLog("Skipping record: [uid="+rdfPerson.uid+"]: entry already exists in ["+ldapUrl+"]")
        
    ldapConn.unbind_s()
    return success
    
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
            
        rdfUsersFile = ' '.join(args)
        sync(rdfUsersFile, ldapUrl, ldapUser, ldapPass)
    except _Usage, err:
        print >>sys.stderr, sys.argv[0].split('/')[-1] + ': ' + str(err.msg)
        return 2
    

if __name__ == '__main__':
    sys.exit(main())
