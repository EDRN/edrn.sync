#!/usr/bin/env python
# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''EDRN RDF Group Sync tool dmccgroupsync - parse user and site RDF from DMCC and build groups in EDRN IC cancer LDAPS server.
'''

import sys, getopt
import xml.dom.minidom
import warnings
import ldap
import re
import time
import ldap.modlist as modlist
from xml.dom.minidom import Node

warnings.filterwarnings("ignore")
_verbose = False
_defaultPhone = '555-555-5555'
_defaultEmail = 'unknown@example.com'
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
        
class _RDFPersonList:
    
    def __init__(self, filePath):
        self.filePath = filePath
        self.persons = []
        self.parse()

    def parse(self):
        doc = xml.dom.minidom.parse(self.filePath)
        for node in doc.getElementsByTagName("rdf:Description"):
            rdfId = self.getRdfId(node)
            siteId = self.getSiteId(node)
            email = self.stripMailTo(self.getSimpleElementText(node, "_3:mbox"))
            if email == None or email == "": 
                email = _defaultEmail
            uid = self.getSimpleElementText(node, "_3:accountName")
            firstname = self.getSimpleElementText(node, "_3:givenname")
            lastname = self.getSimpleElementText(node, "_3:surname")
            if uid == None or uid == "":
                uid = self.constructUID(firstname, lastname)
            
            phone = self.parsePhone(self.getSimpleElementText(node, "_3:phone"))
            verboseLog("Found person: ["+str(lastname)+", "+str(firstname)+"]")
            self.persons.append(_RDFPerson(rdfId, siteId, email, uid, firstname, lastname, phone))
            
    def parsePhone(self, phone):
        if phone == None or phone == "":
            return _defaultPhone
        phonePattern = re.compile(r'''
        # don't match beginning of string, number can start anywhere
        (\d{3})     # area code is 3 digits (e.g. '800')
        \D*         # optional separator is any number of non-digits
        (\d{3})     # trunk is 3 digits (e.g. '555')
        \D*         # optional separator
        (\d{4})     # rest of number is 4 digits (e.g. '1212')
        \D*         # optional separator
        (\d*)       # extension is optional and can be any number of digits
        $           # end of string
        ''', re.VERBOSE)
        parsedPhone = _defaultPhone
        try:
            parsedPhone = '-'.join(phonePattern.search(phone).groups()[0:3])
        except AttributeError, e:
            print e   
        return parsedPhone

    def constructUID(self, firstname, lastname):
        newuid = (firstname[0:1]+lastname).lower()
        # take care of people with ,'s in their user ids
        if newuid.find(",") <> -1:
            newuid = newuid[0:newuid.find(",")]
        return newuid
    
    def stripMailTo(self, email):
        return email[email.find(":")+1:len(email)]
    
    def getSiteId(self, node):
        siteIdUri = self.getFirstElement(node, "_4:site").getAttribute("rdf:resource")
        siteId = siteIdUri[siteIdUri.rfind("/")+1:len(siteIdUri)]
        return siteId
    
    def getRdfId(self, node):
        rdfIdUri = node.getAttribute("rdf:about")
        rdfId = rdfIdUri[rdfIdUri.rfind("/")+1:len(rdfIdUri)]
        return rdfId
    
    def getSimpleElementText(self, node, elemName):
        elemNode = self.getFirstElement(node, elemName)
        if elemNode <> None:
            return elemNode.firstChild.data
        else:
            return ""
    
    def getFirstElement(self, node, elemName):
        return node.getElementsByTagName(elemName).item(0)
        
            

class _RDFPerson:
    
    def __init__(self, rdfId, siteId, email, uid, firstname, lastname, phone):
        self.rdfId = rdfId
        self.siteId = siteId
        self.email = email
        self.uid = uid
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone  
        
        
class _RDFSiteList:
    
    def __init__(self, filePath, personList):
        self.filePath = filePath
        self.personList = personList
        self.sites = []
        self.parse()

    def parse(self):
        doc = xml.dom.minidom.parse(self.filePath)
        for node in doc.getElementsByTagName("rdf:Description"):            
            siteId = self.getSiteId(node)
            abbrevName = self.getSimpleElementText(node, "_3:abbrevName")
            staffIdList = self.getStaffIdList(node)
            title = self.getSimpleElementText(node, "_3:title")
            pi = self.getPi(node)
            program = self.getSimpleElementText(node, "_3:program")
            memberType = self.getSimpleElementText(node, "_3:memberType")
            verboseLog("Found site: ["+str(abbrevName)+"]")
            self.sites.append(_RDFSite(siteId, abbrevName, staffIdList, title, pi, program, memberType))
            
            
    def getPi(self, node):
        piUriNode = self.getFirstElement(node, "_3:pi")
        if piUriNode <> None:
            piUri = piUriNode.getAttribute("rdf:resource")
        else:
            return None
        
        pid = piUri[piUri.rfind("/")+1:len(piUri)]
        pi = self.getPersonById(pid)     
        if pi == None: return None
        return pi.lastname+", "+pi.firstname
            
    def getStaffIdList(self, node):
        staffIdList = []
        for staffNode in node.getElementsByTagName("_3:staff"):
            staffIdUri = staffNode.getAttribute("rdf:resource")
            staffId = staffIdUri[staffIdUri.rfind("/")+1:len(staffIdUri)]
            staffIdList.append(staffId)
        return staffIdList
        
        
    def getSiteId(self, node):
        siteIdUri = node.getAttribute("rdf:resource")
        siteId = siteIdUri[siteIdUri.rfind("/")+1:len(siteIdUri)]
        return siteId  
    
    def getSimpleElementText(self, node, elemName):
        elemNode = self.getFirstElement(node, elemName)
        if elemNode <> None:
            return elemNode.firstChild.data
        else:
            return ""
    
    def getFirstElement(self, node, elemName):
        return node.getElementsByTagName(elemName).item(0)    
    
    def getPersonById(self, personId):
        for person in self.personList:
            if person.rdfId == personId:
                return person 
        return None
       
           
class _RDFSite:
    
    def __init__(self, id, abbrevName, staffIdList, title, pi, program, memberType):
        self.id = id
        self.abbrevName = abbrevName
        self.staffIdList = staffIdList
        self.title = title
        self.pi = pi
        self.program = program
        self.memberType = memberType
        
           
def makeGroups(rdfUsersFile, rdfSiteFile, ldapUrl, adminUser, adminPass):
    rdfPersons = _RDFPersonList(rdfUsersFile)
    rdfSites = _RDFSiteList(rdfSiteFile, rdfPersons.persons)
    
    for site in rdfSites.sites:
        verboseLog("Processing site: ["+site.abbrevName+"]")
    
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
