#!/usr/bin/env python
# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN RDF data structures for use in the sync tools.'''

from rdflib.term import URIRef
import rdflib
import re

# Bogus phone number if we can't figure one out
_defaultPhone = '555-555-5555'

# General predicate URIs
_typeURI  = URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
_titleURI = URIRef(u'http://purl.org/dc/terms/title')

# Predicate URIs for people
_emailURI      = URIRef(u'http://xmlns.com/foaf/0.1/mbox')
_givennameURI  = URIRef(u'http://xmlns.com/foaf/0.1/givenname')
_personTypeURI = URIRef(u'http://edrn.nci.nih.gov/rdf/types.rdf#Person')
_phoneURI      = URIRef(u'http://xmlns.com/foaf/0.1/phone')
_siteURI       = URIRef(u'http://edrn.nci.nih.gov/rdf/schema.rdf#site')
_surnameURI    = URIRef(u'http://xmlns.com/foaf/0.1/surname')
_userIDURI     = URIRef(u'http://xmlns.com/foaf/0.1/accountName')

# Predicate URIs for sites
_abbrevNameURI = URIRef(u'http://edrn.nci.nih.gov/rdf/schema.rdf#abbrevName')
_memberTypeURI = URIRef(u'http://edrn.nci.nih.gov/rdf/schema.rdf#memberType')
_piURI         = URIRef(u'http://edrn.nci.nih.gov/rdf/schema.rdf#pi')
_programURI    = URIRef(u'http://edrn.nci.nih.gov/rdf/schema.rdf#program')
_siteTypeURI   = URIRef(u'http://edrn.nci.nih.gov/rdf/types.rdf#Site')
_staffURI      = URIRef(u'http://edrn.nci.nih.gov/rdf/schema.rdf#staff')

# Predicate URIs for committees
_committeeTypeURI = URIRef(u'http://edrn.nci.nih.gov/rdf/types.rdf#Committee')
_groupTypeURI     = URIRef(u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#committeeType')
_memberURI        = URIRef(u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#member')
_chairURI         = URIRef(u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#chair')
_coChairURI       = URIRef(u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#coChair')
_consultantURI    = URIRef(u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#consultant')
_allMemberURIs    = (_memberURI, _chairURI, _coChairURI, _consultantURI)


def getPersonById(personId, personList):
    '''Get the person with matching ``personId`` out of ``personList``, or None if not found.'''
    if personId == None: return None
    for person in personList:
        if person.rdfId == personId:
            return person 
    return None
    
class _RDFList(object):
    '''An abstract list of objects described by RDF.'''
    def __init__(self, url):
        self.url = url
    def parseRDF(self):
        '''Parse our RDF file and return a mapping of statements of the form {s→{p→o}} where s is a subject's
        URI, p is a predicate URI, and o is a list of objects that may be literals or URI references.'''
        graph = rdflib.ConjunctiveGraph()
        graph.parse(self.url)
        statements = {}
        for s, p, o in graph:
            predicates = statements.get(s, {})
            objects = predicates.get(p, [])
            objects.append(o)
            predicates[p] = objects
            statements[s] = predicates
        return statements
    def getRDFTypeURI(self, predicates):
        '''Get the type of the object being represented by the ``predicates``.  Return None if there's no type URI
        predicate at all.'''
        values = predicates.get(_typeURI, [])
        return values[0] if values else None
    def getSingleValue(self, predicateURI, predicates):
        '''Get the first value in the ``predicates`` with the given ``predicateURI`` or None if there is no such item.'''
        values = predicates.get(predicateURI, [])
        return unicode(values[0]) if values else None

class RDFPersonList(_RDFList):
    '''A list of EDRN people from RDF.'''
    def __init__(self, url):
        super(RDFPersonList, self).__init__(url)
        self.persons = []
        self.parse()
    def parse(self):
        statements = self.parseRDF()
        for subj, preds in statements.iteritems():
            if self.getRDFTypeURI(preds) != _personTypeURI: continue
            uid = self.getSingleValue(_userIDURI, preds)
            if not uid: continue
            email = self.stripMailTo(self.getSingleValue(_emailURI, preds))
            givenname, surname = self.getSingleValue(_givennameURI, preds), self.getSingleValue(_surnameURI, preds)
            siteURI = self.getSingleValue(_siteURI, preds)
            phone = self.parsePhone(self.getSingleValue(_phoneURI, preds))
            person = RDFPerson(unicode(subj), siteURI, email, uid, givenname, surname, phone)
            self.persons.append(person)
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
    def stripMailTo(self, email):
        return None if email is None else email[email.find(":")+1:len(email)]
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
        
class RDFSiteList(_RDFList):
    '''A list of EDRN sites from RDF.'''
    def __init__(self, url, personList):
        super(RDFSiteList, self).__init__(url)
        self.personList = personList
        self.sites = []
        self.parse()
    def parse(self):
        statements = self.parseRDF()
        for subj, preds in statements.iteritems():
            if self.getRDFTypeURI(preds) != _siteTypeURI: continue
            title = self.getSingleValue(_titleURI, preds)
            abbrevName = self.getSingleValue(_abbrevNameURI, preds)
            program = self.getSingleValue(_programURI, preds)
            memberType = self.getSingleValue(_memberTypeURI, preds)
            pi = getPersonById(self.getSingleValue(_piURI, preds), self.personList)
            staff = []
            for staffURI in preds.get(_staffURI, []):
                person = getPersonById(unicode(staffURI), self.personList)
                if person: staff.append(person)
            site = RDFSite(unicode(subj), abbrevName, staff, title, pi, program, memberType)
            self.sites.append(site)
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

class RDFCollaborativeGroupList(_RDFList):
    '''A list of collaborative groups from RDF.'''
    def __init__(self, filePath, personList):
        super(RDFCollaborativeGroupList, self).__init__(filePath)
        self.personList = personList
        self.groups = []
        self.parse()
    def parse(self):
        statements = self.parseRDF()
        for subj, preds in statements.iteritems():
            if self.getRDFTypeURI(preds) != _committeeTypeURI: continue
            title = self.getSingleValue(_titleURI, preds)
            groupType = self.getSingleValue(_groupTypeURI, preds)
            staff = set()
            for predicateURI in _allMemberURIs:
                for staffURI in preds.get(predicateURI, preds):
                    person = getPersonById(unicode(staffURI), self.personList)
                    if person: staff.add(person)
            cg = RDFCollaborativeGroup(unicode(subj), title, staff, groupType)
            self.groups.append(cg)
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
