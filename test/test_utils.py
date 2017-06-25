#!/usr/bin/env python
import os
import sys
import unittest

thispath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(thispath,"github_publish"))

"""
Utility functions needed by all test scripts.
"""
def getTestData(filename=""):
    return os.path.dirname(__file__) + "/data/" + filename


if __name__ == '__main__':
    unittest.main()