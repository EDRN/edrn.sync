# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''EDRN Sync Services — unit tests for classes.'''

import unittest2 as unittest
import pkg_resources
from edrn.sync.rdf import RDFPersonList, RDFSiteList, RDFCollaborativeGroupList
import xml.parsers.expat, xml.sax

class _RDFBaseTestCase(unittest.TestCase):
    '''Abstract testing base for RDF-list generators. Subclasses must implement ``constructTestList``.'''
    def constructTestList(self, url):
        '''Construct the correct RDF-list reading data from the given ``url``.'''
        raise NotImplementedError('Subclasses must implement ``constructTestList``')
    def testNonexistentFile(self):
        '''Ensure that constructing an RDF-list on a nonexistent file fails and raises an ``IOError``.'''
        self.assertRaises(IOError, self.constructTestList, '/some/non/existent/file.rdf')
    def testBadXMLFile(self):
        '''Make certain that making an RDF-list on a file with bad XML in it fails.'''
        badFile = 'file:' + pkg_resources.resource_filename(__name__, 'data/bad.xml')
        with self.assertRaises(Exception) as caught:
            self.constructTestList(badFile)
        # Can't assume what XML parser is being used...
        ex = caught.exception
        # But we can narrow it down a bit:
        if isinstance(ex, xml.sax.SAXParseException):
            ex = ex.getException()
        # And expat we can check:
        if isinstance(ex, xml.parsers.expat.ExpatError):
            self.assertEquals(xml.parsers.expat.errors.XML_ERROR_INVALID_TOKEN, xml.parsers.expat.ErrorString(ex.code))
    def testBadRDFFile(self):
        '''Check that making an RDF-list on a file with good XML but no RDF fails.'''
        badFile = 'file:' + pkg_resources.resource_filename(__name__, 'data/bad.rdf')
        l = self.constructTestList(badFile)
        self.assertEquals(0, len(l))

class RDFPersonListTest(_RDFBaseTestCase):
    '''Test the RDFPersonList class.'''
    def constructTestList(self, url):
        return RDFPersonList(url)
    def testGoodRDFFile(self):
        '''Confirm that we can read a good file of users RDF.'''
        goodFile = 'file:' + pkg_resources.resource_filename(__name__, 'data/users.rdf')
        l = RDFPersonList(goodFile)
        self.assertEquals(3, len(l))
        heathers = [i for i in l if i.uid == 'hkincaid']
        self.assertEquals(1, len(heathers), 'Heather not found in test data users.rdf')
        heather = heathers[0]
        self.assertEquals('http://edrn.nci.nih.gov/data/registered-person/3', heather.rdfId)
        self.assertEquals('http://edrn.nci.nih.gov/data/sites/2', heather.siteId)
        self.assertEquals('heather.kincaid@jpl.nasa.gov', heather.email)
        self.assertEquals('hkincaid', heather.uid)
        self.assertEquals('Heather', heather.firstname)
        self.assertEquals('Kincaid', heather.lastname)
        self.assertEquals('626-989-2216', heather.phone)
    def testPeopleWithoutEmail(self):
        '''Test to see if we can handle people without email addresses.'''
        personWithoutEmail = 'file:' + pkg_resources.resource_filename(__name__, 'data/no-email.rdf')
        l = RDFPersonList(personWithoutEmail)
        self.assertEquals(1, len(l))
        person = l[0]
        self.assertEquals('churchill', person.uid)

class RDFSiteListTest(_RDFBaseTestCase):
    '''Test the RDFSiteList class.'''
    def setUp(self):
        super(RDFSiteListTest, self).setUp()
        self.personList = RDFPersonList('file:' + pkg_resources.resource_filename(__name__, 'data/users.rdf'))
    def constructTestList(self, url):
        return RDFSiteList(url, self.personList)
    def testGoodRDFFile(self):
        '''Verify that we can read a good file of site RDF.'''
        goodFile = 'file:' + pkg_resources.resource_filename(__name__, 'data/sites.rdf')
        l = self.constructTestList(goodFile)
        self.assertEquals(2, len(l))
        jpls = [i for i in l if i.abbrevName == 'JPL']
        self.assertEquals(1, len(jpls), 'JPL not found in test data users.rdf')
        jpl = jpls[0]
        self.assertEquals('http://edrn.nci.nih.gov/data/sites/1', jpl.id)
        self.assertEquals('JPL', jpl.abbrevName)
        self.assertEquals('Jet Propulsion Laboratory', jpl.title)
        self.failUnless(jpl.program.startswith('Lorem ipsum'))
        self.assertEquals('Associate Member A - EDRN Funded', jpl.memberType)
        self.assertEquals('Mattmann', jpl.pi.lastname)
        self.assertEquals(1, len(jpl.staffList))
        self.assertEquals('Ramirez', jpl.staffList[0].lastname)

class RDFCollaborativeGroupListTest(_RDFBaseTestCase):
    '''Test the RDFCollaborativeGroupList class.'''
    def setUp(self):
        super(RDFCollaborativeGroupListTest, self).setUp()
        self.personList = RDFPersonList('file:' + pkg_resources.resource_filename(__name__, 'data/users.rdf'))
    def constructTestList(self, url):
        return RDFCollaborativeGroupList(url, self.personList)
    def testGoodRDFFile(self):
        '''Establish that we can read a good file of committee RDF.'''
        goodFile = 'file:' + pkg_resources.resource_filename(__name__, 'data/committees.rdf')
        l = self.constructTestList(goodFile)
        self.assertEquals(1, len(l))
        sc = l[0]
        self.assertEquals('http://edrn.nci.nih.gov/data/committees/1', sc.id)
        self.assertEquals('Steering Committee', sc.title)
        self.assertEquals('Committee', sc.groupType)
        self.assertEquals(3, len(sc.staffList))
        expected = set(['Kincaid', 'Mattmann', 'Ramirez'])
        got = set([i.lastname for i in sc.staffList])
        self.assertEquals(expected, got, 'Members of committee incorrect, expected %r, got %r' % (expected, got))

def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(RDFPersonListTest),
        unittest.makeSuite(RDFSiteListTest),
        unittest.makeSuite(RDFCollaborativeGroupListTest),
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
