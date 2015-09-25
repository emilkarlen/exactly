import unittest

from shellcheck_lib_test.instructions.assert_phase import test_resources as assert_test_resources
from shellcheck_lib_test.instructions.setup import test_resources as setup_test_resources
from shellcheck_lib_test.instructions.cleanup import test_resources as cleanup_test_resources


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(setup_test_resources.suite())
    ret_val.addTest(assert_test_resources.suite())
    ret_val.addTest(cleanup_test_resources.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
