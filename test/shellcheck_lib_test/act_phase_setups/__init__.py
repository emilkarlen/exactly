import unittest

from . import script_language_setup


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(script_language_setup.suite())
    return ret_val
