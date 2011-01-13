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
            email = self.stripMailTo(self.getSimpleElementText(node, "_3:mbox"))
            if email == None or email == "": 
                email = _defaultEmail
            uid = self.getSimpleElementText(node, "_3:accountName")
            firstname = self.getSimpleElementText(node, "_3:givenname")
            lastname = self.getSimpleElementText(node, "_3:surname")
            if uid == None or uid == "":
                uid = self.constructUID(firstname, lastname)
            
            phone = self.parsePhone(self.getSimpleElementText(node, "_3:phone"))
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
            abbrevName = self.getSimpleElementText(node, "_3:abbrevName")
            staffIdList = self.getStaffList(node)
            title = self.getSimpleElementText(node, "_4:title")
            pi = self.getPi(node)
            program = self.getSimpleElementText(node, "_3:program")
            memberType = self.getSimpleElementText(node, "_3:memberType")
            self.sites.append(RDFSite(siteId, abbrevName, staffIdList, title, pi, program, memberType))
            
            
    def getPi(self, node):
        piUriNode = self.getFirstElement(node, "_3:pi")
        if piUriNode <> None:
            piUri = piUriNode.getAttribute("rdf:resource")
        else:
            return None
        
        pid = piUri[piUri.rfind("/")+1:len(piUri)]
        return self.getPersonById(pid)     
            
    def getStaffList(self, node):
        staffList = []
        for staffNode in node.getElementsByTagName("_3:staff"):
            staffIdUri = staffNode.getAttribute("rdf:resource")
            staffId = staffIdUri[staffIdUri.rfind("/")+1:len(staffIdUri)]
            staffList.append(self.getPersonById(staffId))
        return staffList
        
        
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
       
           
class RDFSite:
    
    def __init__(self, id, abbrevName, staffList, title, pi, program, memberType):
        self.id = id
        self.abbrevName = abbrevName
        self.staffList = staffList
        self.title = title
        self.pi = pi
        self.program = program
        self.memberType = memberType