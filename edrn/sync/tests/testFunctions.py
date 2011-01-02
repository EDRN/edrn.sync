# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''EDRN Sync Services - unit tests for functions.'''

from base import EDRNSyncTestCase
import unittest

class ImportRDFTest(EDRNSyncTestCase):
    '''Test the findFile function.'''
    def setUp(self):
        super(ImportRDFTest, self).setUp()

    def testX(self):
        return True
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ImportRDFTest))
    return suite
    
