import unittest

from shellcheck_lib_test.test_case import error_description
from shellcheck_lib_test.test_case import processing_utils
from shellcheck_lib_test.test_case import preprocessor


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(error_description.suite())
    ret_val.addTest(processing_utils.suite())
    ret_val.addTest(preprocessor.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
