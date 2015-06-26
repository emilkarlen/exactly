import unittest

from . import execution


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(execution.suite())
    return ret_val
