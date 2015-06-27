import unittest

from . import test_case
from . import test_suite


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_case.suite())
    return ret_val
