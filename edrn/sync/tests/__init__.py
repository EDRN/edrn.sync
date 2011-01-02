# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Sync Services: tests.'''

import unittest, testFunctions

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(testFunctions.test_suite())
    return suite
    
