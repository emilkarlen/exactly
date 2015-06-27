import unittest

from . import enumeration
from . import suite_hierarchy_reading
from . import execution


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(enumeration.suite())
    ret_val.addTest(suite_hierarchy_reading.suite())
    ret_val.addTest(execution.suite())
    return ret_val
