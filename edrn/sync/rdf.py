#!/usr/bin/env python
# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN RDF data structures for use in the sync tools.'''

import xml.dom.minidom
import re
from xml.dom.minidom import Node

_defaultPhone = '555-555-5555'
_defaultEmail = 'unknown@example.com'
    
def getSimpleElementText(node, elemName):
    '''Get the text from the first element named ``elemName`` from under the ``node``, or the empty string if
    the named isn't found.'''
    elemNode = getFirstElement(node, elemName)
    return elemName.firstChild.data if elemNode != None else ''

def getFirstElement(node, elemName):
    '''Get the first XML element named ``elemName`` that's under ``node``.'''
    return node.getElementsByTagName(elemName).item(0)   

def getStaffList(node, name, attr, personList):
    '''Get the staff members identified by the node named ``name`` and attribute ``attr`` under the XML
    node ``node`` and looking up people in ``personList``.'''
    staffList = []
    for staffNode in node.getElementsByTagName(name):
        staffId = staffNode.getAttribute(attr)
        staffList.append(getPersonById(staffId, personList))
    return staffList

    
def getPersonById(personId, personList):
    '''Get the person with matching ``personId`` out of ``personList``, or None if not found.'''
    if personId == None: return None
    for person in personList:
        if person.rdfId == personId:
            return person 
    return None
    
class RDFPersonList(object):
    '''A list of EDRN people from RDF.'''
    def __init__(self, filePath):
        self.filePath = filePath
        self.persons = []
        self.parse()
    def parse(self):
        doc = xml.dom.minidom.parse(self.filePath)
        for node in doc.getElementsByTagName("rdf:Description"):
            rdfId = self.getRdfId(node)
            siteId = self.getSiteId(node)
            email = self.stripMailTo(getSimpleElementText(node, "_3:mbox"))
            if email == None or email == "": 
                email = _defaultEmail
            uid = getSimpleElementText(node, "_3:accountName")
            firstname = getSimpleElementText(node, "_3:givenname")
            lastname = getSimpleElementText(node, "_3:surname")
            if uid == None or uid == "":
                uid = self.constructUID(firstname, lastname)
            
            phone = self.parsePhone(getSimpleElementText(node, "_3:phone"))
            self.persons.append(RDFPerson(rdfId, siteId, email, uid, firstname, lastname, phone))
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
        if newuid.find(",") != -1:
            newuid = newuid[0:newuid.find(",")]
        return newuid
    def stripMailTo(self, email):
        return email[email.find(":")+1:len(email)]
    def getSiteId(self, node):
        elem = getFirstElement(node, '_4:site')
        return None if not elem else elem.getAttribute('rdf:resource')
    def getRdfId(self, node):
        return node.getAttribute('rdf:about')
    def __len__(self):
        return len(self.persons)
    def __add__(self, i):
        self.persons.add(i)
    def __getitem__(self, key):
        return self.persons[key]
    def __setitem__(self, key, value):
        self.persons[key] = value
    def __delitem__(self, key):
        del self.persons[key]
    def __iter__(self):
        return iter(self.persons)
    def __contains__(self, item):
        return item in self.persons

class RDFPerson(object):
    '''An EDRN person from RDF.'''
    def __init__(self, rdfId, siteId, email, uid, firstname, lastname, phone):
        self.rdfId = rdfId
        self.siteId = siteId
        self.email = email
        self.uid = uid
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone  
        
class RDFSiteList(object):
    '''A list of EDRN sites from RDF.'''
    def __init__(self, filePath, personList):
        self.filePath = filePath
        self.personList = personList
        self.sites = []
        self.parse()
    def parse(self):
        doc = xml.dom.minidom.parse(self.filePath)
        for node in doc.getElementsByTagName("rdf:Description"):            
            siteId = self.getSiteId(node)
            abbrevName = getSimpleElementText(node, "_3:abbrevName")
            staffIdList = getStaffList(node, "_3:staff", "rdf:resource", self.personList)
            title = getSimpleElementText(node, "_4:title")
            pi = self.getPi(node)
            program = getSimpleElementText(node, "_3:program")
            memberType = getSimpleElementText(node, "_3:memberType")
            self.sites.append(RDFSite(siteId, abbrevName, staffIdList, title, pi, program, memberType))
    def getPi(self, node):
        elem = getFirstElement(node, '_3:pi')
        pid = elem.getAttribute('rdf:resource') if elem else None
        return getPersonById(pid, self.personList) if pid else None
    def getSiteId(self, node):
        return node.getAttribute('rdf:about')
    def __len__(self):
        return len(self.sites)
    def __add__(self, i):
        self.sites.add(i)
    def __getitem__(self, key):
        return self.sites[key]
    def __setitem__(self, key, value):
        self.sites[key] = value
    def __delitem__(self, key):
        del self.sites[key]
    def __iter__(self):
        return iter(self.sites)
    def __contains__(self, item):
        return item in self.sites

 
class RDFSite(object):
    '''An EDRN site.'''
    def __init__(self, id, abbrevName, staffList, title, pi, program, memberType):
        self.id = id
        self.abbrevName = abbrevName
        self.staffList = staffList
        self.title = title
        self.pi = pi
        self.program = program
        self.memberType = memberType

class RDFCollaborativeGroupList(object):
    '''A list of collaborative groups from RDF.'''
    def __init__(self, filePath, personList):
        self.filePath = filePath
        self.personList = personList
        self.groups = []
        self.parse()
    def parse(self):
        doc = xml.dom.minidom.parse(self.filePath)
        for node in doc.getElementsByTagName("rdf:Description"):            
            groupId = self.getGroupId(node)
            title = getSimpleElementText(node, "_4:title")
            staffList = getStaffList(node, "_3:member", "rdf:resource", self.personList)
            groupType = getSimpleElementText(node, "_3:committeeType")
            self.groups.append(RDFCollaborativeGroup(groupId, title, staffList, groupType))
    def getGroupId(self, node):
        return node.getAttribute('rdf:about')
    def __len__(self):
        return len(self.groups)
    def __add__(self, i):
        self.groups.add(i)
    def __getitem__(self, key):
        return self.groups[key]
    def __setitem__(self, key, value):
        self.groups[key] = value
    def __delitem__(self, key):
        del self.groups[key]
    def __iter__(self):
        return iter(self.groups)
    def __contains__(self, item):
        return item in self.groups

class RDFCollaborativeGroup(object):
    '''An EDRN collaborative group.'''
    def __init__(self, id, title, staffList, groupType):
        self.id = id
        self.title = title
        self.staffList = staffList
        self.groupType = groupType
