import unittest

from . import formatting
from . import parse
from .test_resources import test_of_parse_test_resource


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_of_parse_test_resource.suite())
    ret_val.addTest(formatting.suite())
    ret_val.addTest(parse.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
