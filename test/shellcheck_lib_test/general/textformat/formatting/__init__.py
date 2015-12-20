import unittest

from . import lists
from . import paragraph_item
from . import section


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(lists.suite())
    ret_val.addTest(paragraph_item.suite())
    ret_val.addTest(section.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
