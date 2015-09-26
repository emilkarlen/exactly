import unittest

from shellcheck_lib_test.instructions.setup import test_resources
from shellcheck_lib_test.instructions.setup import install


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources.suite())
    ret_val.addTest(install.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
