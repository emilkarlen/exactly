import unittest

from . import argument_parsing


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(argument_parsing.suite())
    return ret_val
