import unittest

from . import formatter
from . import lists


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(lists.suite())
    ret_val.addTest(formatter.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
