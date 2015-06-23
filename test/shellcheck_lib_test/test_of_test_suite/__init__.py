import unittest

from . import suite_hierarchy_reading


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(suite_hierarchy_reading.suite())
    return ret_val
