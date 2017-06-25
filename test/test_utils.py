#!/usr/bin/env python
import os
import sys
import unittest

thispath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(thispath,"github_publish"))

from github_publish.arg_parser import ArgHolder, ArgHandler
"""
Utility functions needed by all test scripts.
"""
def getTestData(filename=""):
    return os.path.dirname(__file__) + "/data/" + filename

class TestArgHolder(unittest.Testcase):
    
    def test_class_exists():
        assertTrue(ArgHolder)

if __name__ == '__main__':
    unittest.main()
