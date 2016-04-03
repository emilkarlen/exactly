import unittest

from . import help
from . import test_case


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_case.suite())
    ret_val.addTest(help.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
