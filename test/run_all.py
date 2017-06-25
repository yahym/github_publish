#!/usr/bin/env python

"""
Main test function to execute all tests found in the current directory
"""

import sys
import logging
import xmlrunner


try:
    import unittest2 as unittest
except ImportError:
    import unittest


def main():
    tests = unittest.TestLoader().discover('.', 'test_*.py')
    testResult=xmlrunner.XMLTestRunner(output='test-reports').run(tests)
    if testResult.wasSuccessful():
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
