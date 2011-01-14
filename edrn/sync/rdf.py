#!/usr/bin/env python
# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''EDRN RDF data structures for use in the sync tools.
'''
import xml.dom.minidom
import re
from xml.dom.minidom import Node

_defaultPhone = '555-555-5555'
_defaultEmail = 'unknown@example.com'

    
def getSimpleElementText(node, elemName):
    elemNode = getFirstElement(node, elemName)
    if elemNode <> None:
        return elemNode.firstChild.data
    else:
        return ""

def getFirstElement(node, elemName):
    return node.getElementsByTagName(elemName).item(0)   

def stripId(node, attr):
    if node == None: return None
    idUri = node.getAttribute(attr)
    id = idUri[idUri.rfind("/")+1:len(idUri)]
    return id

            
def getStaffList(node, name, attr, personList):
    staffList = []
    for staffNode in node.getElementsByTagName(name):
        staffId = stripId(staffNode, attr)
        staffList.append(getPersonById(staffId, personList))
    return staffList

    
def getPersonById(personId, personList):
    if personId == None: return None
    for person in personList:
        if person.rdfId == personId:
            return person 
    return None
    
class RDFPersonList:
    
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
        if newuid.find(",") <> -1:
            newuid = newuid[0:newuid.find(",")]
        return newuid
    
    def stripMailTo(self, email):
        return email[email.find(":")+1:len(email)]
    
    def getSiteId(self, node):
        return stripId(getFirstElement(node, "_4:site"),"rdf:resource")
    
    def getRdfId(self, node):
        return stripId(node, "rdf:about")
            

class RDFPerson:
    
    def __init__(self, rdfId, siteId, email, uid, firstname, lastname, phone):
        self.rdfId = rdfId
        self.siteId = siteId
        self.email = email
        self.uid = uid
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone  
        
        
class RDFSiteList:
    
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
        pid = stripId(getFirstElement(node, "_3:pi"), "rdf:resource")
        return getPersonById(pid, self.personList)     
        
    def getSiteId(self, node):
        return stripId(node, "rdf:resource")
       
           
class RDFSite:
    
    def __init__(self, id, abbrevName, staffList, title, pi, program, memberType):
        self.id = id
        self.abbrevName = abbrevName
        self.staffList = staffList
        self.title = title
        self.pi = pi
        self.program = program
        self.memberType = memberType

class RDFCollaborativeGroupList:

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
        return stripId(node, "rdf:about")
                

class RDFCollaborativeGroup:
    
    def __init__(self, id, title, staffList, groupType):
        self.id = id
        self.title = title
        self.staffList = staffList
        self.groupType = groupType