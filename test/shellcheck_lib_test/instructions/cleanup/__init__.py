import unittest

from shellcheck_lib_test.instructions.cleanup import test_resources
from . import shell
from . import change_dir


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources.suite())
    ret_val.addTest(shell.suite())
    ret_val.addTest(change_dir.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
