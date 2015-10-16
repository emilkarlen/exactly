import unittest

from . import script_language_setup
from . import single_command_setup


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(script_language_setup.suite())
    ret_val.addTest(single_command_setup.suite())
    return ret_val
