import unittest

from . import lists
from . import paragraph_item


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(lists.suite())
    ret_val.addTest(paragraph_item.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
