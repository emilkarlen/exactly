import unittest

from shellcheck_lib_test.instructions.before_assert import shell
from shellcheck_lib_test.instructions.before_assert import test_resources


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTests(test_resources.suite())
    ret_val.addTests(shell.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
